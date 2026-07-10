---
object_type: fable_post_review_gap_audit
trust_zone: proposed
lifecycle_status: draft
review_status: unreviewed
ai_usage_posture: planning_only_not_auto_promote
provenance_note: "Created 2026-07-09 by Codex after the owner asked for an independent check of what the Fable Wave-2 feedback missed and for a repo-family-aware buildout path."
reason_for_inclusion: "The existing trace matrix proves disposition of Fable's recorded feedback, but it did not independently prove that Fable covered the owner's whole brief or that every proposed rule is structurally safe."
---

# Post-Wave-2 Fable Gap Audit

## Verdict

Fable's Wave-2 handoff is high-value and substantially coherent, but it is not complete enough to serve as the final architecture for the Logos family.

The most important distinction is:

```text
Fable-output coverage != owner-requirement coverage != architecture correctness
```

The existing feedback trace matrix validates the first statement. This audit adds the second and third checks.

This file authorizes no content, source import, Scripture or chunk output, reviewed promotion, graph/retrieval/vector truth, theology judgment, runtime agent, or repo creation.

## Repo-Family Baseline

| Repo | Current job | Gap-audit consequence |
|---|---|---|
| `logos-governance-architecture` | Governance, cross-repo contracts, ontology standards, owner decisions, and theological architecture | Must resolve its legacy content/control-plane identity before large content buildout. |
| `logos-scripture-graph` | Canonical 66-book Scripture, original-language and witness evidence, chunking, and Scripture release artifacts | Owns variant, marker, source-language, chunking-risk, and route-isolation corrections. |
| `logos-boundary-literature` | Source, reception, commentary, patristic, theologian-writing, historical, and archaeological support | Owns historical-context and work/edition/locator evidence, never Scripture authority. |
| `logos-doctrine-genealogy` | Active scaffold for doctrine lineage and profile-scoped comparison | Owns future lineage records after separate data authorization, not source corpora. |
| `logos-chunking-harness` | Planned execution/evaluation repo | Should eventually own cross-corpus execution and artifact-closure proofs, not semantic authority. |
| `noesis-atlas` | External advisory only | May inform quarantined comparison, never a governed dependency or authority. |

## Findings

### GAP-01 - The completeness proof starts from Fable's answer, not the owner's request

- Severity: P0 auditability.
- Evidence: `FABLE_FEEDBACK_TRACE_MATRIX.yaml` enumerates Fable gap-pass, queue, completion-audit, Wave-2, red-team, and DAD outputs. It does not register the owner master prompt as a requirement source with one row per requested hard problem and output section.
- Failure mode: a polished but omitted requirement can never appear as missing because the matrix only traces what Fable chose to say.
- Correction: add owner-brief coverage as a distinct source group and require `owner_requirement_id -> fable_response_ref -> disposition/evidence` traceability.
- Owner gate: none for the audit mechanism; owner review is required before accepting substantive corrections.

### GAP-02 - This repo has unresolved identity and data-ownership debt

- Severity: P0 cross-repo authority.
- Evidence: the repo registry calls this repo `governance_control_plane`, while `README.md`, `AI_FRONT_DOOR.md`, `docs/doctrine/`, `data/claims/`, and `data/graph/` still describe or hold theological, Scripture-reference, translation, doctrine, and graph objects from the earlier monorepo shape.
- Failure mode: contributors can follow two internally plausible routes and create duplicate authority surfaces across governance, Scripture, boundary, and doctrine genealogy.
- Correction: an owner docket must choose a target identity and an explicit deprecate/migrate/reference-only map for every legacy content path. No bulk movement or deletion is authorized by this audit.
- Recommended owner option: keep governance as the control plane plus non-data theological architecture and application-policy standards; route Scripture data to Scripture Graph, source/reception material to Boundary Literature, and doctrine-lineage records to Doctrine Genealogy. Preserve redirects and provenance during migration.

### GAP-03 - The variant-boundary invariant is too simple for real variation units

- Severity: P0 textual-critical/chunking.
- Evidence: Kernel H proposes that chunk boundaries coincide with variation-unit edges and that a unit is never absorbed mid-chunk.
- Failure mode: real variation units can be nested, overlapping, discontinuous, insertion-like, omission-like, or differently delimited by apparatuses. Forcing every unit edge to become a chunk boundary can make textual criticism drive chunk output and can be impossible for crossing intervals.
- Correction: model variation-unit topology first. Require chunks to expose full/partial/overlap coverage, dependency status, and renderability without concealment. Boundary alignment may be preferred or required for named high-risk units only after a report-only conflict analysis and owner case decision.
- Owner gate: any output or reviewed-gold boundary consequence remains under the textual-critical case policy.

