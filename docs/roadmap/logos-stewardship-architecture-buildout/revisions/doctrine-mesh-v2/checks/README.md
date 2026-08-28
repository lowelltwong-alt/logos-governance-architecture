---
object_type: doctrine_mesh_revision_validation_runbook
trust_zone: proposed
lifecycle_status: active
provenance_note: "Created on 2026-08-24 by Codex root for deterministic audit-presence, structure, authority, and freeze validation; revised to make UTF-8 text digests checkout-newline stable."
reason_for_inclusion: "Make the doctrine mesh and its completeness-auditor receipts independently replayable without claiming deterministic proof of scholarly completeness."
---

# Doctrine Mesh V2 Validation

From the repository root run:

```powershell
python docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/checks/validate_doctrine_mesh.py
python docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/checks/test_validate_doctrine_mesh.py
```

The validator checks:

- all JSON/YAML parsing and required Logos metadata;
- checkout-stable SHA-256: UTF-8 text normalizes CRLF and lone CR to LF,
  while non-UTF-8 payload bytes remain exact;
- the exact parent checkpoint plus source-file digests without requiring the
  later revision to impersonate that parent HEAD;
- the provider-neutral mesh, single writer, distinct checker, depth-one
  delegation, role dependencies, and manifest digest;
- authority/storage boundaries and all blocked launch, doctrine, source,
  corpus, rights, provider, promotion, and publication gates;
- schemas for role requirements, role gaps, audit events, and audit receipts;
- validity of every included schema plus internal Markdown and campaign-gate
  evidence references;
- a one-to-one, ordered, hash-bound preflight/midflight/postflight event and
  receipt chain;
- event input, coverage-plan, role-gap, execution-attempt, and timeline binding;
- preflight completion before the writer lease, triggered midflight completion
  after its trigger, and postflight completion after worker/checker outputs but
  before completion;
- no missing, duplicate, stale, out-of-order, self-checked, reused-attempt, or
  bad-digest receipt;
- positive replay plus the required negative fixtures;
- the same aggregate draft validator against a fresh, zero-finding audit
  baseline and each isolated mutated candidate;
- all 15 negative fixtures by exact ordered finding identity, with the first
  finding bound as both the intended and primary rule, the complete canonical
  rule set, and every additional finding declared as a causal cascade;
- resealing of non-target event, receipt-chain, and attempt dependencies unless
  stale state is the fixture's named direct mutation, plus forward and reverse
  replay from fresh baselines;
- a complete frozen payload manifest and no pending digest, workstation path,
  deprecated project label, or unreviewed activation.

The deterministic result confirms only the presence and internal consistency of
recorded execution evidence and contract data for exact inputs. It does not
authenticate execution, reviewer identity, or timestamps, and the retained V2
aggregate replay is non-authorizing legacy evidence rather than V4 protected-
release assurance. The separate independent review evaluates whether the
chosen expert coverage, omissions, source policy, and autonomy boundary are
substantively adequate.

`--mode draft` is a non-authorizing authoring check and reports
`pass_draft_non_authorizing` only when its current checks pass; artifact freeze
remains not ready. A final pass is named `pass_artifact_specification_only` and
means only that this specification artifact is frozen and replayable. Runtime
activation remains blocked until separately
implemented semantic validators, adversarial fixtures, qualified adapters,
actual source/ExpertPacks, authenticated human receipts, and exact authority all
pass.
