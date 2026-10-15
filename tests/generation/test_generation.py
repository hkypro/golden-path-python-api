from __future__ import annotations

import hashlib
import json
import tomllib
from pathlib import Path

import pytest
import yaml
from conftest import generate_consumer


def _tree_digest(project: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in project.rglob("*") if item.is_file()):
        digest.update(path.relative_to(project).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


@pytest.mark.parametrize("engine", ["cookiecutter", "cruft", "copier"])
def test_each_entry_point_renders_a_safe_standalone_project(
    engine: str,
    template_repository: Path,
    isolated_workspace: Path,
) -> None:
    output = isolated_workspace / f"generation-{engine}"
    output.mkdir()
    project, _ = generate_consumer(
        engine,
        template_repository,
        output,
        slug=f"{engine}-api",
    )

    package = engine.replace("-", "_") + "_api"
    assert (project / "src" / package / "main.py").is_file()
    assert (project / "tests" / "test_api.py").is_file()
    assert (project / "Dockerfile").is_file()
    assert not (project / "uv.lock").exists()

    pyproject = (project / "pyproject.toml").read_text()
    metadata = tomllib.loads(pyproject)
    assert metadata["project"]["description"] == 'An API with accents éè and "quotes"'
    assert "{{" not in pyproject

    if engine == "cruft":
        cruft_metadata = json.loads((project / ".cruft.json").read_text())
        assert cruft_metadata["directory"] == "templates/cookiecutter/python-api"
    elif engine == "copier":
        copier_metadata = yaml.safe_load((project / ".copier-answers.yml").read_text())
        assert copier_metadata["_commit"] == "v0.1.0"
    else:
        assert not (project / ".cruft.json").exists()
        assert not (project / ".copier-answers.yml").exists()


@pytest.mark.parametrize("engine", ["cookiecutter", "cruft", "copier"])
@pytest.mark.parametrize(
    "slug",
    ["../escape", "bad name", "json", "a" * 64],
)
def test_invalid_slug_is_rejected_without_path_escape(
    engine: str,
    slug: str,
    template_repository: Path,
    isolated_workspace: Path,
) -> None:
    output = isolated_workspace / f"invalid-{engine}-{abs(hash(slug))}"
    output.mkdir()
    project, result = generate_consumer(
        engine,
        template_repository,
        output,
        slug=slug,
        check=False,
    )

    assert result.returncode != 0
    assert not project.exists()
    assert not (output.parent / "escape").exists()


@pytest.mark.parametrize("engine", ["cookiecutter", "cruft", "copier"])
def test_existing_destination_is_not_overwritten(
    engine: str,
    template_repository: Path,
    isolated_workspace: Path,
) -> None:
    output = isolated_workspace / f"existing-{engine}"
    destination = output / "demo-api"
    destination.mkdir(parents=True)
    sentinel = destination / "sentinel.txt"
    sentinel.write_text("preserve me\n")

    _, result = generate_consumer(
        engine,
        template_repository,
        output,
        check=False,
        destination=destination,
    )

    assert sentinel.read_text() == "preserve me\n"
    if engine != "copier":
        assert result.returncode != 0


@pytest.mark.parametrize("engine", ["cookiecutter", "cruft", "copier"])
def test_generation_is_stable_for_the_same_source_and_answers(
    engine: str,
    template_repository: Path,
    isolated_workspace: Path,
) -> None:
    first_root = isolated_workspace / f"stable-first-{engine}"
    second_root = isolated_workspace / f"stable-second-{engine}"
    first_root.mkdir()
    second_root.mkdir()

    first, _ = generate_consumer(engine, template_repository, first_root)
    second, _ = generate_consumer(engine, template_repository, second_root)

    assert _tree_digest(first) == _tree_digest(second)


@pytest.mark.parametrize("engine", ["cookiecutter", "cruft", "copier"])
def test_multiline_or_overlong_free_text_is_rejected(
    engine: str,
    template_repository: Path,
    isolated_workspace: Path,
) -> None:
    output = isolated_workspace / f"invalid-description-{engine}"
    output.mkdir()

    project, result = generate_consumer(
        engine,
        template_repository,
        output,
        check=False,
        context_overrides={"project_description": "x" * 181},
    )

    assert result.returncode != 0
    assert not project.exists()