### GAP-04 - Unknown risk is currently able to masquerade as zero risk

- Severity: P0 algorithmic/theological.
- Evidence: Kernel I defines low complexity as `R_gate = 0` plus absence from dossier queues.
- Failure mode: absence from an incomplete queue is missing evidence, not evidence of absence. An unresearched passage can be ranked as easy.
- Correction: every risk axis needs `known_zero | known_nonzero | unknown | not_applicable`, evidence coverage, assessor method, and freshness. Any material `unknown` fails the low-complexity gate closed. Calibration must measure false-negative rate and reviewer effort on held-out passages, not fit only a weighted sum to a few completed lanes.
- Owner gate: scoring remains review-priority only and never chooses truth, theology, or output.

### GAP-05 - Marker-count equality is not metadata preservation

- Severity: P1 data integrity.
- Evidence: Wave-2 requires marker census equality for WJ, cross-reference, footnote, heading, Strong's-style, and formatting markers.
- Failure mode: counts can remain identical while a marker moves to the wrong token, span, speaker, footnote body, cross-reference target, or nesting position.
- Correction: require identity-preserving round trips: source byte/span pointer, marker type, open/close/nesting relation, ordered payload, attributes, target refs, token anchoring, and render round-trip hash. Count parity stays a fast smoke test, not the proof.

### GAP-06 - The original-language kernel delegates too much of the hard model

- Severity: P1 source-language/theological.
- Evidence: Wave-2 names token, lemma, morphology, Strong's-style alignment, and phrase spans, but does not fully model alternate tokenizations/parses, syntax/discourse analyses, Hebrew/Aramaic phenomena, Ketiv/Qere, pointing/cantillation layers, normalization, lexical senses, idioms, ellipsis, or analysis disagreement.
- Current mitigation: Scripture Graph later added substantial phrase/context, schema-contract, source-view, and evidence-substrate controls. Those reduce this gap but do not close the full expert-reviewed analysis model.
- Correction: distinguish immutable source transcription, editorial layer, tokenization hypothesis, morphology hypothesis, syntax/discourse analysis, lexical-sense proposal, phrase-level observation, and reviewed interpretation. Multiple analyses must coexist without one becoming a hidden default.

### GAP-07 - The lens registry conflates different kinds of things

- Severity: P1 hermeneutic/theological.
- Evidence: Kernel J places methods, canonical approaches, genre controls, covenantal/dispensational systems, and eschatological outcomes in one flat registry. It also treats an absent lens as `not lens-dependent`.
- Failure mode: flat values create category errors, and absence can become an undeclared neutral lens. Two Revelation lenses can still share the same decisive assumptions.
- Correction: use typed, composable dimensions: interpretive method, canonical scope, genre protocol, tradition/system profile, eschatological framework, and application posture. Use explicit `not_evaluated` and `not_applicable`; never infer lens-independence from absence. Apocalyptic coverage must name the approved comparison set or provide a reviewed invariance proof against named dimensions.
- Owner gate: all registry values and comparison sets remain owner-approved under D15-A.

### GAP-08 - Fresh mirrors do not guarantee a coherent family snapshot

- Severity: P1 cross-repo reproducibility.
- Evidence: Kernel K checks child mirrors against upstream `main` and uses staleness budgets.
- Failure mode: individually fresh repos can still be mutually incompatible when a query or evidence packet joins commits from different change windows.
- Correction: add a family release/BOM manifest that pins compatible repo commits, schema versions, data releases, mirror versions, and validator versions. Derived evidence packets cite that immutable family snapshot. Freshness and compatibility are separate checks.

### GAP-09 - Doctrine identity is not safely atemporal

- Severity: P1 doctrine genealogy.
- Evidence: the deep model declares topics, views, and claims atemporal while dating formulations and assessments.
- Failure mode: the apparent same view or proposition can change sense, scope, vocabulary, and presuppositions across time. Treating it as one atemporal object can read later concepts back into earlier sources.
- Correction: stable identity may remain, but semantic states, claim versions, asserted meanings, scope, and equivalence mappings must be time- and source-scoped. Councils also need event/session/canon/redaction/reception structure rather than only agent and instrument identities.
- Owner gate: schema correction can be drafted; any real classification or lineage record remains separately gated.

### GAP-10 - Evidence packets are defined, but safe query algebra is not

- Severity: P1 graph/retrieval.
- Evidence: Kernel D defines namespace-separated disposable packets. Wave-2 does not define how joins, filters, ranking, contradiction preservation, explanation, and result completeness work before packet rendering.
- Failure mode: a retrieval layer can obey the packet schema while ranking lower-authority or single-tradition evidence as the apparent answer.
- Correction: add an authority-preserving query contract: namespace-preserving joins, explicit authority filters, no cross-zone score comparability, contradiction retention, source-row citations, missingness reporting, deterministic snapshots, and candidate-only vector expansion.

