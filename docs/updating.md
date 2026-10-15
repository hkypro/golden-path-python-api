# Updating generated projects

Template updates are source changes, not an overwrite command. Start from a clean committed
consumer, create a branch, select a released template tag, inspect the diff, and rerun every check.

## Cruft

```bash
git switch -c chore/template-v0.2.0
uvx --from cruft==2.16.0 cruft update --checkout v0.2.0
git diff
```

Cruft reads `.cruft.json`, including the original repository, subdirectory, commit, and answers.
Do not hand-edit its commit to simulate a successful update.

## Copier

```bash
git switch -c chore/template-v0.2.0
uvx copier==9.19.1 update --vcs-ref v0.2.0
git diff
```

Copier reads `.copier-answers.yml`. Keep `_src_path` and `_commit`; normal project values can be
reviewed when an update asks for new answers.

## Resolve conflicts

Both engines perform a three-way-style reconciliation and can expose competing edits differently.
Look for command failure, inline Git markers, and `.rej` files. Never force an overwrite merely to
make the command green.

After resolving files:

```bash
uv sync
git diff -- uv.lock
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy src tests
uv run --locked pytest
docker compose build
```

Commit the resolved template metadata and lockfile together with the accepted source changes.
