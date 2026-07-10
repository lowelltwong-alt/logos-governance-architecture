---
object_type: roadmap
trust_zone: proposed
lifecycle_status: draft
review_status: unreviewed
ai_usage_posture: planning_only_not_runtime_agent_creation
provenance_note: "Created 2026-05-01 as the roadmap for the Agent/Skill Capability Registry. Expanded 2026-07-09 after the owner's post-Fable request for token-efficient workers, domain-qualified research agents, and portable mappings across Sol, Terra, Luna, current/future GPT effort tiers, other vendors, and future model names."
reason_for_inclusion: "Plan how Logos will organize future agents, skills, subagents, monitors, orchestrators, capability qualification, economic routing, and replaceable model-specific adapters without creating runtime agents prematurely."
---

# Agent / Skill Registry Roadmap

## Goal

Build a model- and vendor-agnostic control plane that sends each task to the cheapest agent proven capable of doing it safely, while reserving specialist research and high-risk architecture for agents with the required domain and reasoning capability.

The durable instruction is the role/capability contract. A current model label is only an adapter.

```text
governed work contract
  -> required capability + domain + tools + authority ceiling + independence
  -> qualification/eval evidence
  -> cheapest eligible current adapter
  -> staged output
  -> validator and, where required, independent/human review
```

This roadmap is planning only. It does not authorize runtime agents, source imports, doctrine or Scripture claims, gate satisfaction by AI, promotions, output changes, or theology authority.

## Family Placement

| Surface | Owner |
|---|---|
| Capability ontology, role-card schema, risk/authority classes, qualification rules, adapter contract, composition rules | `logos-governance-architecture` |
| Scripture-specific worker/reviewer cards and local path permissions | `logos-scripture-graph` mirror/adapter |
| Source, archaeology, reception, patristics, and work/edition specialist cards | `logos-boundary-literature` mirror/adapter |
| Doctrine-lineage and profile-comparison specialist cards | `logos-doctrine-genealogy` mirror/adapter after readiness gates |
| Cross-corpus chunk execution workers | future `logos-chunking-harness` mirror/adapter |
| Advisory comparison | `noesis-atlas`, quarantined and never a governed dependency |

## Orthogonal Routing Dimensions

Do not collapse these dimensions into one label such as `reasoner` or one vendor model name.

### Work complexity

| Class | Meaning | Typical work |
|---|---|---|
| `W0_mechanical` | Fully specified, deterministic, narrow | import rows, normalize fields, checksums, manifests, link repair, generated indexes |
| `W1_bounded_engineering` | Implementation to an approved contract | schemas, wrappers, validators, tests, migrations, CI wiring |
| `W2_specialist_research` | Source-sensitive analysis inside one discipline | Koine grammar packet, manuscript evidence packet, archaeological source dossier |
| `W3_cross_domain_architecture` | Novel design across authority, theology, ontology, algorithms, or repos | Fable-style kernels, risk math, ontology boundaries, authority-safe query design |

### Authority ceiling

| Class | AI may produce | AI may not produce |
|---|---|---|
| `A0_observation_only` | deterministic observations and reports | semantic claims or promotions |
| `A1_candidate_only` | sourced candidate records or research packets | reviewed truth or gate satisfaction |
| `A2_review_preparation` | comparison, conflict, and decision packets | owner/expert decisions |
| `A3_human_reserved` | no AI output can satisfy this class | theology/canon decisions, reviewed promotion, output authorization, authority changes |

### Effort and cost budget

| Portable band | Intent |
|---|---|
| `E0_minimal` | Cheapest qualified adapter; short deterministic task; compressed inputs. |
| `E1_low` | Bounded task with light reasoning or tool use. |
| `E2_standard` | Multi-file engineering or ordinary research synthesis. |
| `E3_high` | Difficult specialist reasoning, ambiguity, or adversarial review. |
| `E4_maximum` | Rare cross-domain architecture or highest-risk independent review. |

An adapter may translate these bands to provider settings such as `low`, `high`, `xhigh`, `ultra`, or future equivalents. Provider terms never appear in the canonical role definition.

### Domain capability

Domain capability is evidence-backed and independent from general model strength. Initial capability tags:

- software architecture, ontology, taxonomy, knowledge graphs, algorithms/math, validation, data engineering, security/red-team;
- biblical literary scholarship and genre-specific chunking;
- Koine Greek; Biblical Hebrew; Biblical Aramaic;
- textual criticism, manuscript studies, codicology, and source editions;
- Ancient Near East, Egypt, Assyria, Babylon, Persia, Second Temple Judaism, Greco-Roman history, archaeology, epigraphy, and material culture;
- patristics, councils/creeds, medieval/scholastic, Reformation/confessional, modern theology, hermeneutics, and doctrine genealogy;
- source provenance, licensing, citation resolution, and translation dependence.

