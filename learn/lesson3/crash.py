import docker

client = docker.from_env()

container = client.containers.create(
    "sandbox-runner:latest",
    ["python", "-c", "raise ValueError('boom')"],
)
try:
    container.start()
    result = container.wait()
    print("exit code:", result["StatusCode"])
    print(container.logs().decode())
finally:
    container.remove()
