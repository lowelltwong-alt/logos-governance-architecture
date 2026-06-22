# Scripture Taxonomy and Ontology

## Purpose

This file defines how the repository should model biblical texts, interpretive units, hermeneutic approaches, and downstream theological usage.

The goal is to make the project capable of drilling down from:
- theological architecture
- tradition
- canon thinker
- doctrine
- concept

into:
- biblical book
- chapter
- pericope or passage
- verse cluster
- interpretive question
- hermeneutic approach
- competing readings
- doctrinal implications
- governance and AI implications

This layer is necessary if the repository is to support serious biblical reasoning rather than only theologian summaries.

## Core principle

Do not collapse the following into one node:
- biblical text
- interpretation
- doctrine
- modern application

These should be related, but not treated as identical.

The repository should preserve the difference between:
1. what the text is
2. how the text is interpreted
3. what doctrine is drawn from it
4. how that doctrine is translated into governance or AI reasoning

## Source-Language And Manuscript Horizon

The long-range Scripture graph should eventually be able to move below
English-facing passage nodes into manuscript witnesses and source-language
evidence.

That future root graph should keep distinct:

- Hebrew, Aramaic, and Koine Greek witness evidence;
- manuscript and fragment records;
- diplomatic and normalized transcriptions;
- textual variants and reconstruction judgments;
- lemmata, morphology, syntax, and lexical evidence;
- translation renderings;
- interpretation and doctrinal use.

This is a roadmap horizon, not a present AI authority claim. AI may help stage
candidate alignments, parses, and lexical notes, but source-language graph
promotion requires licensed sources, controlled vocabulary, confidence fields,
human expert review, and validators that keep evidence layers separate.

## Main node families

### 1. `scripture_book`
Use for a biblical book as a whole.

Examples:
- `scripture.genesis`
- `scripture.romans`
- `scripture.matthew`

Purpose:
- preserve book-level context
- support chapter and pericope children
- maintain canonical location

### 2. `scripture_chapter`
Use for chapter-level nodes when chapter context matters.

Examples:
- `scripture.genesis.1`
- `scripture.genesis.3`
- `scripture.romans.13`

Purpose:
- preserve local chapter logic
- support pericope and verse-cluster children

### 3. `pericope_node`
Use for meaningful interpretive units rather than isolated proof texts.

Examples:
- `pericope.genesis.image_of_god`
- `pericope.genesis.fall`
- `pericope.romans.authorities`

Purpose:
- preserve context beyond one verse
- support tradition-specific readings
- provide the preferred retrieval unit for many theological questions

### 4. `scripture_text`
Use for a discrete passage or verse cluster.

Examples:
- `text.genesis.1.26-28`
- `text.genesis.3.1-19`
- `text.romans.13.1-7`

Purpose:
- define the exact cited text span
- support close interpretation and comparison
- link to pericopes, concepts, and doctrine nodes

### 5. `interpretation_node`
Use for a particular reading of a passage.

Examples:
- `interpretation.genesis.1.26-28.augustinian`
- `interpretation.romans.13.1-7.reformed_confessional`
- `interpretation.genesis.3.orthodox`

Purpose:
- separate reading from raw text
- allow multiple interpretations to coexist explicitly
- support comparison across traditions and thinkers

### 6. `hermeneutic_node`
Use for a hermeneutic method or interpretive approach.

Examples:
- `hermeneutic.grammatical_historical`
- `hermeneutic.typological`
- `hermeneutic.canonical`
- `hermeneutic.patristic`
- `hermeneutic.reformed_confessional`

Purpose:
- define how an interpretation is being made
- prevent hidden interpretive assumptions
- support comparison of interpretive methods

### 7. `biblical_theme_node`
Use for recurring biblical themes that are not limited to one passage.

Examples:
- `biblical_theme.image_of_god`
- `biblical_theme.stewardship`
- `biblical_theme.authority`
- `biblical_theme.wisdom`

Purpose:
- connect multiple texts into a thematic map
- support doctrine and synthesis buildout

## Fractal structure

This layer should remain recursive.

Example hierarchy:
- `scripture.genesis`
  - `scripture.genesis.1`
    - `pericope.genesis.image_of_god`
      - `text.genesis.1.26-28`
        - `interpretation.genesis.1.26-28.augustinian`
        - `interpretation.genesis.1.26-28.thomistic`
        - `interpretation.genesis.1.26-28.reformed`

