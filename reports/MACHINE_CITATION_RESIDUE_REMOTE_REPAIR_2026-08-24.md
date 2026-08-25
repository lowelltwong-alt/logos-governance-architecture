---
object_type: machine_citation_residue_remote_repair_receipt
trust_zone: canonical
lifecycle_status: active
provenance_note: "Created 2026-08-24 by Codex root from snapshot-pinned local Git evidence and live GitHub ref/PR checks during the owner-authorized repository-wide repair."
reason_for_inclusion: "Preserve an auditable account of the exact remote mutations, history-preservation proofs, privacy redactions, validator coverage, limits, and retained human gates."
---

# Machine Citation Residue Remote Repair — 2026-08-24

## Outcome

The ordered remote repair completed without history rewrite:

- two contaminated remote branch names with no unique commits were removed only
  after exact ancestry and merged-PR checks;
- ten contaminated branch heads with nineteen unique commits were advanced by one
  ordinary non-force child commit each;
- all nineteen pre-repair unique commits remain ancestors of their repaired heads;
- five branch-specific trace matrices retained their unique content while only
  the provenance note and three private attachment references were redacted;
- the final live remote set contains thirteen heads and the deterministic
  all-origin-head scan reports no machine-citation, private-use, obfuscated
  locator, or local profile attachment-path finding.

This operation repaired live branch heads. It did not purge deleted or
unreachable Git objects and makes no claim about forks, other remotes,
pull-request-only refs, local-only refs, or LFS payloads.

## Authority and fail-closed preflight

Lowell authorized one fresh, one-time, read-only protected-hold-aware family
preflight for WORK-GOV-REPO-RESIDUE-REMOTE-REPAIR-001 at checkpoint
08eab8e3edf44ab22175e3e47b1828153a84d716. The preflight:

- ran once and passed;
- suppressed only eight exact clean, non-writing protected holds;
- preserved claim-registry SHA-256
  F995F1747A10479BE858FF8CF76E578AE302F433AE5611077ED522DCD760C96B;
- preserved then-current lifecycle-registry SHA-256
  4849E3385E44F74B0F0ACC5B4CB0AD75EA328CF7A40EA7F0CABAF9259BF0C21B;
- made no repository, ref, worktree, or protected-hold mutation.

The exact unsandboxed global workspace validator passed before the preflight,
after the fresh fetch, before the remote sequence, after the remote sequence,
and after the branch was normally reconciled with current origin/main.

## Two contained remote names removed

| Remote branch | Exact former head | Preservation proof |
|---|---|---|
| codex/logos-convergence-public-projection | bc1ede16be924bf050ff394f4fea42ac217453a3 | Zero commits outside main; ancestor of 91fa8560fecade6b7dd557edad8edf91609efd9b; exact merged head of PR #116 |
| fable/main-exposure-hotfix | 8b20675c676f8715d69cd2c1295d02f8870186cd | Zero commits outside main; ancestor of 91fa8560fecade6b7dd557edad8edf91609efd9b; exact merged head of PR #114 |

Each remote name was queried at its exact expected SHA immediately before
deletion and confirmed absent afterward. The commits remain reachable through
main and retained local refs. No local branch or worktree was deleted.

## Ten ancestry-preserving fast-forwards

Every new commit has exactly the pre-action remote tip as its sole parent. Before
each push, the live remote tip was required to equal the recorded old SHA. Each
push used an ordinary refspec with no force option, and the remote was queried
again for the exact new SHA.

