# Ontology Discipline

## Purpose

This file defines the structural discipline required to keep the Logos repository recursive, machine-usable, and extensible.

This project is not a loose note dump. It is a theological architecture intended to support:
- human reading
- semantic retrieval
- RAG-style interrogation
- recursive comparison across thinkers, doctrines, concepts, and traditions
- future ontology development

Because of that, vocabulary drift and structural drift are architecture problems, not merely formatting problems.

## Core rule

Do not create new anchors, tags, node types, relationship verbs, concept labels, or category names casually.

New vocabulary should be added only when the existing structure cannot represent the new concept without distortion.

## Preferred order of extension

When adding something new, use this order:

1. Can this be modeled as a new node using existing vocabulary?
2. Can it be represented as a child of an existing node?
3. Can it be handled using existing tags or relationship types?
4. Does it require one new controlled term?
5. Only then consider adding a new field family or changing the structure.

## Stable-shell rule

The repository should grow by adding nodes and relationships within a recurring shell.

The shell should not be rewritten every time the project expands.

In practice, this means:
- prefer new nodes over new top-level sections
- prefer new relationships over duplicate prose
- prefer controlled vocabulary expansion over redesign
- prefer optional fields over structural drift

## Fractal rule

The project is fractal when the same structural logic repeats at multiple levels.

That means:
- major repository domains are nodes
- thinker pages are nodes
- doctrine pages are nodes
- concept pages are nodes
- comparison pages are nodes
- important sub-sections may become child nodes when needed

A concept that repeats across multiple thinker pages should eventually become its own reusable concept node.

## Controlled vocabulary rule

Use existing vocabulary whenever possible.

Contributors should not introduce synonyms casually when a controlled term already exists.

For example, do not mix several equivalents when one approved term already exists:
- `aligns_with` vs `agrees_with` vs `fits_with`
- `concept.imago_dei` vs `concept.image_of_god`
- `comparison` vs `contrast` vs `crosswalk`

Choose one controlled term and reuse it consistently.

## Extension threshold

A new vocabulary term is justified when all of the following are true:
- the concept matters to the architecture
- the concept cannot fit existing terms without distortion
- the distinction will likely recur
- the term can be defined clearly enough for reuse

If those conditions are not met, prefer existing vocabulary.

## Naming rule

Names should be:
- stable
- semantically clear
- predictable
- reusable
- minimally ambiguous

Avoid:
- trendy phrasing
- redundant synonyms
- overlong labels
- vague category names

## Retrieval and chunking rule

Files and sections should be chunked in semantically meaningful ways.

This matters because retrieval systems work best when concepts are:
- distinct enough to retrieve cleanly
- large enough to preserve conceptual integrity
- consistent enough to compare across files

When a section becomes too broad or too dense, consider promoting it into a child node.

## Comparison rule

Comparison should be explicit rather than buried.

Where possible, comparisons should be modeled through:
- relationship edges
- comparison pages
- shared concept nodes
- alignment and tension maps

Do not rely only on readers inferring connections from prose.

## Documentation rule

If a new controlled vocabulary term is introduced, document it in the relevant registry before using it broadly.

At minimum, this means:
- add the term to the relevant governance file
- define it briefly
- use it consistently thereafter

## Summary principle

Keep the shell stable.
Let the branches grow.
Promote repeated patterns into reusable nodes.
Document vocabulary before letting it spread.

That is the core discipline of this repository.

## Academic extension rule

Future academic domains extend the stable shell through versioned domain packs;
they do not expand one universal kernel until it contains every discipline. A
pack must preserve unknown extension data losslessly, use a stable namespace,
declare its consumers, and remain within the authority ceiling in
[`academic-extension-contract.md`](academic-extension-contract.md). A new domain
is not evidence that an existing identity, relationship, or trust rule should be
silently redefined.
