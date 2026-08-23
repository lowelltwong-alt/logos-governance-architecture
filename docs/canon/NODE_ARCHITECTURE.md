# Canon Node Architecture

> **CITATION REPAIR STATUS (owner decision HABITAT-HD-SESSION1-2026-08-19, HD-4a; repair item Q-01).**
> The former chat-local citation placeholders in "AI and retrieval rationale" were removed in the local Q-01 repair candidate and replaced with durable first-party Microsoft Learn links. This status records citation hygiene only; it does not increase the document's theological or governance authority.

This document defines the standard recursive architecture for canon nodes in the Logos Fractal Theological Architecture repository.

## Purpose

The canon branch should be structurally legible to both humans and future AI retrieval systems. That means the branch needs enough visible architecture to support recursive growth, but not so much fragmentation that every thinker is split into thin, low-context files before the content is mature.

The governing rule is:

**Begin with a strong single-file canon node. Promote it into a recursive folder only when complexity, reuse, or metadata needs justify the expansion.**

This preserves semantic coherence now while keeping the future fractal shell visible from the beginning.

## Current live node pattern

Each canon source should begin as a single strong file:

- `docs/canon/<name>.md`

Examples:
- `canon.augustine`
- `canon.bavinck`
- `canon.kuyper`

A single-file canon node should be strong enough to stand as one coherent retrieval object. It should usually include:
- why the thinker belongs in the shared core or in an overlay
- the major theological contributions relevant to this project
- doctrine areas most shaped by that thinker
- governance and AI-era implications where relevant
- strengths the thinker brings to the repository
- tensions or cautions in using the thinker
- downstream derivation or ordering relevance

## Future promoted node pattern

When a canon node becomes dense enough to justify recursive expansion, it may be promoted into a folder node using the following shell:

- `docs/canon/<name>/README.md`
- `docs/canon/<name>/artifact.json`
- `docs/canon/<name>/sources-and-lineage.md`
- `docs/canon/<name>/core-theology.md`
- `docs/canon/<name>/creation-fall-redemption.md`
- `docs/canon/<name>/governance-and-institutions.md`
- `docs/canon/<name>/ai-governance-implications.md`
- `docs/canon/<name>/notes.md`

Not every canon figure will require every file, but this shell provides a stable recursive pattern for future development.

## Promotion triggers

A single-file canon node should be promoted into a folder only when one or more of the following becomes true:

1. the file is becoming too long to function as one coherent retrieval object
2. the figure’s thought is clearly doing work across multiple major themes that deserve separate treatment
3. the node needs explicit machine-readable lineage metadata
4. separate application tracks are emerging, such as one file for theology and another for AI governance or institutional design
5. the figure is becoming a major anchor node whose reuse across the repository justifies deeper recursive structure

## AI and retrieval rationale

The repository should not oversplit too early. Microsoft Learn describes semantic chunks as meaningful units that preserve context and semantic relationships, and notes that Markdown headings can support section-based chunking. Its RAG architecture guidance likewise recommends defining document structure from headings, subheadings, and other structural elements. In practice, that means a canon node should first be written as a dense, well-structured file, then promoted only when the content naturally divides into multiple coherent parts. See [Chunk large documents for RAG and vector search in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents) and [Develop a RAG solution on Azure: Chunking phase](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-chunking-phase).

## Relationship to the rest of the repository

This pattern should mirror the broader fractal logic of the project:
- doctrine nodes begin as strong files and may later become folders
- weighting profiles begin as strong files and may later gain sidecars or comparison notes
- derivation examples begin as single worked artifacts and may later expand into multi-file recursive nodes

The same rule applies everywhere:

**Let complexity earn structure.**

That is the cleanest way to keep the repository both human-legible and AI-legible.

## Recommended canon branch convention

For now, the canon branch should contain:
- one strong file per major thinker
- one shared branch-level architecture note
- future expansion paths embedded inside major canon files

That gives the repository visible recursive discipline without forcing premature empty folders.