| Remote branch | Preserved old tip | Verified repaired head |
|---|---|---|
| benchmark-question-corpus-foundation | 32c91efb39669d55780e23c4c9362f8d12644a3c | 454400e7746d92dbf2935aa7194acf13bcb1ba45 |
| chore/refresh-retrieval-neighborhoods | 4d212cd33ed5f4f11a30d3448f548829ff1f9df2 | 88bb09484a9ac0dd9c425467ec33a63541e42493 |
| codex/fable-gap-agent-buildout | 33cf762705021abe7409c256adcbdcee45be87e1 | 561203b8bfccd1cd4f6dee1bd4e3c634022457d6 |
| codex/family-work-coordination | 649bee9fe2b0b3795b6631d03e85ef288f74df2e | d1de75a6a2911fb836b75f93bfc1ba9f198491f5 |
| codex/gov-goal-prompt-dependency-map | 89a31f7a0e0e7fd1f111f5230d6bc391f481997d | 2666608575a67181b379bc06af86d5d537c63078 |
| codex/governance-child-mirror-gate | 88b9df9f1ec9ad51273f56c76fa108db32e8af9e | c5ab8ca69b641dc268ab1d16f590d7980a66ab64 |
| codex/governance-map-update-gate | ea1a8f6cb0560c9be0efc6145bd72c8629c1c04c | 028d64bc393991d5978caf1932f2908805989c56 |
| codex/llos-v1-governance | 14a500bd669a2d5b119e37239e088a15c533f77e | c5e85d6809549fd70a7f517df277aa0ca4d901b9 |
| codex/od-c-open-independent-study | d83b65c9032be5deb03ef4208c197c5b941ee792 | 3c4a4c359d9f0f32ebd881253e53241fad0e4bd3 |
| codex/premortem-goal-prompt-preflight | 4b99c936269bc78d1f91f27ff6122d6035fe471d | 477d2ee8792b1f73182886bcf60401c1904dfaa8 |

Candidate-map SHA-256
6C53DF0037CDDD39602B4BD69642CED9F897771A2D846E1E7FBD1730C01DE8A5
records the exact parent, tree, path, and clean-blob checks. Push-receipt
SHA-256
C7215DDC7E6FA97F0751D62CFF1C73A39DDD92CA45328682989230B6EC8C3463
records all ten exact live before/after ref checks. Both receipts also record an
unchanged ordinary branch, index, claim-file hash, and status across the
alternate-index construction and push sequence.

## Exact content scope

All ten repair children replace only the seven contaminated primary-source
example blobs plus:

- docs/canon/NODE_ARCHITECTURE.md
- docs/canon/augustine/README.md

with their byte-identical clean main blobs. None of the nineteen unique commits
had modified those nine paths. The Augustine blob remains exactly
1b68838d9ba92e74b5341c602ef647864f924b55, so its whole-node no-cite gate and
pending qualified patristics review are unchanged.

Exactly these five heads also received the surgical trace-matrix repair:

- chore/refresh-retrieval-neighborhoods
- codex/fable-gap-agent-buildout
- codex/family-work-coordination
- codex/llos-v1-governance
- codex/od-c-open-independent-study

For each, only line 5 and the three attachment-reference lines changed. The two
branches with unique trace-matrix work retained every other branch-specific
line; no whole-file replacement from main occurred.

## Post-repair verification

After a prune-synchronizing fetch, the live remote inventory contained exactly
thirteen heads:

- unchanged clean main at
  91fa8560fecade6b7dd557edad8edf91609efd9b;
- unchanged clean retained heads
  codex/citation-residue-repair and
  codex/logos-stewardship-buildout;
- the ten repaired heads listed above.

The hardened validator scanned all thirteen fetched origin heads: 8,533 UTF
text blobs, zero skipped non-text objects, and zero findings.

## Permanent recurrence controls

scripts/validate_machine_citation_artifacts.py now:

- scans immutable Git index blobs by default instead of mutable worktree files;
- fails closed on conflicted index stages, missing refs, malformed Git output,
  unsafe paths, unreadable objects, and invalid text-like blobs;
- supports repeatable exact --ref targets;
- supports --all-origin-heads for every fetched non-symbolic origin head;
- detects literal and bounded escaped/HTML/percent-encoded private-use markers;
- detects literal and Unicode/percent/invisible-control-obfuscated supported
  chat-local locator forms;
- detects raw and URI-encoded user-profile attachment paths;
- reports only target, path, line, and rule identifiers, never matched payloads.

.github/workflows/machine-citation-residue-sweep.yml runs a daily, read-only
sweep. It explicitly fetches all live origin heads with prune and then invokes
the all-origin-head mode. Pull-request validation continues to run the default
index mode through the governed validation contract.

## Retained limits and gates

- No force-push, reset, rebase, history rewrite, protection bypass, cleanup,
  local branch/worktree deletion, or held-lane mutation occurred.
- The remote repair does not authorize source use, theological approval,
  publication beyond this governed code change, or cleanup.
- The Augustine whole-node gate remains pending qualified patristics review.
- Deleted/unreachable Git objects may remain retained by hosting infrastructure;
  this receipt claims clean live heads, not cryptographic erasure.
- The hardening PR still requires deterministic validation, independent
  exact-diff review, required CI, unchanged-head review, and normal merge.
