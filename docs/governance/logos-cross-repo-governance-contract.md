---
object_type: cross_repo_governance_contract
trust_zone: governance_instructions
lifecycle_status: active
provenance_note: "Created 2026-06-05 after GitHub issues #54 and lowelltwong-alt/logos-scripture-graph#7 linked the two repositories as one governed project family."
reason_for_inclusion: "Make the upstream/downstream relationship between Logos Governance Architecture and Logos Scripture Graph explicit and enforceable."
---

# Logos Cross-Repo Governance Contract

## Purpose

This repository is the upstream governance and theological architecture authority
for the Logos repo family. This document records the active Scripture data-plane
contract. The broader repo registry and relationship process now live in
`governance/LOGOS_REPO_REGISTRY.yaml`,
`governance/LOGOS_REPO_REGISTRY.md`, and
`governance/REPOSITORY_LINK_CONTRACTS.md`.

The downstream Scripture data-plane repository is:

- Upstream: `lowelltwong-alt/logos-governance-architecture`
- Downstream: `lowelltwong-alt/logos-scripture-graph`

The relationship is coordinated in GitHub by:

- parent governance issue: `https://github.com/lowelltwong-alt/logos-governance-architecture/issues/54`
- child data-plane issue: `https://github.com/lowelltwong-alt/logos-scripture-graph/issues/7`
- intended Project board: `Logos governed Scripture graph`

## Hierarchy

```text
logos-governance-architecture
  -> upstream theological / governance authority
  -> approved vocabulary, derivation, trust, and review obligations
  -> logos-scripture-graph
     -> governed Scripture data-plane / knowledge-plane implementation
     -> validated release artifacts for future runtime consumers
```

## Link Type

The link type is `governance_contract`.

The repos are not linked by:

- submodule
- hidden runtime dependency
- automatic promotion
- shared working tree
- model-generated authority

## Authority Rules

1. This repo defines upstream theological architecture, governance hierarchy,
   source-trust vocabulary, derivation logic, and human review obligations.
2. `logos-scripture-graph` implements deterministic Scripture data artifacts under
   that governance.
3. Downstream data-plane artifacts must not silently redefine upstream governance
   meaning.
4. New authority concepts, trust-zone rules, relationship vocabulary, or review
   obligations should be proposed here before the downstream repo consumes them.
5. GitHub issues and Project fields are coordination surfaces, not canonical
   theological or governance authority.
6. Child repos may mirror registry facts, but the governance repo is the source
   of truth for cross-repo authority direction and relationship changes.
7. `logos-scripture-graph` and `logos-boundary-literature` may own local
   implementation or support surfaces, but neither may outrank this governance
   repo's registry, contracts, or owner-approved authority direction.
8. `logos-boundary-literature` may support comparison, reception, and boundary
   analysis, but it must never equal, override, or outrank canonical Scripture.
9. Noesis Atlas may connect only as reviewed, read-only advisory comparison
   context. It must not modify, gate, govern, promote, demote, or supply
   authority or derivation for any Logos repo.

## Deterministic Enforcement

This contract is enforced locally by:

```bash
python scripts/validate_cross_repo_governance_contract.py
```

The validator is part of the default validation suite through
`scripts/validation_contracts.py`.

## Data Flow

```text
governance contract / source-trust vocabulary / review obligation
  -> downstream Scripture data-plane control files
  -> raw source manifests
  -> canonical passage and witness records
  -> derived chunks and context packets
  -> candidate or asserted graph claims
  -> validated release artifacts
  -> future runtime consumers
```

The data-plane repo may publish validated artifacts. It does not publish upstream
governance authority unless this repo has approved the relevant contract surface.
