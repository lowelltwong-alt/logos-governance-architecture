---
object_type: logos_repo_registry_roadmap
trust_zone: proposed
lifecycle_status: active
provenance_note: "Created 2026-06-08 to connect the repo registry branch to the public roadmap surface."
reason_for_inclusion: "Summarize the current and planned Logos repository topology without creating planned repos."
---

# Logos Repo Registry And Future Architecture

This roadmap note tracks the governance work needed to make Logos repo
relationships self-describing.

## Current Topology

- `logos-governance-architecture` owns cross-repo policy, registry, contracts,
  update rules, and validation patterns.
- `logos-scripture-graph` owns canonical 66-book Scripture records, chunks, and
  reviewed Scripture gold/evaluator surfaces.
- `logos-boundary-literature` owns boundary, noncanonical, commentary,
  reception, trust, and source-intake governance.

## Planned Topology

- `logos-chunking-harness` is planned as a cross-corpus execution/evaluation
  plane, not semantic authority.
- `logos-doctrine-genealogy` is planned as a doctrine lineage and
  profile-comparison plane, not canonical Scripture authority.

## Sequencing

1. Establish the registry and repo-registration process here.
2. Confirm or mirror routing guardrails in child repos where needed.
3. Use registration issues before adding any new Logos repo.
4. Keep T327 canonical-scope correction in `logos-scripture-graph` separate from
   future repo scaffolding.

## Deferred

- Creating `logos-chunking-harness`.
- Creating `logos-doctrine-genealogy`.
- Runtime adapters.
- Text ingestion.
- Any chunk-output or evaluator changes.
