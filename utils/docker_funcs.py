"""
Utility functions for using docker to run bash commands
Specifically to check the setup/build image and run a command
"""

import os

import docker
from dotenv import load_dotenv


load_dotenv()

image_name = os.getenv("DOCKER_IMAGE_NAME")
workspace_dir = os.getenv("WORKSPACE_DIR")
client = docker.from_env()


def _build_image():
    # assume Dockerfile is in root
    client.images.build(path=".", tag=image_name)


def check_docker_setup():
    """
    Checks the docker environment variables
    If image does not exist, builds it
    """

    assert image_name, "DOCKER_IMAGE_NAME environment variable not found"
    assert workspace_dir, "WORKSPACE_DIR environment variable not found"

    # tests if the image exists
    try:
        client.images.get(image_name)
    except docker.errors.ImageNotFound:
        # if not, builds it
        _build_image()


def run_bash_command(command):
    """
    Run the given command in bash command
    """

    client.containers.run(
        image_name,
        command=["bash", "-c", command],
        remove=True,
        network_disabled=True,
        mem_limit="512m",
        cpu_count=1,
        privileged=False,
        volumes={workspace_dir: {"bind": "/workspace", "mode": "rw"}},
    )
