---
object_type: dad_ready_lesson_outbox
trust_zone: learning-sidecar
lifecycle_status: active
provenance_note: "Created 2026-07-06 by Codex after owner request to make DAD aware of Fable feedback, Codex implementations, reusable kernels, lessons learned, and cross-domain transfer patterns."
reason_for_inclusion: "Capture reusable architecture lessons from the Fable/Codex doctrine-genealogy buildout so future agents and a future DAD workflow can discover, reuse, audit, and adapt them without relying on chat memory."
---

# DAD Lesson Outbox: Fable Kernels and Reusable Architecture

This file is a DAD-ready knowledge-capture packet. The repo does not yet expose
a formal DAD runtime or ingestion API, so this file is the durable outbox
surface for DAD or any future learning system.

This file is not authority. It does not authorize repo creation, doctrine
records, source imports, Scripture output, chunk output, graph truth, retrieval
truth, vector truth, reviewed-lineage promotion, legal advice, or secular client
implementation. It captures lessons and reusable patterns that must still pass
the target repo's governance, privacy, source, and review gates.

## Source Packet

Primary source surfaces:

- [`fable-master-architecture-buildout-plan.md`](../fable-master-architecture-buildout-plan.md)
- [`README.md`](README.md)
- [`OWNER-DECISIONS-AND-PILOTS.md`](OWNER-DECISIONS-AND-PILOTS.md)
- [`CODEX_HANDOFF.md`](CODEX_HANDOFF.md)
- [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md)
- [`KERNEL-A-object-model-and-vocabulary.md`](KERNEL-A-object-model-and-vocabulary.md)
- [`KERNEL-B-orthodoxy-and-authority.md`](KERNEL-B-orthodoxy-and-authority.md)
- [`KERNEL-C-provenance-and-gates.md`](KERNEL-C-provenance-and-gates.md)
- [`KERNEL-D-evidence-product.md`](KERNEL-D-evidence-product.md)
- [`KERNEL-E-codex-theology-tripwire.md`](KERNEL-E-codex-theology-tripwire.md)

Implementation evidence:

- Governance PRs #70-#80 recorded the master plan, kernels, owner decisions,
  family map, vocabulary, schemas, validators, examples, boundary hardening,
  Scripture front-door split, registration drafts, and implementation status.
- Boundary PR #14 and Scripture Graph PR #156 are referenced by
  [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md).

## DAD Ingestion Rules

DAD or any future learning system should ingest this as:

- `lesson_type: reusable_architecture_pattern`
- `source_basis: governed_repo_files`
- `authority_level: non_authorizing_learning_sidecar`
- `reuse_domains: logos_doctrine_genealogy, knowledge_graph_architecture, legal_kg_design, document_comparison, version_lineage, contract_derivative_analysis`
- `must_preserve: provenance, scope, authority separation, review gates, no-semantic-similarity-as-truth`

DAD must not ingest this as:

- a doctrinal classification engine;
- a Scripture authority source;
- a legal advice source;
- a permission to create repos, data records, source imports, or production legal workflows;
- a permission for AI to infer theology, law, contract meaning, or client advice.

## Lessons Captured

