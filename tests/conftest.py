from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COOKIECUTTER_DIRECTORY = "templates/cookiecutter/python-api"


def run(
    command: list[str],
    *,
    cwd: Path = REPO_ROOT,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    process_env = os.environ.copy()
    process_env.update(env or {})
    return subprocess.run(
        command,
        cwd=cwd,
        check=check,
        env=process_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def initialise_git(repository: Path, message: str = "Initial template") -> None:
    run(["git", "init", "-b", "main"], cwd=repository)
    run(["git", "config", "user.name", "Golden Path Tests"], cwd=repository)
    run(["git", "config", "user.email", "tests@example.invalid"], cwd=repository)
    run(["git", "add", "."], cwd=repository)
    run(["git", "commit", "-m", message], cwd=repository)


def copy_template_repository(destination: Path) -> Path:
    shutil.copytree(
        REPO_ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", ".venv", ".tmp", "__pycache__"),
    )
    initialise_git(destination)
    run(["git", "tag", "v0.1.0"], cwd=destination)
    return destination


def answers(slug: str = "demo-api") -> dict[str, str]:
    return {
        "project_slug": slug,
        "project_description": 'An API with accents éè and "quotes"',
        "author_name": "Project contributors",
    }


def generate_consumer(
    engine: str,
    source: Path,
    output_root: Path,
    *,
    slug: str = "demo-api",
    check: bool = True,
    destination: Path | None = None,
    context_overrides: dict[str, str] | None = None,
) -> tuple[Path, subprocess.CompletedProcess[str]]:
    context = answers(slug)
    context.update(context_overrides or {})
    if engine == "cookiecutter":
        command = [
            "cookiecutter",
            str(source / COOKIECUTTER_DIRECTORY),
            "--no-input",
            "--default-config",
            "--output-dir",
            str(output_root),
            *(f"{key}={value}" for key, value in context.items()),
        ]
        project = output_root / slug
    elif engine == "cruft":
        command = [
            "cruft",
            "create",
            str(source),
            "--output-dir",
            str(output_root),
            "--directory",
            COOKIECUTTER_DIRECTORY,
            "--checkout",
            "v0.1.0",
            "--no-input",
            "--default-config",
            "--extra-context",
            json.dumps(context),
        ]
        project = output_root / slug
    elif engine == "copier":
        project = destination or output_root / slug
        command = [
            "copier",
            "copy",
            "--defaults",
            "--vcs-ref",
            "v0.1.0",
            *(item for key, value in context.items() for item in ("--data", f"{key}={value}")),
            str(source),
            str(project),
        ]
    else:
        raise ValueError(f"Unknown engine: {engine}")

    result = run(command, check=check)
    return project, result


@pytest.fixture(scope="session")
def isolated_workspace() -> Iterator[Path]:
    parent = REPO_ROOT / ".tmp"
    parent.mkdir(exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix="pytest-", dir=parent))
    try:
        yield workspace
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


@pytest.fixture(scope="session")
def template_repository(isolated_workspace: Path) -> Path:
    return copy_template_repository(isolated_workspace / "template-source")
