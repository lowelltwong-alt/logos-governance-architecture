---
object_type: governance_reference
trust_zone: proposed
lifecycle_status: draft
provenance_note: "Promoted 2026-06-04 from bible-kg-taxonomy-scaffold v0.2 review; the scaffold's strongest contribution (multi-axis classification) landed here, with missing biblical-studies genres added and asserted/inferred/tradition rules enforced downstream."
reason_for_inclusion: "Shared theological/literary classification vocabulary for the Bible knowledge graph. Referenced by logos-scripture-graph's classification_assignment schema."
review_status: unreviewed
ai_usage_posture: reference_vocabulary_not_auto_promote
---

# Bible Classification Taxonomy (multi-axis)

A biblical passage is classified across **several independent axes at once**, not by
one flat tag. This document is the controlled vocabulary; the *structural* assignment
(with assertion_mode, provenance, tradition_scope) lives in
`logos-scripture-graph: schemas/classification_assignment.schema.json`.

## Separation rule (non-negotiable)

- **Asserted-textual** axes (textual_form, speech_act structure, language_layer) may be
  stated as facts of the text.
- **Interpretive** axes (theological_concept, doctrine, affective_tone, moral_use,
  typology, liturgical_use, ethical_domain, intertextual_relation) are **claims** —
  they require `assertion_mode` + `provenance` + evidence, and `tradition_scope` when
  tradition-dependent. They are never bare properties of a passage node.
- Canon status is **tradition-scoped**, never a global boolean.

## Axis 1 — TextualForm (literary/compositional form; asserted-textual)

- Narrative: creation, patriarchal, exodus, conquest, royal, exile, gospel, acts_church
- **Genealogy**: linear_genealogy, segmented_genealogy, regnal_list  *(added v0.2)*
- LawTorah: moral, civil_judicial, ceremonial, purity, sacrificial, case_law, apodictic_command, covenant_stipulation
- **CovenantTreatyForm** *(added v0.2; ANE suzerain-vassal)*: preamble, historical_prologue, stipulations, deposit_and_reading, witnesses, blessings_and_curses
- Poetry: hymn, lament/qinah, thanksgiving_psalm, royal_psalm, wisdom_psalm, penitential_psalm, imprecatory_psalm, acrostic_poem, victory_song, love_song  *(qinah/victory/love added v0.2)*
- **Superscription/Colophon** *(added v0.2)*: psalm_title, musical_ascription, colophon, postscript
- **LiturgicalRubric** *(added v0.2)*: selah, musical_notation, performance_direction
- Wisdom: proverb, instruction, disputation, theodicy, wisdom_poem, futility_meditation, riddle, fable  *(riddle/fable added v0.2)*
- Prophecy: judgment_oracle, salvation_oracle, woe_oracle, covenant_lawsuit, symbolic_act, restoration_promise, vision_report
- **AnnalsRegnal** *(added v0.2)*: regnal_formula, royal_annal, etiology, itinerary, dream_report
- GospelDiscourse: parable, miracle_story, controversy_dialogue, sermon, farewell_discourse, passion_prediction
- Epistle: greeting, thanksgiving, doctrinal_argument, paraenesis, household_code, vice_virtue_list, benediction
- Apocalyptic: vision_report, angelic_interpretation, beast_kingdom_symbol, heavenly_throne_scene, eschatological_judgment

## Axis 2 — LanguageLayer (asserted-textual) *(added v0.2)*

- hebrew | aramaic | greek
- flags: `aramaic_section` (Dan 2:4b–7:28, Ezra 4:8–6:18, Jer 10:11), `words_of_jesus` (`\wj`), `divine_name`

## Axis 3 — SpeechAct (what the language does)

Prayer (petition, intercession, lament, penitential_confession, thanksgiving, praise,
imprecation, dedication, vow, surrender); Confession (of_sin, of_faith, of_christ,
of_gods_character, of_covenant_identity, creedal_formula, liturgical); Command;
Promise; Warning; Blessing; CurseWoe; PraiseDoxology; OathVow; Question; Testimony;
Proclamation. *(unchanged from scaffold — strong as-is)*

## Axis 4 — RedemptiveHistoryStage (curated)

creation → fall → flood_judgment → patriarchs → exodus → sinai_covenant → wilderness →
land_and_conquest → judges_cycle → united_monarchy → divided_kingdom → exile → return →
second_temple_expectation → incarnation → kingdom_proclamation → cross → resurrection →
ascension → pentecost → church_mission → consummation → new_creation.
*(Mark as curated, not asserted-textual — it embeds a biblical-theology frame.)*

## Axis 5 — TheologicalConcept / Doctrine (interpretive — claims only)

Concept (SKOS theme) vs Doctrine (tradition-scoped reception) are **distinct**:
- `theological_concept` = textual motif (mercy, covenant, exile, kingdom) — `asserted_curated`.
- `doctrine` = systematic/reception formulation (justification, Christology) — `asserted_by_tradition`, REQUIRES `tradition_scope`.

## Axis 6 — IntertextualRelation (interpretive)

quotes_from, cites_formula, alludes_to, echoes, parallel_to, retells, interprets,
fulfills, typifies, contrasts_with, reverses, escalates, recapitulates.
(Editorial `\x` cross-refs are NOT auto-promoted to these — see MASTER_CONTEXT §4.)

## Axis 7 — AffectiveTone / LiturgicalUse / EthicalDomain / MoralUse (interpretive)

As in the scaffold (joy/fear/grief/…; confession/benediction/lectionary/…;
justice/neighbor_love/…; direct_command/wisdom_principle/narrative_example/…) —
all require `assertion_mode` + evidence.

## Axis 8 — Typology (interpretive, graded)

type_category: person/event/institution/object/place/office/pattern.
strength: explicit_nt | strong_canonical_pattern | traditional_theological | speculative.
REQUIRES `tradition_scope`. Strength is **attestation**, not proof of truth.

## Axis 9 — CanonStatus + TraditionScope (tradition-scoped)

CanonStatus: canonical, deuterocanonical, anaginoskomena, apocryphal, pseudepigraphal,
noncanonical_but_referenced, liturgically_read, doctrinally_authoritative, edifying_not_doctrinal.
TraditionScope: JewishRabbinic, Protestant, RomanCatholic, EasternOrthodox,
OrientalOrthodox, EthiopianOrthodox, Anglican, Lutheran, Reformed, Evangelical,
AcademicBiblicalStudies, ChristianCanonical.
(Canon membership per book is enforced in the companion
[logos-scripture-graph canon profile config](https://github.com/lowelltwong-alt/logos-scripture-graph/blob/main/config/canon/canon_profiles.yaml).)

## Extra-biblical context fence

ANE / Second-Temple / Greco-Roman / inscription / archaeology / apologetic sources are
NOT classified on these axes. They live in the companion
[logos-scripture-graph extra-biblical source schema](https://github.com/lowelltwong-alt/logos-scripture-graph/blob/main/schemas/extra_biblical_source.schema.json)
with `layer: context` and link to scripture only via tradition-scoped
RelationshipObjects. See `docs/governance/trust-zones.md`.
