"""Evaluation harness: settings, runner, and agent backends.

Re-exports the public evaluation API. All concepts trace to FRAMING.md.
"""

from chronoception.bench.eval.runner import Runner, run_instance
from chronoception.bench.eval.settings import EvalSetting, epsilon_by_setting

__all__ = [
    "EvalSetting",
    "epsilon_by_setting",
    "Runner",
    "run_instance",
]
