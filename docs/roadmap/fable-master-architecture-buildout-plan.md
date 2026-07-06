---
object_type: cross_repo_master_architecture_roadmap
trust_zone: canonical
lifecycle_status: active
provenance_note: "Created on 2026-07-06 after owner request to prepare a Fable-led master architecture pass across the Logos repo family, with Codex handling lower-risk scaffolding and implementation support."
reason_for_inclusion: "Future agents need one governed handoff surface that explains how the repos should work together, which hard problems require Fable-level architecture, and which supporting work can be delegated to Codex."
---

# Fable Master Architecture Buildout Plan

## Purpose

This roadmap prepares the next Fable pass across the Logos repo family.

Fable should act as the master architect for high-risk, cross-disciplinary work that combines biblical scholarship, orthodox theological method, source-history modeling, software architecture, graph design, and knowledge management. Codex should handle deterministic scaffolding, validation, templates, registries, tests, and PR hygiene after Fable has supplied the architecture kernels.

This file is a roadmap and handoff surface. It does not authorize Scripture output changes, graph truth, doctrine authority, repo creation, source import, or denominational systematic theology as chunking authority.

## Current Repo Roles

| Repo | Current or planned role | Authority boundary |
| --- | --- | --- |
| `logos-governance-architecture` | Cross-repo governance, ontology discipline, repo registry, contracts, theological architecture roadmaps | Governs repo roles and vocabularies; does not store Scripture data-plane outputs |
| `logos-scripture-graph` | Canonical 66-book Scripture data plane, chunking decisions, metadata, validators, review packets | Owns Scripture data and chunk outputs; must not import boundary or doctrine material as Scripture authority |
| `logos-boundary-literature` | Boundary, reception, patristic, commentary, theologian-writing source metadata and scoped support | Supports comparison and reception; must not override or equal Scripture authority |
| `logos-chunking-harness` | Planned execution and evaluation plane for cross-corpus chunking | No semantic authority; should prove isolation and preservation |
| `logos-doctrine-genealogy` | Planned doctrine lineage, theologian, tradition, and profile-comparison plane | No canonical Scripture authority; should reference Scripture and boundary records by contract |
| `noesis-atlas` | External advisory comparison context | Read-only advisory; cannot modify, gate, or govern Logos |

## Desired Architecture

The Logos family should become one governed architecture with multiple validated shells:

1. Scripture records and chunk outputs remain in `logos-scripture-graph`.
2. Boundary, reception, patristic, commentary, and theologian source records route to `logos-boundary-literature`.
3. Doctrine development across time routes to the planned `logos-doctrine-genealogy` repo after explicit registration.
4. Chunking execution and large-scale evaluation route to the planned `logos-chunking-harness` repo after explicit registration.
5. Governance rules, vocabularies, repo contracts, AI discovery surfaces, and dependency maps remain in `logos-governance-architecture`.
6. Joined evidence products must remain derived artifacts with hard namespaces such as `scripture_*`, `boundary_*`, `doctrine_*`, and `evidence_*`.
7. Semantic similarity, embeddings, generated confidence, and model judgments may create candidates or review queues, but not truth.

## Fable Hard Problems

Fable should focus on problems where a wrong abstraction would permanently bend the project.

### 1. Doctrine Genealogy Ontology

Design the future `logos-doctrine-genealogy` object model before the repo is created.

The model should represent:
- doctrine topics
- doctrine views
- doctrine assessments
- theologians
- schools and traditions
- councils and confessions
- source works
- claims
- derivations
- modifications
- objections
- condemnations
- counterclaims
- reception history
- downstream influence

The key question is how to trace "what derived from what" without flattening theology into a single timeline or letting a later systematic framework secretly govern earlier sources.

### 2. Theological Slice Method

Define how a vertical slice of theology should be built from Scripture, source texts, theologians, councils, traditions, and later interpretations.

Each slice should answer:
- What is the doctrine or question?
- What Scripture passages are materially involved?
- Which original-language or textual issues matter?
- Which early sources and councils matter?
- Which theologians shaped the doctrine?
- Which later traditions developed it differently?
- Which deviations were corrected, condemned, or left disputed?
- Which claims are orthodox core, tradition-scoped, disputed, heterodox, or non-authorizing comparison?

### 3. Orthodoxy Boundary Without Denominational Capture

Specify how the project affirms Nicene and Chalcedonian orthodox Christianity while refusing both hidden liberal-critical defaults and a single denominational systematic theology as project authority.

The architecture must distinguish:
- Scripture authority
- orthodox boundary
- tradition-scoped doctrinal development
- denominational profile
- theologian-specific formulation
- historical description
- heresy or non-orthodox counterclaim
- advisory scholarship

### 4. Source Authority Stratification

Create a source authority ladder that can handle Scripture, original-language evidence, textual witnesses, creeds, councils, fathers, theologians, confessions, commentaries, modern scholarship, and sectarian or heterodox materials.

The hardest part is preserving usefulness without collapsing authority. A source can be historically important, reception-important, or adversarially useful without becoming doctrine authority.

### 5. Relationship Vocabulary For Theological Derivation

Define the relationship verbs that make theology traceable across time.

Likely candidates include:
- `derives_from`
- `clarifies`
- `modifies`
- `systematizes`
- `depends_on`
- `interprets_passage`
- `cites_source`
- `receives`
- `rejects`
- `counters`
- `condemns`
- `is_condemned_by`
- `partially_aligns_with`
- `tensions_with`
- `requires_original_language_review`
- `requires_textual_critical_review`

