---
object_type: logos_repo_registry_documentation
trust_zone: canonical
lifecycle_status: active
provenance_note: "Created 2026-06-08 alongside governance/LOGOS_REPO_REGISTRY.yaml."
reason_for_inclusion: "Explain the Logos repository registry for humans and agents."
---

# Logos Repo Registry

`logos-governance-architecture` owns the Logos repo registry. Child repos may
mirror registry facts for local routing, but this governance repo is the source
of truth for repo identity, authority direction, and relationship changes.

Machine-readable registry: [`LOGOS_REPO_REGISTRY.yaml`](LOGOS_REPO_REGISTRY.yaml)

## Current Repos

| Repo | Role | Authority | Status |
|---|---|---|---|
| `logos-governance-architecture` | `governance_control_plane` | `cross_repo_policy_authority` | active |
| `logos-scripture-graph` | `canonical_scripture_data_plane` | `canonical_scripture_authority` | active |
| `logos-boundary-literature` | `boundary_reception_support_plane` | `supporting_context_not_canonical` | active |

## Current Ownership

### logos-governance-architecture

Owns cross-repo policy, repository registration, authority contracts, update
rules, validation patterns, the AI front-door standard, and data-flow map
standards.

It must not import texts, mutate Scripture data, mutate boundary-literature data,
or implement runtime integration as part of registry work.

### logos-scripture-graph

Owns the canonical 66-book Scripture corpus, canonical Scripture chunks,
reviewed Scripture gold/evaluator surfaces, and Scripture stress atlas/review
packets.

It must not own deuterocanonical/apocrypha corpora, noncanonical or boundary
texts, commentary corpora, gnostic/heterodox/fake/forged texts, or unscoped
boundary claims.

### logos-boundary-literature

Owns noncanonical and boundary literature metadata, deuterocanonical/apocrypha
source-intake planning, heterodox/gnostic/disputed/forged text governance,
commentary/reception claims, the trust hierarchy, and source-intake policy.

It supports `logos-scripture-graph`, but it must not override Scripture, equal
Scripture authority, mutate canonical Scripture records, supply default
Scripture meaning, or auto-promote claims into the Scripture graph.

## Planned Repos

Planned repos may be listed with `status: planned_not_created`. That status is
descriptive only. It does not create the repo, authorize source ingestion, or
authorize runtime integration.

| Planned repo | Future role | Authority |
|---|---|---|
| `logos-chunking-harness` | `cross_corpus_chunking_execution_plane` | `execution_harness_not_semantic_authority` |
| `logos-doctrine-genealogy` | `doctrine_lineage_and_profile_comparison_plane` | `interpretive_historical_profile_scoped` |

`logos-chunking-harness` may later own source-mode adapters, chunking execution,
cross-corpus experiments, evaluation harnesses, and promotion gates. It must not
own canonical Scripture truth or mix output namespaces.

`logos-doctrine-genealogy` may later own doctrine lineage, tradition/profile
comparison, ethical implication mapping, alignment/disalignment classifications,
and human judgment gates. It must not rewrite canonical Scripture or flatten
contested doctrine into universal truth.

## Registry Rules

- Any new Logos repo requires a registration issue before being treated as part
  of the project.
- Any new Logos repo must include an `AI_FRONT_DOOR.md`.
- Any new Logos repo must include a table of contents, data map, or documented
  exception.
- Any repo relationship change must update the governance registry first or in
  the same coordinated PR.
- Child repos may mirror registry entries, but the governance repo is the source
  of truth.
- AI must stop and report when it cannot determine the correct repo for a task.
- Creating a planned repo requires a new issue and a scaffold PR.

## Stop And Report

Stop and report when:

- the task owner repo cannot be determined;
- boundary material appears necessary to modify canonical Scripture output;
- a boundary-layer task treats governance as a target for workaround or weakening;
- a boundary-originated request targets higher-authority governance, repository-link
  contracts, canonical Scripture authority, canonical scope, trust hierarchy, or
  cross-repo policy;
- a boundary-originated higher-layer request lacks explicit Lowell Wong owner
  authorization in the higher-authority repo;
- a planned repo is treated as already created;
- a child repo contract conflicts with this registry;
- source text ingestion is requested without source-intake review;
- authority direction is unclear or reversed.

## Boundary-Originated Higher-Layer Changes

`BOUNDARY-GOV-001 - Governance Is Constraint, Not Obstacle` and
`BOUNDARY-GOV-002 - Owner-Reserved Authorization for Boundary-Originated
Higher-Layer Changes` are P0 stop-the-line rules.

Boundary-layer awareness of the wider Logos repo structure exists for routing,
provenance, and contamination control only. It does not authorize the boundary
repo, a boundary-layer agent, a contributor group, or an automated
recommendation to weaken governance or canonical Scripture authority.

Only Lowell Wong, as project owner, may authorize a boundary-originated request
to change higher-authority governance, canonical Scripture authority,
repository-link contracts, canonical scope, trust hierarchy, or cross-repo
policy.

Required policy and warning text:
[`BOUNDARY_GOVERNANCE_CONSTRAINTS.md`](BOUNDARY_GOVERNANCE_CONSTRAINTS.md)