Tags record demonstrated task capability, not model self-description.

## Agent Card Contract

Every governed card should include:

- stable `role_id`, purpose, owner, lifecycle, trust zone, and repo scope;
- work complexity, maximum authority class, and default effort band;
- required domain capabilities with minimum qualification level;
- required tools, internet/research posture, source classes, and context budget;
- exact inputs, allowed outputs, forbidden outputs, and writable paths;
- escalation triggers and stop conditions;
- validator/eval suite and minimum passing thresholds;
- independence requirement: may implement, may review, or must be independent;
- token/cost ceiling, batching policy, cache/ledger reuse, and early-stop rule;
- human gate and non-authorizations;
- adapter compatibility and last qualification date.

## Economic Routing Algorithm

1. Classify the work contract, not the prose request: repo, paths, output type, authority impact, source sensitivity, and reversibility.
2. Determine required work class, authority ceiling, domain capabilities, tools/research access, context size, and independence.
3. Reject adapters missing any hard requirement. Unknown capability never counts as qualified.
4. Among qualified adapters, choose the lowest expected total cost, including expected retries, review burden, and failure risk, not token price alone.
5. Give W0/W1 workers structured, compressed inputs and deterministic acceptance tests. Do not make them reread whole corpora when a governed ledger can supply the needed facts.
6. Give W2/W3 agents source access and the exact disciplinary packet schema. Their output remains candidate/review-prep unless a human gate says otherwise.
7. Require an independent adapter or human reviewer when the work contract names independence. The implementer cannot self-certify independent review.
8. Escalate on ambiguity, missing evidence, source conflict, failed eval, authority pressure, or scope expansion.
9. Record actual tokens, elapsed time, retries, defects, and reviewer minutes so later routing uses observed economics.

## Initial Low-Cost Worker Cards

These should be built first because they save tokens without creating semantic authority:

| Role | Work | Ceiling |
|---|---|---|
| source-manifest worker | fetch approved source, checksum, rights/status metadata, immutable manifest | A0 |
| structured-import worker | transform approved rows to schema, preserve source pointers, emit reject ledger | A0 |
| duplicate/identity candidate worker | detect exact/fuzzy duplicates and emit candidates only | A1 |
| link/reference worker | check paths, IDs, checksums, mirrors, and family snapshot refs | A0 |
| schema/fixture worker | implement approved schema and passing/failing fixtures | A0 |
| validator/CI worker | implement deterministic fail-closed checks to a written contract | A0 |
| report/index worker | generate derived TOCs, coverage ledgers, and non-authorizing reports | A0 |
| DAD/LLOS reporter | package a qualifying lesson and no-change rationale | A1 |

Efficiency requirements: bounded file list, no unnecessary corpus text, deterministic parser first, cached source metadata, resume checkpoint, output-size limit, and fail-fast escalation.

## Initial Specialist Research Cards

Specialist agents gather and structure evidence. They do not make owner decisions or satisfy human gates.

| Role family | Required capability | Output |
|---|---|---|
| Greek evidence preparer | Koine syntax, morphology, discourse, textual context, source editions | phrase/context packet with alternate analyses and citations |
| Hebrew/Aramaic evidence preparer | grammar, syntax, discourse, Masoretic/editorial layers, source traditions | phrase/context packet with alternate analyses and citations |
| textual-critical/codex scout | apparatus use, witness identity, codicology, variants, edition discipline | variation/witness evidence packet; no preferred reading |
| archaeology/history scout | relevant period, material evidence, provenance, competing chronology | observation/interpretation-separated context packet |
| patristic/council scout | primary works, editions, council/instrument/reception history | source/formulation candidate packet |
| doctrine-genealogy scout | claim granularity, derivation evidence, labels/referents, time scope | candidate lineage packet |
| hermeneutics reviewer | approved lens dimensions, genre method, hidden-default detection | lens comparison/invariance review packet |
| biblical literary reviewer | book/genre/discourse structure and chunking risk | review packet; no output authority |
| ontology/math architect | graph semantics, uncertainty, calibration, reproducibility | proposed kernel and eval specification |
| adversarial auditor | independent no-context, theology-smuggling, provenance, and failure review | findings only; cannot approve its own fixes |

## Qualification And Adapter Layer

Current names such as Sol, Terra, Luna, GPT, Claude, Gemini, Cursor, or a future model belong in a dated adapter registry, never in a durable card.

An adapter record should state:

