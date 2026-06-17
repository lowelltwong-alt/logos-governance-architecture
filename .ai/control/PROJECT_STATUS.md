---
object_type: governance_project_status
trust_zone: governance_instructions
lifecycle_status: active
provenance_note: "Created 2026-06-08 for the Logos repo registry and future architecture branch."
reason_for_inclusion: "Record current cross-repo governance state for agents entering this repo."
---

# Project Status

**Last updated:** 2026-06-17
**Updated by:** Codex on branch `codex/governance-dependency-map`

## Current Status

`logos-governance-architecture` is the cross-repo governance/control-plane
authority for the Logos repo family.

Current active repos:

- `logos-governance-architecture`
- `logos-scripture-graph`
- `logos-boundary-literature`

Planned repos, not created:

- `logos-chunking-harness`
- `logos-doctrine-genealogy`

## Active Governance Work

Current governance/control-plane surfaces include:

- Logos repo registry;
- current three-repo data-flow map;
- planned five-repo architecture map;
- repository link contracts;
- AI front-door standard;
- issue-based repo registration process;
- governance status surface;
- governance dependency map at `governance/GOVERNANCE_DEPENDENCY_MAP.yaml`.

The dependency map records governance artifacts, owner authorization,
dependencies, downstream controls, mirrors, validators, and update triggers. It
is non-authorizing: it does not permit child repos to override governance,
change canonical Scripture data, or import boundary material.

## Boundary-Originated Governance Stop Rules

Active P0 rules:

- `BOUNDARY-GOV-001 - Governance Is Constraint, Not Obstacle`
- `BOUNDARY-GOV-002 - Owner-Reserved Authorization for Boundary-Originated Higher-Layer Changes`

Boundary-layer agents must stop and produce a human-readable warning when a
boundary-originated request appears to require changing higher-authority
governance, canonical Scripture authority, repository-link contracts, canonical
scope, trust hierarchy, or cross-repo policy. Only Lowell Wong, as project
owner, may authorize such a change in the higher-authority repository.

## Boundaries

This is governance/control-plane documentation only.

No Scripture data was mutated.
No boundary-literature data was mutated.
No texts were imported.
No runtime integration was created.
No chunk output, evaluator, leaderboard, or scorecard behavior changed.

## Next

After review, child repos may mirror or confirm registry entries as needed.
`logos-scripture-graph` T327B should proceed only after T327A and Scripture-side
routing guardrails are live.
