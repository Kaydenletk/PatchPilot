import docker
import pytest


def _docker_available() -> bool:
    try:
        docker.from_env().ping()
    except Exception:
        return False
    return True


def pytest_collection_modifyitems(config, items):
    if _docker_available():
        return
    skip = pytest.mark.skip(reason="Docker daemon not running")
    for item in items:
        if "docker" in item.keywords:
            item.add_marker(skip)