- provider/surface/model alias and effective dates;
- supported effort settings and tool/research capabilities;
- privacy, retention, licensing, and source-handling constraints;
- context/output limits and expected price/latency;
- role-eval results, defect rate, escalation quality, and calibration date;
- eligible cards and explicit exclusions;
- rollback adapter and expiry/re-evaluation date.

No alias is mapped by reputation alone. Sol/Terra/Luna and low/high/ultra variants must run the same qualification pack before the router may use them.

## Qualification Pack

Use fixed, versioned, source-safe fixtures:

1. deterministic import with malformed rows and exact provenance preservation;
2. schema/validator implementation with fail-open mutant detection;
3. repo-routing and authority-boundary test;
4. Koine phrase/context test with competing parses and no doctrinal overclaim;
5. Hebrew/Aramaic grammar test with editorial-layer and source-tradition traps;
6. textual-critical test with nested/overlapping variation units and no preferred reading;
7. archaeology test separating observation, dating assertion, and interpretation;
8. doctrine-genealogy test separating label, referent, formulation, assessment, and influence;
9. hermeneutic-lens smuggling test;
10. cross-repo architecture and release-snapshot test;
11. independent red-team test on an intentionally plausible but unsafe design;
12. economy test: tokens, latency, retries, defects, and reviewer minutes.

Passing a software fixture does not qualify an adapter for Greek, theology, archaeology, or another domain.

## Build Sequence

### Phase 0 - Resolve repo identity

Prepare the owner docket for governance control-plane boundaries and legacy content migration/reference-only status. Do not move or delete content yet.

### Phase 1 - Canonical capability vocabulary

Add machine-readable vocabularies for work class, authority class, effort band, domain capability, independence, and escalation. Reconcile the existing `reasoner | executor | orchestrator` profiles as compatibility aliases, not the final ontology.

### Phase 2 - Card schema and validators

Add role/card, adapter, qualification-result, and work-contract schemas. Validate required non-authorizations, path permissions, source/research posture, authority ceiling, and independence.

### Phase 3 - Low-cost workers

Create and test W0/W1 cards first. Pilot them on non-semantic governance maintenance such as link checks, mirror manifests, fixture generation, and report indexes.

### Phase 4 - Specialist research roles

Create W2 cards and packet contracts for each discipline. Use invented or already-approved public fixtures only. Do not populate real doctrine/source lanes through this phase.

### Phase 5 - Adapter qualification

Register current aliases and effort settings only after eval results exist. Choose cheapest-qualified routing using measured total cost. Expire stale mappings automatically; never expire the durable role card with the adapter.

### Phase 6 - Orchestration and composition safety

Add a work DAG, token/retry budgets, source isolation, independent-review edges, stop propagation, and no-cycle validator. Every composed chain is reviewed as a new governed object.

### Phase 7 - Child-repo mirrors

Mirror the standard into Scripture, Boundary, and Doctrine Genealogy with repo-local path permissions and validators. Keep current local role files as adapters until migrated.

### Phase 8 - Controlled pilots

Run three non-authorizing pilots: low-cost governance maintenance, specialist source research packet, and independent architecture red-team. Compare quality, cost, reviewer burden, and escalation behavior.

### Phase 9 - Runtime decision

Only after cards, schemas, validators, qualification results, audit ledger, rollback, and stop controls are proven may the owner authorize runtime orchestration or the future chunking-harness adapter.

## PR Queue

1. `AGENT-W0`: record post-Fable gap audit and owner-requirement trace.
2. `AGENT-W1`: completed owner decision AGENT-W1-A and validator-backed inventory; later work remains limited to path-level migration packets, never bulk moves.
3. `AGENT-W2`: capability/authority/effort/domain vocabularies and compatibility aliases.
4. `AGENT-W3`: card, adapter, work-contract, and qualification schemas.
5. `AGENT-W4`: validators and mutant fixtures.
6. `AGENT-W5`: low-cost worker cards and economy ledger.
7. `AGENT-W6`: specialist research cards and packet contracts.
8. `AGENT-W7`: provider/model adapter registry and qualification results for current aliases.
9. `AGENT-W8`: orchestration DAG, composition review, stop propagation, and independent-review rules.
10. `AGENT-W9`: child-repo mirrors and three non-authorizing pilots.

## Stop Rules

Stop for owner review if work would:

- assign a theological, canon, variant, source-tradition, or reviewed status;
- let an AI satisfy a human/expert gate;
- infer expertise from a model name without qualification evidence;
- use cost savings to weaken source, review, independence, or authority controls;
- migrate/delete legacy governance content;
- create runtime agents, schedules, repo writes, or external side effects;
- create a new lens, vocabulary, profile, relationship verb, or authority rung;
- allow a worker output to become source, graph, retrieval, vector, doctrine, or Scripture truth.
