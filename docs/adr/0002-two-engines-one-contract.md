# ADR 0002: Compare two engines against one contract

- Status: accepted
- Date: 2026-10-15

## Decision

Cookiecutter 2.7.1 with Cruft 2.16.0 and Copier 9.19.1 render separate, readable template trees.
They share generation, application, container, and lifecycle acceptance tests. Tags version the
single API contract and both implementations together.

## Consequences

Some source duplication is intentional. The project does not create an intermediate template
language or converter. Future template types are not added to this repository merely to reuse the
tooling; Copier's tag-based update model is especially clearer when a repository owns one logical
template.
