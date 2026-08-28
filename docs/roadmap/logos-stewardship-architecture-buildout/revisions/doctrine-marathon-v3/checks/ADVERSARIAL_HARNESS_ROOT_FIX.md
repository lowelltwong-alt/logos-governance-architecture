---
object_type: adversarial_harness_root_fix_report
trust_zone: proposed
lifecycle_status: active
provenance_note: "Created on 2026-08-28 from a repository-wide false-green oracle audit, guarded migrations, and independent non-author reviews."
reason_for_inclusion: "Expose the systemic cause, cross-package impact, durable control, completed repairs, and fail-closed migration debt without overstating test or release maturity."
---

# Adversarial-harness root fix

## Root cause

Several older negative-fixture suites treated `expected_rule in observed_rules`
as success. That membership check can pass when a baseline is already broken,
an incidental schema or digest error occurs first, the intended mutation is a
no-op, or a prior case leaves cache state behind. A large suite can therefore
look stronger while still admitting false greens.

The durable repair is the
[deterministic adversarial-harness contract](DETERMINISTIC_ADVERSARIAL_HARNESS_CONTRACT.md):
clean aggregate baselines, actual candidate change, intended-equals-primary
failure, exact ordered finding identities, causal closure, dependency resealing,
forward/reverse isolated replay, digest-bound execution evidence, and
independent runner review.

## Current migration state

| Surface | Current state | Release meaning |
| --- | --- | --- |
| Portable root control | Independently reviewed and active as receipt/core V4 plus registry/discovery V3 | Structural receipt and discovery contract only; protected-release eligibility remains false |
| Doctrine Mesh V2 | 15 cases migrated to fresh aggregate replay with exact ordered identities, intended/primary equality, causal closure, and forward/reverse replay | Conforming local regression evidence; package refreeze and release evidence remain separate gates |
| Biblical Evidence / P66 | All 77 fixtures now use one full-package byte-overlay aggregate boundary with actual mutation proof, intended/primary equality, exact ordered identities, causal closure, and forward/reverse replay; the latest cases reject aliased auditor/checker actors, checker override of auditor failure, broken phase-pair chains, and impossible self-referential receipt hashes | Frozen digests, actor-bound completeness receipts, and academic, graph/mesh, and rights reviews now replay against the same exact specification-only package; they grant no translation, doctrine, runtime, or human authority |
| Academic Extension Contract | The guarded 12-fixture migration now binds exact first and ordered rules; 28 focused tests pass and the canonical frozen manifest replays without findings | The static specification is refrozen locally, but public release still depends on the surrounding exact Git chain, CI, unchanged-head review, and normal merge |
| Doctrine Marathon V3 | 197 source cases are now derived from 164 legacy membership/component cases plus 33 exact-ordered component cases; four mapped high-risk cases pass a local copied-root aggregate sentinel, but no V4 receipt, V3 registry, clean-checkout adapter, or CI binding exists | Public maturity is `blocked_specification_only`; final validation deliberately retains `adversarial_harness_release_gate` |
| Portfolio release harness | A targeted current-byte audit found eight membership assertions and one nonempty assertion in its scoped test file; its public truth model now accepts only one exact declared V3 blocker and no unexpected findings | The portfolio may index a transparent blocked specification, but it may not call V3 validated or treat the four sentinels as full migration |

## Family audit boundary

A fresh read-only recurrence check confirmed a high-risk sibling occurrence in
the **protected local** M7 Scripture candidate, not in immutable
`origin/main`. At observation time its branch was `scratch/t423-m7-sol`, HEAD
`eaf31a940d3166b49c38ca26eb279392e0a3b25b`, while `origin/main` was
`c6982050a0a8f1b9508e1d2c5b767513bc92d2fa`; the named M7 scripts were absent
from `origin/main`. That lane was already very dirty and remains untouched.

The strongest current examples are the protected M7 validator named
`validate_m7_sol_whole_bible_packet_convergence.py`, which derives
`all_packets_complete` from file presence and three self-reported boss fields,
and its audit named `audit_t521_goal_requirements.py`, which hard-codes exact
coverage and convergence as `proven`. A writer can also emit an audit after validator
failure, while candidate-inventory and scaffold checks validate labels or
remain informational. These are protected follow-up findings, not permission
to inspect further, edit M7, or treat its work as invalid.

