from __future__ import annotations

import shutil
import socket
import time
import urllib.request
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
import yaml
from conftest import generate_consumer, run


@pytest.fixture(scope="session")
def consumer_projects(
    template_repository: Path,
    isolated_workspace: Path,
) -> Iterator[dict[str, Path]]:
    projects: dict[str, Path] = {}
    for engine in ("cookiecutter", "cruft", "copier"):
        output = isolated_workspace / f"contract-{engine}"
        output.mkdir()
        project, _ = generate_consumer(
            engine,
            template_repository,
            output,
            slug=f"contract-{engine}-api",
        )
        run(["uv", "sync"], cwd=project, env={"UV_LINK_MODE": "copy"})
        projects[engine] = project
    yield projects


@pytest.mark.integration
@pytest.mark.parametrize("engine", ["cookiecutter", "cruft", "copier"])
def test_generated_project_passes_the_common_quality_contract(
    engine: str,
    consumer_projects: dict[str, Path],
) -> None:
    project = consumer_projects[engine]
    commands = (
        ["uv", "run", "--locked", "ruff", "check", "."],
        ["uv", "run", "--locked", "ruff", "format", "--check", "."],
        ["uv", "run", "--locked", "mypy", "src", "tests"],
        ["uv", "run", "--locked", "pytest"],
    )

    for command in commands:
        result = run(command, cwd=project, check=False)
        assert result.returncode == 0, result.stdout


@pytest.mark.integration
@pytest.mark.parametrize("engine", ["cruft", "copier"])
def test_lockfile_is_required_after_bootstrap(
    engine: str,
    consumer_projects: dict[str, Path],
    isolated_workspace: Path,
) -> None:
    source = consumer_projects[engine]
    project = isolated_workspace / f"missing-lock-{engine}"
    shutil.copytree(source, project, ignore=shutil.ignore_patterns(".venv", "uv.lock"))

    result = run(["uv", "sync", "--locked"], cwd=project, check=False)

    assert result.returncode != 0
    assert "lock" in result.stdout.lower()


def test_rendered_workflow_is_valid_and_uses_pinned_actions(
    consumer_projects: dict[str, Path],
) -> None:
    workflow = consumer_projects["copier"] / ".github" / "workflows" / "ci.yml"
    parsed = yaml.safe_load(workflow.read_text())
    content = workflow.read_text()

    assert isinstance(parsed, dict)
    assert "actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803" in content
    assert "astral-sh/setup-uv@37802adc94f370d6bfd71619e3f0bf239e1f3b78" in content
    assert "pull_request_target" not in content
    assert "uv sync --locked" in content


def _free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _wait_until_ready(port: int) -> None:
    url = f"http://127.0.0.1:{port}/health/ready"
    last_error: Exception | None = None
    for _ in range(40):
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception as error:
            last_error = error
            time.sleep(0.5)
    raise AssertionError(f"Container did not become ready: {last_error}")


@pytest.mark.docker
@pytest.mark.integration
@pytest.mark.skipif(shutil.which("docker") is None, reason="Docker is not installed")
@pytest.mark.parametrize("engine", ["cruft", "copier"])
def test_generated_container_runs_as_non_root_and_serves_health(
    engine: str,
    consumer_projects: dict[str, Path],
) -> None:
    project = consumer_projects[engine]
    suffix = uuid.uuid4().hex[:10]
    image = f"golden-path-python-api-{engine}:{suffix}"
    container = f"golden-path-python-api-{engine}-{suffix}"
    port = _free_port()

    build = run(["docker", "build", "--tag", image, "."], cwd=project, check=False)
    assert build.returncode == 0, build.stdout
    identity = run(["docker", "run", "--rm", image, "id", "-u"], cwd=project)
    assert identity.stdout.strip() != "0"

    try:
        run(
            [
                "docker",
                "run",
                "--detach",
                "--rm",
                "--name",
                container,
                "--publish",
                f"127.0.0.1:{port}:8000",
                image,
            ],
            cwd=project,
        )
        _wait_until_ready(port)
    finally:
        run(["docker", "rm", "--force", container], cwd=project, check=False)
        run(["docker", "image", "rm", "--force", image], cwd=project, check=False)
