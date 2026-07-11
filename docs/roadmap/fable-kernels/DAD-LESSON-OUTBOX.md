---
object_type: dad_ready_lesson_outbox
trust_zone: learning-sidecar
lifecycle_status: active
provenance_note: "Created 2026-07-06 by Codex after owner request to make DAD aware of Fable feedback, Codex implementations, reusable kernels, lessons learned, and cross-domain transfer patterns. Updated 2026-07-07 to add feedback-trace and Wave-2 reusable lessons DAD-FABLE-021 through DAD-FABLE-032. Updated 2026-07-09 with post-Wave-2 audit and portable agent-routing lessons DAD-FABLE-033 through DAD-FABLE-039. Updated 2026-07-10 with AGENT-W1-A through OD-C-OPEN-A lessons DAD-FABLE-040 through DAD-FABLE-043 and deterministic multi-worktree coordination lesson DAD-FABLE-044."
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
- [`FABLE_FEEDBACK_TRACE_MATRIX.yaml`](FABLE_FEEDBACK_TRACE_MATRIX.yaml)
- [`FABLE_POST_WAVE2_GAP_AUDIT.md`](FABLE_POST_WAVE2_GAP_AUDIT.md)
- [`../agent-skill-registry-roadmap.md`](../agent-skill-registry-roadmap.md)
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
| DAD-FABLE-021 | Treat expert feedback as a disposition ledger, not a memory burden. | "Fable addressed this" was not mechanically auditable across gap passes, Wave-2 kernels, red-team findings, and future queues. | Wave-2 handoff; owner request for 100 percent traceability | `FABLE_FEEDBACK_TRACE_MATRIX.yaml` plus `validate_fable_feedback_trace_matrix.py`. | Legal and secular KGs should trace every expert/auditor item to implemented, planned, deferred, rejected, or owner-gated status with evidence and target queue. |
| DAD-FABLE-022 | Use planned/deferred statuses as explicit governance, not failure. | Some Fable items are intentionally future-gated; hiding them as "not done" or pretending completion would both be wrong. | Completion audit; Wave-2 queue | Matrix dispositions require reasons, evidence, and target queues for planned or deferred items. | Law-firm systems should distinguish implemented controls from counsel-gated, data-gated, or future-release controls so audits can see intentional sequencing. |
| DAD-FABLE-023 | Make mirror freshness and path drift validator-visible. | Child mirrors and cross-repo references can silently drift after upstream changes. | Kernel K; W2-1/W2-2 | Mirror freshness standard, cross-repo reference manifest, and child freshness validators. | Contract, policy, and schema mirrors in legal systems need source commit, staleness budget, local existence checks, and fail-closed drift reports. |
| DAD-FABLE-024 | Treat recension and edition identity as part of authority basis. | A citation to a boundary instrument or source can overclaim if it ignores recension, edition, or variant form. | W2-16; Kernel N | Planned recension-aware S1 validator and work-edition-locator discipline. | Legal KGs should distinguish statute version, court slip/opinion reporter version, contract revision, and negotiated redline when a rule depends on exact wording. |
| DAD-FABLE-025 | Lint free-text fields for advisory smuggling. | Prose fields can carry hidden Noesis/advisory, liberal-critical, sectarian, or unreviewed assumptions around structured validators. | W2-15; external advisory firewall | Planned advisory/free-text smuggling lint. | Compliance and legal systems should lint notes, rationale, PR bodies, and summaries for unauthorized authority leakage, not just structured fields. |
| DAD-FABLE-026 | Keep the learning loop thin, indexed, and admission-tested. | A lesson system can become noisy enough that agents stop reading it. | Kernel L; D11-A | Implemented governance LLOS v1 standard with admission tests, route/category loading, reading-cost-aware attention, P0/constitutional/catastrophic retention, human sunset review, and a DAD read-only bridge; child indexes are pending their W2-8/W2-9 merges. | Learning systems for law firms should rank lessons by trigger and criticality, require admission criteria, and sunset low-utility lessons without demoting rare catastrophic safeguards. |
| DAD-FABLE-027 | Model variation units without preferred readings. | Textual-critical evidence can become a hidden preferred-text decision if witnesses carry rank or originality fields. | Kernel H; W2-3 | Planned report-only variation-unit registry with no preferred field and no output change. | Document comparison systems should separate observed variants, attestation, and publication basis from normative "best version" selection. |
| DAD-FABLE-028 | Keep historical context background-only. | Context, archaeology, parallels, or culture data can be useful yet become an authority shortcut. | Kernel G; D14-A | Planned boundary context-evidence taxonomy with context firewall. | Legal and policy systems should separate background industry context from controlling authority, client instruction, or legal conclusion. |
| DAD-FABLE-029 | Make hermeneutic lenses declared profiles, never hidden defaults. | Lens choice can quietly decide the output while appearing neutral. | Kernel J; D15-A | Planned owner-gated lens registry, no default lens, and apocalyptic multi-lens or invariance rule. | Legal analysis systems should declare interpretive frames, jurisdictional posture, client strategy profile, or doctrinal lens instead of embedding one as a default. |
| DAD-FABLE-030 | Split labels from referents and influence from proof. | Labels like "-ism" names and contested influence can misrepresent a person's actual claim. | Kernel F; D16-A | Planned label objects, influence_case objects, contribution_facet fields, and negative-evidence predicates. | Legal KGs should distinguish party labels, theory names, cited influence, actual text, and disputed genealogy; labels should never substitute for the underlying formulation. |
| DAD-FABLE-031 | Use max-risk gates for high-consequence pipelines. | Summed scores can let many easy dimensions outvote one high-risk dimension. | Kernel I | Planned chunking risk math uses `max(axes)` for gating and weighted sums only for review-priority ordering. | Legal triage should fail closed on any privileged, jurisdictional, sanctions, confidentiality, or conflict-risk axis even if other scores look easy. |
| DAD-FABLE-032 | Preserve review economics before adding contributors. | Queue pressure can tempt agents or maintainers to weaken gates. | Kernel M; D12 conditional | Contributor-triggered reviewer-role/two-key model before outside contributors join. | Legal systems should activate role-based review and two-key approvals before workload or new contributors create pressure to rubber-stamp. |
| DAD-FABLE-033 | Trace the request separately from the response. | A feedback matrix can be internally complete while the responder omitted a user requirement. | Post-Wave-2 GAP-01 | Owner-master-brief source group plus independent correction group in the Fable trace matrix. | Audits of legal memos, architecture reports, or vendor deliverables should map original requirements to response sections and implementation evidence separately. |
| DAD-FABLE-034 | Unknown is not low risk. | Absence from a queue or missing evidence was able to look like a zero risk score. | Post-Wave-2 GAP-04 | Planned explicit `known_zero`, `known_nonzero`, `unknown`, and `not_applicable` states with fail-closed low-risk routing. | Legal triage and compliance scoring must distinguish cleared risk from unassessed risk. |
| DAD-FABLE-035 | Count parity is not structural parity. | Equal marker counts can hide moved spans, targets, payloads, or nesting. | Post-Wave-2 GAP-05 | Planned identity-preserving source-span and render-round-trip contracts. | Document comparison should preserve clause location, parent structure, annotations, links, and payload identity rather than only counts. |
| DAD-FABLE-036 | Fresh components do not prove a coherent release. | Individually current repos can be incompatible when joined at different commits. | Post-Wave-2 GAP-08 | Planned family release/BOM manifest pinning compatible commits, schemas, releases, mirrors, and validators. | Multi-system legal evidence products need a reproducible bill of materials, not just latest documents. |
| DAD-FABLE-037 | Separate capability, domain expertise, authority, independence, and cost. | Broad model tiers made expensive agents do grunt work and let model names stand in for expertise. | Post-Wave-2 GAP-15 | Economically tiered capability roadmap with qualification fixtures and replaceable adapters. | Route law-firm work to the cheapest qualified tool while separately enforcing legal-domain competence, privilege, independence, and attorney authority. |
| DAD-FABLE-038 | Flat lens registries create hidden category errors. | Methods, genres, traditions, systems, and conclusions were mixed into one enum, and missing data could look neutral. | Post-Wave-2 GAP-07 | Planned typed composable lens dimensions and explicit not-evaluated/not-applicable states. | Legal analysis should separate interpretive method, jurisdiction, client posture, authority set, and strategy rather than calling all of them a single lens. |
| DAD-FABLE-039 | Resolve repo identity before scaling content. | A renamed/split repo can retain old content lanes that conflict with its new ownership contract. | Post-Wave-2 GAP-02 | Owner-gated legacy-path disposition and migration/reference-only docket before buildout. | After a legal platform split, every legacy data path needs a governed owner, compatibility alias, migration target, and sunset criterion. |
| DAD-FABLE-040 | Inventory before migration. | A repo split can create pressure to move or delete files before their future owner, inbound links, and compatibility posture are known. | AGENT-W1-A | Exact-one-disposition inventory with a fail-closed validator and path-level migration-packet stop rule. | Before moving legal knowledge, client policy, or contract artifacts between systems, classify every scoped path and preserve links/provenance before any migration. |
| DAD-FABLE-041 | Separate capability, qualification, authority, independence, and cost in executable routing rules. | A provider name or low token price can masquerade as domain expertise or permission to bypass review. | AGENT-W2-A; DAD-FABLE-037 | Canonical non-runtime routing vocabulary with fail-closed specialist qualification and `A3_human_reserved` checks. | Legal work routing must independently establish competence, privilege/review authority, conflict independence, and cost; a preferred vendor or bargain rate cannot substitute for any of them. |
| DAD-FABLE-042 | Missing adapter evidence is an explicit unqualified result, not a zero-risk default. | A fixture harness can create false confidence when no callable runtime actually produced results. | AGENT-W7-A | Source-safe pack plus current-alias register records `not_run`, null metrics, empty eligibility, and no role assignment until auditable execution occurs. | Vendor evaluation in legal systems must distinguish a completed benchmark from an unavailable integration; absence of evidence cannot quietly approve production use. |
| DAD-FABLE-043 | Research quality is evidence-based, not credential-gated; purpose, access, and rights remain separate. | University affiliation can become an unjustified proxy for rigor, while noncommercial intent or a `.edu` login can be overread as blanket copying, text-mining, redistribution, or AI permission. | OD-C-OPEN-A | Recognize independent, personal, church, ministry, lay, and teaching research; assess evidence/provenance/reproducibility/source competence/review; allow owner-gated voluntary institutional access while retaining exact provider rights and credential boundaries. | Legal and policy systems should welcome self-represented, community, nonprofit, and independent researchers while keeping account access, confidentiality, text-mining, redistribution, and AI permissions explicit. |
| DAD-FABLE-044 | Make the scrum board a projection of governed claims plus live repository evidence. | Manual boards, chats, branch names, and old roadmaps can each forget work, while stale age or a deleted card can be mistaken for permission to restart or discard it. | Owner request for deterministic worktree/roadmap awareness; professional Git worktree, GitHub Project, issue/PR, concurrency, and lease patterns | Stable work IDs, path and semantic claims, reciprocal owner overlap resolutions, heartbeat leases, live `git worktree --porcelain -z` inventory, squash/tree-equivalence detection, short Windows worktree roots, and fail-closed PR-branch claims. | Multi-repo legal, research, and knowledge-graph programs should reconstruct work from source control and durable task identity, use boards as views, and route stale/dirty/overlapping work to reconciliation rather than auto-deletion or duplicate execution. |

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
with stable lesson IDs `DAD-FABLE-001` through `DAD-FABLE-045`, preserving:

- source file references;
- owner decision references;
- non-authorizations;
- reusable kernel map;
- legal/secular transfer watchpoints;
- validation and governance dependency references.

### DAD-FABLE-045: Engineering practice is evidence, not authority

Use a recurring observatory with deterministic path triggers, explicit source
freshness, Logos-specific fit dimensions, independent review for high-leverage
adoptions, and redundant scheduling. Ask whether a leading organization would
recognize the method and what evidence supports it, then separately ask whether
it fits the solo maintainer, authority boundaries, theological safeguards,
audit needs, cost, and operational capacity. Never imitate an organization only
because it is large or prestigious.

Reusable kernel: source registry + recommendation registry + due-date watcher +
event triggers + owner-gated adoption + retained rejection/supersession history.

Future agents should update this outbox and the feedback trace matrix when they
create or discover a reusable architecture lesson from Fable, Codex, audits, PR
failures, red-team findings, or cross-domain implementation work.
