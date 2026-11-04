import docker
from requests.exceptions import ConnectionError, ReadTimeout

client = docker.from_env()

container = client.containers.create(
    "sandbox-runner:latest",
    ["python", "-c", "while True: pass"],
)
try:
    container.start()
    try:
        container.wait(timeout=3)
    except (ReadTimeout, ConnectionError):
        ___  # 1: stop the container
        print("timed out, killed")
finally:
    ___  # 2: delete the container, even though it may still be running
