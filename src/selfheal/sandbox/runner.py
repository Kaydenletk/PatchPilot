"""Run untrusted code inside a locked-down Docker container.

YOUR JOB: implement run_in_sandbox(). The helper below is already done.
Everything you need was in learn/lesson3 (crash.py, timeout.py) plus Lesson 2.
"""

from __future__ import annotations

import io
import tarfile

import docker

from selfheal.config import Settings
from selfheal.models import SandboxResult

PYTEST_COMMAND = ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider"]


def _make_tar(files: dict[str, str]) -> bytes:
    """Pack {filename: text} into an in-memory tar archive for put_archive()."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as tar:
        for name, text in files.items():
            data = text.encode("utf-8")
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            info.mode = 0o644
            info.uid = 1000
            info.gid = 1000
            tar.addfile(info, io.BytesIO(data))
    return buffer.getvalue()


def run_in_sandbox(files: dict[str, str], settings: Settings | None = None) -> SandboxResult:
    """Run pytest on `files` in a container and report what happened.

    Steps (see the README in the chat for hints):
      1. client = docker.from_env()
      2. containers.create(...) with the walls from `settings`
      3. put_archive("/workspace", _make_tar(files))
      4. start, then wait(timeout=settings.timeout_s)
         - on timeout: kill the container and remember timed_out=True
      5. reload(); read State.OOMKilled and State.ExitCode
      6. read stdout and stderr separately with logs(...)
      7. ALWAYS remove(force=True) in a finally block
      8. measure duration with time.perf_counter()
    """
    settings = settings or Settings()
    raise NotImplementedError("TODO: write run_in_sandbox")
