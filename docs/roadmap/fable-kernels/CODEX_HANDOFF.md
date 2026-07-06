---
object_type: fable_to_codex_handoff
trust_zone: proposed
lifecycle_status: draft
provenance_note: "Created 2026-07-06 by Fable. Deterministic implementation queue for Codex (high effort) after the owner records decisions D1–D10."
reason_for_inclusion: "Codex must not decide ontology, vocabulary, orthodoxy, or slices; this handoff gives it exact, sequenced, validator-backed tasks that require no theological judgment."
owner_decision_record_ref: "docs/roadmap/fable-kernels/OWNER-DECISIONS-AND-PILOTS.md#recorded-owner-selections-2026-07-06"
---

# Codex Handoff — Kernel Implementation Queue

**Preconditions for every PR below:** read the repo AI front door and
`docs/governance/ai-workflow/goal-prompt-premortem-preflight.md`; work on a fresh task branch
from clean `main`; run the repo's validation suite before finishing; one narrow PR per row; no
mega-branches. Where a PR touches gated governance paths (`governance/`, `docs/governance/`,
front doors, TOC, `scripts/validate_*`, workflows), the **same PR** must update
`governance/GOVERNANCE_DEPENDENCY_MAP.yaml`, register the changed paths in map coverage, review
the discovery surfaces, and pass `scripts/validate_governance_dependency_map.py` — the gate
fails closed (GD-014). Child-repo mirror updates follow the existing mirror controls.

**Hard stop rules (all PRs):** no doctrine/genealogy **data records** anywhere; no repo
creation (PR-8 drafts the issue only); no source imports; no Scripture output/chunk changes; no
reviewed-gold or reviewed-lineage content promotion; no new relationship verbs, profiles, enum
values, or rungs beyond the kernels; if a kernel is ambiguous, stop and ask the owner — do not
interpolate theology.

Owner decisions D1-D10 are recorded in
`docs/roadmap/fable-kernels/OWNER-DECISIONS-AND-PILOTS.md`, section
`Recorded Owner Selections (2026-07-06)`, decision record ID
`FABLE-D1-D10-2026-07-06`. This unblocks the D1-D5/D10 decision dependency for PR-2 and the
D7 decision dependency for PR-8 only after the decision record is present in the working branch
or merged main. All non-authorizations remain in force.

## Sequenced queue

### PR-1 — Kernel registration and family root *(gated paths: yes — TOC + map)*
Blocked on: nothing (may precede owner decisions; registers drafts as drafts).
1. Add `docs/roadmap/fable-kernels/` to `AI_TABLE_OF_CONTENTS.md` (one entry pointing at the
   kernel README) and extend dependency-map artifact GD-015 `paths` (or add GD-016
   `fable_architecture_kernels`) with these files; register coverage.
2. Create root `LOGOS_FAMILY_MAP.md` (~1 page): the five-repo table from
   `docs/roadmap/fable-master-architecture-buildout-plan.md` §Current Repo Roles, one-line
   jobs, links to each repo's front door, Noesis marked external-advisory-only /
   not-a-development-target. Link it from `AI_FRONT_DOOR.md` and the TOC.

### PR-2 — Governance vocabulary surfaces *(gated: yes; blocked on D1–D5, D10)*
Owner-decision dependency status: satisfied by `FABLE-D1-D10-2026-07-06` once this decision
record is present in the working branch or merged main.

1. Extend `docs/governance/relationship-registry.md` with the Kernel A3 verb registry
   (12 verbs, families, evidence floors, forbidden list, derived-only condemnation rule).
2. Add `governance/registry/entity_ids.yaml` scaffold: schema comment header, ID convention
   (`person/…`, `council/…`, `instrument/…`, `school/…`), empty or seeded ONLY with entities
   named in the kernels (Nicaea-325, Constantinople-381, Ephesus-431, Chalcedon-451, the two D1
   instruments) — identity rows only, zero doctrinal fields.
3. Add controlled-vocabulary doc for the Kernel B enums: `orthodoxy_status`, `claim_role`,
   `tradition_scope` seed registry (per D3), ladder rungs S0–S7, `evidence_utility` flags.
   Location: `docs/governance/doctrine-genealogy-vocabulary.md`.

### PR-3 — Schemas *(not gated unless touching listed paths; blocked on PR-2)*
JSON Schemas under `schemas/doctrine_genealogy/` in this governance repo (standards only; the
future repo will consume them): the 8 node types + `genealogy_edge` (Kernel A2),
`doctrine_provenance.v1` (Kernel C1 block, field-for-field), `evidence_packet.v1` (Kernel D1
incl. row contract and `non_authority_block` as required const values), shared `date_block`
(A4). Mark every schema `$comment: draft, non-authorizing, owner decisions D1–D10 apply`.