### GAP-11 - Archaeological/context evidence needs observation-vs-interpretation depth

- Severity: P1 source context.
- Evidence: Kernel G supplies a useful top-level taxonomy and context firewall.
- Failure mode: a closed `culture_sphere` and publication reference do not preserve excavation context, stratigraphic unit, find provenance, dating method, custody, reconstruction status, forgery dispute, competing chronology, or the difference between observed artifact and scholarly interpretation.
- Correction: split material observation, provenance event, dating assertion, interpretation claim, comparison claim, and dependence hypothesis. Keep identity and time scope separate from broad cultural labels.

### GAP-12 - Reviewer delegation lacks qualification and conflict governance

- Severity: P1 governance/theological.
- Evidence: Kernel M defines roles, scope, and two keys, but not qualification evidence, term/expiry, conflicts, recusal, dissent, appeals, or quality re-evaluation.
- Failure mode: a named expert can become a permanent opaque authority, or an algorithmic risk score can silently expand what a reviewer may satisfy.
- Correction: reviewer appointments need qualification basis, scope, effective dates, conflicts, recusal, renewal, disagreement preservation, and audit outcomes. Delegable scope is owner-defined; a risk score may route review effort but may not grant authority.
- Current decision: D12 remains owner-only while Lowell is the sole builder and activates the reviewer-role/two-key model before outside contributors are onboarded.

### GAP-13 - Keyword lint cannot detect hidden methodological assumptions

- Severity: P1 authority boundary.
- Evidence: W2-15 proposes free-text lint for URLs/Noesis markers and advisory smuggling.
- Failure mode: anti-supernatural, anti-canonical, sectarian, or denominational assumptions usually arrive as ordinary prose without a banned marker. Conversely, a legitimate non-authorizing citation can contain a flagged URL.
- Correction: retain lint as a narrow detector, but add structured source role, methodological-presupposition disclosure where relevant, authority-flow validation, and reviewer questions. Lint never proves theological safety.

### GAP-14 - LLOS sunset rules can bury rare catastrophic lessons

- Severity: P1 learning loop.
- Evidence: Kernel L proposes trigger-based loading, a P0 count budget, and 90-day sunset review.
- Failure mode: a low-frequency but catastrophic lesson, such as canon or authority leakage, may appear unused and be demoted.
- Correction: sunset eligibility must consider severity, irreversibility, and blast radius. Constitutional/P0 lessons are exempt from usage-based demotion; attention budgets should be measured by route relevance and reading cost, not raw item count alone.

### GAP-15 - The subagent map is role-rich but not economically or technically portable

- Severity: P1 operational/architecture.
- Evidence: Fable lists useful specialist roles, while existing Scripture routing uses broad `reasoner | executor | orchestrator` profiles and dated vendor/model names in adapters.
- Failure mode: a model name becomes a proxy for expertise; expensive models perform grunt work; cheap models are assigned tasks requiring specialist judgment; a vendor rename breaks routing.
- Correction: separate task complexity, domain qualification, authority ceiling, tool/source needs, independence, and cost/effort. Select the cheapest currently qualified adapter using benchmark evidence. Names such as Sol, Terra, Luna, GPT, Claude, or future labels belong only in dated adapters.
- Buildout: `docs/roadmap/agent-skill-registry-roadmap.md` records the proposed durable architecture.

## Corrective Sequence

1. Record this audit and extend requirement traceability.
2. Present the governance-repo identity/ownership docket to the owner before content buildout.
3. Build the model-agnostic capability and cost-routing control plane as proposed-only schemas, cards, validators, and eval fixtures.
4. Add the family release/BOM compatibility contract.
5. Correct the high-risk technical kernels before implementing their downstream validators: variation topology, unknown-risk handling, structural metadata round trips, typed lenses, and temporal doctrine identity.
6. Mirror only approved contracts into child repos.
7. Use low-cost workers for deterministic work and domain-qualified research agents for evidence packets, with independent review and existing owner gates.

## Owner Decisions Needed Next

Only one decision blocks the governance repo's structural buildout:

- Choose the target identity and migration posture for legacy `docs/doctrine/`, `data/claims/`, `data/graph/`, `data/retrieval/`, Scripture-reference nodes, and theological application content.

The capability registry, eval fixtures, and adapter architecture may be drafted without deciding which current model label fills each role. Runtime activation, real expert delegation, and content migration remain separate owner gates.
