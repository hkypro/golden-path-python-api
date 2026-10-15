# Cookiecutter + Cruft and Copier

This comparison is limited to the API template and the versions locked by this repository.

| Concern | Cookiecutter + Cruft | Copier |
| --- | --- | --- |
| Direct generation | Familiar Cookiecutter questionnaire and hooks | Copier questionnaire and validators |
| Provenance | `.cruft.json` when created through Cruft | `.copier-answers.yml` |
| Repository subdirectory | Explicit `--directory` preserved by Cruft | Root `copier.yml` selects one rendered subdirectory |
| Update | Cruft regenerates and applies a diff | Copier uses its answers and Git-tag history |
| Validation | Small local Python pre-generation hook | Declarative Jinja validators |
| Consumer runtime dependency | None | None |

Observed locally: both engines generate the same installable application, preserve engine-specific
provenance, update from released Git tags, retain an independently committed consumer file, and
surface a concurrent edit instead of silently deleting it. Both resolved consumers passed their
application tests. Direct Cookiecutter remains useful when ongoing template updates are not
required.

Copier has the more compact update model because generation and updates are native to one tool.
Cookiecutter plus Cruft is useful when an existing Cookiecutter ecosystem matters or direct
Cookiecutter consumption must remain available. The MVP keeps both variants; a later template type
should choose one engine from its actual maintenance needs instead of duplicating both by default.

GitHub's “Use this template” feature is not the primary path because it creates a snapshot without
Cruft or Copier update metadata.
