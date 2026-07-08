---
object_type: fable_architecture_kernel_index
trust_zone: proposed
lifecycle_status: draft
provenance_note: "Created 2026-07-06 by Fable during the owner-commissioned master architecture pass (Phase 1 of docs/roadmap/fable-master-architecture-buildout-plan.md), following the Opus pre-read handoff. Updated 2026-07-06 by Codex to point future agents to the recorded owner selections D1-D10. Updated 2026-07-07 to route agents to DR-OPTION-A schema mirror status, audit evidence, and the Wave-2 architecture handoff with owner selections D11-D16."
reason_for_inclusion: "One index for the Fable architecture kernels so Codex, reviewers, and the owner can find every kernel, its status, and its non-authorizations."
---

# Fable Architecture Kernels — Index

These files are the Phase 1 deliverable of
[`../fable-master-architecture-buildout-plan.md`](../fable-master-architecture-buildout-plan.md).
They are **architecture decisions, not implementations, and not authority**.

`ai_usage_posture: staging_only_not_auto_promote`

## Non-authorization block (applies to every file in this folder)

These kernels do **not** authorize:

- creating `logos-doctrine-genealogy` or `logos-chunking-harness`;
- creating any doctrine, view, formulation, assessment, or genealogy-edge data record in any repo;
- Scripture output or chunk changes; reviewed-gold promotion;
- graph/retrieval/vector truth; source imports; boundary material as Scripture authority;
- Noesis as Logos authority; any denominational systematic theology as project authority.

Every structural decision below marked **(Dn)** requires the owner decision recorded in
[`OWNER-DECISIONS-AND-PILOTS.md`](OWNER-DECISIONS-AND-PILOTS.md) before Codex may implement it
as a governed surface.

Owner selections D1-D10 are recorded in
[`OWNER-DECISIONS-AND-PILOTS.md`](OWNER-DECISIONS-AND-PILOTS.md), section
`Recorded Owner Selections (2026-07-06)`, decision record ID
`FABLE-D1-D10-2026-07-06`.

Wave-2 owner selections D11-D16 are recorded in the same file, section
`Recorded Wave-2 Owner Selections (2026-07-07)`, decision record ID
`FABLE-WAVE2-D11-D16-2026-07-07`.

## Kernel map

| File | Covers | Hard problems |
|---|---|---|
| [`KERNEL-A-object-model-and-vocabulary.md`](KERNEL-A-object-model-and-vocabulary.md) | Doctrine-genealogy object model, relationship-verb registry, time discipline, cross-repo entity identity | HP1, HP8 |
| [`KERNEL-B-orthodoxy-and-authority.md`](KERNEL-B-orthodoxy-and-authority.md) | Orthodoxy boundary as structure, denominational-capture prevention, source authority ladder S0–S7 | HP2, HP3 |
| [`KERNEL-C-provenance-and-gates.md`](KERNEL-C-provenance-and-gates.md) | Evidence/provenance standard, promotion ladder, original-language and textual-critical gates | HP4, HP6 |
| [`KERNEL-D-evidence-product.md`](KERNEL-D-evidence-product.md) | Cross-repo evidence packet shape, namespace rules, packet linter | HP5 |
| [`KERNEL-E-codex-theology-tripwire.md`](KERNEL-E-codex-theology-tripwire.md) | Mechanical test separating transcription of recorded decisions from theological judgment during implementation | HP9 (gap pass) |
| [`OWNER-DECISIONS-AND-PILOTS.md`](OWNER-DECISIONS-AND-PILOTS.md) | Pilot slice options + recommendation, consolidated owner decisions D1–D10 | HP7 |
| [`CODEX_HANDOFF.md`](CODEX_HANDOFF.md) | Sequenced deterministic work queue for Codex after owner decisions | — |
| [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md) | Evidence-backed status ledger for PR-E through PR-8, child scaffold/readiness work, and DR-OPTION-A schema mirrors | — |
| [`COMPLETION_AUDIT.md`](COMPLETION_AUDIT.md) | Requirement-by-requirement audit of completed Fable recommendations, child schema mirrors, and remaining successor owner gates | -- |
| [`FABLE_FEEDBACK_TRACE_MATRIX.yaml`](FABLE_FEEDBACK_TRACE_MATRIX.yaml) | Machine-readable disposition matrix for Fable feedback, including implemented, planned, deferred, rejected, and owner-gated items | -- |
| [`DAD-LESSON-OUTBOX.md`](DAD-LESSON-OUTBOX.md) | DAD-ready reusable lesson capture for Fable feedback, Codex solutions, doctrine-genealogy kernels, knowledge-graph transfer, and legal/secular adaptation watchpoints | -- |
| [`WAVE2-ARCHITECTURE-HANDOFF.md`](WAVE2-ARCHITECTURE-HANDOFF.md) | Fable Wave-2 hard-problem handoff, D11-D16 decision summary, PR queue, red-team findings, and D15 lens guardrail clarification | Wave 2 |

## Reading order

1. This index.
2. Kernel A → B → C → D (each depends on the previous).
3. Owner decisions.
4. Codex handoff (implementation only after owner decisions).

## Standing rule for this folder

Where these kernels restate an existing governed control
(anti-guessing discipline, orthodox hermeneutic firewall, boundary trust hierarchy,
repository link contracts), the existing control remains the source of truth and the kernel
is an application of it, not a replacement.
