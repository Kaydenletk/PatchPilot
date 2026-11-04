"""Tests for the sandbox runner. They start RED; make them GREEN one by one.

Run one at a time:   uv run pytest tests/test_sandbox.py -k passing -v
Run all:             uv run pytest tests/test_sandbox.py -v
"""

import pytest

from selfheal.config import Settings
from selfheal.models import SandboxResult
from selfheal.sandbox import run_in_sandbox

pytestmark = pytest.mark.docker

FAST = Settings(timeout_s=3)


def test_passing_code_succeeds():
    files = {"test_ok.py": "def test_ok():\n    assert 2 + 2 == 4\n"}

    result = run_in_sandbox(files, FAST)

    assert isinstance(result, SandboxResult)
    assert result.passed
    assert result.exit_code == 0
    assert "1 passed" in result.stdout


def test_failing_assertion_reports_failure():
    files = {"test_bad.py": "def test_bad():\n    assert 1 == 2\n"}

    result = run_in_sandbox(files, FAST)

    assert not result.passed
    assert result.exit_code == 1
    assert "assert 1 == 2" in result.stdout


def test_two_files_can_import_each_other():
    files = {
        "calc.py": "def add(a, b):\n    return a + b\n",
        "test_calc.py": "from calc import add\n\ndef test_add():\n    assert add(1, 2) == 3\n",
    }

    result = run_in_sandbox(files, FAST)

    assert result.passed


def test_infinite_loop_is_killed_by_timeout():
    files = {"test_loop.py": "def test_loop():\n    while True:\n        pass\n"}

    result = run_in_sandbox(files, FAST)

    assert result.timed_out
    assert not result.passed
    assert result.duration_ms < 6000  # killed near the 3s limit, not left running


def test_memory_hog_is_reported_as_oom():
    files = {
        "test_hog.py": (
            "def test_hog():\n"
            "    x = []\n"
            "    while True:\n"
            "        x.append('a' * 10**6)\n"
        )
    }

    result = run_in_sandbox(files, Settings(timeout_s=20))

    assert result.oom
    assert result.exit_code == 137
    assert not result.passed


def test_network_is_blocked():
    # This test PASSES inside the container only if the network is really off.
    files = {
        "test_net.py": (
            "import urllib.request, urllib.error\n"
            "import pytest\n\n"
            "def test_net():\n"
            "    with pytest.raises(urllib.error.URLError):\n"
            "        urllib.request.urlopen('http://example.com', timeout=2)\n"
        )
    }

    result = run_in_sandbox(files, FAST)

    assert result.passed


def test_no_container_is_left_behind():
    import docker

    client = docker.from_env()
    before = {c.id for c in client.containers.list(all=True)}

    run_in_sandbox({"test_ok.py": "def test_ok():\n    assert True\n"}, FAST)
    run_in_sandbox({"test_loop.py": "def test_l():\n    while True:\n        pass\n"}, FAST)

    after = {c.id for c in client.containers.list(all=True)}
    assert after == before
