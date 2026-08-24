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

The public doctrine-mesh release contains exactly 90 managed source/evidence
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
python scripts/validate_portfolio_front_door.py
python -m pytest tests/test_portfolio_front_door.py
python docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/checks/validate_doctrine_mesh.py --mode final
python docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/checks/test_validate_doctrine_mesh.py
python scripts/validate_internal_links.py --all-markdown
```

Also inspect the exact Git diff and commit. A receipt is useful evidence, but the
source and reproducible command remain stronger than a summary of either.

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