| ID | Lesson | Problem or feedback solved | Fable kernel / decision source | Codex solution surface | Reusable transfer |
|---|---|---|---|---|---|
| DAD-FABLE-001 | Use a master-architect / implementer split. | Hard cross-disciplinary questions were too risky for Codex to infer while coding. | Master plan, `CODEX_HANDOFF.md` | Sequenced PR queue with hard stops and validators before data. | Use expert/architect kernels for legal ontology, then let coding agents scaffold schemas/tests only. |
| DAD-FABLE-002 | Record owner decisions before implementation. | Chat decisions were easy to lose or silently project too far. | `OWNER-DECISIONS-AND-PILOTS.md` D1-D10 | Decision record `FABLE-D1-D10-2026-07-06` unblocked only named surfaces. | Legal systems should record client/steward decisions before creating interpretations, mappings, or automation. |
| DAD-FABLE-003 | Split topic, view, formulation, assessment, agent, instrument, claim, and controversy. | "Doctrine" was too blunt; it blurred questions, positions, expressions, judgments, speakers, and events. | Kernel A1-A2 | Doctrine-genealogy schemas and examples. | For law, split legal issue, interpretation, clause/opinion formulation, court/client assessment, authority, claim, and dispute. |
| DAD-FABLE-004 | Use closed relationship verbs and forbid vague edges. | `related_to` and `influences` hide the actual claim and invite graph drift. | Kernel A3, D4 | Relationship registry v1 and validators. | Legal/document KGs should prefer precise verbs such as `derives_from`, `modifies`, `cites_source`, `counters`, or `partially_aligns_with`; keep vague links as candidates. |
| DAD-FABLE-005 | Treat condemnation or adverse judgment as an assessment, not a raw edge. | A bare "X condemns Y" edge erases assessor, scope, date, and authority. | Kernel A3 | Derived-only condemnation rule. | In law, adverse treatment or invalidation should be a scoped ruling/assessment object, not a naked graph edge. |
| DAD-FABLE-006 | Make time discipline structural. | Later systems can accidentally govern earlier sources if timelines are flattened. | Kernel A4 | Date blocks and anachronism validator. | For contracts and legal history, every derivation, amendment, ruling, and policy version needs date precision and basis. |
| DAD-FABLE-007 | Separate classification axes. | Orthodoxy status, tradition scope, and claim role were easy to collapse. | Kernel B1-B4, D1-D5 | Closed vocabularies and capture-prevention validators. | Legal analog: separate legal force, jurisdiction/client scope, and role such as controlling rule, historical background, argument, or comparison. |
| DAD-FABLE-008 | Separate authority rung from evidence utility. | Useful sources can wrongly become authoritative sources. | Kernel B3, D5 | S0-S7 ladder, utility flags, no-upward-flow rules. | Legal analog: controlling law, persuasive authority, commentary, client policy, opponent argument, and historical context can all be useful but carry different force. |
| DAD-FABLE-009 | Do not let scholarship or analysis become hidden normativity. | External analysis can smuggle assumptions into classifications. | Kernel B3 S6 firewall | Validator rules block S6 analysis as basis for normative positions. | Legal analog: treat secondary sources, AI summaries, and analyst notes as evidence/context, not controlling law or client authorization. |
| DAD-FABLE-010 | Require a shared provenance block before promotion. | Promoted edges/claims need consistent evidence, method, review, counterclaims, and downstream risk. | Kernel C1 | `doctrine_provenance.v1` schemas and validators. | Legal KGs should require citation locator, authority type, scope, method, review status, counterparty risks, and reviewer before asserted links. |
| DAD-FABLE-011 | Use promotion-blocking gates for specialized review. | Original-language and textual-critical issues should not be bypassed by AI confidence. | Kernel C2-C3 | Gate-trigger registry and validators. | Legal analog: jurisdiction, privilege, confidentiality, regulatory, or expert-domain gates block promotion until specialist review. |
| DAD-FABLE-012 | Keep reviewed exemplars narrow and non-generalizing. | A reviewed slice could be mistaken for a universal method approval. | Kernel C1, D9 | `reviewed_lineage` promotion policy remains owner-gated per object. | In law, a reviewed contract map or case-lineage slice should not auto-approve all similar matters. |
| DAD-FABLE-013 | Use derived evidence packets, never blended authority rows. | Cross-repo reports can blur Scripture, boundary, doctrine, and advisory authority. | Kernel D | Evidence packet schema with namespace row contract and non-authority block. | Legal reports should separate statute/case/contract/client-policy/commentary/AI-summary rows and never let a report become source authority. |
| DAD-FABLE-014 | Prevent report feedback loops. | A generated packet can become a fake source if cited later. | Kernel D2, V-PKT-3 | Validator forbids packet refs as `source_basis`. | Legal generated summaries and comparison reports must not become the cited authority for later claims. |
| DAD-FABLE-015 | Add a mechanical tripwire between transcription and judgment. | Codex could accidentally make theology while writing schemas/examples. | Kernel E | V-CODEX-1 and `decision_basis` requirement. | Legal analog: any non-floor legal classification needs an explicit client, lawyer, court, statute, or policy basis. |
| DAD-FABLE-016 | Use floor-only defaults. | Defaults can smuggle authority. | Kernel E | Schema defaults use floor values only. | Default legal statuses should be candidate/unreviewed/historical, never valid, enforceable, privileged, controlling, or approved. |
| DAD-FABLE-017 | Put validators before records. | Data before guardrails makes cleanup and authority drift likely. | `CODEX_HANDOFF.md` PR order | PR-2 vocabulary, PR-3 schemas, PR-4 validators before examples and repo registration. | Legal KGs should land schemas, controlled vocabularies, privacy gates, and validators before ingesting client matter data. |
| DAD-FABLE-018 | Use TOC tags and dependency maps for discoverability. | Good lessons are lost if agents cannot find them. | Owner feedback, GD-014 | AI TOC and governance dependency map updates. | Every reusable legal architecture decision should have tags, read-when guidance, owner/steward source, and validation coverage. |
| DAD-FABLE-019 | Keep planned repos planned until readiness tests are met. | Premature repo creation creates data-plane pressure before guardrails exist. | D7-D8 | Registration drafts only; no repo creation. | Create a legal KG repo/module only after scope, authority, privacy, validation, and source-ingest rules are explicit. |
| DAD-FABLE-020 | Model multi-parent derivation with explicit scoped edges. | "Derived from multiple parents" can hide which parent contributed what. | Kernel A3, Kernel C1 | One edge per parent with verb, evidence basis, method, date, scope, and review status. | Contract and document-version lineage should state exactly which clause, precedent, matter, playbook, or regulation each derived part depends on or modifies. |

