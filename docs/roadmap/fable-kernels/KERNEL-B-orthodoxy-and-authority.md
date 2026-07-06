---
object_type: fable_architecture_kernel
trust_zone: proposed
lifecycle_status: draft
provenance_note: "Created 2026-07-06 by Fable. Kernel for HP2 (orthodoxy boundary without denominational capture, as structure) and HP3 (source authority stratification)."
reason_for_inclusion: "Convert the orthodox hermeneutic firewall's prose affirmations into typed structure and validators before any doctrine record exists."
---

# Kernel B — Orthodoxy Boundary Structure and Source Authority Ladder

Design goal: affirm Nicene/Chalcedonian orthodoxy as a fixed, small, cited boundary while making
denominational capture, liberal-critical defaults, and heterodox smuggling *structurally*
inexpressible — not merely discouraged.

## B1. Three orthogonal axes (never one field)

Every claim, view, and formulation carries all three:

1. **`orthodoxy_status`** — position relative to the *project boundary* (B2). Closed enum:
   - `orthodox_core` — entailed by a boundary instrument (must cite it);
   - `orthodox_permitted_diversity` — inside the boundary; multiple readings preserved;
   - `disputed_within_orthodoxy` — contested whether inside;
   - `heterodox` — outside the boundary per recorded assessments (must cite them);
   - `non_christian_comparative` — not a Christian claim (advisory comparison only);
   - `unclassified_candidate` — **the machine default.** Nothing ever defaults to
     `orthodox_core` or `heterodox`; classification is a reviewed act with a basis.
2. **`tradition_scope`** — whose view/judgment this is. Closed profile registry (B4).
3. **`claim_role`** — `historical_description` | `normative_position` | `comparative_note`.
   Storing what Arius taught is description; it never becomes normative by storage. This is the
   single most important field for letting the corpus hold heterodox material accurately
   without platforming it.

## B2. The project boundary (owner decision D1)

**Recommendation:** the boundary instrument set is exactly two documents:

- the Niceno-Constantinopolitan Creed (381), **both recensions** (with and without filioque);
- the Chalcedonian Definition (451).

The Apostles' Creed is a compatible witness (rung S2), not a boundary instrument. Everything
beyond these two — Athanasian Creed, councils V–VII, all confessions — is tradition-scoped.
Keeping the boundary this small is the anti-capture architecture: the smaller the fixed core,
the less surface any single tradition can annex.

**The filioque precedent (owner decision D2).** The model's first stress test is inside the
boundary instrument itself. Recommendation: classify filioque as
`disputed_within_orthodoxy`, tradition-scoped (Western adoption as a recension), **not**
`orthodox_core`. Hardcoding filioque as core would be Western capture in the boundary's own
text. Record this as the precedent-setting example of how the boundary refuses annexation.

**Descriptive vs. normative separation.** Per-communion judgments live as scoped `assessment`
objects (Kernel A): "Chalcedon is rejected by the Oriental Orthodox communion" is a stored,
dated, scoped fact. The project-boundary classification (`heterodox` relative to Chalcedon) is
a separate reviewed field. Both are true in the model at once; neither erases the other. The
system can therefore describe miaphysitism accurately and respectfully while keeping the
Chalcedonian boundary fixed.

## B3. Source authority ladder S0–S7 (owner decision D5)

Two **orthogonal** dimensions. The scout finding stands: usefulness must never imply authority.

**Axis 1 — `authority_rung`** (normative force for doctrine in this project):

