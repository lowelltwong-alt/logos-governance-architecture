# AI Work Start Here

This file is the operational front door for AI agents, coding assistants, and future maintainers working inside this repository.

Human readers should start with [`README.md`](README.md). AI agents should start here, then consult [`AI_TABLE_OF_CONTENTS.md`](AI_TABLE_OF_CONTENTS.md).

## Project identity

This repository is **Logos Governance Architecture**: a Logos-grounded theological source architecture for AI-era governance.

It exists to make assumptions about truth, personhood, authority, delegation, provenance, and human accountability explicit, traceable, and reviewable.

Do not treat this repository as a generic notes collection, chatbot prompt library, or ordinary AI ethics checklist.

## Core thesis

No decision architecture is neutral.

Every decision system already assumes answers to questions about reality, truth, personhood, authority, responsibility, delegation, and what counts as a good outcome. This repository makes those assumptions explicit and governable.

## Non-negotiable guardrails

AI agents working in this repository must follow these guardrails:

1. **Do not invent canonical claims.**
   - New theology, doctrine, authority, node types, tags, anchors, relationship verbs, or governance rules require explicit review and registration.

2. **Do not collapse doctrine, ordering, and weighting.**
   - Doctrine states a theological object.
   - Ordering defines consultation sequence.
   - Weighting defines relative force in judgment.

3. **Do not let runtime examples become canon.**
   - Exceptions, examples, and observed failures can inform review, but they do not automatically rewrite source authority.

4. **Do not make model outputs self-certifying.**
   - Model outputs may assist work, but governance validity comes from source authority, derivation, review, and human accountability.

5. **Do not redesign the recursive shell casually.**
   - Prefer adding nodes and relationships inside the existing structure before changing the structure itself.

6. **Do not dilute the theological grounding into generic ethics.**
   - This project is explicitly Logos-grounded and theological.

## Recommended reading order

1. [`README.md`](README.md)
2. [`AI_TABLE_OF_CONTENTS.md`](AI_TABLE_OF_CONTENTS.md)
3. [`docs/governance/README.md`](docs/governance/README.md)
4. [`docs/governance/ontology-discipline.md`](docs/governance/ontology-discipline.md)
5. [`docs/governance/anchor-conventions.md`](docs/governance/anchor-conventions.md)
6. [`docs/governance/tag-registry.md`](docs/governance/tag-registry.md)
7. [`docs/governance/relationship-registry.md`](docs/governance/relationship-registry.md)
8. [`docs/governance/node-types.md`](docs/governance/node-types.md)
9. [`docs/roadmap/theological-buildout-roadmap.md`](docs/roadmap/theological-buildout-roadmap.md)
10. [`docs/roadmap/repository-integration-map.md`](docs/roadmap/repository-integration-map.md)

## Preferred work pattern

Before changing files:

1. Identify which layer the change belongs to:
   - source authority
   - doctrine
   - ordering
   - weighting
   - derivation
   - LAIRCA configuration
   - AIRCA crosswalk
   - scripture / interpretation
   - original-language / manuscript / translation control
   - graph / relationship object
   - primary-sources horizon
   - maintenance / tooling

2. Check whether the relevant vocabulary already exists.

3. Prefer extending existing structure over creating a new structure.

4. Add or update cross-references only where they are real.

5. Do not create fake file paths, fake registries, fake schemas, or fake build status.

6. Report what changed, what was not verified, and what remains risky.

## Output expectations for AI work

When producing patches or recommendations, report:

- files changed
- files added
- files intentionally not changed
- assumptions
- commands run
- tests or validations run
- tests or validations not run
- remaining risks

## Maintenance commands

Long maintenance runs belong in [`docs/maintenance.md`](docs/maintenance.md). Do not keep operational runbook details in the README unless they are needed by first-time readers.

