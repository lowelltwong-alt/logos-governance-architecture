---
object_type: public_portfolio_evidence_packet
trust_zone: proposed
lifecycle_status: active
provenance_note: "Created on 2026-08-24 as the evidence drill-down behind the root Logos portfolio landing page."
reason_for_inclusion: "Give technical reviewers and their AI tools a compact map from recruiter-facing claims to schemas, source files, validators, receipts, and explicit non-claims."
---

# Logos trust-layer portfolio evidence packet

Start with [`PORTFOLIO.md`](../../../PORTFOLIO.md). This directory is the
machine- and reviewer-facing drill-down behind that page.

The packet is designed for skeptical inspection. It does not ask a reviewer to
infer delivered capability from a roadmap, a file count, a Mermaid diagram, or a
validator pass.

## Packet contents

| Artifact | Purpose | Authority limit |
|---|---|---|
| [`project-evidence.yaml`](project-evidence.yaml) | Claim-to-evidence map, exact public snapshot commits, maturity, metrics, and non-claims | Proposed public evidence; repository sources remain authoritative |
| [`project-evidence.schema.json`](project-evidence.schema.json) | Fail-closed shape and fixed doctrine-mesh boundary contract | Structural contract only; no semantic or theological approval |
| [`AI-INTERROGATION-PROMPT.md`](AI-INTERROGATION-PROMPT.md) | Copy-paste prompt for an independent AI audit | Read-only investigation; no release or source authority |
| [`agent-mesh-manifest.json`](agent-mesh-manifest.json) | Single-writer, independent-review, and mechanical-release role contract for this packet | Coordination metadata; it cannot grant execution authority |
| [`validation-receipt.json`](validation-receipt.json) | Exact commands, input state, results, review lineage, and residual risks | Dated snapshot; invalid after material input drift |
| [`scripts/validate_portfolio_front_door.py`](../../../scripts/validate_portfolio_front_door.py) | Deterministic schema, evidence, privacy, navigation, diagram, and doctrine-freeze checks | Bounded structural/policy proof only |
| [`tests/test_portfolio_front_door.py`](../../../tests/test_portfolio_front_door.py) | Positive and negative regression cases | Test coverage is not completeness |

## Release accounting

PR #118 carries 131 unique base-to-head paths, not merely the latest public
packet. Its composite is 25 historical V1 campaign paths, 90 Doctrine Mesh V2
paths, and 21 post-V1 portfolio/governance paths, with five paths shared between
V1 and the later portfolio slice: `25 + 90 + 21 - 5 = 131`.

The later post-`410c7e4` candidate is a distinct 111-path slice: 90 Doctrine
Mesh V2 paths plus 21 portfolio/governance paths. The validation receipt records
both scopes separately. Twenty V1-only paths remain byte-identical to their
reviewed checkpoint; five shared V1 paths were changed and revalidated in the
later slice. The [historical V1 validation receipt](../../roadmap/logos-stewardship-architecture-buildout/checks/validation-receipt.json)
and [independent review](../../roadmap/logos-stewardship-architecture-buildout/checks/final-independent-review.json)
retain their original staged-candidate digest convention and are cited as
historical evidence rather than rewritten as current V2 proof. The manifest
labels that Windows-path/index convention as environment-bound historical
evidence and adds a separate ordinal Git-object replay digest for portable
verification of the same 23 non-receipt blobs.

At the integration anchor, the validator requires all 131 composed release
paths to byte-match the pinned content and receipt commits. On later `main`
descendants it instead guards the current recruiter front door, root AI
navigation, Doctrine Mesh V2 package, and validation-contract surfaces. Shared
registry and dependency-map records may evolve under their own governance, so
this does not claim that every later `HEAD` byte equals the historical release;
historic-state claims must use the receipt's pinned commits.

## Five ways to inspect the work

### Recruiter or hiring manager

