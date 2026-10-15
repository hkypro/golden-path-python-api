# Quickstart

The repository exposes three entry points for one generated API contract. Use a released Git tag in
real projects. The public repository is owned by `hkypro`.

## Prerequisites

- Git;
- uv 0.11.21 or a compatible verified release;
- Docker with Compose for the container path.

Python 3.13 is downloaded by uv when it is not already available. WSL2 is the documented Windows
path; Linux is the validated reference.

## Generate with Cruft

Cruft adds update provenance to the Cookiecutter generation:

```bash
uvx --from cruft==2.16.0 cruft create \
  https://github.com/hkypro/golden-path-python-api.git \
  --directory templates/cookiecutter/python-api \
  --checkout v0.1.0
```

## Generate with Copier

```bash
uvx copier==9.19.1 copy \
  --vcs-ref v0.1.0 \
  https://github.com/hkypro/golden-path-python-api.git demo-api
```

Cookiecutter 2.7.1 can use the same Cookiecutter subdirectory directly, but that entry point does
not write Cruft provenance.

## Bootstrap and verify

From the generated directory:

```bash
uv sync
git init
git add .
git commit -m "Bootstrap generated API"
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy src tests
uv run --locked pytest
```

The first `uv sync` creates the consumer-owned `uv.lock`. Commit it. The template repository lock
is never copied into a consumer.

## Run

Use the exact package name shown in the generated README:

```bash
uv run --locked uvicorn demo_api.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Or use the locked non-root container:

```bash
docker compose up --build -d
curl --fail http://127.0.0.1:8000/health/ready
docker compose down --remove-orphans
```