## Reusable Kernel Map For Secular / Legal Knowledge Graphs

The Fable/Codex pattern can be adapted outside theology if the domain authority
terms are replaced and the authority boundaries are re-reviewed.

| Logos pattern | Secular/legal analog | Transfer rule |
|---|---|---|
| `doctrine_topic` | legal issue, regulatory topic, contract issue | A stable question or issue, not a position. |
| `doctrine_view` | legal interpretation, party position, policy view | A distinguishable position scoped to jurisdiction, client, court, agency, or practice group. |
| `formulation` | clause text, memo argument, opinion reasoning, policy wording | A concrete dated expression by an identified author/source. |
| `assessment` | court ruling, regulator action, client approval, attorney review | A scoped judgment; never collapse it into the underlying view. |
| `instrument` | statute, regulation, contract, policy, court order | A document with binding scope and version history. |
| `agent` | court, regulator, client, lawyer, firm group, counterparty | Identity must be stable and separate from labels. |
| `genealogy_edge` | derivation, citation, amendment, override, reliance, conflict | One precise relationship per claim, with evidence and review. |
| authority ladder | controlling / persuasive / internal / commentary / adverse | Usefulness does not equal authority. |
| evidence packet | matter report or comparison memo | Derived read-only report; no authority feedback loop. |
| `decision_basis` | client instruction, attorney signoff, court cite, policy cite | Required for any non-floor classification. |

## Legal Buildout Watchpoints

DAD should flag these as high-risk when adapting the pattern for a law-firm
knowledge graph:

- Privilege and confidentiality must become first-class gates before client data
  is ingested.
- Jurisdiction, court level, effective date, version, and client scope must be
  explicit fields, not prose.
- AI similarity, embeddings, and document proximity may propose candidate links
  but cannot assert legal lineage or legal meaning.
- Contract clauses need version lineage and parent-edge granularity; one clause
  can derive from multiple playbooks, statutes, negotiations, and prior matters.
- Generated comparison reports must never become source authority for later
  legal claims.
- "Approved by client," "approved by attorney," "controlling law," and
  "enforceable" must be reviewed classifications with explicit basis.
- Reusable architecture may transfer across domains; theological authority and
  legal authority do not transfer across domains.

## Future DAD Work

When a formal DAD workflow exists, ingest this file into a DAD lesson registry
with stable lesson IDs `DAD-FABLE-001` through `DAD-FABLE-020`, preserving:

- source file references;
- owner decision references;
- non-authorizations;
- reusable kernel map;
- legal/secular transfer watchpoints;
- validation and governance dependency references.

Future agents should update this outbox when they create or discover a reusable
architecture lesson from Fable, Codex, audits, PR failures, red-team findings,
or cross-domain implementation work.
