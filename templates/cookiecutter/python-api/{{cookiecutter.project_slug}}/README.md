# {{ cookiecutter.project_slug }}

{{ cookiecutter.project_description }}

This project was generated from the Python API golden path. It is intentionally small: application
code, tests, a reproducible dependency lock, a non-root container, and CI use the same commands.

## Bootstrap

Install [uv](https://docs.astral.sh/uv/), then create and commit the consumer lockfile:

```bash
uv sync
git add uv.lock
```

The first resolution needs network access. Later checks refuse a missing or stale lockfile.

## Verify

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy src tests
uv run --locked pytest
```

## Run locally

```bash
uv run --locked uvicorn {{ cookiecutter.__package_name }}.main:app \
  --host 127.0.0.1 --port 8000 --no-access-log
```

Try:

```bash
curl --fail http://127.0.0.1:8000/health/ready
curl --fail 'http://127.0.0.1:8000/api/v1/hello?name=Alice'
```

Copy `.env.example` to `.env` for development overrides. Process environment variables take
precedence. `.env` is ignored by Git and Docker.

## Run in Docker

The image build requires the committed `uv.lock`:

```bash
docker compose up --build -d
curl --fail http://127.0.0.1:8000/health/ready
docker compose logs
docker compose down --remove-orphans
```

If port 8000 is occupied, set `API_PORT`, for example `API_PORT=8080 docker compose up --build`.

## Template updates

Commit local work and use a dedicated branch before updating.

- Cruft consumer: `cruft update --checkout <template-tag>`
- Copier consumer: `copier update --vcs-ref <template-tag>`

Inspect the diff, resolve any conflict markers or `.rej` files, regenerate `uv.lock` when
dependencies change, and rerun all checks. Direct Cookiecutter generations have no update
provenance unless they are linked to Cruft explicitly.