Read the [one-minute brief](../../../PORTFOLIO.md#the-one-minute-brief), the
[maturity table](../../../PORTFOLIO.md#what-existsand-what-does-not), and
[what the work demonstrates](../../../PORTFOLIO.md#what-this-work-demonstrates).
Then use the AI prompt to challenge any claim that matters to the role.

### AI or knowledge-systems engineer

Inspect:

1. [`governance/GOVERNANCE_DEPENDENCY_MAP.yaml`](../../../governance/GOVERNANCE_DEPENDENCY_MAP.yaml)
2. [`schemas/logos_node_min.schema.json`](../../../schemas/logos_node_min.schema.json)
3. [`schemas/logos_claim_min.schema.json`](../../../schemas/logos_claim_min.schema.json)
4. [`schemas/doctrine_genealogy/genealogy_edge.v1.schema.json`](../../../schemas/doctrine_genealogy/genealogy_edge.v1.schema.json)
5. [`scripts/validation_contracts.py`](../../../scripts/validation_contracts.py)
6. [`docs/governance/anti-guessing-and-evidence-discipline.md`](../../governance/anti-guessing-and-evidence-discipline.md)

These surfaces show how identity, trust, provenance, evidence, graph relations,
downstream impact, and executable checks fit together.

### Agent-workflow engineer

Inspect the specification-only:

- [agent mesh](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/mesh/agent-mesh.v2.json)
- [bounded role factory](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/mesh/autonomous-role-factory.yaml)
- [completeness auditor](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/mesh/completeness-auditor-contract.yaml)
- [expertise taxonomy](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/mesh/expertise-taxonomy.yaml)
- [source-pack contract](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/research/expert-pack-contract.yaml)
- [risk and decision contract](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/governance/decision-and-risk-contract.yaml)
- [red-team premortem](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/redteam/premortem.yaml)

The architecture is provider-neutral and depth-one. Workers do not create
workers. One writer owns mutations, independent roles challenge material work,
and high-risk disagreement is routed to a person.

### Governance, safety, or trust reviewer

Trace:

- [AI front-door authority rules](../../../AI_FRONT_DOOR.md)
- [repository custody](../../../governance/LOGOS_REPO_REGISTRY.yaml)
- [link contracts](../../../governance/REPOSITORY_LINK_CONTRACTS.md)
- [external advisory firewall](../../../governance/EXTERNAL_ADVISORY_AUTHORITY_FIREWALL.md)
- [learning-loop standard](../../../governance/LOGOS_LEARNING_LOOP_OPERATING_STANDARD.yaml)
- [portfolio validator](../../../scripts/validate_portfolio_front_door.py)

Look specifically for authority transfer by copy, self-certified model output,
semantic similarity treated as evidence, missing provenance, unbounded agent
delegation, and maturity inflation.

### Theological or domain reviewer

Begin with the non-claims. The public packet does not ask an engineering reviewer
to approve theology. Scripture interpretation, source authority, canonicity,
exegesis, doctrine, tradition policy, and qualified domain review remain separate
human gates. The doctrine mesh specifies how future evidence and review could be
organized; it contains no substantive doctrine result.

## Diagram index

All diagrams live in [`PORTFOLIO.md`](../../../PORTFOLIO.md), with a prose reading
immediately below each diagram for accessibility and non-Mermaid clients:

1. [Repository custody and authority](../../../PORTFOLIO.md#1-repository-custody-and-authority)
2. [Candidate-to-governed-record lifecycle](../../../PORTFOLIO.md#2-candidate-to-governed-record-lifecycle)
3. [Hierarchical specialist mesh](../../../PORTFOLIO.md#3-hierarchical-specialist-mesh)
4. [Deterministic completeness audit](../../../PORTFOLIO.md#4-deterministic-completeness-audit)
5. [Provenance graph and reverse blast radius](../../../PORTFOLIO.md#5-provenance-graph-and-reverse-blast-radius)
6. [Maturity evidence ladder](../../../PORTFOLIO.md#6-maturity-is-a-one-way-evidence-ladder-not-a-marketing-shortcut)

## Doctrine Mesh V2 receipt chain

The public doctrine-mesh package contains exactly 90 managed source/evidence
files: 85 frozen payload files plus 5 administrative files.

Follow this order:

1. [README](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/README.md)
2. [revision manifest](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/revision-manifest.yaml)
3. [saved-version index](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/FINAL-SAVED-VERSION.yaml)
4. [deterministic validation receipt](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/checks/validation-receipt.json)
5. [independent specification review](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/checks/independent-review.json)
6. [negative fixtures](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/checks/fixtures/negative-cases.json)

The freeze receipt says publication was not authorized at freeze time. The
current maintainer authorization permits this exact specification-only public
release; it does not retroactively change the frozen bytes or authorize runtime,
research, source ingestion, doctrine, or cross-repository writes.

## Reproduce the packet checks

```bash
python -B scripts/validate_portfolio_front_door.py
python -B -m pytest -q --assert=plain -p no:cacheprovider tests/test_portfolio_front_door.py
python -B scripts/validate_biblical_evidence_demo.py
python -B -m pytest -q --assert=plain -p no:cacheprovider tests/test_biblical_evidence_demo.py
python -B docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/checks/validate_doctrine_mesh.py --mode final
python -B docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/checks/test_validate_doctrine_mesh.py
python -B docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/validate_doctrine_marathon.py --mode final
python -B docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/test_validate_doctrine_marathon.py
python -B scripts/validate_internal_links.py --all-markdown
```

Also inspect the exact Git diff and commit. A receipt is useful evidence, but the
source and reproducible command remain stronger than a summary of either.

## Academic extension and public evidence demonstration

The [Academic Extension Contract](../../governance/academic-extension-contract.md)
defines the lossless domain-pack boundary for future academic graph work. The
[Biblical Evidence Graph Demonstration V1](../../roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/README.md)
is its first public, concrete, source-linked demonstration. It includes the exact
licensed P66 verso image, a separate combined-object record, an explicit
unresolved side-coverage boundary, a non-contiguous object-catalog John 19
crosswalk, bounded archaeology claim packets, a claim-mediated graph, a
provider-neutral specialist mesh, deterministic negative fixtures, frozen
digests, and independent reviews.

Read the demonstration in this order:

1. [scope and nonclaims](../../roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/SCOPE.md);
2. [P66 source and rights](../../roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/sources/p66-source-and-rights.yaml);
3. [academic source pack](../../roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/sources/archaeology-source-pack.yaml);
4. [evidence graph](../../roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/graph/evidence-graph.yaml);
5. [agent mesh](../../roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/mesh/agent-mesh.v3.json);
6. [release manifest](../../roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/release/public-release-manifest.yaml); and
7. [validation receipt](../../roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/validation-receipt.json).

The image and static candidate records are public evidence; they are not a
transcription, preferred reading, completed archaeology or doctrine corpus,
running graph, reviewed-gold M7/M8 convergence result, or theological authority.
The production academic domain-pack registry remains empty.

## Doctrine Marathon V3 receipt chain

The [Doctrine Marathon V3 entrypoint](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/README.md)
documents the long-run campaign control plane. It is an 83-file blocked
specification-only public design: 78 payload files plus five administrative
records. Strict prefinal validation passes, but final validation must expose
exactly one `adversarial_harness_release_gate` until the repository-specific V4
adapter, registry, per-case receipts, clean-checkout CI binding, and unchanged-
head evidence exist. Review its
[canonical prompt](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/DOCTRINE_MARATHON_MASTER_PROMPT.md),
[agent mesh](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/agent-mesh.v3.json),
[completeness auditor](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/completeness-auditor-v3.yaml),
[design-time assignment and independence fixture](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/examples/design-time-independence-fixture.json),
[runtime assignment-bundle contract](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/role-assignment-bundle.schema.json),
[typed qualification registry](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/qualification-registry.json),
[qualification-receipt contract](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/qualification-receipt.schema.json),
[correlation-exception contract](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/correlation-acceptance-receipt.schema.json),
[role and capability catalog](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/mesh/role-catalog.yaml),
[typed evidence registry](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/evidence/evidence-registry.json),
[evidence-review receipt contract](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/evidence/evidence-review-receipt.schema.json),
[changed-input trigger matrix](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/firewall/trigger-matrix.yaml),
[action-to-checker requirements](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/firewall/action-checker-requirements.yaml),
[prompt-neutrality review contract](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/firewall/prompt-neutrality-contract.yaml),
[empty append-only event ledger](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/events/event-ledger.json),
[fresh-context verification receipt contract](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/state/fresh-context-verification-receipt.schema.json),
[unresolved weekly-gate fixture](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/state/examples/initial-weekly-fresh-context-gate.json),
[dependency firewall](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/graph/event-driven-invalidation-contract.yaml),
[inactive human-identity authority root](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/graph/human-identity-authority-root.yaml),
[empty human-authority registry](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/graph/authority-registry.yaml),
[review-debt queue](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/debt/initial-review-debt.json),
[repair ledger](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/redteam/repair-ledger.yaml),
[public mistake-escalation receipt](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/redteam/ai-mistake-escalation-2026-08-27.yaml),
[root-cause and sibling-recurrence report](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/ADVERSARIAL_HARNESS_ROOT_FIX.md),
[public V4 receipt / V3 registry contract summary](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/DETERMINISTIC_ADVERSARIAL_HARNESS_CONTRACT.md),
[blocked repository migration contract](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/adversarial-harness-migration.yaml),
[164-case legacy component catalog](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/fixtures/negative-cases.json),
[33-case exact-ordered isolated catalog](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/fixtures/strict-isolated-cases.json),
[four-case aggregate sentinel subset](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/fixtures/aggregate-sentinel-cases.json),
[copied-root aggregate runner](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/run_adversarial_harness.py),
[aggregate-runner regression tests](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/test_run_adversarial_harness.py),
[revision manifest](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/revision-manifest.yaml),
[bounded public-release authorization](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/public-release-authorization.json),
[final saved-version index](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/FINAL-SAVED-VERSION.yaml),
[validation receipt](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/validation-receipt.json),
and [independent review](../../roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/independent-review.json).

The package freezes a blocked design only when its manifest, saved-version
index, validation receipt, independent review, and exact one-blocker final replay
agree; it is not aggregate-assured, protected-release eligible, a runtime, or a
body of doctrine. No patristic source is ingested, no expert is qualified merely
by an agent role, and a required prompt-review binding does not prove neutrality
or that a checker ran. The weekly fixture remains unverified and authorizes no
continuation. The human-identity root is deliberately inactive, the authority
registry has no qualified approver or active frame, and V3 rejects activation
until a separate reviewed identity-and-authority mechanism is implemented.

The outer portfolio oracle has five copied-input aggregate sentinels for V3
maturity overclaim, migration-gate erasure, authority elevation, required-route
omission, and Release 004 chain drift. It also binds one start/end input
snapshot, rejects duplicate JSON/YAML keys, derives every alternate-root path
from that root, reads the release receipt once, and preserves raw finding order
and duplicates. Those controls are implemented in the
[portfolio validator](../../../scripts/validate_portfolio_front_door.py) and
[tests](../../../tests/test_portfolio_front_door.py); they do not complete the
still-blocked V3 repository migration.

## Non-claims that must survive every summary

- Validated specification does not mean running system.
- Static checks do not mean theological or semantic correctness.
- Role profiles do not mean qualified agents or humans are staffed.
- Source pointers and source-pack blueprints do not mean content was ingested.
- A graph relation cannot create source authority.
- An AI conclusion, majority vote, or low disagreement score cannot close a human gate.
- File counts describe repository surface, not delivery quality.
- Roadmap value describes possibility, not a completed product or schedule.

If another page, résumé, interview summary, or AI report contradicts these
boundaries, treat the stronger claim as unsupported until new evidence and human
authority are recorded.
