# AI Table of Contents

This file maps the repository for AI agents, coding assistants, maintainers, and reviewers.

## Primary entry points

- [`README.md`](README.md) — human-facing landing page and project overview
- [`AI_WORK_START_HERE.md`](AI_WORK_START_HERE.md) — AI-agent operating instructions and guardrails
- [`docs/governance/README.md`](docs/governance/README.md) — governance conventions and vocabulary discipline
- [`docs/roadmap/theological-buildout-roadmap.md`](docs/roadmap/theological-buildout-roadmap.md) — practical buildout sequence
- [`docs/roadmap/repository-integration-map.md`](docs/roadmap/repository-integration-map.md) — repo-wide layer integration

## Constituent repositories (external surfaces)

- [`logos-scripture-graph`](https://github.com/lowelltwong-alt/logos-scripture-graph) — data-plane substrate implementing the scripture, translation/manuscript, boundary-source, and graph/concordance layers (3, 4, 6, 7, 8). Coupled by contract; see `docs/roadmap/repository-integration-map.md` → "Constituent repositories".

## Governance and vocabulary discipline

- [`docs/governance/ontology-discipline.md`](docs/governance/ontology-discipline.md)
- [`docs/governance/anchor-conventions.md`](docs/governance/anchor-conventions.md)
- [`docs/governance/anchor-conventions-scripture-and-graph-extension.md`](docs/governance/anchor-conventions-scripture-and-graph-extension.md)
- [`docs/governance/tag-registry.md`](docs/governance/tag-registry.md)
- [`docs/governance/tag-registry-scripture-and-boundary-extension.md`](docs/governance/tag-registry-scripture-and-boundary-extension.md)
- [`docs/governance/relationship-registry.md`](docs/governance/relationship-registry.md)
- [`docs/governance/node-types.md`](docs/governance/node-types.md)
- [`docs/governance/node-types-scripture-and-boundary-extension.md`](docs/governance/node-types-scripture-and-boundary-extension.md)

## Scripture, translation, and boundary-source governance

- [`docs/governance/scripture-taxonomy-and-ontology.md`](docs/governance/scripture-taxonomy-and-ontology.md)
- [`docs/governance/bible-classification-taxonomy.md`](docs/governance/bible-classification-taxonomy.md) — multi-axis passage classification vocabulary (promoted from taxonomy-scaffold v0.2; consumed by logos-scripture-graph)
- [`docs/governance/scholarly-crosscheck-bibliography.md`](docs/governance/scholarly-crosscheck-bibliography.md) — frameworks to validate the taxonomy before promotion
- [`docs/governance/textual-traditions-translation-and-noncanonical-sources.md`](docs/governance/textual-traditions-translation-and-noncanonical-sources.md)
- [`docs/governance/noncanonical-and-heresy-classification.md`](docs/governance/noncanonical-and-heresy-classification.md)
- [`docs/governance/translation-trust-and-sectarian-classification.md`](docs/governance/translation-trust-and-sectarian-classification.md)

## Exception lake and learning loop

- [`docs/governance/exceptions-lake-and-learning-loop.md`](docs/governance/exceptions-lake-and-learning-loop.md)
- [`docs/governance/exceptions-lake-integration-note.md`](docs/governance/exceptions-lake-integration-note.md)
- [`docs/roadmap/exceptions-lake-learning-loop-roadmap-extension.md`](docs/roadmap/exceptions-lake-learning-loop-roadmap-extension.md)
- [`data/graph/schemes/exceptions-lake.md`](data/graph/schemes/exceptions-lake.md)

## Graph and concordance surfaces

- [`data/graph/README.md`](data/graph/README.md)
- [`data/graph/schemes/primary-sources.md`](data/graph/schemes/primary-sources.md)

## Primary-sources horizon

- [`docs/roadmap/biblical-primary-sources-future-framework.md`](docs/roadmap/biblical-primary-sources-future-framework.md)
- [`docs/primary-sources/README.md`](docs/primary-sources/README.md)
- [`docs/primary-sources/ontology-and-taxonomy.md`](docs/primary-sources/ontology-and-taxonomy.md)

## Maintenance

- [`docs/maintenance.md`](docs/maintenance.md)

## AI-agent rule

If a referenced file does not exist in the local checkout, do not invent its contents. Report it as missing and recommend either creating it or removing the link.
