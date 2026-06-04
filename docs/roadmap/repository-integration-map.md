# Repository Integration Map

## Purpose

This file explains how the major layers of the repository fit together after the recent expansion of scripture, translation, manuscript, noncanonical, and graph-oriented concordance work.

It is meant to reduce drift between:
- the human-readable theological architecture
- the ontology-ready scripture and source layers
- the graph or concordance side of the project

## Core principle

The repository should be understood as one architecture with multiple surfaces, not as separate projects.

The major surfaces are:
- theological source architecture
- scripture and interpretation architecture
- source-control and boundary architecture
- graph and concordance architecture

These should reinforce one another rather than diverge.

## Constituent repositories (surfaces in separate shells)

"One architecture, multiple surfaces" does not require one git repository. Some
surfaces are best expressed as their own deterministic, separately-validated
repositories, coupled to this architecture **by contract** (validated release
artifacts + schemas), not by merge or submodule. The ontology stays continuous;
the shells differ in format.

| Repository | Role | Implements layers |
|------------|------|-------------------|
| `logos-governance-architecture` (this repo) | Theological source architecture: taxonomy, ontology, ordering/weighting logic, governance | 1–2 (canon, doctrine/concept), 5 (biblical theme), and the governance of 3–9 |
| [`logos-scripture-graph`](https://github.com/lowelltwong-alt/logos-scripture-graph) | **Data-plane substrate**: deterministic Bible ingest, passage/witness records, canon profiles, boundary claims, retrieval chunks, provenance + validation | 3 (scripture), 4 (original-language/translation/manuscript, via Strong's WordTokens), 6 (boundary-source, via canon profiles), 7 (graph/concordance), 8 (primary-sources, future) |

The substrate consumes this repo's taxonomy/ontology/canon discipline and emits
machine-readable, provenance-stamped artifacts the graph/concordance layer can
govern. Its own `ADR-0001` keeps it standalone so source-fidelity and validation
evolve independently of the theological node surface, while remaining a governed
surface of the same architecture. See its `.ai/control/PROJECT_CONTEXT.md` for the
reciprocal mapping.

## Main repository layers

### 1. Canon layer
This holds major thinker nodes and their local substructure.

Examples:
- Augustine
- Aquinas
- Calvin
- Athanasius

### 2. Doctrine and concept layers
These hold reusable theological objects and shared conceptual nodes.

Examples:
- anthropology
- grace
- institutions
- imago Dei
- vocation

### 3. Scripture layer
This holds biblical books, chapter nodes, pericopes, and text nodes.

Examples:
- Genesis
- Genesis 1
- Genesis 3
- Genesis 11
- later passage clusters and pericope nodes

### 4. Original-language, translation, and manuscript layers
These hold lexical, translation, and textual-witness nodes that help preserve fidelity and traceability.

Examples:
- Hebrew terms
- modern translation witnesses
- Masoretic Text
- Septuagint
- text-critical notes

### 5. Biblical theme layer
This holds recurring scriptural themes that bridge text, doctrine, and theology.

Examples:
- image of God
- stewardship
- Babel
- covenant

### 6. Boundary-source layer
This holds deuterocanonical, pseudepigraphal, forged, or heretical materials in a controlled and explicitly limited way.

Examples:
- 1 Enoch
- later deuterocanonical nodes
- forged or sectarian materials requiring warning blocks

### 7. Graph and concordance layer
This holds machine-readable graph artifacts, relationship objects, and verse/topic edge structures when a connection becomes important enough to govern explicitly.

Examples:
- verse graph datasets
- relationship objects
- reusable edge objects with provenance
- 
### 8. Primary-sources layer
This future layer holds governed source objects related to biblical primary materials and their interpretive handling.

Examples:
- manuscript witnesses
- fragments
- transcriptions
- passage reconstructions
- lexical evidence objects
- translation comparison objects

This layer is meant to connect the repository’s theological and graph logic to a future confidence-aware textual corpus rather than functioning as a separate manuscript project.

### 9. Exceptions-lake and learning-loop layer
This layer captures expectation failures, pressure vectors, and governed adaptation proposals so the architecture can learn without silent doctrinal drift.

Examples:
- nine-layer exception addresses
- exception event objects
- adaptation promotion records
- links from exception pressure to rule/taxonomy/ontology/governance updates

## How the layers connect
The primary-sources layer extends the scripture, lexical, manuscript, and translation layers by preserving a path from witness or fragment to reconstruction, lexical analysis, translation comparison, and downstream doctrine or theology.

The intended pattern is:

- scripture text informs biblical theme
- lexical and translation nodes clarify scripture text
- manuscript witnesses qualify textual confidence and tradition history
- biblical themes connect into doctrine and concept nodes
- canon thinkers interact with doctrine, concept, and scriptural themes
- boundary layers document what may not function as primary doctrinal authority
- graph/concordance layers make the connections machine-readable and reviewable
- exceptions-lake records preserve model resistance and route reviewed adaptation back into governed layers

## Practical repository reading order

A contributor can usually understand the project in this order:

1. root `README.md`
2. `docs/governance/README.md`
3. `docs/roadmap/theological-buildout-roadmap.md`
4. canon, doctrine, concept, and scripture nodes
5. translation / manuscript / original-language support nodes
6. graph or concordance structures where explicit machine-readable edge control is needed

## Coherence rule

When a new layer is added, it should be integrated in three places where relevant:
- governance
- roadmap or integration guidance
- the actual node surface itself

That keeps the repository from accumulating silent architectural side tracks.

## Summary principle

The repository should keep one recursive architecture across:
- human-readable nodes
- scripture and source-control nodes
- graph and concordance nodes

The shells may differ in format, but the ontology should remain continuous.
