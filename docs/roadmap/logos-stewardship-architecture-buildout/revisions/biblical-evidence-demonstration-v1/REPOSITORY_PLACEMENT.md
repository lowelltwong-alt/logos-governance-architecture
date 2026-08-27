---
object_type: repository_placement_decision
trust_zone: proposed
lifecycle_status: draft
provenance_note: "Created 2026-08-26 by applying the Logos Academic Extension Contract to a concrete evidence slice."
reason_for_inclusion: "Keep portfolio demonstration, Scripture identities, contextual evidence, and doctrine genealogy separated while preserving typed cross-repository links."
---

# Repository placement

| Repository | Owns | Does not own in this slice |
|---|---|---|
| `logos-governance-architecture` | This public demonstration, contracts, schemas, prompts, validators, rights gates, and portfolio navigation. | Canonical verse/chunk payloads, an archaeology corpus, or doctrine conclusions. |
| `logos-scripture-graph` | Stable Scripture/verse identities, translation witnesses, original-language alignment, candidate chunks, and future manuscript pointers. | Archaeological truth or doctrine promotion. |
| `logos-boundary-literature` | Candidate contextual-source and reception records when a separately authorized domain pack is approved. | Canonical Scripture or Christian doctrine authority. |
| `logos-doctrine-genealogy` | Later, tradition-scoped doctrine lineage and reception objects. | Raw archaeology/manuscript evidence or authority inherited from context. |

The P66 JPEG is duplicated here only as a licensed public demonstration asset,
not as the canonical manuscript repository. A future source repository may hold
the durable asset identity and expose a content-addressed pointer. Creating a new
`logos-historical-evidence` repository remains a human-gated scaling decision.

Cross-repository references must identify repository, ref/commit, path, object
identifier, and lifecycle status. A missing or uncommitted source is represented
as non-durable evidence, never silently upgraded to a stable endpoint.
