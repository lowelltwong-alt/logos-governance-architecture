# Governance

The [Engineering Practice Observatory](engineering-practice-observatory.md)
provides a recurring evidence and fit check for agent and software-development
methods. It never treats company size, reputation, or fashion as authority.

This folder holds the structural discipline documents for the Logos project.

These files exist to keep the repository recursive, ontology-ready, retrieval-friendly, and extensible without uncontrolled drift.

## Why this folder exists

This repository is designed to support:
- human-readable theological architecture
- semantic chunking for retrieval and RAG-style use
- recursive buildout across thinkers, doctrines, concepts, comparisons, and traditions
- future ontology promotion of repeated concepts
- scripture, translation, manuscript, and boundary-source control
- graph and concordance growth without silent architectural drift

Because of that, structure and vocabulary discipline are not cosmetic concerns. They are part of the architecture itself.

If anchors, tags, relationship verbs, node types, concept names, provenance fields, or trust classifications drift casually, the repository becomes harder to search, harder to compare, harder to extend, and harder to turn into a serious ontology later.

## Core operating rule

Contributors should avoid casually inventing new anchors, tags, node types, relationship verbs, or category names.

Preferred order of extension:

1. model the new thing as a node first
2. fit it into existing structure and vocabulary where possible
3. expand vocabulary only when the concept cannot fit cleanly
4. register new vocabulary before broad use
5. avoid structural redesign unless the current shell cannot represent the concept without distortion

## Files in this folder

### Core governance
- `ontology-discipline.md` — the main structural rule set
- `anchor-conventions.md` — base anchor families and address logic
- `tag-registry.md` — base controlled tag families and extension guidance
- `relationship-registry.md` — approved relationship verbs and usage guidance
- `anti-guessing-and-evidence-discipline.md` - guardrails against treating semantic similarity, embeddings, generated confidence, or graph convenience as evidence
- `node-types.md` — approved base node families

### Governance extensions and architecture control
- `architecture-invariants.md` — non-negotiable architecture invariants stated in testable terms
- `pr-architecture-invariants-checklist.md` — lightweight PR checklist for invariant validation
- `rollback-protocol-trust-zone-and-invariant-violations.md` — incident and rollback runbook for merges that violate trust-zone or invariant rules
- `anchor-conventions-scripture-and-graph-extension.md` — address extensions for scripture, boundary, and graph layers
- `tag-registry-scripture-and-boundary-extension.md` — tag extensions for scripture, translation, manuscript, and boundary-source layers
- `node-types-scripture-and-boundary-extension.md` — node-type extensions for scripture, hermeneutic, translation, manuscript, and noncanonical layers
- `exceptions-lake-and-learning-loop.md` — governed exception-capture and adaptation-promotion model aligned to AIRCA stages
- `exceptions-lake-architecture-decision.md` — architecture-level decision preserving the exceptions-lake layer as reviewable memory instead of silent mutation
- `exceptioncase-and-learningsignal-primitives.md` — governed learning primitives that keep exception capture separate from approved change
- `exceptions-lake-integration-note.md` — landing map showing where exceptions-lake import concepts were absorbed
- `change-taxonomy.yaml` — machine-readable change classification vocabulary aligned to the cleaned governance surface
- `branch-reconciliation-register.md` — branch cleanup, preservation, unknown-branch docket, and clean-trunk audit evidence for stale branches, safety branches, Codex worktrees, and parallel-agent leftovers
- `family-work-coordination.md` - mandatory work identity, claim, lease, overlap, reconciliation, and GitHub Project projection workflow for all family tasks and worktrees
- `biblical-connection-vocabulary.md` — first approved subset of scholar-recognizable biblical and theological relationship terms for future governed graph and retrieval work
- `doctrine-genealogy-vocabulary.md` - controlled vocabulary for planned doctrine-genealogy schemas and validators
- `scripture-taxonomy-and-ontology.md` — scripture-layer ontology design for books, chapters, pericopes, texts, and interpretations
- `textual-traditions-translation-and-noncanonical-sources.md` — structure for original languages, translations, manuscripts, and noncanonical source handling
- `noncanonical-and-heresy-classification.md` — classification framework for noncanonical, pseudepigraphal, forged, and heretical materials
- `translation-trust-and-sectarian-classification.md` — trust and boundary framework for Bible translations and disputed renderings
- `internal-link-conventions.md` — canonical style guide for internal relative links and file naming policy

### Machine-readable registries
- `../../governance/registry/entity_ids.yaml` - shared identity registry scaffold for persons, councils, schools/movements, and instruments
- `../../governance/registry/FAMILY_WORK_REGISTRY.yaml` - active family work IDs, task/path claims, leases, dependencies, and overlap resolutions

## How to use this folder

A contributor usually should read this governance layer in roughly this order:

1. `ontology-discipline.md`
2. `anchor-conventions.md`
3. `tag-registry.md`
4. `relationship-registry.md`
5. `anti-guessing-and-evidence-discipline.md`
6. `inference-policy.md`
7. `node-types.md`

Then read the relevant extensions when working in:
- scripture
- original languages
- translations
- manuscripts
- noncanonical materials
- graph or concordance structures

## Related governed branches

The repository now also includes a future primary-sources branch that should be read as a governed extension of the ontology rather than as a separate side project.

See:
- `docs/primary-sources/README.md`
- `docs/primary-sources/ontology-and-taxonomy.md`
- `docs/roadmap/biblical-primary-sources-future-framework.md`

## Project principle

The shell should stay stable.  
The branches can keep growing.  
Repeated concepts can become trunks of their own.

That is the practical meaning of fractal discipline in this repository.

## Decision traceability

- `pr-decision-ledger-2026-04-08.md` — maps major merged PRs to architecture-rule touchpoints and approval rationale
- `pr-decision-ledger-inferred-mappings-2026-04-08.md` — proposed-zone sidecar for inferred PR-to-rule mappings pending reviewer validation
- `module-intentional-change-and-drift-notes-2026-04-08.md` — proposed-zone notes for last intentional change and suspected drift by module
- `governed-metadata-audit-2026-04-08.md` — metadata coverage checkpoint for governed governance docs
- `zone-promotion-periodic-review-checklist.md` — recurring checklist for trust-zone promotions (for example proposed -> canonical)