| Rung | Name | Contents | Normative force |
|---|---|---|---|
| S0 | `canonical_scripture` | 66-book canon (lives in `logos-scripture-graph` only) | norma normans — the only self-authorizing rung |
| S1 | `ecumenical_boundary_instrument` | the two D1 instruments | fixed project boundary (norma normata) |
| S2 | `conciliar_or_creedal_witness` | Apostles' Creed; councils Ephesus 431, and V–VII with per-tradition reception recorded | weighty; reception is tradition-scoped |
| S3 | `confessional_instrument` | Augsburg, Westminster, 39 Articles, Trent, LBCF 1689, etc. | binds **only its own profile scope** — uniformly, including Trent; capture-neutrality cuts every direction |
| S4 | `patristic_and_doctor_witness` | fathers, doctors, early commentaries | strong reception evidence; never binding |
| S5 | `theologian_formulation` | any theologian, ancient or modern | positions to be traced, not authorities |
| S6 | `scholarly_analysis` | modern academic scholarship of any confessional stance | evidence for historical/linguistic/textual **fields only**; zero doctrine authority |
| S7 | `adversarial_or_heterodox_source` | sectarian, heterodox, forged, fake | comparison/refutation targets only |

**Axis 2 — `evidence_utility` flags** (orthogonal, per source): `historical_value`,
`linguistic_value`, `reception_value`, `adversarial_value` (high/medium/low each). A forged
gospel can be high `reception_value` at S7. 1 Enoch is high `historical_value` and stays
non-authoritative. Utility never raises rung.

**Hard rules:**

- **No upward flow (V-LADDER-1):** an S-n source may never be the basis for classifying,
  reclassifying, or grounding anything at a higher rung. Owner authorization + review is the
  only exception path, and it is audited.
- **The S6 firewall (V-LADDER-2):** scholarly analysis may inform date blocks, language fields,
  attribution, and historical context — with review — but may never appear as basis for
  `orthodoxy_status`, a `normative_position` claim, or a boundary classification. This is the
  *structural* form of the firewall rules FIREWALL-ORTH-001/004: liberal-critical scholarship
  is welcome as evidence about history and language, and firewalled out of normativity, by
  schema rather than by vigilance.
- **S1 immutability:** rungs S0–S1 membership changes are owner-reserved (BOUNDARY-GOV-002
  pattern applies).

**Crosswalk to the boundary repo's 9-tier trust hierarchy.** The two systems answer different
questions and both stay: boundary tiers govern *contamination and retrieval* of source
material; the ladder governs *doctrinal authority weight*. Codex implements a crosswalk file
(e.g. `patristic_reception` tier ↔ S4; `heterodox_or_gnostic`/`known_forgery_or_fake` ↔ S7;
`historical_context_source` ↔ S6-adjacent utility). Neither system may be collapsed into the
other.

## B4. Profile registry (owner decision D3)

Seed the closed `tradition_scope` vocabulary from the orthodox hermeneutic firewall's
`preserved_options` (Reformed, Arminian/Wesleyan, Baptist, Anglican, Lutheran, Presbyterian,
Methodist, Pentecostal/charismatic, patristic/creedal), **plus descriptive profiles required
for honest history**: `roman_catholic`, `eastern_orthodox`, `oriental_orthodox`,
`church_of_the_east`, plus `pre_division_patristic`. Descriptive presence in the registry is
not doctrinal endorsement — the registry exists so scope can be stated, and capture requires
scope-erasure. New profiles are owner-gated registrations.

## B5. Capture-prevention validators (Codex implements; fail closed)

| ID | Rule |
|---|---|
| V-ORTH-1 | `orthodox_core` requires a cited S1 boundary-instrument basis. |
| V-ORTH-2 | A `normative_position` claim without `tradition_scope` fails unless `orthodoxy_status: orthodox_core`. |
| V-ORTH-3 | No source at S3 or below may be the sole basis for `orthodox_core`. |
| V-ORTH-4 | `tradition_scope` and verbs are closed vocabularies; unknown values fail. |
| V-ORTH-5 | `heterodox` requires ≥1 cited assessment ref; bare heresy labels fail. |
| V-TIME-1 | Anachronism check (Kernel A4). |
| V-LADDER-1/2 | No-upward-flow and S6 firewall, as above. |

**Capture audit metric (audit surface, not a validator):** per slice, report the distribution
of instrument citations grounding asserted normative claims. If one S3 confession dominates the
basis fields of claims marked broader than its scope, flag for owner review. Drift detection,
not automated judgment.
