---
object_type: logos_learning_loop_operating_guide
trust_zone: canonical
lifecycle_status: active
provenance_note: "Created 2026-07-11 to explain the owner-approved D11 LLOS v1 contract."
reason_for_inclusion: "Make the learning loop usable without turning it into a new platform or authority channel."
---

# Logos Learning Loop Operating Standard

LLOS v1 is the Logos-family learning contract. It is a thin standard over each
repository's existing preflight, local candidate capture, human admission,
validation, postflight, and later effectiveness review. It is not a new DAD
runtime, a theological authority, or permission to change outputs.

The canonical machine contract is
[`governance/LOGOS_LEARNING_LOOP_OPERATING_STANDARD.yaml`](../../governance/LOGOS_LEARNING_LOOP_OPERATING_STANDARD.yaml).
Lessons conform to
[`schemas/llos/lesson.v1.schema.json`](../../schemas/llos/lesson.v1.schema.json)
and load categories from the governed route registry.

## Admission

A useful observation begins as `candidate`. Admission requires evidence,
scope limits, danger-if-misapplied, a validator reference, and human review.
AI, DAD, popularity, graph rank, or repeated use cannot admit a lesson or
satisfy an owner gate.

P0 and catastrophic or irreversible lessons never auto-sunset. Ordinary stale
lessons become review candidates; records are not automatically deleted.

## DAD Boundary

DAD is an external metadata sidecar. It may read an explicitly approved local
lesson index or outbox and copy allowlisted metadata to `DAD_DATA_ROOT`. It may
not write an inbox, contract, index, task, source file, or any other file inside
a Logos repository. Every future DAD-originated Logos write requires a new,
explicit approval from Lowell Wong. The 2026-07-11 rollout approval authorizes
this installation only and is not standing write permission.

Recommendations returning from DAD remain central candidates until a Logos
maintainer re-authors and reviews them locally. Raw source text, corpus rows,
private payloads, secrets, unreviewed theology claims, and authority-bearing
conclusions never cross the bridge.

Communication remains two-way without granting DAD a reverse write channel.
A Logos-local process writes its own outbox; DAD reads it and writes central
candidate records. Logos-local tooling may then read or pull those central
candidates. Any resulting Logos file change is a new local action subject to
local review, never a DAD push or direct inbox write.
