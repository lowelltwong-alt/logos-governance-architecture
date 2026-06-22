---
object_type: governance_control
trust_zone: canonical
lifecycle_status: active
provenance_note: "Added 2026-06-22 from owner request to create anti-guessing guardrails for Scripture chunking, vector retrieval, graph edges, and reusable decisions across unrelated repos."
reason_for_inclusion: "Prevent semantic closeness, generated confidence, or informal vibes from becoming governed structure without source basis, scope, provenance, and review."
---

# Anti-Guessing And Evidence Discipline

## Purpose

This control protects the repository family from a subtle failure mode:
turning semantic similarity, AI confidence, topical resemblance, or convenient
data shape into authority.

It applies especially to Scripture chunking, vector indexes, graph edges,
retrieval neighborhoods, doctrine-lineage links, and any future repo where a
machine proposes structure faster than a human can review it.

## Core Rule

No chunk boundary, vector neighborhood, graph edge, doctrine-lineage link,
classification, or repo-placement decision may be treated as asserted truth
unless it declares:

- source basis;
- authority owner;
- trust zone;
- scope;
- method or transformation used;
- asserted versus inferred status;
- review status;
- provenance.

If those cannot be named, the object stays a candidate, quarantine item,
derived artifact, or research note.

## What Counts As Guessing

The following are not sufficient evidence by themselves:

- embedding closeness;
- shared keywords;
- topical co-occurrence;
- smooth AI prose;
- high model confidence;
- a generated summary that sounds right;
- a graph algorithm ranking;
- a vector-search result;
- a commentary or tradition note with no scope;
- a downstream application that feels useful.

These may create questions, candidates, or review queues. They do not create
Scripture authority, doctrine authority, graph truth, or repo-governance truth.

## Scripture Chunking Rule

Canonical Scripture chunks belong to `logos-scripture-graph`.

Every governed Scripture chunk should be able to name:

- canonical passage ID or range;
- source text, edition, or translation policy;
- license posture;
- chunking method;
- whether the boundary is canonical, editorial, discourse-based, semantic, or
  retrieval-only;
- review status;
- downstream use limits.

A retrieval-friendly chunk is not automatically a theological unit. A semantic
chunk boundary is not automatically a canonical boundary. A vector-friendly
split must never rewrite, replace, or imply authority over the canonical
passage structure.

## Source-Language Root Graph Horizon

The long-range Scripture graph should become manuscript- and
source-language-aware rather than English-translation-rooted.

The likely root evidence layer is:

- Hebrew and Aramaic witnesses for the Old Testament where applicable;
- Koine Greek witnesses for the New Testament and relevant ancient versions;
- manuscript witnesses, fragments, transcriptions, variants, lemmata,
  morphology, syntax, and lexical evidence;
- passage and reconstruction objects that preserve witness, reading, and
  confidence distinctions.

This is a horizon, not a current authorization. The project must not pretend
that present AI resources can safely replace expert biblical-language,
text-critical, philological, historical, or manuscript review.

Before source-language graph promotion, the system needs:

- licensed or public-domain source data with provenance;
- controlled vocabulary for witness, reading, lemma, morphology, syntax,
  variant, and reconstruction relations;
- gold sample passages reviewed by qualified humans;
- explicit confidence fields for dating, reading, reconstruction, lexical, and
  syntactic judgments;
- validation that separates manuscript evidence, original-language analysis,
  translation rendering, interpretation, and doctrine;
- stop rules for hallucinated Greek/Hebrew/Aramaic analysis.

AI may assist with lookup, alignment, candidate parsing, and review queues. AI
must not self-certify original-language expertise, silently normalize variants,
invent manuscript evidence, or promote language analysis as reviewed truth.

## Vector And Embedding Rule

Embeddings are retrieval aids, not authority sources.

Vector output may:

- suggest candidate neighborhoods;
- help find related passages or source records;
- propose review queues;
- support recall in search.

Vector output may not:

- create canonical Scripture relationships;
- create doctrine claims;
- promote commentary into Scripture meaning;
- rank one tradition's reading as universal truth;
- bypass controlled relationship vocabulary;
- become default retrieval policy without review.

## Graph Edge Rule

A governed edge must name the strongest accurate relationship type without
overstating the evidence.

Every graph edge should declare:

- subject object;
- predicate or controlled relationship verb;
- object target;
- evidence basis;
- direction;
- scope;
- asserted or inferred status;
- review status;
- source or method provenance.

If the relationship is only "these seem connected," it is not ready for a
governed edge. Keep it as a candidate relation, retrieval-neighborhood hint, or
research question.

## Scripture Edge Caution

Scripture graph edges need extra care because downstream systems may mistake
graph convenience for biblical authority.

Different edge families must stay distinct:

- quotation;
- allusion;
- echo;
- lexical relation;
- translation rendering;
- textual witness attestation;
- textual variant relation;
- manuscript provenance;
- thematic connection;
- typological correspondence;
- doctrine grounding;
- reception-history interpretation.

Do not flatten these into generic `related_to` edges when the stronger or more
careful term matters. Do not use AI-inferred similarity as source support.

## Edge Authority Ladder

Use the lowest honest status.

| Status | Meaning | Allowed use |
|---|---|---|
| `retrieval_candidate` | Suggested by search, embeddings, co-occurrence, or AI. | Review queue only. |
| `derived_view` | Computed from already governed objects. | Derived products with labels. |
| `proposed_relationship` | Human-authored or AI-staged with named evidence. | Reviewable graph candidate. |
| `asserted_relationship` | Reviewed edge using controlled vocabulary and evidence. | Governed traversal. |
| `canonical_scripture_record` | Scripture text, witness, fragment, or variant record owned by Scripture Graph. | Scripture data plane only. |

Commentary, patristic writing, theologian writing, doctrine lineage, vectors,
and generated reports never become `canonical_scripture_record`.

## General Repo-Design Transfer

For any unrelated future repo, ask the same questions before creating structure:

- What is the source of truth?
- What is generated convenience?
- What is inferred from governed structure?
- What is merely a candidate?
- What must be scoped to a tradition, profile, license, corpus, time period, or
  reviewer?
- What validator would fail if the system guessed?

This pattern should travel beyond Scripture work. The antidote to vibes is not
more ceremony. It is naming the source, scope, method, trust level, and review
gate before structure becomes durable.

## Stop Conditions

Stop and report when:

- an edge, chunk, vector result, or graph relation lacks evidence basis;
- semantic similarity is being treated as source support;
- a generated result is being promoted without review status;
- a Scripture chunk boundary is being treated as canonical without authority;
- a commentary, patristic, theologian, or doctrine-lineage claim is being used
  as Scripture authority;
- an inferred connection would change default retrieval or theological meaning;
- the correct repo owner cannot be named.

## Summary Principle

Machines may surface candidates.
Governance decides what can endure.
