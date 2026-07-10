---
object_type: governance_policy
trust_zone: proposed
lifecycle_status: draft
provenance_note: "Created 2026-04-30 as a draft Bible source, licensing, and ingestion policy for Logos. Updated 2026-07-10 to recognize OD-C-OPEN-A independent, personal, church, ministry, lay, teaching, and noncommercial educational study without treating research purpose as a rights override."
reason_for_inclusion: "Set source-use boundaries before Bible text, theology, or RAGGraph ingestion work."
review_status: unreviewed
ai_usage_posture: policy_draft_not_legal_advice
---

# Bible Source and Licensing Policy

## Status

Draft governance policy. This is not legal advice. Every source must be reviewed before ingestion, indexing, embedding, publication, or redistribution.

The canonical owner-purpose boundary is
[`governance/INDEPENDENT_STUDY_SOURCE_AUTHORIZATION.yaml`](../../governance/INDEPENDENT_STUDY_SOURCE_AUTHORIZATION.yaml).
It recognizes rigorous independent and ecclesial scholarship without requiring
university, seminary, employer, credential, or institutional affiliation.
Research quality is evaluated through evidence, provenance, reproducibility,
source competence, and review. Those purposes do not override source rights.

An optional institutional-access route may be available through a household
academic who voluntarily uses her own account. When a needed source is not
otherwise available, stop and ask the owner. A `.edu` identity or library login
is an access channel, not permission to redistribute, text-mine, transmit to AI,
or place material in Git. Never request, store, share, or automate another
person's credentials; review the institution and provider terms for the exact
proposed use.

## Core rule

Logos may store references, metadata, citations, source profiles, and brief review excerpts for protected modern Bible translations and theology works.

Logos must not add full protected modern works, bulk extracts, public chunks, or embeddings unless a reviewed lawful basis exists.

## Source-use categories

### Category A: public repository ingestion candidate

Use this category only when review confirms that the text or edition may be stored in the public repository.

Possible candidates to investigate:

- public-domain English Bible translations;
- open-license Bible translations;
- older public-domain original-language editions;
- public-domain theology editions.

### Category B: reference-only public profile

Use this category when the source is useful for routing, comparison, and citation but should not become public corpus text.

Allowed:

- bibliography;
- source profile;
- doctrine routing;
- citation pointers;
- short review excerpts;
- original summaries.

Not included in the public repo:

- full source text;
- bulk source chunks;
- embeddings derived from the full source;
- public RAG corpus derived from the full source.

### Category C: private licensed connector

Use this category when an independent researcher, self-educated student, user,
church, ministry, seminary, or institution has its own lawful access and wants
private retrieval.

Public repo may store only connector policy, source manifest schema, and non-sensitive metadata. Private source text, chunks, and embeddings remain outside the public repository.

## Original-language route

Ancient biblical words and manuscripts must be distinguished from modern editions, transcriptions, databases, morphology, and critical apparatuses.

Track separately:

- ancient work;
- edition;
- digital source;
- transcription;
- morphology;
- lemma mapping;
- apparatus;
- manuscript images;
- license or terms of use.

## Bible source registry fields

Every source candidate should eventually declare:

- source_id
- title
- language
- text_family
- scope
- translation_or_edition
- rights_status
- license_or_terms
- jurisdiction_notes
- allowed_public_repo_use
- allowed_private_index_use
- allowed_embedding_use
- source_url
- canonical_reference_format
- ingestion_status
- review_status
- reviewer
- notes

## RAGGraph ingestion gates

Before any Bible text is chunked or embedded:

1. Source registry entry exists.
2. Source-use status is reviewed.
3. Canonical reference format is defined.
4. Chunking rules are defined.
5. Metadata sidecar contract is defined.
6. Biblical connection vocabulary exists.
7. Protected modern works are not used as public corpus text without review.
8. Raw full-text corpus material is not promoted into higher trust zones by default.

## Preferred first pilot

A safe pilot should use one book, one or two public-domain or open texts, and one original-language source only if its terms permit.

Suggested pilot:

- Romans or John;
- one public-domain or open English text;
- optional original-language source after review;
- metadata sidecars;
- no broad graph promotion until reviewed.
