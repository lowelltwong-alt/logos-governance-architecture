# Relationship Registry

## Purpose

Relationship verbs make the ontology legible.

They should be controlled, stable, and semantically distinct.

Do not casually vary them in prose or metadata when the project is trying to make comparison, derivation, provenance, and translation explicit.

This file exists to stabilize how the repository expresses:
- structural relationships
- comparison relationships
- derivation relationships
- synthesis relationships
- appropriation relationships
- translation and misalignment relationships

Relationship verbs are not just descriptive prose. They are part of the governed architecture of the repository.

## Core rule

Use approved relationship verbs whenever possible.

Do not casually substitute looser or more conversational phrasing when a controlled term already captures the intended relationship.

The goal is not to sound artificial. The goal is to preserve semantic precision, comparison discipline, and future ontology readiness.

## Core relationship families

### Structural relationships

Use these when one node structurally relates to another within the repository.

- `parent`
- `children`
- `depends_on`
- `enables`
- `derived_from`
- `related_to`

### Comparison relationships

Use these when comparing thinkers, doctrines, concepts, traditions, or frameworks.

- `aligns_with`
- `partially_aligns_with`
- `misaligns_with`
- `tensions_with`
- `contradicts`
- `corrects`
- `sharpens`
- `requires_translation_to_compare`

### Canon, concept, and architecture-development relationships

Use these when a node is being developed, extended, instantiated, or constrained in the repository.

- `promotes_to`
- `instantiates`
- `extends`
- `constrains`
- `grounds`
- `translates_into`

### Provenance and synthesis relationships

Use these when a node has traceable source lineage or when a node is built from multiple sources.

- `synthesizes`
- `appropriates_from`
- `adapts`

These relationships are especially important where:
- a node is substantially built from several Christian thinkers
- a Christian thinker appropriates from a non-Christian philosophical source
- a project synthesis draws on multiple theological strands
- a category is borrowed, revised, transformed, or translated into a new frame

## Definitions

### `aligns_with`
Use when two thinkers, concepts, or nodes substantially converge on a point.

This should imply a fairly strong degree of conceptual compatibility.

### `partially_aligns_with`
Use when there is meaningful overlap, but not full convergence.

This is useful where the similarity is real, but bounded.

### `misaligns_with`
Use when two nodes do not simply stand in productive tension, but are structurally or semantically out of alignment in important ways.

Use this when the issue is stronger than minor tension but not necessarily full contradiction.

This term is especially useful in comparison work that is more vector-like or semantic in character, where the issue is degree and direction of non-alignment rather than only opposition.

### `tensions_with`
Use when two nodes are not outright contradictory, but exert real pressure against one another.

This is often appropriate where both nodes remain comparable within a shared frame, but cannot be harmonized without qualification.

### `contradicts`
Use when the disagreement is strong enough that both claims cannot be carried together without major revision or denial of one side.

### `corrects`
Use when one thinker, concept, or node is being used as a substantive correction to another.

This should imply more than nuance. It should imply a meaningful rectification or critique.

### `sharpens`
Use when one thinker or node clarifies, intensifies, or gives more precision to another without fundamentally opposing it.

### `requires_translation_to_compare`
Use when two nodes can be compared only after translating categories, assumptions, vocabulary, or conceptual structure.

This is especially important where Christian theology intersects with non-Christian philosophy, or where different traditions use adjacent but non-equivalent conceptual language.

### `grounds`
Use when one node provides a deeper basis or underlying rationale for another.

This is one of the most important verbs in the repository because it expresses downward support without implying identity.

### `translates_into`
Use when one node moves into a downstream expression, such as theology translating into governance, doctrine translating into application, or concept translating into policy logic.

### `constrains`
Use when one node sets a limit on another, narrows its valid use, or establishes a boundary condition.

### `instantiates`
Use when a downstream node is a concrete instantiation of a broader source logic, doctrine, concept, or synthesis.