Fable should decide which belong in governance vocabulary, which belong in doctrine genealogy, and which should remain provisional.

### 6. Evidence And Provenance Standard

Define the minimum proof needed before a theology-lineage claim can become machine-readable.

Every promoted claim should record:
- source basis
- citation target
- claim type
- authority zone
- tradition scope
- lifecycle status
- reviewer or owner decision
- upstream dependencies
- downstream risks
- contested status
- known counterclaims
- related Scripture references
- boundary-source references
- validation coverage

### 7. Cross-Repo Evidence Product Shape

Design how a future query can safely say, for example:

"Show the development of Trinitarian doctrine from Scripture through early councils, major theologians, confessional traditions, and modern disputes, including where later formulations clarified, opposed, or deviated from earlier claims."

The query result must not blur authority. It should show Scripture data, boundary/reception sources, doctrine-lineage objects, and advisory notes in separate namespaces.

### 8. Pilot Slice Selection

Pick the first three theological slices for doctrine-genealogy MVP work.

Recommended candidates:
- Trinity and Christology, because orthodoxy boundaries are central and early-source material is rich.
- Scripture authority and canon, because it governs all downstream use.
- Salvation or anthropology, because later theologians and traditions diverge in ways that matter for chunking, retrieval, and AI governance.

Fable should present options, risks, and recommended order before implementation.

## Codex Work After Fable

Codex should do the deterministic work once Fable supplies architecture decisions:

- create or update repo registration issues and manifests
- scaffold schemas and templates
- update AI front doors and AI tables of contents
- add validators and tests
- add no-context audit instructions
- create cross-repo link checks
- build handoff packets
- add migration queues
- write example objects from approved templates
- keep branch, PR, merge, and cleanup hygiene clean

Codex should not decide hard theological ontology questions by itself.

## Buildout Phases

### Phase 0: Mirror And Branch Hygiene

Confirm each repo has a clean live-main worktree or a clearly named scratch worktree. Do not build from dirty parallel-agent branches.

Deliverables:
- repo status matrix
- open PR matrix
- branch cleanup docket
- decision on which local worktrees are canonical, scratch, or archive

### Phase 1: Fable Architecture Memo

Fable produces the master architecture memo for doctrine genealogy and cross-repo evidence products.

Deliverables:
- hard-problem recommendations
- planned repo registration decision packet
- doctrine genealogy object model
- relationship vocabulary proposal
- source authority stratification proposal
- first three pilot slices with repercussions

### Phase 2: Governance Registration

Codex turns approved Fable architecture into governed surfaces.

Deliverables:
- updated repo registry if `logos-doctrine-genealogy` or `logos-chunking-harness` should move from planned to active
- updated dependency map
- updated AI TOC and front-door surfaces
- validation gates for any new governance surface

### Phase 3: Boundary Source Readiness

Strengthen `logos-boundary-literature` to hold patristic, commentary, theologian, confessional, and reception-history source metadata without becoming doctrine authority.

Deliverables:
- source metadata schema
- authority-scope fields
- heresy and adversarial-source handling
- source import review packets
- validators for non-authorizing source use

### Phase 4: Doctrine Genealogy MVP

Create or prepare the doctrine-lineage plane only after owner authorization.

Deliverables:
- repo scaffold or governed module decision
- claim, source, theologian, tradition, council, and relationship schemas
- sample objects for the first approved slice
- no-authority-transfer validators

### Phase 5: Cross-Repo Query And Audit Surface

Build derived evidence views that join Scripture, boundary, and doctrine data without transferring authority.

Deliverables:
- namespace-separated evidence packet format
- query examples
- no-context audit instructions
- provenance completeness validator

### Phase 6: Scale Across Theology

Expand from pilot slices to the wider map of Christian theology across time.

Deliverables:
- slice backlog
- source backlog
- theologian backlog
- tradition profile backlog
- unresolved controversy docket
- review cadence

## Fable Prompt

Use this prompt when asking Fable to continue:

```text
You are Fable acting as master architect for the Logos repo family. Read the governance repo front door, AI table of contents, data-flow map, repo registry, repository integration map, theological buildout roadmap, and this Fable master architecture buildout plan.

Your task is not to implement code. Your task is to produce the architecture kernels Codex should implement later.

Design the doctrine-genealogy and cross-repo evidence architecture for tracing theology across time: Scripture, original-language evidence, source witnesses, councils, fathers, theologians, traditions, confessions, objections, deviations, condemnations, and downstream influence.

Preserve Nicene and Chalcedonian orthodox Christianity as the boundary. Do not let anti-supernatural, anti-canonical, heterodox, liberal-critical, or sectarian assumptions become hidden defaults. Also do not hardcode one denominational systematic theology as project authority.

Return:
1. the hardest architecture risks,
2. the proposed doctrine-genealogy ontology,
3. the source authority stratification model,
4. the relationship vocabulary,
5. the first three recommended theological slices,
6. what should live in governance, boundary literature, scripture graph, doctrine genealogy, chunking harness, and Noesis,
7. what Codex can safely implement after your pass,
8. what owner decisions are required before implementation.

Do not authorize Scripture output changes, graph/retrieval/vector truth, doctrine authority, source imports, repo creation, or chunk output.
```

## Stop Rules

Stop and ask the owner before:
- creating `logos-doctrine-genealogy`
- creating `logos-chunking-harness`
- promoting a doctrine-lineage object to reviewed status
- importing source corpora
- using boundary literature as Scripture authority
- using Noesis as Logos authority
- changing Scripture chunks or graph truth
- changing orthodox boundary policy
- selecting a denominational systematic theology as project authority
