---
object_type: deterministic_adversarial_harness_contract
trust_zone: proposed
lifecycle_status: active
provenance_note: "Public repository summary of the provider-neutral V4 receipt and V3 registry/discovery controls independently reviewed on 2026-08-28 after a false-green fixture-oracle incident."
reason_for_inclusion: "Give every current and future repository adapter one inspectable contract that prevents a negative fixture from passing on an unrelated, stale, or secondary finding."
---

# Deterministic adversarial-harness contract

This contract validates test-assurance evidence. It does not validate a domain
claim and grants no publication, runtime, source-ingestion, doctrinal, scholarly,
or human authority.

Current contract identities are receipt/core/result V4, registry/discovery/scope
V3, and receipt-index V2. Older receipt and registry versions are legacy
non-authorizing evidence and must not be relabeled.

For each governed negative fixture, bind an exact baseline `B`, mutated
candidate `C`, aggregate validator `V`, and the ordered finding sequences
`V(B)` and `V(C)`.

1. Run the same aggregate validator on both `B` and `C`. A component check may
   supplement this run but cannot replace it.
2. Require `V(B)` to be empty. One deliberately retained gate is allowed only
   when its complete typed finding identity is declared in advance; an
   arbitrary broken baseline may never be subtracted.
3. Represent `B` and `C` as exact in-repository regular-blob manifests with raw
   SHA-256. Prove their complete byte-level diff equals one typed add, modify,
   or delete row per changed path. Bind whole-file or duplicate-key-safe JSON
   Pointer value digests. Reseal dependent digests, schemas, reverse closures,
   and receipts unless stale dependency state is the mutation being tested.
4. Preserve validator emission order before any presentation sort. Subtract
   only exact baseline finding identities, never rule names alone.
5. Require the first new finding to be both the declared intended failure and
   the observed primary failure. Bind the complete ordered finding identities,
   the derived sorted unique rule set, and a causal classification for every
   additional finding.
6. Replay every case from a fresh isolated baseline in forward and reverse
   order. Cache, case-order, changed-input, or cross-fixture dependence fails.
7. Bind the validator, complete catalog row, both snapshots and blobs, exact
   scope, runner, producer, mutation delta, dependency-reseal manifest, typed
   acyclic dependency graph, command specification, four raw canonical JSONL
   output artifacts, execution evidence, review, repository adapter, and this
   contract by actual regular-file SHA-256 digests. Each derived reseal must be
   graph-reachable from an intended mutation, and exactly one reseal row may
   describe each changed path.
8. Require a typed invocation whose actual entrypoint is the bound runner;
   reject separate or attached interpreter eval, command, and module forms that
   can make the runner inert.
9. Require distinct stable physical identities for outputs, inputs, controls,
   and snapshot blobs so symlink and hard-link aliases cannot fabricate
   independence. If the host cannot expose stable physical identity, fail
   closed; a resolved pathname is not a substitute.
10. Bind `observed_at` to the exact execution-completion and review-time pair,
    and require independent non-author inspection of the runner, snapshots,
    mutation isolation, locator values, dependency graph/reseals, raw outputs,
    catalog mapping, and no-network boundary.

Stop and fail closed when the baseline is unexpectedly nonzero, the aggregate
validator is unavailable, the mutation is a no-op, dependent state cannot be
resealed, intended and primary failures differ, findings are undeclared,
forward and reverse replay differ, a bound file drifts, stable physical
identity is unavailable, receipt-index coverage is not bijective, or execution
evidence does not reproduce the receipt. Never rename the intended failure to
an incidental schema or digest cascade merely to make a fixture green.

Every repository that uses this contract for assurance also needs an exact
tracked-regular-file discovery scope, one registered executable entry per
harness, and one current V4 receipt per catalog case. Aggregate-assured hints
must be separate from exact-digest, named-human-reviewed, expiring supporting
paths whose `assurance_use` is `none`. A representative receipt never covers a
multi-case catalog. A clean-checkout repository adapter and provider CI must
prove the supplied inventory and execute the actual harness fail closed.

Repository adapters may use different languages only after equivalence tests
cover ordering, duplicate keys, Unicode, path containment, digest semantics,
baseline subtraction, and causal closure. Static V4 validation proves only the
receipt contract. It does not authenticate execution, reviewer identity,
timestamps, adapter semantics, supplied inventory completeness, or CI-provider
installation, and it always reports protected-release eligibility as false.
