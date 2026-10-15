"""Reject unsafe or unsupported answers before creating the project."""

from __future__ import annotations

import keyword
import re
import sys

PROJECT_SLUG = {{ cookiecutter.project_slug | jsonify }}
PACKAGE_NAME = {{ cookiecutter.__package_name | jsonify }}
PROJECT_DESCRIPTION = {{ cookiecutter.project_description | jsonify }}
AUTHOR_NAME = {{ cookiecutter.author_name | jsonify }}

SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
RESERVED_PACKAGES = {
    "fastapi",
    "uvicorn",
    "pydantic",
    "pytest",
    "typing",
    "logging",
    "json",
}
WINDOWS_RESERVED = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}


def fail(message: str) -> None:
    print(f"Template validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


if len(PROJECT_SLUG) > 63 or not SLUG_PATTERN.fullmatch(PROJECT_SLUG):
    fail(
        "project_slug must be 1-63 characters, start with a lowercase ASCII letter, "
        "and contain lowercase letters, digits, and single hyphens only"
    )

if keyword.iskeyword(PACKAGE_NAME) or PACKAGE_NAME in RESERVED_PACKAGES:
    fail("project_slug produces a reserved Python package name")

if PROJECT_SLUG.lower() in WINDOWS_RESERVED or PACKAGE_NAME.lower() in WINDOWS_RESERVED:
    fail("project_slug produces a reserved Windows path name")

if not 1 <= len(PROJECT_DESCRIPTION) <= 180 or "\n" in PROJECT_DESCRIPTION or "\r" in PROJECT_DESCRIPTION:
    fail("project_description must contain 1-180 characters on one line")

if not 1 <= len(AUTHOR_NAME) <= 100 or "\n" in AUTHOR_NAME or "\r" in AUTHOR_NAME:
    fail("author_name must contain 1-100 characters on one line")
