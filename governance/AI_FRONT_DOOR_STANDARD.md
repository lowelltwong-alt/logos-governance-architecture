---
object_type: logos_ai_front_door_standard
trust_zone: governance_instructions
lifecycle_status: active
provenance_note: "Created 2026-06-08 to define the required front-door block for every Logos repo."
reason_for_inclusion: "Ensure agents can identify repo identity, authority, routing, and stop conditions before acting."
---

# AI Front Door Standard

Every Logos repo must include an `AI_FRONT_DOOR.md`. The front door is the first
file an AI or human contributor should read before changing repository state.

## Required Sections

1. Repo identity.
2. Authority level.
3. Current project topology.
4. Future project topology, if planned.
5. What this repo owns.
6. What this repo must not own.
7. Related repos.
8. Routing table.
9. Data-flow direction.
10. Stop-and-report triggers.
11. Validation commands.
12. How to add or update repo relationships.

## Required Rules

- The front door must name the repo and its authority level.
- The front door must point to this governance registry when cross-repo routing
  is relevant.
- The front door must state what the repo owns and what it must not own.
- The front door must include a routing table for common cross-repo tasks.
- The front door must list stop-and-report triggers.
- The front door must not grant itself authority above the governance registry.

## Stop-And-Report Triggers

A Logos front door must tell agents to stop and report when:

- the correct repo cannot be determined;
- a task would move data against authority direction;
- source text ingestion lacks source-intake review;
- boundary material would modify canonical Scripture records;
- a boundary-layer task treats governance as a target for workaround,
  weakening, automated approval routing, or bundled policy change;
- a boundary-originated request to change higher-authority governance,
  canonical Scripture authority, repository-link contracts, canonical scope,
  trust hierarchy, or cross-repo policy lacks explicit Lowell Wong owner
  authorization in the higher-authority repo;
- execution harness output is treated as semantic authority;
- doctrine-lineage claims are treated as universal truth without profile scope;
- a planned repo is treated as active without registration.

## Validation

Each repo should publish its local validation commands. If no validation exists
yet, the front door must say so and require a basic file-existence and YAML parse
check for registry or control-plane changes.