### PR-4 — Validators and tests *(gated: yes — scripts/validate_*; blocked on PR-3)*
Implement fail-closed validators + pytest coverage, validating schemas/examples (no data
exists yet): `validate_doctrine_vocabulary.py` (V-ORTH-4 closed vocab),
`validate_doctrine_provenance.py` (V-PROV-1..5, V-ORTH-1/2/3/5, V-LADDER-1/2),
`validate_genealogy_edges.py` (V-TIME-1 anachronism, verb registry, derived-only condemnation),
`validate_evidence_packet.py` (V-PKT-1..5), `validate_gate_triggers.py` (V-GATE-1, list-driven
from a trigger-registry file that *references* the Scripture repo queues by path — do not copy
their contents). Wire into `scripts/run_validation_suite.py` per existing pattern.

### PR-5 — Worked examples *(blocked on PR-4 and D1/D2/D4/D5)*
Under `examples/doctrine_genealogy/`: one minimal Chalcedon exemplar — topic, two views
(dyophysite/miaphysite), two formulations, Chalcedon instrument with `binding_scope` showing
per-tradition reception, one assessment, two edges (`counters`, `derives_from`), one
`evidence_packet` shape. All records `lifecycle_status: draft`, `review_status: unreviewed`,
`trust_zone: proposed`. These are schema-conformance exemplars, **not** promoted content; they
must pass every PR-4 validator.

### PR-6 — Boundary repo hardening *(in `logos-boundary-literature`; blocked on PR-3)*
1. Add schema-conformance validators for the four existing JSON schemas + trust-tier
   closed-vocab check + a contamination lint (flag verse-length quoted strings in data files as
   suspected Scripture text — heuristic, warn-level).
2. Add `governance/AUTHORITY_LADDER_CROSSWALK.md`: the Kernel B3 tier↔rung crosswalk
   (contamination/retrieval vs doctrinal-authority-weight; neither collapses into the other).
3. Update local mirror surfaces per that repo's mirror control if governance paths changed.

### PR-7 — Scripture front-door decomposition *(in `logos-scripture-graph`; independent)*
Target structure (mechanical, content-preserving — no rule may be weakened or dropped):
1. `AI_FRONT_DOOR.md` shrinks to a stable operating-rules document (≤ ~250 lines): mandatory
   read order (fix the duplicate 6/10/11/12 numbering), cross-repo governance, canonical-scope
   rules, standing non-authorizations, pointer to the ledger and to the TOC tag index as the
   routing surface.
2. New `docs/roadmap/TASK_LEDGER.md` (or `.ai/control/task_ledger.md`): move the T3xx–T4xx
   per-task narrative paragraphs there verbatim, newest first. Every task-ID string, path, and
   non-authorization sentence must survive the move byte-preserved; only location changes.
3. Update that repo's TOC, mirror files, and any validator that asserts front-door content;
   run the full suite with the recorded timeout ceilings (`test_runtime_preflight.yaml`).
   This PR is large-surface: propose it as its own reviewed PR with a no-context audit note per
   that repo's audit protocol.

### PR-8 — Registration drafts *(blocked on D7; drafts only)*
Owner-decision dependency status: satisfied by `FABLE-D1-D10-2026-07-06` for draft-only
registration materials. Repo creation remains separately unauthorized.

Draft (do not open until owner says go): the `register_new_logos_repo` issue body for
`logos-doctrine-genealogy` (role, authority = interpretive_historical_profile_scoped,
link contracts per registry `planned_repos` entry, scaffold checklist incl. front door, TOC,
mirror control + validator, source-trust rules, profile scope rules, validation commands) and
the scaffold-PR file list. Store under `incoming/research/doctrine-genealogy-registration/`.

## Sequencing summary

PR-1 anytime → PR-2 after D1–D5/D10 → PR-3 → PR-4 → PR-5 (needs D1/D2/D4/D5) → PR-6 parallel
after PR-3 → PR-7 fully parallel → PR-8 drafts after D7. Repo creation itself is **not in this
queue**; it happens through the registration process only after owner selection.

## Reporting

Each PR reports per `AI_WORK_START_HERE.md` output expectations: files changed/added/not
changed, assumptions, commands run, validations run and not run, remaining risks — plus, for
gated PRs, the governance-map impact statement required by GD-014.
