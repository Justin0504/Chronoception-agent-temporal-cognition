"""Tests for the T3.1 paraphrase-robustness experiment.

Covers (1) the run script's guarantee that paraphrase variants see identical
sub-tasks, and (2) the analyzer's within-agent spread and cross-agent rank
stability logic.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS = _ROOT / "scripts"
for p in (str(_ROOT), str(_SCRIPTS)):
    if p not in sys.path:
        sys.path.insert(0, p)

import analyze_t31_paraphrase as ana  # noqa: E402
import run_t31_paraphrase_robustness as run  # noqa: E402
from chronoception.bench import generate_t3_1_instances  # noqa: E402


# ---------- sub-task matching (the experiment's control) ----------


def test_matched_sub_tasks_reproduce_generator_selection() -> None:
    """Every paraphrase must see the same sub-tasks the generator would pick."""
    matched = run._matched_sub_tasks(seed=0, count=10)
    gen = generate_t3_1_instances(seed=0, count=10)
    gen_sub_tasks = [run._T3_1_SUB_TASKS[inst.metadata["sub_task_index"]] for inst in gen]
    assert matched == gen_sub_tasks


def test_build_instances_applies_template_and_keeps_subtasks() -> None:
    sub_tasks = ["Write a haiku about autumn.", "Explain what photosynthesis is in plain language."]
    insts = run._build_instances("v1_casual", run.PARAPHRASES["v1_casual"], sub_tasks)
    assert len(insts) == 2
    assert "Write a haiku about autumn." in insts[0].prompt
    assert insts[0].metadata["paraphrase_variant"] == "v1_casual"
    # Different variant, same sub-task -> different wording, same task content.
    insts_b = run._build_instances("v2_formal", run.PARAPHRASES["v2_formal"], sub_tasks)
    assert insts_b[0].prompt != insts[0].prompt
    assert "Write a haiku about autumn." in insts_b[0].prompt


# ---------- rho ----------


def test_rho_log_ratio() -> None:
    assert ana._rho({"self_narrated_duration": 100.0, "tau_wall": 10.0}) == 1.0
    assert ana._rho({"self_narrated_duration": 10.0, "tau_wall": 10.0}) == 0.0


def test_rho_none_on_zero_wall() -> None:
    assert ana._rho({"self_narrated_duration": 10.0, "tau_wall": 0.0}) is None
    assert ana._rho({"self_narrated_duration": None, "tau_wall": 5.0}) is None


# ---------- spearman ----------


def test_rankdata_handles_ties() -> None:
    assert ana._rankdata([10.0, 20.0, 20.0, 40.0]) == [1.0, 2.5, 2.5, 4.0]


def test_spearman_perfect_and_anti() -> None:
    assert abs(ana._spearman([1, 2, 3, 4], [10, 20, 30, 40]) - 1.0) < 1e-9
    assert abs(ana._spearman([1, 2, 3, 4], [40, 30, 20, 10]) - (-1.0)) < 1e-9


# ---------- end-to-end analyze ----------


def _write(base: Path, agent: str, variant: str, setting: str, tau_self: float, tau_wall: float, n: int = 5) -> None:
    d = base / agent / variant / "T3.1" / setting
    d.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        traj = {
            "self_narrated_duration": tau_self,
            "tau_wall": tau_wall,
            "metadata": {"setting": setting, "paraphrase_variant": variant},
        }
        (d / f"T3.1.{i:03d}.json").write_text(json.dumps(traj), encoding="utf-8")


def test_within_agent_robust(tmp_path: Path) -> None:
    # All variants give nearly the same |rho| (~1.0) -> small spread -> robust.
    for v, ts in zip(run.PARAPHRASES, [100, 105, 98, 102, 99]):
        _write(tmp_path, "agentA", v, "no_injection", tau_self=ts, tau_wall=10.0)
    res = ana.analyze(tmp_path, "no_injection", spread_threshold=0.20, rank_threshold=0.80)
    assert res["within_agent"]["agentA"]["robust"] is True
    assert res["within_verdict"] == "ROBUST"


def test_within_agent_not_robust(tmp_path: Path) -> None:
    # One variant is a wild outlier -> spread exceeds threshold -> not robust.
    for v, ts in zip(run.PARAPHRASES, [100, 105, 98, 102, 10000]):
        _write(tmp_path, "agentA", v, "no_injection", tau_self=ts, tau_wall=10.0)
    res = ana.analyze(tmp_path, "no_injection", spread_threshold=0.20, rank_threshold=0.80)
    assert res["within_agent"]["agentA"]["robust"] is False
    assert res["within_verdict"] == "NOT ROBUST"


def test_cross_agent_rank_stability(tmp_path: Path) -> None:
    # Two agents with a consistent ordering across all variants:
    # agentA always higher |rho| than agentB -> Spearman = 1.0 on every pair.
    for v in run.PARAPHRASES:
        _write(tmp_path, "agentA", v, "no_injection", tau_self=1000.0, tau_wall=10.0)  # |rho|=2
        _write(tmp_path, "agentB", v, "no_injection", tau_self=100.0, tau_wall=10.0)   # |rho|=1
    res = ana.analyze(tmp_path, "no_injection", spread_threshold=0.20, rank_threshold=0.80)
    rs = res["rank_stability"]
    assert abs(rs["mean_pairwise_spearman"] - 1.0) < 1e-9
    assert rs["rank_stable"] is True
