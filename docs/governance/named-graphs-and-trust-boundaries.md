# Named Graphs and Trust Boundaries

## Purpose

This file defines how the repository should think about named graphs, trust boundaries, and scoped graph partitions as the ontology grows more machine-readable.

This file should be read together with:
- `trust-zones.md`
- `asserted-inferred-and-boundary-layers.md`
- `translation-trust-and-sectarian-classification.md`
- `noncanonical-and-heresy-classification.md`

## Core principle

A future theological knowledge graph should be able to separate not only objects by type, but also claims by trust boundary and assertion context.

Named-graph thinking is one of the cleanest ways to preserve that separation.

## What this means in practice

The repository does not need to implement a full named-graph runtime immediately.

But it should be designed so that future exports, graph builds, or query layers can distinguish between different graph contexts.

Examples of future graph contexts include:
- core asserted graph
- inferred graph
- tradition-specific graph
- canonical boundary graph
- quarantine or AI-generated graph

## Why named-graph thinking matters

Without graph-context separation, future systems may wrongly flatten:
- direct assertions and computed derivations
- core trusted material and experimental material
- one tradition's boundary claims and another's
- reviewed objects and machine-generated candidates

That weakens both trust and interpretability.

## Recommended future graph families

### Core asserted graph
Contains reviewed, directly authored, high-trust local assertions.

### Inference graph
Contains computed or derived structure that should remain distinguishable from authored local truth.

### Tradition-scoped graph
Contains claims explicitly local to one tradition, canon model, or theological boundary framework.

### Boundary graph
Contains warnings, restricted materials, sectarian translation notes, noncanonical classifications, and related comparison logic.

### Quarantine graph
Contains low-trust, AI-extracted, or review-pending material not yet suitable for normal repository trust assumptions.

## Governance rule

A graph boundary is not only a data-format decision.
It is a meaning decision.

The boundary tells future systems how to interpret the claim, how far to trust it, and whether it should be mixed with other materials.

## Retrieval rule

Future graph retrieval should be able to choose between graph families.

Examples:
- only core asserted graph
- asserted plus inferred
- one tradition-scoped graph plus the core graph
- exclusion of quarantine graph by default

## Provenance rule

Graph boundaries should work together with provenance.

That means a future system should ideally know both:
- which graph context a claim belongs to
- who or what generated or asserted it

## Fractal rule

Named-graph thinking should recur across scales.

That means the same logic may apply to:
- a full export dataset
- a branch-level graph family
- a specialized witness subgraph
- a local doctrinal comparison graph

## Summary principle

A mature ontology should preserve graph context as part of meaning.

Named trust boundaries are one of the strongest ways to do that.

## Academic hypothesis and context graphs

The [Academic Extension Contract](academic-extension-contract.md) adds a draft
interoperability rule for future domain packs: competing hypotheses occupy
distinct named graphs and no default graph supplies an automatic winner.
Contextual material remains in its domain and trust graph. Graph reachability,
centrality, model confidence, or consensus cannot raise its authority or let it
ground doctrine. Any later adjudication must preserve alternatives, evidence,
dissent, and the human decision record.
