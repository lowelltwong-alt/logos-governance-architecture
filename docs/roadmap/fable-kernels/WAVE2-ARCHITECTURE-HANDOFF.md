---
object_type: fable_wave2_architecture_handoff
trust_zone: proposed
lifecycle_status: draft
ai_usage_posture: staging_only_not_auto_promote
provenance_note: "Created 2026-07-07 by Codex from the Fable Wave-2 architecture handoff after owner review of decisions D11-D16."
reason_for_inclusion: "Preserve the Wave-2 hard-problem kernels, blockers, owner decisions, PR queue, and non-authorizations so future agents do not rely on chat memory or attachment state."
---

# Fable Wave-2 Architecture Handoff

This handoff records the Fable Wave-2 architecture pass after governance PR #92 and
`logos-doctrine-genealogy` PR #6. It is proposed, non-authorizing architecture
guidance. It does not create data records, promote lineage, import sources, alter
Scripture/chunk output, create graph/retrieval/vector truth, create a repo, or give
Codex theology authority.

## Verdict

The repo family is coherent after PR #92. The control plane has Fable kernels A-E,
owner decisions D1-D10, doctrine-genealogy schema mirrors, and non-authorization
surfaces in place.

Fable found five next issues:

| Issue | Shape | Next queue |
|---|---|---|
| Successor doctrine-genealogy lane gate | Owner decision required before further readiness, data/source, runtime, or theology work | D13 |
| Mirror freshness | Child mirrors are checksum-pinned but do not detect upstream drift after later governance changes | W2-1/W2-2 |
| Cross-repo path drift | Gate-trigger registry references Scripture paths without checking existence | W2-1/W2-2 |
| Review economics | Owner-only review does not scale once outside contributors arrive | D12 / W2-6 later |
| Stale local checkouts | Scripture and boundary local branches may not reflect live main | W2-14 |

## Wave-2 Kernels

| Kernel | Problem | Codex queue |
|---|---|---|
| F | Derivative theology composition: multi-parent derivation, counter-derivation, contested influence, label-vs-referent, negative evidence | W2-10 after D16 |
| G | Historical/archeological/context evidence plane without context becoming Scripture or doctrine authority | W2-13 after D14 |
| H | Manuscript/codex witness model and variation-unit substrate without preferred readings | W2-3 |
| I | Whole-Bible chunking scale algorithm with risk/readiness math and route isolation | Future chunking queue; no output authorization |
| J | Hermeneutic lens registry and slice/consequence modeling without hidden defaults | W2-5 after D15 |
| K | Cross-repo mirror freshness and reference integrity | W2-1/W2-2 |
| L | Learning-loop operating standard as a thin federated standard, not a new platform | W2-7/W2-8/W2-9 after D11 |
| M | Reviewer-role registry and two-key promotion without authority leakage | W2-6 when D12 trigger is active |
| N | Citation resolution and translation-dependence discipline | W2-12 |

## Owner Decisions

Owner selections D11-D16 are recorded in
[`OWNER-DECISIONS-AND-PILOTS.md`](OWNER-DECISIONS-AND-PILOTS.md) under decision
record ID `FABLE-WAVE2-D11-D16-2026-07-07`.

Important nuance: D12 is not selected as an immediate implementation task while the
project remains owner-built and no outside contributors are active. The owner selected
a conditional contributor-triggered transition: preserve current owner-only review
for speed now, then adopt the reviewer-role and two-key model before onboarding
outside contributors beyond the current builder/agent setup.

## High-Leverage PR Queue

| PR | Repo | Purpose | Blocked by |
|---|---|---|---|
| W2-0 | governance | Land this Wave-2 handoff and owner-decision record | None |
| W2-14 | scripture/boundary | Branch reconciliation and stale-checkout hygiene | None |
| W2-1 | governance | Mirror-freshness standard and cross-repo reference manifest | W2-0 |
| W2-2 | doctrine/scripture/boundary | Child freshness checks and manifest fields | W2-1 |
| W2-15 | governance | Advisory/free-text smuggling lint | W2-0 |
| W2-16 | governance | Recension-aware S1 boundary-instrument validator | W2-0 |
| W2-7 | governance | LLOS standard and lesson schema | D11 |
| W2-8/W2-9 | boundary/doctrine | Lesson-index bootstrap | W2-7 |
| W2-6 | governance | Reviewer-role registry and two-key promotion fields | D12 trigger active |
| W2-10 | governance | Kernel-F vocabulary and validators | D16 |
| W2-3 | scripture | Variation-unit registry and report-only chunk-boundary check | W2-0 |
| W2-12 | boundary | Work-edition-locator and verified-against discipline | W2-0 |
| W2-5 | governance | Lens registry seed | D15 |
| W2-13 | boundary | Context-evidence taxonomy scaffold | D14 |
| W2-11 | governance to doctrine | Pilot-slice-1 staged research skeletons | D13 |
| W2-4 | scripture | Preflight tiering proposal packet | W2-7 |

## Red-Team Findings To Preserve

Fable identified these concrete current risks:

- Gate-trigger registry references Scripture paths but does not check path existence.
- Child schema mirrors pin a governance commit without drift-detection cadence.
- `orthodox_core` S1 citations need recension awareness so disputed recension content cannot
  silently ground core orthodoxy.
- Free-text fields remain an advisory-smuggling surface.
- Scripture preflight/front-door material is at risk of required-reading saturation.
- Variant-sensitive passages need a structural variation-unit rule before scaled chunking.
- Boundary and doctrine-genealogy need lesson surfaces so cross-repo lessons do not get lost.
- Citation records need work-edition-locator and `verified_against` discipline.
- Labels such as `Arianism` or `Nestorianism` must not replace the actual claim/formulation.

## D15 Clarification

D15 approves an owner-gated lens registry seed. It does not permit agents to invent
new hermeneutical lenses. Any future lens/profile addition requires owner approval.
The registry records lenses descriptively so agents must declare them instead of
hiding them. It specifically blocks liberal-critical, anti-supernatural,
anti-canonical, heterodox, sectarian, or odd speculative theology from entering as
an invisible default.

## Non-Authorizations

This handoff does not authorize Scripture output changes, chunk output changes,
reviewed-gold promotion, reviewed-lineage promotion, graph/retrieval/vector truth,
source imports, source rows, repo creation, doctrine-genealogy data records,
boundary material as Scripture authority, Noesis as Logos authority, denominational
systematic theology as project authority, hermeneutic-lens authority, textual-reading
authority, recension authority, variant-status authority, gate satisfaction by AI,
or theology authority by Codex/subagents.

Scoring, risk math, readiness math, and calibration are for review sequencing only.
They may not determine truth, orthodoxy, canon, doctrine, or Scripture meaning.
