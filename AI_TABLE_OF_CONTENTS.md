# AI Table of Contents

This file maps the repository for AI agents, coding assistants, maintainers, and reviewers.

## Cross-Repo Project Family

- [`AI_FRONT_DOOR.md`](AI_FRONT_DOOR.md) - contribution lanes and cross-repo governance boundary
- [`DATA_FLOW_MAP.md`](DATA_FLOW_MAP.md) - current and future repo hierarchy and data flow
- [`governance/LOGOS_REPO_REGISTRY.md`](governance/LOGOS_REPO_REGISTRY.md) - human-readable repo registry
- [`governance/LOGOS_REPO_REGISTRY.yaml`](governance/LOGOS_REPO_REGISTRY.yaml) - machine-readable repo registry
- [`governance/BOUNDARY_GOVERNANCE_CONSTRAINTS.md`](governance/BOUNDARY_GOVERNANCE_CONSTRAINTS.md) - P0 stop rules for boundary-originated pressure on higher-authority repos
- [`governance/THREE_REPO_DATA_FLOW.md`](governance/THREE_REPO_DATA_FLOW.md) - current active three-repo data-flow map
- [`governance/FUTURE_FIVE_REPO_ARCHITECTURE.md`](governance/FUTURE_FIVE_REPO_ARCHITECTURE.md) - planned future five-repo topology
- [`governance/REPOSITORY_LINK_CONTRACTS.md`](governance/REPOSITORY_LINK_CONTRACTS.md) - link types and authority direction
- [`governance/AI_FRONT_DOOR_STANDARD.md`](governance/AI_FRONT_DOOR_STANDARD.md) - required front-door sections for Logos repos
- [`governance/ADDING_NEW_LOGOS_REPOS.md`](governance/ADDING_NEW_LOGOS_REPOS.md) - issue-based repo registration process
- [`docs/governance/logos-cross-repo-governance-contract.md`](docs/governance/logos-cross-repo-governance-contract.md) - upstream/downstream contract with `logos-scripture-graph`
- [`docs/governance/agent-hostile-protection.md`](docs/governance/agent-hostile-protection.md) - fail-closed agent-hostile protection policy
- [`docs/governance/noesis-boundary.md`](docs/governance/noesis-boundary.md) - Noesis may inform Logos, but may not modify or govern Logos

## Primary entry points

- [`README.md`](README.md) — human-facing landing page and project overview
- [`AI_WORK_START_HERE.md`](AI_WORK_START_HERE.md) — AI-agent operating instructions and guardrails
- [`docs/governance/README.md`](docs/governance/README.md) — governance conventions and vocabulary discipline
- [`docs/roadmap/theological-buildout-roadmap.md`](docs/roadmap/theological-buildout-roadmap.md) — practical buildout sequence
- [`docs/roadmap/repository-integration-map.md`](docs/roadmap/repository-integration-map.md) — repo-wide layer integration

## Constituent repositories (external surfaces)

- [`logos-scripture-graph`](https://github.com/lowelltwong-alt/logos-scripture-graph) - canonical 66-book Scripture data plane. Coupled by governance contract.
- [`logos-boundary-literature`](https://github.com/lowelltwong-alt/logos-boundary-literature) - supporting boundary/reception plane. It must not override or equal Scripture authority.
- `logos-chunking-harness` - planned, not created; future execution/evaluation plane, not semantic authority.
- `logos-doctrine-genealogy` - planned, not created; future doctrine lineage/profile-comparison plane, not canonical Scripture authority.

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
