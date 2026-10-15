from __future__ import annotations

from pathlib import Path

import pytest
from conftest import copy_template_repository, generate_consumer, initialise_git, run


def _template_readme(source: Path, engine: str) -> Path:
    if engine == "cruft":
        return source / "templates/cookiecutter/python-api/{{cookiecutter.project_slug}}/README.md"
    return source / "templates/copier/python-api/README.md.jinja"


def _commit_version_two(source: Path, engine: str, *, conflict: bool) -> None:
    readme = _template_readme(source, engine)
    content = readme.read_text()
    if conflict:
        content = content.replace(
            "This project was generated from the Python API golden path.",
            "This template now requires the version-two onboarding path.",
        )
    else:
        content += "\n## Template maintenance proof\n\nThis section arrived with template v0.2.0.\n"
    readme.write_text(content)
    run(["git", "add", "."], cwd=source)
    run(["git", "commit", "-m", "Release template v0.2.0"], cwd=source)
    run(["git", "tag", "v0.2.0"], cwd=source)


def _update(engine: str, source: Path, project: Path, *, check: bool = True) -> int:
    if engine == "cruft":
        command = [
            "cruft",
            "update",
            "--project-dir",
            str(project),
            "--template-path",
            str(source),
            "--checkout",
            "v0.2.0",
            "--skip-apply-ask",
        ]
    else:
        command = [
            "copier",
            "update",
            "--defaults",
            "--vcs-ref",
            "v0.2.0",
            str(project),
        ]
    return run(command, check=check).returncode


@pytest.mark.lifecycle
@pytest.mark.parametrize("engine", ["cruft", "copier"])
def test_update_adds_template_change_and_preserves_local_file(
    engine: str,
    isolated_workspace: Path,
) -> None:
    root = isolated_workspace / f"lifecycle-clean-{engine}"
    source = copy_template_repository(root / "source")
    output = root / "consumers"
    output.mkdir()
    project, _ = generate_consumer(engine, source, output)
    initialise_git(project, "Generated consumer")

    local_file = project / "src" / "demo_api" / "local_feature.py"
    local_file.write_text('LOCAL_VALUE = "preserved"\n')
    run(["git", "add", "."], cwd=project)
    run(["git", "commit", "-m", "Add local feature"], cwd=project)

    _commit_version_two(source, engine, conflict=False)
    _update(engine, source, project)

    assert local_file.read_text() == 'LOCAL_VALUE = "preserved"\n'
    assert "This section arrived with template v0.2.0." in (project / "README.md").read_text()


@pytest.mark.lifecycle
@pytest.mark.integration
@pytest.mark.parametrize("engine", ["cruft", "copier"])
def test_concurrent_change_surfaces_a_conflict_that_can_be_resolved(
    engine: str,
    isolated_workspace: Path,
) -> None:
    root = isolated_workspace / f"lifecycle-conflict-{engine}"
    source = copy_template_repository(root / "source")
    output = root / "consumers"
    output.mkdir()
    project, _ = generate_consumer(engine, source, output)
    initialise_git(project, "Generated consumer")

    readme = project / "README.md"
    readme.write_text(
        readme.read_text().replace(
            "This project was generated from the Python API golden path.",
            "This consumer keeps a local onboarding path.",
        )
    )
    run(["git", "add", "README.md"], cwd=project)
    run(["git", "commit", "-m", "Customize onboarding"], cwd=project)

    _commit_version_two(source, engine, conflict=True)
    result = _update(engine, source, project, check=False)

    conflict_files = list(project.rglob("*.rej"))
    rendered = readme.read_text()
    assert result != 0 or conflict_files or "<<<<<<<" in rendered

    readme.write_text("# demo-api\n\nResolved lifecycle conflict explicitly.\n")
    for conflict_file in conflict_files:
        conflict_file.unlink()
    run(["uv", "sync"], cwd=project, env={"UV_LINK_MODE": "copy"})
    run(["uv", "run", "--locked", "pytest"], cwd=project)
