---
object_type: governance_reference
trust_zone: proposed
lifecycle_status: draft
provenance_note: "Created 2026-06-04 from bible-kg-taxonomy-scaffold v0.2 review (Patch 10)."
reason_for_inclusion: "Frameworks against which the bible classification taxonomy must be validated before scholarly review / promotion past draft."
review_status: unreviewed
ai_usage_posture: reference_not_auto_promote
---

# Scholarly Cross-Check & Bibliography

Before `bible-classification-taxonomy.md` moves past `draft`, validate each axis
against recognized frameworks (not against systematic-theology intuition).

## By axis

| Axis | Cross-check against |
|------|---------------------|
| TextualForm / genre | Form-criticism genre inventories (Gunkel for Psalms: hymn/lament/thanksgiving/royal/wisdom; Westermann; prophetic Gattungen — Westermann, Sweeney; Pentateuch law forms — apodictic vs casuistic, Alt); ANE treaty form (Mendenhall/Kitchen). |
| SpeechAct | Speech-act theory (Austin/Searle) as applied to biblical texts (e.g. Briggs); use as analytic, flag as modern. |
| RedemptiveHistoryStage | Biblical-theology frames (note tradition-dependence; do not present as neutral). |
| TheologicalConcept vs Doctrine | Keep theme (SKOS) ≠ doctrine (reception). Cross-check doctrine labels against the specific confession/tradition that holds them. |
| Lexical / SemanticDomain | Louw-Nida *Greek-English Lexicon Based on Semantic Domains*; SDBH (Semantic Dictionary of Biblical Hebrew); BDB/HALOT (Hebrew), BDAG/LSJ (Greek). Record license. |
| IntertextualRelation | Quotation/allusion/echo criteria (Hays, *Echoes of Scripture*); NT-use-of-OT methodology (Beale & Carson, *Commentary on the NT Use of the OT*). |
| Typology | Grade explicit-NT vs later-pattern; Goppelt; Beale. Strength = attestation, not proof. |
| CanonStatus / TraditionScope | Tradition canon lists: Jewish (Tanakh), Protestant 66, Roman Catholic (Trent), Eastern Orthodox (incl. anaginoskomena), Oriental/Ethiopian (broader). Never a global boolean. |

## Reference / data standards

- **OSIS** and **USFM** for references and source markup (the corpus is USFM; see
  `logos-scripture-graph: config/ingest/usfm_marker_coverage.yaml`).
- **NA28 / UBS5** (Greek NT) and **BHS / BHQ** (Hebrew) apparatus conventions for the
  witness/variant model (`witness` + `textual_variant` schemas).
- **Rahlfs / Göttingen** for LXX witnesses; **Leon Levy / DJD** for Dead Sea Scrolls;
  **INTF / NT.VMR** for Greek manuscripts.

## Extra-biblical corpora (context layer only)

- ANE: *The Context of Scripture* (Hallo & Younger); *ANET* (Pritchard).
- Second Temple: OTP (Charlesworth); DSS editions.
- Greco-Roman: Loeb editions; standard epigraphic/papyrological corpora (OGIS, P.Oxy.).
- These attach via fenced `extra_biblical_source` records only — never as canonical facts.

## Open scholarly questions to resolve before promotion

1. Are RedemptiveHistoryStage and Typology too tied to one tradition? (Mark scope.)
2. Do law sub-categories (moral/civil/ceremonial) encode a Reformed frame? (Offer an
   alternative form-critical split: apodictic/casuistic/ritual.)
3. Are liturgical-use categories broad enough for Jewish, Catholic, Orthodox, Anglican use?