### `extends`
Use when one node carries another further without fundamentally replacing it.

### `promotes_to`
Use when a recurring section, subtheme, or repeated pattern becomes a more formal reusable node of its own.

### `derived_from`
Use when one node is substantially derived from another source node or source object.

This is the default provenance relationship for direct lineage.

Use this when the derivation is strong enough that the source should be named explicitly as an upstream contributor rather than merely as background influence.

### `synthesizes`
Use when a node is intentionally built from several sources together and should not be treated as if it came from only one source.

This is especially useful for:
- synthesis nodes
- project-level arguments
- governance or application nodes built from multiple theologians
- doctrine nodes informed by several canon figures

Use this instead of flattening multi-source development into a misleading single-source derivation.

### `appropriates_from`
Use when a thinker, doctrine node, concept node, or synthesis draws from a source outside its immediate theological frame, especially a non-Christian philosophical source, conceptual tradition, or historical category.

This is important when the repository wants to acknowledge that a category has been borrowed rather than pretending it is simply native to one tradition.

Examples:
- Augustine and Platonism
- Aquinas and Aristotelianism
- Christian theology and modern political theory

### `adapts`
Use when a borrowed or inherited category is not simply repeated, but reshaped, redirected, or transformed for a new theological or conceptual frame.

This is especially useful where a node neither merely derives from nor merely appropriates from a source, but actively revises it.

### `related_to`
Use when two nodes are meaningfully connected but the precise relationship is not yet specific enough to justify a stronger controlled verb.

This should be used sparingly. Prefer a more precise verb when possible.

## Provenance guidance

The repository should increasingly preserve provenance more explicitly.

That means relationship language should help distinguish between:
- direct derivation from one source
- synthesis from several sources
- appropriation from external philosophical sources
- adaptation of inherited categories
- comparison that requires translation before evaluation

Do not flatten all of those into generic influence language.

If a node is strongly shaped by more than one source, prefer explicit multi-source language.
If a philosophical category is borrowed from outside Christian theology, prefer explicit appropriation language.
If a comparison only works after conceptual translation, make that visible.

## Synonym rule

Do not casually introduce uncontrolled alternatives such as:
- agrees with
- fits with
- kind of opposes
- parallels
- loosely resembles
- overlaps with
- clashes with
- borrows from
- inspired by
- shaped by
- influenced by

These may sound natural in ordinary prose, but they are too vague, too casual, or too semantically unstable for governed ontology work unless the registry formally adopts them.

Prefer controlled language that makes:
- degree of alignment
- degree of misalignment
- provenance type
- translation burden
- conceptual force

more explicit.

## Usage rule

Choose the strongest accurate relationship, but do not overstate.

For example:
- use `partially_aligns_with` instead of `aligns_with` when the overlap is real but bounded
- use `misaligns_with` instead of `contradicts` when the issue is structural non-alignment rather than total opposition
- use `tensions_with` instead of `misaligns_with` when the pressure is real but still comfortably comparable
- use `synthesizes` instead of `derived_from` when multiple thinkers are jointly doing the work
- use `appropriates_from` instead of `derived_from` when the source is external and borrowed into a new frame
- use `adapts` when a borrowed category is actively revised rather than merely carried over

For graph, retrieval, vector, or Scripture-edge work, also apply
`docs/governance/anti-guessing-and-evidence-discipline.md`. Semantic similarity
or embedding closeness may suggest candidate edges, but it does not justify a
governed relationship verb by itself.

## Documentation rule

If a new relationship verb becomes necessary, define it here before using it broadly.

That means:
1. identify the need
2. test whether an existing verb already fits
3. add the new verb here only if the distinction is recurrent and architecturally meaningful
4. use it consistently thereafter

## Extension note

For newer scripture, boundary, and graph-oriented relationship use, read this file together with:

- `docs/governance/scripture-taxonomy-and-ontology.md`
- `docs/governance/textual-traditions-translation-and-noncanonical-sources.md`
- `docs/governance/noncanonical-and-heresy-classification.md`
- `docs/roadmap/repository-integration-map.md`

This registry remains the base controlled relationship vocabulary for the entire repository, including newer concordance and graph surfaces.

## Doctrine-Genealogy Extension

Decision basis: `FABLE-D1-D10-2026-07-06` D4 and Kernel A3. These verbs are approved for the planned doctrine-genealogy plane and for governance schemas/validators that prepare that plane. `logos-doctrine-genealogy` may consume this registry later, but it may not mint relationship verbs locally.

These verbs do not authorize doctrine records, source imports, graph truth, reviewed lineage, or repo creation. Semantic similarity, embedding closeness, co-occurrence, or generated confidence may create only candidates.

### Derivation Family

| Verb | Meaning | Evidence floor | Decision basis |
|---|---|---|---|
| `derives_from` | A later object developed from an earlier object. | Citation showing the later object used or knew the earlier object. | Kernel A3; D4 |
| `depends_on` | Logical dependence without requiring temporal development. | Stated inferential dependence. | Kernel A3; D4 |
| `clarifies` | A later object makes an earlier object more precise without changing content. | Side-by-side content basis. | Kernel A3; D4 |
| `modifies` | A later object alters earlier content. | Side-by-side content basis. | Kernel A3; D4 |
| `systematizes` | A later object organizes earlier material and other sources into a system. | Cited organization as a later act. | Kernel A3; D4 |
| `reads_back_into` | A later object retrospectively interprets an earlier object. | Cited interpretive act. | Kernel A3; D4 |

### Citation Family

| Verb | Meaning | Evidence floor | Decision basis |
|---|---|---|---|
| `interprets_passage` | A formulation references a Scripture passage ID as interpretation history. | Passage ID plus provenance; never Scripture meaning. | Kernel A3; D4 |
| `cites_source` | A formulation references a boundary work ID. | Source ID plus citation mode. | Kernel A3; D4 |

### Response Family

| Verb | Meaning | Evidence floor | Decision basis |
|---|---|---|---|
| `receives` | Affirmative uptake of an object or formulation. | Cited reception basis. | Kernel A3; D4 |
| `rejects` | A scoped agent rejects a view or formulation. | Cited rejection basis. | Kernel A3; D4 |
| `counters` | A formulation is constructed against another formulation or view. | Cited response basis. | Kernel A3; D4 |

### Comparative Family

| Verb | Meaning | Evidence floor | Decision basis |
|---|---|---|---|
| `partially_aligns_with` | Meaningful but bounded overlap. | Cited comparison basis; may not exceed `proposed_relationship` without review. | Kernel A3; D4 |
| `tensions_with` | Real pressure without total contradiction. | Cited comparison basis; may not exceed `proposed_relationship` without review. | Kernel A3; D4 |

### Doctrine-Genealogy Verb Stop Rules

- `condemns` and `is_condemned_by` are not hand-authored doctrine-genealogy edges. Condemnation is represented by an `assessment` object; any edge projection is machine-derived and scoped.
- `requires_original_language_review` and `requires_textual_critical_review` are not verbs. They are promotion-blocking gate fields.
- `related_to` and `influences` are forbidden for doctrine-genealogy asserted edges. Use a stronger approved verb, keep the pair as `retrieval_candidate`, or stop for owner/Fable review.
- A real historical relationship that requires choosing between plausible verbs must cite a determinative basis or stop under Kernel E.

## Summary principle

Relationship verbs are part of the ontology, not just descriptive prose.

Use them carefully enough that a human or machine could reliably infer:
- whether two nodes substantially align
- whether they are only partially aligned
- whether they are in productive tension
- whether they are structurally misaligned
- whether one grounds, constrains, or translates into another
- whether a node is directly derived, synthesized, appropriated, or adapted

The goal is not verbal variety.
The goal is semantic discipline.