The earlier broad family-audit paragraph named additional canonical
Scripture-first, doctrine-genealogy, and boundary-literature surfaces. This
scoped current-byte recheck did not reproduce those claims at the cited
`origin/main` anchors, so they are withdrawn from the current finding set
rather than carried forward as fact. Any future family inventory must be
rebuilt from exact immutable objects and separately reviewed.

| Repository audit anchor | Confirmed unadapted surface | Minimum next claim |
| --- | --- | --- |
| protected local `logos-scripture-graph` M7 candidate at `eaf31a940d3166b49c38ca26eb279392e0a3b25b` | packet-convergence, goal-requirement, audit-writer, inventory, and scaffold controls | Wait for a stable owner checkpoint; then add a claimed Scripture adapter, exact registry, aggregate replay, V4 receipts, CI, and unchanged-head review without modifying active M7 work |
| `logos-governance-architecture` `f320d8430c10f82d4fdd80567c4d533fa90c25d5` | current portfolio truth model and release-oracle migration in this claimed lane | Preserve the exact blocker projection, frozen payload, independent reviews, and aggregate sentinels through the governed Git release chain |

## Recurrence prevention

During the 2026-08-28 actor-bound completeness-receipt repair, the owner lane
caught an attempted evidence design that would have embedded the digest of the
[P66 exit-completeness receipt](../../biblical-evidence-demonstration-v1/release/exit-completeness-audit.yaml)
inside that same mutable file. The defect
was contained before any v2 pass receipt was written or released. Its credible
counterfactual was a permanently stale receipt, an unprovable fixed point, or a
future validator that silently accepted a prior-file digest. The repair removes
the self-reference, requires immutable external inputs plus canonical receipt
sub-payload digests, and adds an aggregate negative fixture whose primary rule is
`receipt_self_reference`.

- Global agent routing now requires this contract whenever a negative fixture,
  mutation test, fault-injection catalog, red-team catalog, or aggregate harness
  is created, changed, refrozen, or used as evidence.
- The portable V4/V3 control now defines deterministic per-repository registration
  and discovery. Static hints may identify candidates, but only an explicit
  digest-bound registry can classify a governed harness or a narrowly
  human-reviewed, expiring ordinary-test exception; unregistered candidates
  fail closed.
- Repository packages must carry their own deterministic adapter and immutable
  receipt index with exactly one current V4 receipt per governed catalog case.
  A global instruction or one representative receipt is not release evidence.
- Membership-only checks may remain solely as labeled, non-authorizing legacy
  regression observations while migration is underway.
- Executable case identity and counts are now derived from two exact catalogs.
  The prior hand-maintained `193` total, its unsupported `43/36/85` buckets,
  and the older receipt's `164 + 24` statement are invalidated rather than
  relabeled. Independent replay found 78 of the 164 legacy candidates currently
  fail first on a rule other than the fixture's claimed rule.
- A package with unresolved intended/primary mismatch, aggregate-run absence,
  changed-input drift, or unreviewed causal closure remains blocked even when
  its component tests are green.
- V4 binds exact baseline/candidate blobs, byte-diff equality, typed add/modify/
  delete deltas, JSON Pointer value digests, one reseal row per changed path,
  an acyclic dependency graph, raw ordered output artifacts, actual invocation,
  and stable physical file identities. Missing physical identity fails closed;
  a pathname fallback cannot hide hard-link aliasing.
- Every failed migration attempt and transaction-safety defect is preserved for
  causal analysis; no failed chain is rewritten or used as release evidence.

The portable checker does not install itself into sibling repositories or
prove that a CI provider invoked a bound adapter. Each repository still needs
a separately claimed adapter, exact tracked-file inventory, adapter test,
machine-readable CI binding, current V4 receipts, and observed CI execution.
Until then, the family-audit findings above remain protected-release blockers,
not silently inherited coverage from this global control.

## Explicit nonclaims

This repair does not establish factual, archaeological, textual-critical,
historical, theological, or doctrinal correctness. It does not qualify an AI
or human expert. It does not activate a runtime, ingest a source, approve a
translation, resolve a human-gated architecture decision, or authorize
publication.
