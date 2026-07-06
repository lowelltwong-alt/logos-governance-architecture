---
object_type: fable_owner_decision_packet
trust_zone: canonical
lifecycle_status: active
provenance_note: "Created 2026-07-06 by Fable. Updated 2026-07-06 by Codex to record Lowell Wong's owner selections D1-D10 for the architecture kernels, preserving recommendations, repercussions, and non-authorizations."
reason_for_inclusion: "Owner selections D1-D10 unblock only the named governance-surface implementation queue and prevent future agents from relying on chat memory for these architecture decisions."
---

# Owner Decisions and Pilot Slices

Current status: owner selections D1-D10 are recorded in this file under
`Recorded Owner Selections (2026-07-06)`.

Each decision below has a recorded owner selection by Lowell Wong. Recommendation remains distinct from selection unless the recorded selection says so.
Codex implementation (see `CODEX_HANDOFF.md`) is sequenced against these.

## Recorded Owner Selections (2026-07-06)

Decision record ID: `FABLE-D1-D10-2026-07-06`.

These are owner selections for the Fable architecture kernels. They authorize only the named
governance surfaces, schemas, registries, validators, examples, discovery updates, and
registration drafts. They do not authorize doctrine data records, source imports, Scripture or
chunk changes, reviewed-gold promotion, reviewed-lineage promotion, graph/retrieval/vector
truth, repo creation, boundary material as Scripture authority, Noesis as Logos authority, or
denominational systematic theology as project authority.

| Decision | Owner selection |
|---|---|
| D1 | Select option A. Project boundary instrument set is Niceno-Constantinopolitan 381 plus Chalcedonian Definition 451 only. Apostles' Creed remains honored as S2 witness, not S1 boundary. Athanasian Creed is not added to the project boundary. |
| D2 | Select option A. Filioque is classified as `disputed_within_orthodoxy` and tradition-scoped, not `orthodox_core`. The project records the dispute without adjudicating it as project boundary. |
| D3 | Approve the Kernel B4 tradition/profile seed list: the preserved firewall options plus `roman_catholic`, `eastern_orthodox`, `oriental_orthodox`, `church_of_the_east`, and `pre_division_patristic`. Descriptive presence is not endorsement. Future additions are owner-gated. |
| D4 | Approve the Kernel A3 relationship-verb registry v1: the 12 verbs, derived-only condemnation rule, gate-fields-not-verbs rule, and forbidden verbs `related_to` and `influences`. |
| D5 | Approve ladder placements. Ephesus 431 and councils V-VII sit at S2 with per-tradition reception records, not inside S1. All confessional instruments sit uniformly at S3 and bind only their own profile scope. |
| D6 | Approve pilot slice order 1 -> 2 -> 3: first Trinity and Christology to Chalcedon, second Canon and Scripture authority, third Justification. Slice 3 waits until validators are proven on slices 1 and 2. |
| D7 | Select option A. Create `logos-doctrine-genealogy` only after D1-D6 are recorded and Codex PRs 1-5 are merged in governance. Before that, draft registration materials only. |
| D8 | Confirm `logos-chunking-harness` remains `planned_not_created` until a real cross-corpus execution need meets the registry readiness test. |
| D9 | Approve `reviewed_lineage` promotion policy as owner-gated, per-object, non-generalizing, chunking-gold-analog promotion. No owner-pattern projection in this plane without separate future decision. |
| D10 | Approve governance ownership of future path governance/registry/entity_ids.yaml for persons, councils, schools/movements, and instruments. Boundary owns work IDs. Scripture owns passage IDs. |

## D1 — Project boundary instrument set

- **Options:** (a) Niceno-Constantinopolitan 381 + Chalcedonian Definition 451 only;
  (b) add Apostles' Creed as a third boundary instrument; (c) add the Athanasian Creed.
- **Repercussions:** (a) smallest fixed core, maximal anti-capture, Apostles' Creed still honored
  at S2. (b) adds a Western baptismal text to the boundary — mild Western tilt, little gained.
  (c) Athanasian contains filioque and damnatory clauses — imports the exact capture problem
  into the boundary.
- **Recommendation: (a).**

## D2 — Filioque classification precedent

- **Options:** (a) `disputed_within_orthodoxy`, tradition-scoped recension;
  (b) `orthodox_permitted_diversity`; (c) `orthodox_core` (Western text as normative).
- **Repercussions:** (c) is structural Western capture inside the boundary instrument itself and
  contradicts FIREWALL-ORTH-005's spirit. (a) vs (b) differ in tone: (a) records live East–West
  dispute honestly; (b) declares both readings acceptable, which is itself a theological ruling.
- **Recommendation: (a)** — describe the dispute; don't adjudicate it.

