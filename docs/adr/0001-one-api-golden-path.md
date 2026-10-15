# ADR 0001: Ship one API golden path

- Status: accepted
- Date: 2026-10-15

## Decision

The first public product is one stateless Python API golden path. It includes generation, local
development, quality checks, container execution, CI, diagnostics, and template updates. Database,
authentication, cloud deployment, Backstage, data pipelines, web applications, and libraries are
outside this release.

## Consequences

The repository can be finished and tested as one release unit. Future golden paths receive their
own repository only when they have a distinct lifecycle and a demonstrated repeated use case.
