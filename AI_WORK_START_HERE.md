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

6. **Do not let semantic similarity masquerade as evidence.**
   - Chunking, vectorizing, retrieval neighborhoods, graph edges, and doctrine-lineage links require source basis, authority owner, scope, method, review status, and provenance before they can be treated as governed structure.

7. **Do not dilute the theological grounding into generic ethics.**
   - This project is explicitly Logos-grounded and theological.

8. **Do not change governance without correcting the governance map.**
   - Any governance-path change must update
     [`governance/GOVERNANCE_DEPENDENCY_MAP.yaml`](governance/GOVERNANCE_DEPENDENCY_MAP.yaml),
     register the changed governance path in map coverage, and review the
     relevant front-door, table-of-contents, work-start, validation, test, and
     downstream mirror surfaces.

## Recommended reading order

1. [`README.md`](README.md)
2. [`AI_TABLE_OF_CONTENTS.md`](AI_TABLE_OF_CONTENTS.md)
3. [`docs/governance/family-work-coordination.md`](docs/governance/family-work-coordination.md)
4. [`governance/registry/FAMILY_WORK_REGISTRY.yaml`](governance/registry/FAMILY_WORK_REGISTRY.yaml)
5. [`docs/governance/README.md`](docs/governance/README.md)
6. [`docs/governance/ontology-discipline.md`](docs/governance/ontology-discipline.md)
7. [`docs/governance/anchor-conventions.md`](docs/governance/anchor-conventions.md)
8. [`docs/governance/tag-registry.md`](docs/governance/tag-registry.md)
9. [`docs/governance/relationship-registry.md`](docs/governance/relationship-registry.md)
10. [`docs/governance/anti-guessing-and-evidence-discipline.md`](docs/governance/anti-guessing-and-evidence-discipline.md)
11. [`docs/governance/inference-policy.md`](docs/governance/inference-policy.md)
12. [`docs/governance/node-types.md`](docs/governance/node-types.md)
13. [`docs/roadmap/theological-buildout-roadmap.md`](docs/roadmap/theological-buildout-roadmap.md)
14. [`docs/roadmap/repository-integration-map.md`](docs/roadmap/repository-integration-map.md)
15. [`docs/governance/ai-workflow/goal-prompt-premortem-preflight.md`](docs/governance/ai-workflow/goal-prompt-premortem-preflight.md) before generating any goal prompt, next-agent prompt, handoff prompt, slash-style command prompt, or prompt sequence.

## Preferred work pattern

Before changing files:

0. Run family work preflight. Read the registry and latest worktree audit, then
   search the proposed task ID, roadmap refs, semantic tags, branch, and paths.
   Reuse or update the existing work ID where one exists. Register a new claim
   before non-claim edits. Stop for the owner if the validator finds risky or
   ambiguous overlap.

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

6. For chunking, vectorizing, graph, or retrieval work, identify what is asserted, what is inferred, what is only a candidate, and what evidence would be needed for promotion.

7. Report what changed, what was not verified, and what remains risky.

8. When generating a goal prompt or prompt sequence, include route/scope
   preflight, premortem, red-team, fix loop, validation, PR/merge policy, and
   residual-risk reporting. Slash-style commands are intent hints, not authority
   overrides.

9. When changing governance, include a governance-map impact check: name the
   dependency-map artifact updated, name any discovery surfaces updated or
   intentionally left unchanged, and run the dependency-map validator.

10. When work creates a reusable architecture lesson, audit finding, Fable/Codex
    feedback resolution, validator pattern, schema pattern, or cross-domain
    transfer pattern, update the relevant lesson/outbox surface. For the Fable
    doctrine-genealogy queue, use
    [`docs/roadmap/fable-kernels/DAD-LESSON-OUTBOX.md`](docs/roadmap/fable-kernels/DAD-LESSON-OUTBOX.md).

## Output expectations for AI work

When producing patches or recommendations, report:

- files changed
- files added
- files intentionally not changed
- assumptions
- commands run
- tests or validations run
- tests or validations not run
- lessons or DAD/outbox surfaces updated, or why no reusable lesson was created
- remaining risks

## Maintenance commands

Long maintenance runs belong in [`docs/maintenance.md`](docs/maintenance.md). Do not keep operational runbook details in the README unless they are needed by first-time readers.

