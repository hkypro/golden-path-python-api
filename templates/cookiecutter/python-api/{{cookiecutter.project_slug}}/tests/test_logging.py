from __future__ import annotations

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from {{ cookiecutter.__package_name }}.config import Settings
from {{ cookiecutter.__package_name }}.main import create_app


def _records(output: str) -> list[dict[str, object]]:
    return [json.loads(line) for line in output.splitlines() if line.startswith("{")]


def test_request_log_is_correlated_and_omits_query_string(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = create_app(Settings(app_name="log-api"))

    with TestClient(app) as client:
        response = client.get("/api/v1/hello", params={"name": "Alice"})

    captured = capsys.readouterr()
    matching = [
        record for record in _records(captured.out) if record["event"] == "request_completed"
    ]
    assert len(matching) == 1
    record = matching[0]
    assert response.headers["X-Request-ID"] == record["request_id"]
    assert record["route"] == "/api/v1/hello"
    assert record["service"] == "log-api"
    duration_ms = record["duration_ms"]
    assert isinstance(duration_ms, int | float)
    assert duration_ms >= 0
    assert "Alice" not in captured.out


def test_internal_error_is_generic_and_correlated(capsys: pytest.CaptureFixture[str]) -> None:
    app: FastAPI = create_app(Settings(app_name="error-api"))

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("private detail")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/boom")

    captured = capsys.readouterr()
    failed = [record for record in _records(captured.out) if record["event"] == "request_failed"]
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert response.headers["X-Request-ID"] == failed[0]["request_id"]
    assert "private detail" not in response.text
