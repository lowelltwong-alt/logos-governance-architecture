---
object_type: family_worktree_audit
trust_zone: proposed
lifecycle_status: audit_snapshot
provenance_note: "Generated 2026-07-10T18:19:37Z by scripts/audit_family_work.py from Git worktree, branch, status, PR, and governed registry evidence."
reason_for_inclusion: "Preserve a rediscoverable snapshot of every observed family worktree and its reconciliation state without treating age as deletion authority."
---

# Family Worktree Audit

Observed: `2026-07-10T18:19:37Z`

This is a reconciliation docket, not a deletion authorization. Dirty, detached, unknown, or stale work stays preserved until owner review.

## Summary

- Repositories scanned: 5
- Worktrees observed: 40
- Dirty worktrees: 9
- Detached worktrees: 2
- Unregistered worktrees: 37

## Worktrees

| Repo | Worktree | Branch / task | Dirty | Age days | Ahead / behind | Registered | Classification |
|---|---|---|---:|---:|---:|---|---|
| `logos-governance-architecture` | `logos-governance-architecture` | `codex/od-c-open-independent-study` | no | 0.03 | 1 / 1 | NO | `merged_or_superseded_cleanup_candidate` |
| `logos-governance-architecture` | `logos-gov-workcoord` | `codex/family-work-coordination` | yes | 0.0 | 0 / 0 | WORK-GOV-FAMILY-COORD-001 | `preserve_dirty_owner_reconciliation` |
| `logos-scripture-graph` | `logos-scripture-graph-repo` | `codex/w2-2-scripture-mirror-freshness` | yes | 0.02 | 1 / 13 | WORK-SCR-T468-W2-2 | `preserve_dirty_owner_reconciliation` |
| `logos-scripture-graph` | `logos-scripture-governance-map-child-gate` | `codex/governance-map-child-gate` | no | 10.92 | 1 / 112 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-pr123-conflict-fix` | `codex/pr123-conflict-fix` | no | 10.7 | 5 / 111 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t391-source-catalog-research-packet` | `detached / T391` | no | 17.2 | 0 / 119 | NO | `detached_review_required` |
| `logos-scripture-graph` | `logos-scripture-t392-source-catalog-sqlite-shell` | `codex/t392-source-catalog-sqlite-shell / T392` | no | 17.65 | 3 / 123 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t394-eph1-reviewed-gold-promotion` | `codex/t394-eph1-reviewed-gold-promotion / T394` | no | 16.89 | 2 / 118 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t397-eph1-route-isolation-harness` | `codex/t402-low-complexity-runway / T397, T402` | no | 15.01 | 2 / 113 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t398-bible-wide-phase-one-research` | `codex/t398-bible-wide-phase-one-research / T398` | no | 16.8 | 1 / 117 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t399-focused-bible-wide-research` | `codex/t399-focused-bible-wide-research / T399` | no | 16.67 | 1 / 116 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t411-cursor-readiness-gate` | `codex/t411-cursor-readiness-gate / T411` | no | 9.64 | 0 / 96 | NO | `merged_or_superseded_cleanup_candidate` |
| `logos-scripture-graph` | `logos-scripture-t423-M1-cursor` | `scratch/t423-M1-cursor / T423` | yes | 6.01 | 0 / 67 | NO | `preserve_dirty_owner_reconciliation` |
| `logos-scripture-graph` | `logos-scripture-t423-M5-gemini-thinking` | `scratch/t423-M5-gemini-thinking / T423` | yes | 5.98 | 2 / 67 | NO | `preserve_dirty_owner_reconciliation` |
| `logos-scripture-graph` | `logos-scripture-t423-six-model-marathon` | `codex/t423-six-model-marathon-complete / T423` | no | 4.12 | 1 / 47 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t424-modular-rust-validators` | `codex/t424-modular-rust-validators / T424` | no | 4.08 | 3 / 46 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t424-rust-fast-validators` | `codex/t424-rust-fast-validators / T424` | no | 5.08 | 0 / 56 | NO | `merged_or_superseded_cleanup_candidate` |
| `logos-scripture-graph` | `logos-scripture-t425-rust-validator-hardening` | `codex/t425-rust-validator-hardening / T425` | no | 5.03 | 0 / 54 | NO | `merged_or_superseded_cleanup_candidate` |
| `logos-scripture-graph` | `logos-scripture-t426-rust-validator-contract-parity` | `codex/t426-rust-validator-contract-parity / T426` | yes | 5.02 | 0 / 53 | NO | `preserve_dirty_owner_reconciliation` |
| `logos-scripture-graph` | `logos-scripture-t430-original-language-evidence` | `codex/t430-original-language-evidence-roadmap / T430` | yes | 5.95 | 0 / 67 | NO | `preserve_dirty_owner_reconciliation` |
| `logos-scripture-graph` | `logos-scripture-t431-original-language-intake` | `codex/t431-original-language-intake / T431` | no | 5.77 | 6 / 67 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t431-t442-integration` | `detached / T431` | no | 3.91 | 0 / 23 | NO | `detached_review_required` |
| `logos-scripture-graph` | `logos-scripture-t432-bible-edge-taxonomy` | `codex/t451-bible-edge-taxonomy-deepening / T432, T451` | no | 4.88 | 3 / 53 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t432-original-language-schema-contracts` | `codex/t432-original-language-schema-contracts / T432` | no | 5.75 | 7 / 67 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t433-phlm-alignment-pilot` | `codex/t433-phlm-alignment-pilot / T433` | no | 5.71 | 8 / 67 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t435-original-language-observation` | `codex/t435-original-language-observation / T435` | no | 5.67 | 9 / 67 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t436-jonah-hebrew-pilot` | `codex/t436-jonah-hebrew-pilot / T436` | no | 5.63 | 10 / 67 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t437-oshb-lemma-drift` | `codex/t442-production-root-decision-packet / T437, T442` | no | 5.45 | 18 / 67 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t450-bible-edge-taxonomy` | `codex/t465-multi-model-reconciliation-gate / T450, T465` | no | 3.59 | 0 / 17 | NO | `merged_or_superseded_cleanup_candidate` |
| `logos-scripture-graph` | `logos-scripture-t456-runtime-env` | `codex/t456-runtime-env-dad-lesson / T456` | no | 4.77 | 1 / 53 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t457-fast-canonical-qa` | `codex/t457-fast-canonical-qa / T457` | no | 4.73 | 1 / 53 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t458-rust-subagent-charter` | `codex/t458-rust-subagent-charter / T458` | no | 4.7 | 1 / 53 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t459-word-token-signals` | `codex/t459-word-token-signal-scanner / T459` | no | 4.64 | 2 / 53 | NO | `unpublished_or_unmerged_commits` |
| `logos-scripture-graph` | `logos-scripture-t460-rust-dad-stack` | `codex/t460-rust-dad-stack-integration / T460` | no | 4.58 | 0 / 48 | NO | `merged_or_superseded_cleanup_candidate` |
| `logos-scripture-graph` | `logos-scripture-t461-original-language-stack` | `codex/t461-original-language-stack-integration / T461` | yes | 4.2 | 18 / 47 | NO | `preserve_dirty_owner_reconciliation` |
| `logos-scripture-graph` | `logos-scripture-t467-harness-hardening` | `codex/t471-near-boundary-docket-refinement / T467, T471` | yes | 0.66 | 0 / 9 | NO | `preserve_dirty_owner_reconciliation` |
| `logos-scripture-graph` | `logos-scripture-t469-primary-witness-plan` | `codex/t469-primary-witness-acquisition-plan / T469` | no | 0.01 | 1 / 0 | WORK-SCR-T469 | `open_pr_review` |
| `logos-boundary-literature` | `logos-boundary-literature` | `main` | no | 2.98 | 0 / 0 | NO | `active_base_or_current_checkout` |
| `logos-doctrine-genealogy` | `logos-doctrine-genealogy` | `main` | no | 2.98 | 0 / 0 | NO | `active_base_or_current_checkout` |
| `noesis-atlas` | `noesis-atlas` | `main` | yes | 41.88 | 0 / 0 | NO | `preserve_dirty_owner_reconciliation` |

## Duplicate Task Signals

- `T423` appears in 3 worktrees: `logos-scripture-graph:logos-scripture-t423-M1-cursor`, `logos-scripture-graph:logos-scripture-t423-M5-gemini-thinking`, `logos-scripture-graph:logos-scripture-t423-six-model-marathon`
- `T424` appears in 2 worktrees: `logos-scripture-graph:logos-scripture-t424-modular-rust-validators`, `logos-scripture-graph:logos-scripture-t424-rust-fast-validators`
- `T431` appears in 2 worktrees: `logos-scripture-graph:logos-scripture-t431-original-language-intake`, `logos-scripture-graph:logos-scripture-t431-t442-integration`
- `T432` appears in 2 worktrees: `logos-scripture-graph:logos-scripture-t432-bible-edge-taxonomy`, `logos-scripture-graph:logos-scripture-t432-original-language-schema-contracts`

## Required Reconciliation

1. Preserve every dirty or unpublished worktree.
2. Match each unfinished item to a governed work ID and roadmap/task.
3. Record continue, extend, supersede, split, parallel-boundary, or preserved-abandon decision.
4. Remove a worktree only after clean-state, merge/ancestry, and preservation evidence agree.