## D3 — Tradition/profile registry seed list

- Approve the Kernel B4 seed list (firewall `preserved_options` + `roman_catholic`,
  `eastern_orthodox`, `oriental_orthodox`, `church_of_the_east`, `pre_division_patristic`).
  Descriptive presence ≠ endorsement. Additions owner-gated thereafter.
- **Recommendation: approve as listed.**

## D4 — Relationship-verb registry v1

- Approve the 12 verbs of Kernel A3, the derived-only rule for condemnation edges, gate-fields-
  not-verbs, and the forbidden list (`related_to`, `influences`).
- **Recommendation: approve;** any verb you doubt can ship as `provisional` instead of governed.

## D5 — Ladder placements

- (i) Councils Ephesus 431 and V–VII at **S2 with per-tradition reception records** (vs. inside
  the S1 boundary). Recommendation: S2 — keeps the boundary at two documents; reception records
  carry the real information.
- (ii) All confessional instruments — Westminster, Augsburg, Trent, 39 Articles, LBCF — sit
  **uniformly at S3, each binding only its own profile**. Recommendation: approve; this is
  capture-neutrality applied evenly to every tradition including Rome.

## D6 — Pilot slices (HP7)

**Slice 1 — Trinity & Christology to Chalcedon** (Arian controversy → Nicaea 325 →
Constantinople 381 → Ephesus 431 → Chalcedon 451).
Richest early lineage; exercises *every* object type (topics, views, formulations, agents,
councils, instruments, assessments, condemnations, controversies), both review gates
(homoousios, theotokos, monogenēs; no variant-critical dependency traps), S7 adversarial
handling (Arius), and the Oriental-Orthodox scope subtlety. Sources are public-domain and
abundantly catalogued. **Risk:** largest slice; scope-creep into post-Chalcedonian disputes —
cut at 451.

**Slice 2 — Canon & Scripture authority** (Muratorian fragment → Athanasius' 39th Festal
Letter → conciliar lists → Trent → Reformation confessions).
Governs everything downstream; directly exercises the boundary repo's deuterocanon
tradition-scoping and instrument `binding_scope`. **Risk:** touches canon-scope sensitivities —
every record stays `historical_description`; the project's 66-book scope is not up for
modeling-based revision (existing canon-scope stop rules apply in full).

**Slice 3 — Justification** (Augustine ↔ Pelagius → Orange 529 → medieval developments →
Reformation → Trent → 1999 Joint Declaration).
Maximal denominational-capture stress test; exercises S3 profile scoping,
`partially_aligns_with` (Joint Declaration), and `contested_status` handling. **Risk:** highest
capture pressure — run only after V-ORTH validators are proven on slices 1–2.

- **Options:** order 1→2→3; order 2→1→3 (canon first); pick one slice only for MVP.
- **Recommendation: 1 → 2 → 3.** Slice 1 is the best full-model exercise with the least
  capture pressure; slice 3 is deliberately last as the stress test.

## D7 — `logos-doctrine-genealogy` creation timing

- **Options:** (a) create after D1–D6 recorded **and** Codex PRs 1–5 (schemas + validators +
  examples) merged in governance; (b) create immediately; (c) defer indefinitely, model inside
  governance repo.
- **Repercussions:** (b) recreates the records-before-guardrails risk the kernels exist to
  prevent. (c) violates the registered five-repo topology and bloats the control plane.
- **Recommendation: (a).** Registration issue + scaffold PR per
  `governance/ADDING_NEW_LOGOS_REPOS.md`, only after the kernel surfaces exist and validate.

## D8 — `logos-chunking-harness`

- **Recommendation: remains `planned_not_created`.** No current cross-corpus execution task
  requires it (the registry's own readiness test is not met). Confirm deferral.

## D9 — `reviewed_lineage` promotion policy

- Approve the chunking-gold-analog pattern (Kernel C1): per-object, owner-gated, non-
  generalizing promotions of exemplar lineage subgraphs. No owner-pattern projection policy in
  this plane without a separate future decision.
- **Recommendation: approve pattern; first promotion candidate = a completed pilot slice 1
  subgraph, later.**

## D10 — Entity-ID registry ownership

- Approve governance ownership of future path governance/registry/entity_ids.yaml for persons/councils/
  schools/instruments (Kernel A5), boundary keeps work IDs, Scripture keeps passage IDs.
- **Recommendation: approve.**

## Non-authorizations

Recording these decisions authorizes Codex to build the named *governance surfaces* (schemas,
registries, validators, examples, discovery updates) and nothing else. It does not authorize
doctrine data records, source imports, Scripture/chunk changes, reviewed-gold or
reviewed-lineage promotion of any content, graph/retrieval/vector truth, or repo creation
(D7 gates that separately through the registration process).