The same structural logic should repeat again for Romans, Matthew, Psalms, and other books.

## Required distinctions

### Text node
Defines the passage itself.

### Interpretation node
Defines a particular reading of that passage.

### Doctrine node
Defines the theological object derived from one or more texts.

### Concept node
Defines a reusable theological or philosophical concept that may be informed by doctrine and text.

### Application node
Defines downstream institutional, governance, or AI implications.

## Recommended coordinate fields for scripture-related nodes

Major scripture-related nodes should use the document header standard and include fields such as:
- `id`
- `anchor`
- `node_type`
- `parents`
- `children`
- `broader`
- `narrower`
- `related`
- `depends_on`
- `derived_from`
- `enables`
- `tradition`
- `tags`
- `authors`
- `reviewers`
- `tradition_review`
- `status`

### Additional recommended fields for scripture and interpretation nodes
- `scripture_book`
- `chapter`
- `verses`
- `pericope`
- `book_context`
- `chapter_context`
- `canonical_context`
- `interpretive_question`
- `hermeneutic_approach`
- `interpretive_options`
- `favored_reading`
- `major_support`
- `major_objections`
- `tradition_associations`
- `downstream_doctrinal_implications`
- `downstream_governance_implications`

## Folder taxonomy recommendation

### Scripture layer
- `docs/scripture/README.md`
- `docs/scripture/genesis/README.md`
- planned scripture-book roots for Romans and Matthew as the layer expands

### Hermeneutics layer
- `docs/hermeneutics/README.md`
- planned method notes such as `grammatical-historical.md`, `patristic.md`, `canonical.md`, and `reformed-confessional.md`

### Interpretations layer
Use either a dedicated interpretations branch later or place interpretation nodes under the most relevant scripture folder if locality is more important.

### Biblical themes layer
- `docs/biblical-themes/README.md`
- `docs/biblical-themes/image-of-god.md`
- `docs/biblical-themes/fall.md`
- planned future theme nodes such as `stewardship.md` and `authority.md`

## Recommended anchor patterns

### Scripture books
- `scripture.<book>`

### Chapters
- `scripture.<book>.<chapter>`

### Pericopes
- `pericope.<book>.<theme_or_unit>`

### Text nodes
- `text.<book>.<chapter>.<verse_span>`

### Interpretations
- `interpretation.<book>.<chapter>.<verse_span>.<tradition_or_reader>`

### Hermeneutics
- `hermeneutic.<approach>`

### Biblical themes
- `biblical_theme.<theme>`

## Relationship model

### Vertical relationships
- `parents`
- `children`
- `broader`
- `narrower`

### Lateral relationships
- `related`
- `aligns_with`
- `partially_aligns_with`
- `tensions_with`
- `requires_translation_to_compare`

### Derivational relationships
- `derived_from`
- `depends_on`
- `translates_into`
- `enables`
- `constrains`

## Build order recommendation for scripture ontology

### Phase 1
- create `docs/scripture/README.md`
- create `docs/hermeneutics/README.md`
- create `docs/biblical-themes/README.md`
- define first text cluster around Genesis 1 and Genesis 3

### Phase 2
Build initial text and theme nodes most relevant to the current theological architecture:
- `scripture.genesis`
- `scripture.genesis.1`
- `scripture.genesis.3`
- `text.genesis.1.26-28`
- `text.genesis.3.1-19`
- `biblical_theme.image_of_god`
- `biblical_theme.stewardship`
- `biblical_theme.fall`

### Phase 3
Add interpretation and hermeneutic nodes:
- Augustinian reading
- Thomistic reading
- Reformed reading
- Orthodox reading where relevant
- grammatical-historical and canonical method notes

### Phase 4
Link scripture nodes to doctrine, concept, and canon nodes.

### Future source-language phase
After source, licensing, and expert-review gates are in place, extend the graph
toward manuscript and original-language evidence:

- witness and fragment records;
- Hebrew, Aramaic, and Koine Greek transcription layers;
- lemma, morphology, syntax, and lexical-evidence objects;
- variant and passage-reconstruction objects;
- translation-comparison objects downstream of the source-language evidence.

## Summary principle

This project should be able to move from a theological architecture all the way down to text-level interpretation without losing context, method, or doctrinal mediation.

The scripture layer should therefore be:
- recursive
- context-preserving
- multi-interpretation capable
- hermeneutically explicit
- ontology-ready
