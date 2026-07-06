---
object_type: doctrine_genealogy_vocabulary
trust_zone: canonical
lifecycle_status: active
provenance_note: "Created 2026-07-06 by Codex as PR-2 of the Fable kernel implementation sequence, transcribing Kernel B vocabulary and owner decisions D1-D5/D10 without adding doctrine data records."
reason_for_inclusion: "Give future doctrine-genealogy schemas, validators, examples, and repo scaffolds one governed vocabulary surface for orthodoxy status, claim role, tradition scope, authority rungs, and evidence utility flags."
---

# Doctrine-Genealogy Vocabulary

This file records controlled vocabulary for future doctrine-genealogy schemas and validators. It is a vocabulary surface only. It does not create doctrine records, source imports, graph truth, reviewed lineage, or a doctrine-genealogy repo.

Every non-floor theological classification below cites its decision basis under Kernel E.

## `orthodoxy_status`

Machine default: `unclassified_candidate`.

| Value | Meaning | Default allowed | Decision basis |
|---|---|---:|---|
| `orthodox_core` | Entailed by a cited S1 boundary instrument. | No | Kernel B1; Kernel B2; D1 |
| `orthodox_permitted_diversity` | Inside the boundary with multiple readings preserved. | No | Kernel B1 |
| `disputed_within_orthodoxy` | Contested whether or how the position is inside the boundary. | No | Kernel B1; D2 |
| `heterodox` | Outside the boundary per recorded assessments. | No | Kernel B1; Kernel B5 |
| `non_christian_comparative` | Not a Christian claim; advisory comparison only. | No | Kernel B1 |
| `unclassified_candidate` | Candidate classification awaiting review. | Yes | Kernel B1; Kernel E |

## `claim_role`

Machine default: `historical_description`.

| Value | Meaning | Default allowed | Decision basis |
|---|---|---:|---|
| `historical_description` | Describes a claim, source, or position without making it normative. | Yes | Kernel B1; Kernel E |
| `normative_position` | Records a scoped normative position. | No | Kernel B1; Kernel E |
| `comparative_note` | Records comparison without granting doctrine authority. | No | Kernel B1 |

## `tradition_scope`

No schema may silently infer a tradition scope for a real historical object. These values are allowed scopes; applying them to real material requires the relevant object provenance and, where non-floor classification is involved, `decision_basis`.

| Value | Display label | Decision basis |
|---|---|---|
| `reformed` | Reformed | D3; Kernel B4 |
| `arminian_wesleyan` | Arminian/Wesleyan | D3; Kernel B4 |
| `baptist` | Baptist | D3; Kernel B4 |
| `anglican` | Anglican | D3; Kernel B4 |
| `lutheran` | Lutheran | D3; Kernel B4 |
| `presbyterian` | Presbyterian | D3; Kernel B4 |
| `methodist` | Methodist | D3; Kernel B4 |
| `pentecostal_charismatic` | Pentecostal/charismatic | D3; Kernel B4 |
| `patristic_creedal` | Patristic/creedal | D3; Kernel B4 |
| `roman_catholic` | Roman Catholic | D3; Kernel B4 |
| `eastern_orthodox` | Eastern Orthodox | D3; Kernel B4 |
| `oriental_orthodox` | Oriental Orthodox | D3; Kernel B4 |
| `church_of_the_east` | Church of the East | D3; Kernel B4 |
| `pre_division_patristic` | Pre-division patristic | D3; Kernel B4 |

Descriptive presence in this registry is not endorsement.

## `authority_rung`

| Rung | Value | Contents | Normative force | Decision basis |
|---|---|---|---|---|
| S0 | `canonical_scripture` | The 66-book canon in `logos-scripture-graph` only. | Only self-authorizing rung. | Kernel B3 |
| S1 | `ecumenical_boundary_instrument` | The two D1 boundary instruments. | Fixed project boundary. | D1; Kernel B3 |
| S2 | `conciliar_or_creedal_witness` | Apostles' Creed; Ephesus 431; councils V-VII with per-tradition reception. | Weighty witness; reception is scoped. | D5; Kernel B3 |
| S3 | `confessional_instrument` | Confessions and catechisms such as Westminster, Augsburg, Trent, 39 Articles, LBCF. | Binds only its own profile scope. | D5; Kernel B3 |
| S4 | `patristic_and_doctor_witness` | Fathers, doctors, early commentaries. | Reception evidence; never binding by itself. | Kernel B3 |
| S5 | `theologian_formulation` | Ancient or modern theologian formulations. | Positions to trace, not authorities. | Kernel B3 |
| S6 | `scholarly_analysis` | Modern academic scholarship of any confessional stance. | Historical, linguistic, attribution, or textual fields only. | Kernel B3 |
| S7 | `adversarial_or_heterodox_source` | Sectarian, heterodox, forged, or fake sources. | Comparison or refutation targets only. | Kernel B3 |

## `evidence_utility`

Evidence utility is orthogonal to authority rung. Utility never raises a source's rung.

Allowed utility flags:

- `historical_value`
- `linguistic_value`
- `reception_value`
- `adversarial_value`

Allowed utility levels:

- `high`
- `medium`
- `low`

Decision basis: Kernel B3.

## Default And Stop Rules

- Schema defaults may only use floor values such as `unclassified_candidate`, `historical_description`, `retrieval_candidate`, and `review_status: unreviewed`.
- Unknown `tradition_scope` or doctrine-genealogy relationship verb values must fail closed.
- `orthodox_core` requires a cited S1 boundary-instrument basis.
- `heterodox` requires at least one cited assessment reference.
- No source at S3 or below may be the sole basis for `orthodox_core`.
- Scholarly analysis may inform historical, linguistic, attribution, or textual fields, but not orthodoxy status, normative position, or boundary classification.
- New values require owner-gated governance vocabulary update.
