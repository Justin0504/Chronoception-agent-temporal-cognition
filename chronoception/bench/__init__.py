"""ChronoBench — diagnostic benchmark for agent temporal cognition.

Re-exports the public API. All definitions trace back to FRAMING.md.
"""

from chronoception.bench.eval import EvalSetting, Runner, epsilon_by_setting, run_instance
from chronoception.bench.eval.agents import (
    AgentBackend,
    AgentResponse,
    EchoBackend,
    FixedResponseBackend,
    Message,
)
from chronoception.bench.metrics import (
    car,
    chronoceptive_calibration_error,
    confabulation_ratio,
    epsilon,
    parkinson_coefficient,
)
from chronoception.bench.tasks.instances import (
    generate_full_benchmark_instances,
    generate_pilot_instances,
    generate_t1_1_instances,
    generate_t1_2_instances,
    generate_t1_3_instances,
    generate_t2_1_instances,
    generate_t2_2_instances,
    generate_t2_3_instances,
    generate_t3_1_instances,
    generate_t3_2_instances,
    generate_t3_3_instances,
)
from chronoception.bench.trajectory import (
    Step,
    Trajectory,
)

__all__ = [
    # trajectory
    "Step",
    "Trajectory",
    # metrics
    "parkinson_coefficient",
    "car",
    "confabulation_ratio",
    "chronoceptive_calibration_error",
    "epsilon",  # alias
    # evaluation settings + runner
    "EvalSetting",
    "epsilon_by_setting",
    "Runner",
    "run_instance",
    # agent backends
    "AgentBackend",
    "AgentResponse",
    "Message",
    "EchoBackend",
    "FixedResponseBackend",
    # pilot task generators
    "generate_t1_1_instances",
    "generate_t1_2_instances",
    "generate_t1_3_instances",
    "generate_t2_1_instances",
    "generate_t2_2_instances",
    "generate_t2_3_instances",
    "generate_t3_1_instances",
    "generate_t3_2_instances",
    "generate_t3_3_instances",
    "generate_pilot_instances",
    "generate_full_benchmark_instances",
]
