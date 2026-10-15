from __future__ import annotations

import pytest
from pydantic import ValidationError

from {{ cookiecutter.__package_name }}.config import Settings


def test_process_environment_overrides_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_NAME", "configured-api")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings()

    assert settings.app_name == "configured-api"
    assert settings.log_level == "DEBUG"


def test_invalid_log_level_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "VERBOSE")

    with pytest.raises(ValidationError):
        Settings()
