# Python API Golden Path

Two maintainable project-template implementations for the same production-minded FastAPI
contract. The repository compares **Cookiecutter with Cruft** and **Copier** through generated
projects, not feature checklists.

## What the generated project includes

- Python 3.13, uv, FastAPI, Pydantic Settings, Ruff, mypy, and pytest;
- liveness, readiness, OpenAPI, and a small versioned endpoint;
- structured JSON request logs with server-generated request IDs;
- a non-root Docker image and a local Compose entry point;
- a locked GitHub Actions workflow;
- documented, testable template updates.

This is a local golden path with CI. It does not provision cloud infrastructure or publish
packages and images.

## Quick start

Install [uv](https://docs.astral.sh/uv/), then choose one entry point.

### Cookiecutter + Cruft

```bash
uvx --from cruft==2.16.0 cruft create \
  https://github.com/YOUR_GITHUB_OWNER/python-api-golden-path.git \
  --directory templates/cookiecutter/python-api
cd demo-api
uv sync
```

Use Cookiecutter directly when update provenance is not required:

```bash
uvx cookiecutter==2.7.1 \
  https://github.com/YOUR_GITHUB_OWNER/python-api-golden-path.git \
  --directory templates/cookiecutter/python-api
```

### Copier

```bash
uvx copier==9.19.1 copy \
  https://github.com/YOUR_GITHUB_OWNER/python-api-golden-path.git demo-api
cd demo-api
uv sync
```

Commit the generated `uv.lock`, then follow the generated README. Local development and template
maintenance are documented in [the quickstart](docs/quickstart.md) and
[the update guide](docs/updating.md).

## Verify this repository

```bash
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```

The test suite creates all consumers under temporary directories. It does not keep generated
demo applications in this repository.

## Status

See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for the evidence attached to each delivery
lot. The comparison remains evidence-driven; neither engine is presented as a universal winner.

## License

MIT. Generated projects also receive the MIT license.
