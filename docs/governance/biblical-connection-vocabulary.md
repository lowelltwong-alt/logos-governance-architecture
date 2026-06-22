---
object_type: governance_reference
trust_zone: proposed
lifecycle_status: draft
provenance_note: "Created 2026-04-30 as a governed bridge from the staged biblical-connection-vocabulary-and-hermeneutics research packet."
reason_for_inclusion: "Approve a first narrow subset of biblical and theological relationship terms before any schema, validator, Bible-text, claim-object, or graph-object promotion."
review_status: unreviewed
ai_usage_posture: reference_bridge_not_auto_promote
---

# Biblical Connection Vocabulary

## Purpose

This document promotes a small governed subset of biblical and theological relationship vocabulary from the staged research packet at:

`incoming/research/biblical-connection-vocabulary-and-hermeneutics/`

The goal is to make future graph, Bible-reference, translation, original-language, textual-evidence, archaeology/context, and doctrine-support work use more precise scholar-recognizable relation language than generic GraphRAG labels.

This is a governance bridge, not a graph rollout.

## Status

Current status:

- first approved subset only;
- no Bible text import;
- no claim objects;
- no graph relationship objects;
- no validator or schema changes;
- no prophecy system;
- no canonical doctrinal promotion.

This file approves vocabulary for future use. It does not itself create governed machine-readable relations.

## Why this bridge is needed

Generic relation labels such as `related_to` are too weak for biblical and theological work.

The repository needs vocabulary that can distinguish:

- quotation from allusion and echo;
- typological correspondence from direct prediction;
- lexical relation from translation rendering;
- textual witness from textual reading;
- reception history from direct scriptural assertion;
- archaeology as contextual evidence rather than doctrinal proof;
- doctrinal grounding from downstream application constraint.

Without those distinctions, future AI retrieval or graph work will flatten different kinds of evidence into one misleading answer surface.

## Relationship rendering rule

Future uses of this vocabulary should expose, where relevant:

- relationship type;
- source basis;
- authority scope;
- tradition scope;
- evidence type;
- hermeneutical method;
- asserted versus inferred status;
- review status;
- confidence or caution note.

Do not use validation success, schema presence, or graph storage as proof that a theological relation is correct.

Also apply `anti-guessing-and-evidence-discipline.md`: embedding closeness,
generated confidence, or topical resemblance may create review candidates, but
not governed biblical-theological relations.

## Approved first subset

The first approved subset is intentionally narrow.

### Intertextuality

#### `quotes`

Use when one text directly reproduces wording from another in a way that should be rendered as quotation rather than weaker resonance.

Do not use for:

- loose thematic similarity;
- probable allusion;
- weak echo;
- typology.

#### `alludes_to`

Use when a text likely invokes another text without reproducing it as a direct quotation.

Do not use for:

- exact quotation;
- vague topic overlap;
- AI-inferred similarity without source support.

#### `echoes`

Use when a text resonates with an earlier text at a weaker level than direct quotation or probable allusion.

Do not use for:

- explicit citation;
- simple shared vocabulary without contextual linkage;
- doctrinal dependence by itself.

### Typology and fulfillment

#### `typologically_corresponds_to`

Use when a person, event, institution, or pattern is interpreted as corresponding meaningfully to a later reality in a typological sense.

Do not use for:

- direct prediction;
- bare analogy;
- generic similarity.

Render with explicit caution that typology is not the same as direct prediction.

#### `claims_fulfillment_of`

Use when a text or interpreter explicitly presents a later event, person, or reality as fulfilling an earlier promise, oracle, pattern, or expectation.

Do not use for:

- every typological relation;
- modern-event speculation;
- a full prophecy classification system.

Render with method and scope. Show whether the fulfillment claim is direct, typological, canonical, or interpreter-dependent where that matters.

### Original-language and translation

#### `has_lemma`

Use when a wordform or token is linked to a lexical lemma or headword.

Do not use for:

- text-critical lemma in the apparatus sense unless that sense is explicitly distinguished;
- translation equivalents by themselves.

