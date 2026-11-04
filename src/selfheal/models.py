"""Shared data types. Frozen: build a new object instead of changing one."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SandboxResult(BaseModel):
    """What happened when code ran inside the container."""

    model_config = ConfigDict(frozen=True)

    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    oom: bool = False
    timed_out: bool = False

    @property
    def passed(self) -> bool:
        return self.exit_code == 0 and not self.oom and not self.timed_out
