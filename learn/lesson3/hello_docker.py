import docker

client = docker.from_env()
container = client.containers.create(
    "sandbox-runner:latest",
    ["python", "-c", "print(2 + 2)"],
)
try:
     container.start()
     container.wait()
     print(container.logs().decode())
finally:
     container.remove()
     