#### `translated_as`

Use when a source-language expression is rendered by a target-language expression in a translation witness or translation comparison context.

Do not use for:

- lexical meaning by itself;
- doctrinal conclusion by itself;
- proof that a translation rendering is the only legitimate reading.

Keep translation rendering distinct from original-language meaning.

### Textual evidence

#### `has_reading`

Use when a passage, variant unit, or textual location is linked to a specific reading.

Do not use for:

- witness support by itself;
- lexical lemma;
- doctrinal weighting.

#### `attested_by_witness`

Use when a reading or text form is attested by a manuscript witness, versional witness, or other defined witness type.

Do not use for:

- theological authority ranking by itself;
- direct proof that a reading is original;
- absence caused by lacuna.

Keep witness attestation distinct from reading probability and from doctrinal authority.

### Reception and context

#### `interpreted_by`

Use when a text, doctrine, or theme is interpreted by a named interpreter, commentary tradition, or receiving community.

Do not use for:

- source authorship;
- direct textual quotation;
- flattening multiple traditions into one undifferentiated view.

Render tradition scope and interpreter identity where known.

#### `archaeologically_contextualized_by`

Use when a text, event, practice, or setting is illuminated by material culture, site evidence, inscriptional evidence, historical geography, or related contextual evidence.

Do not use for:

- direct doctrinal proof;
- certainty beyond the evidence;
- dependence claims based on similarity alone.

Archaeology contextualizes. It does not automatically prove theology.

### Doctrine and downstream application

#### `grounds_doctrine`

Use when a text, theme, or source materially grounds a doctrine topic or doctrine claim in a way that should be rendered as upstream theological support.

Do not use for:

- downstream policy by itself;
- prudential application by itself;
- weak thematic resonance.

#### `supports_claim`

Use when a source, relation bundle, or evidence set materially supports a specific claim without by itself implying full doctrinal grounding.

Do not use for:

- vague relevance;
- generic co-occurrence;
- claim promotion without source-basis review.

This term is narrower than `grounds_doctrine` and broader than raw textual adjacency.

#### `constrains_application`

Use when an upstream text, doctrine, concept, or evidence pattern limits, qualifies, or blocks a downstream prudential application.

Do not use for:

- direct doctrinal grounding;
- unrestricted policy generation;
- machine-generated governance conclusions presented as self-authenticating.

This term belongs downstream of theology and should remain clearly distinguishable from doctrine-level assertions.

## Explicitly disallowed generic fallback

Do not use `related_to` for meaningful biblical or theological relations when one of the approved specific terms fits the case.

If none of the approved terms fits, pause and route the case back into vocabulary review instead of inventing a weak catch-all edge.

## Scope cautions

### Bible text caution

This bridge does not authorize Bible-text ingestion.

For source and storage boundaries, see:

- `docs/governance/bible-source-and-licensing-policy.md`

### Prophecy caution

This bridge does not create a prophecy system.

`claims_fulfillment_of` is included only as a narrow relation label with explicit caution against flattening prophecy, typology, canonical reading, and modern-event speculation into one model.

### Tradition-scope caution

Some future uses of these terms will depend on tradition, interpreter, canon scope, or hermeneutical method.

Do not present a method-dependent or tradition-dependent relation as if it were neutral, canonical, or universally shared without explicit review.

## How this vocabulary should be promoted later

Use this order:

1. governed bridge reference;
2. limited approved term subset;
3. later schema and validator updates only if needed;
4. later claim or graph object work only after relation meanings are reviewable in prose.

Do not skip from staged research straight to machine-readable graph rollout.

## What this file does not do

This file does not:

- ingest Bible text;
- define a complete prophecy taxonomy;
- create machine-readable graph objects;
- create claim objects;
- change validators;
- settle disputed doctrinal interpretations;
- authorize AI to infer new biblical-theological relations without review.

## Recommended next step

The next safe step is to review whether this first approved subset should later be mirrored into controlled graph-contract or schema work in a separate, narrower PR.
