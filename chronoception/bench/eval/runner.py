"""Runner that converts (TaskInstance, AgentBackend, EvalSetting) -> Trajectory.

The runner is the single point where chrono-measurement actually happens.
Setting A vs Setting B (FRAMING.md §3.1) is applied here via system-prompt
construction. Wall-clock timestamps are taken from the backend's response.
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone

from chronoception.bench.eval.agents.base import AgentBackend, Message
from chronoception.bench.eval.settings import EvalSetting
from chronoception.bench.tasks.schema import TaskInstance
from chronoception.bench.trajectory import Step, Trajectory

__all__ = ["Runner", "run_instance"]


_INJECTION_TEMPLATE = "Current date and time: {iso_timestamp}."


class Runner:
    """Runs a single TaskInstance against an AgentBackend under a setting.

    The runner emits one Trajectory per call. Multi-turn interaction is not
    yet supported in the pilot scope (Phase 2 W1); each instance produces a
    single assistant response and a one-step trajectory.
    """

    def __init__(
        self,
        *,
        agent: AgentBackend,
        setting: EvalSetting,
        base_system_prompt: str = "You are a helpful assistant.",
    ) -> None:
        self._agent = agent
        self._setting = setting
        self._base_system_prompt = base_system_prompt

    def __call__(self, instance: TaskInstance) -> Trajectory:
        return run_instance(
            instance=instance,
            agent=self._agent,
            setting=self._setting,
            base_system_prompt=self._base_system_prompt,
        )


def run_instance(
    *,
    instance: TaskInstance,
    agent: AgentBackend,
    setting: EvalSetting,
    base_system_prompt: str = "You are a helpful assistant.",
) -> Trajectory:
    """Run a single TaskInstance against an AgentBackend.

    Setting B prepends a `Current date and time:` string to the system prompt.
    Setting A leaves the system prompt unchanged.

    The returned Trajectory has:
    - Two steps: one for the user message at t_start, one for the agent's
      response at t_end. (Multi-turn extension is future work.)
    - capability_code copied from instance.task
    - budget and budget_kind copied from instance and instance.task
    - tau_min copied from instance.task
    - metadata records the setting and the instance_id
    - self_narrated_duration left None; parsers fill it in later
    """
    system_prompt = base_system_prompt
    if setting is EvalSetting.WITH_INJECTION:
        iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
        injection = _INJECTION_TEMPLATE.format(iso_timestamp=iso)
        system_prompt = f"{injection}\n\n{base_system_prompt}"

    messages = [
        Message(role="system", content=system_prompt),
        Message(role="user", content=instance.prompt),
    ]

    t_start = time.time()
    response = agent(messages)
    t_end = response.wall_clock_emitted_at

    steps = [
        Step(state="<user_prompt>", action=instance.prompt, timestamp=t_start),
        Step(state="<agent_response>", action=response.content, timestamp=t_end),
    ]

    return Trajectory(
        task_id=instance.instance_id,
        agent_id=agent.agent_id,
        steps=steps,
        capability_code=instance.task.capability_code,
        budget=instance.budget,
        budget_kind=instance.task.budget_kind,
        tau_min=instance.task.tau_min_seconds,
        self_narrated_duration=None,
        metadata={
            "setting": setting.value,
            "instance_id": instance.instance_id,
            "task_id": instance.task.task_id,
            "system_prompt": system_prompt,
            "response_metadata": response.metadata,
            "runner_uuid": uuid.uuid4().hex,
        },
    )
