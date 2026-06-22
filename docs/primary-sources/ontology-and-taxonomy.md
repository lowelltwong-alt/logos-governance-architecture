# Primary Sources Ontology and Taxonomy

## Purpose

This file defines how the future biblical primary-sources branch should fit the repository's ontology, taxonomy, graph layer, and governance discipline.

It is intended as a handoff-ready framework for a future lead and team.

## Core principle

This branch should extend the current ontology recursively.

It should not introduce a second unrelated metadata language or a separate ungoverned manuscript project.

The same larger repository grammar should still apply:
- stable identity
- controlled object families
- typed relationships
- provenance
- trust zones
- promotion rules
- validation

## Source-Language Root Graph Direction

The long-range direction is a manuscript- and source-language-rooted Scripture
graph.

English translation surfaces should remain valuable access, comparison, and
application layers, but the deepest evidence layer should eventually be able to
trace claims back through:

- manuscript witnesses and fragments;
- Hebrew, Aramaic, and Koine Greek transcriptions where applicable;
- lemmata, morphology, syntax, and phrase-level evidence;
- variants and reconstruction judgments;
- translation renderings and interpretation layers as downstream, labeled
  objects.

This direction requires capability gates. AI-assisted source-language work must
not be promoted merely because it sounds learned or parses fluently. It needs
licensed source data, controlled vocabulary, expert review, confidence fields,
and validators that keep manuscript evidence, lexical analysis, translation,
interpretation, and doctrine distinct.

## Major object families

### `witness_object`
Use for a manuscript witness, textual-tradition witness, or other substantial text-bearing witness object.

Examples:
- papyrus witness
- codex witness
- witness preserving a whole book
- witness preserving a letter or major continuous-text section
- MT witness/tradition object
- LXX witness/tradition object

### `fragment_object`
Use for one identifiable fragment, especially where a witness survives in pieces or only partial portions of a larger text-bearing object remain.

### `transcription_object`
Use for diplomatic or normalized transcription layers.

### `passage_reconstruction_object`
Use for a governed assembly of evidence around a passage span.

### `lexical_evidence_object`
Use for original-language word or phrase evidence tied to witness and passage context.

### `translation_comparison_object`
Use for governed comparison across target-language renderings.

## Future taxonomy branches

This future branch will likely need recursive subdomains such as:
- witnesses
- witness-parts or subwitnesses where needed
- fragments
- transcriptions
- reconstructions
- lexical-evidence
- translation-comparisons
- external-reference or catalog metadata

## Relationship families

The future branch should use the existing controlled relationship grammar as much as possible, with additions only where truly necessary.

Likely high-value relationships include:
- `witness_for`
- `fragment_of`
- `transcribes`
- `reconstructs`
- `attests`
- `variant_of`
- `has_lemma`
- `has_morphology`
- `has_syntactic_relation`
- `grounds`
- `translation_witness_for`
- `requires_review`

## Metadata groups

### Witness metadata
- witness ID
- witness kind
- whether the witness is fragmentary, partial, or more complete
- institution
- shelfmark
- date range
- language
- script
- material
- coverage
- authenticity confidence

### Fragment metadata
- fragment ID
- parent witness
- image refs
- IIIF refs where available
- transcription status
- passage coverage estimate
- reconstruction confidence

### Reconstruction metadata
- passage ID
- linked witnesses
- linked fragments
- diplomatic text
- normalized comparison text
- variant list
- confidence summary

### Lexical metadata
- term ID
- lemma
- passage occurrences
- contextual meaning notes
- non-biblical comparative usage notes where appropriate
- lexical confidence

### Source-language analysis metadata
- language
- script
- token or phrase span
- lemma
- morphology
- syntactic relation where known
- parsing confidence
- analyst or tool provenance
- expert-review status
- caution notes for disputed or ambiguous parses

### Translation metadata
- target language
- likely renderings
- context-sensitive notes
- confidence tiers
- doctrinal sensitivity notes

## Trust and confidence model

This branch should preserve confidence explicitly.

Likely confidence dimensions include:
- authenticity confidence
- dating confidence
- reading confidence
- reconstruction confidence
- lexical confidence
- translation confidence

Trust zones from the wider repository should still apply.

AI-generated parses, alignments, or lexical observations should default to
candidate or inferred status until reviewed. They should never overwrite
transcriptions, variant records, or source-language evidence objects.

## Fractal rule

This future branch should remain self-similar with the wider repository.

That means:
- local READMEs for subbranches
- stable IDs for every governed object
- interface use where object families share behavior
- shared properties for repeated metadata
- validation shapes for repeatable object families
- graph schemes for bounded domains

## Summary principle

The future primary-sources branch should be able to move from witness or fragment to theology without losing provenance, confidence, or contextual meaning.
