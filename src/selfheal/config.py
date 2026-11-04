"""Runtime configuration. All limits live here so CLI, dashboard and sandbox agree."""

from __future__ import annotations

import os
from dataclasses import dataclass

SANDBOX_IMAGE = "sandbox-runner:latest"
MEM_LIMIT = "256m"
CPU_QUOTA = 1.0
PIDS_LIMIT = 64
DEFAULT_TIMEOUT_S = 5
DEFAULT_MAX_RETRIES = 3
DEFAULT_MODEL = "gpt-5"


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")
    return value


@dataclass(frozen=True)
class Settings:
    image: str = SANDBOX_IMAGE
    mem_limit: str = MEM_LIMIT
    cpu_quota: float = CPU_QUOTA
    pids_limit: int = PIDS_LIMIT
    timeout_s: int = DEFAULT_TIMEOUT_S
    max_retries: int = DEFAULT_MAX_RETRIES
    model: str = DEFAULT_MODEL

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            timeout_s=_env_int("SELFHEAL_TIMEOUT_S", DEFAULT_TIMEOUT_S),
            max_retries=_env_int("SELFHEAL_MAX_RETRIES", DEFAULT_MAX_RETRIES),
            model=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL),
        )
