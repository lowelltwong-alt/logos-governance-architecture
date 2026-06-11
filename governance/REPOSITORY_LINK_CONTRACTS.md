---
object_type: logos_repository_link_contracts
trust_zone: canonical
lifecycle_status: active
provenance_note: "Created 2026-06-08 to define link types and authority direction for Logos repos."
reason_for_inclusion: "Prevent cross-repo references from becoming implicit authority transfers."
---

# Repository Link Contracts

Repository links are governance contracts. A link may permit reference,
comparison, validation, or execution, but it does not automatically transfer
authority.

## Link Types

| Link type | Meaning | Authority transfer |
|---|---|---|
| `governance_contract` | Governance repo defines policy, registry, authority direction, and update rules. | From governance repo to child repo only. |
| `supporting_context_link` | A supporting repo provides scoped background, reception, comparison, or refutation material. | No canonical authority transfer. |
| `read_only_adapter` | A future execution repo reads another repo through an adapter. | No semantic authority transfer. |
| `external_advisory_link` | An external project may provide reviewed comparison context. | No write access, governance, authority, promotion, demotion, or derivation transfer. |
| `registration_issue` | A GitHub issue proposes a new repo or relationship change. | No authority until registry update is accepted. |

## Active Contracts

| From | To | Link type | Rule |
|---|---|---|---|
| `logos-governance-architecture` | `logos-scripture-graph` | `governance_contract` | Governance defines cross-repo policy; Scripture owns canonical Scripture data. |
| `logos-governance-architecture` | `logos-boundary-literature` | `governance_contract` | Governance defines cross-repo policy; boundary repo owns scoped boundary/reception support material. |
| `logos-scripture-graph` | `logos-boundary-literature` | `supporting_context_link` | Scripture refs may point outward to boundary/reception materials as background or comparison. |
| `logos-boundary-literature` | `logos-scripture-graph` | `supporting_context_link` | Boundary material may reference Scripture, but it must not override or equal Scripture authority. |

## External Advisory Contracts

| From | To | Link type | Rule |
|---|---|---|---|
| `noesis-atlas` | Logos repo family | `external_advisory_link` | Noesis may connect as reviewed, read-only advisory comparison context. It must not modify, gate, govern, promote, demote, or supply authority or derivation for any Logos repo. |

External advisory links do not become stronger when advisory material is pasted
into a PR body, issue, review comment, handoff, task note, generated note, or
committed file. `EXTERNAL-ADVISORY-001` and `COMMENT-AUTHORITY-001` require
quarantine, non-authoritative labeling, Logos-native re-authoring, and explicit
owner authorization before advisory material can affect Logos behavior.

## Planned Contracts

| From | To | Link type | Rule |
|---|---|---|---|
| `logos-chunking-harness` | `logos-scripture-graph` | `read_only_adapter` | Future canonical-mode chunking reads Scripture data without owning canonical truth. |
| `logos-chunking-harness` | `logos-boundary-literature` | `read_only_adapter` | Future boundary-mode chunking preserves boundary namespace and authority. |
| `logos-chunking-harness` | `logos-doctrine-genealogy` | `read_only_adapter` | Future doctrine-mode chunking must preserve profile scope and human gates. |
| `logos-doctrine-genealogy` | `logos-scripture-graph` | `supporting_context_link` | Doctrine lineage may reference Scripture IDs, but it must not rewrite Scripture records. |
| `logos-doctrine-genealogy` | `logos-boundary-literature` | `supporting_context_link` | Doctrine lineage may reference boundary/reception materials with trust and provenance scope. |

## Contract Rules

- Authority direction must be explicit.
- Data-flow direction must be explicit.
- A child repo may mirror a contract but must not redefine the registry source
  of truth.
- Child Logos repos must not claim authority above the governance registry,
  repository contracts, or canonical Scripture scope.
- Noesis may connect through `external_advisory_link` only; it must not modify,
  govern, gate, promote, demote, or provide authority or derivation for Logos.
- Noesis may not indirectly authorize Logos changes through comments, PR
  reviews, issues, handoffs, task files, generated notes, hidden advisory text,
  or pasted rationale.
- GitHub comments, PR bodies, issue comments, review comments, chat transcripts,
  generated notes, and pasted external analysis are not Logos authority.
- A planned contract must not be treated as a runtime integration.
- A boundary-originated request must not automate a permission request, route an
  approval request into a higher-authority repo, or bundle a governance change
  with boundary intake.
- A boundary-originated request to change higher-authority governance,
  canonical Scripture authority, repository-link contracts, canonical scope,
  trust hierarchy, or cross-repo policy requires explicit owner authorization by
  Lowell Wong in the higher-authority repo.
- If a task would reverse authority direction, stop and report.

## Boundary-Originated Conflict Warning

When a boundary-layer task conflicts with higher-authority governance, use the
warning in [`BOUNDARY_GOVERNANCE_CONSTRAINTS.md`](BOUNDARY_GOVERNANCE_CONSTRAINTS.md).
