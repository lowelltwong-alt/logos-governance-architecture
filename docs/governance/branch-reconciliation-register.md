---
object_type: branch_reconciliation_register
trust_zone: canonical
lifecycle_status: active
provenance_note: "Created on 2026-06-22 during the clean, auditable, chunking-ready trunk reconciliation pass after Scripture Graph PR #105 preserved stale-branch rediscovery instructions. Updated on 2026-06-22 after Scripture Graph PR #107 merged the T390 manuscript source catalog metadata plan and the stale detached Scripture worktree was removed. Updated on 2026-06-22 to docket the dirty parallel-agent T391 Scripture worktree with a local safety snapshot. Updated on 2026-07-07 for Fable Wave-2 W2-14 stale-branch hygiene after governance PR #93. Updated on 2026-07-10 to link the deterministic family worktree audit and reconciliation workflow."
reason_for_inclusion: "Keep branch cleanup, preservation, and unknown-branch decisions discoverable from the governance front door instead of relying on chat memory or local branch lists."
---

# Branch Reconciliation Register

## Purpose

This register records branch cleanup evidence for active Logos-family repos.

It exists so future agents can distinguish:

- branches proven safe to delete because they are merged or explicitly superseded;
- branches preserved for safety or audit;
- branches that require review before deletion;
- branch cleanup that must not be confused with theological, data-plane, or output authority.

## Non-Authorizations

This register does not authorize:

- canonical Scripture text or passage-record changes;
- chunk output, reviewed-gold promotion, child spans, route behavior, evaluator behavior, graph edges, retrieval truth, vectors, or boundary imports;
- preferred textual readings, source-tradition preference, canon-scope change, or denominational systematic theology as chunk authority;
- direct merging of stale branches into current `main`;
- deletion of unknown or safety branches without preservation/audit evidence.

## Operating Rule

Use each repo's live GitHub `main` branch as the active base. Do not collapse unrelated work into one mega-branch. Delete only branches with one of these evidence types:

- GitHub PR state is `MERGED`;
- branch is an ancestor of current `origin/main`;
- a merged audit file explicitly preserves the branch signal and authorizes cleanup;
- the owner explicitly authorizes deletion after preservation.

If none of those is true, classify the branch as `unknown_review_required` or `safety_preserve`.

## 2026-06-22 Snapshot

| Repo | Active base | Result |
|---|---|---|
| `logos-scripture-graph` | `main` at `1f5c623` | Clean active base on `main`; merged T388/T389/T390/T390-readiness work is on main, and the dirty parallel-agent T391 worktree is preserved/docketed rather than deleted. |
| `logos-boundary-literature` | `main` at `b38531e` | Clean on `main`; only `main` remains locally/remotely after deleting merged PR branches. |
| `logos-governance-architecture` | `main` at `8112503` | Clean on `main`; one local Claude safety branch remains preserved, and two remote branches remain review-required. |
| `noesis-atlas` | `main` at `8fb557b` | Clean on `main`; merged feature branches removed, local `master` remains review-required. |

## 2026-07-07 W2-14 Wave-2 Stale-Branch Hygiene Snapshot

| Repo | Active base after cleanup | Result |
|---|---|---|
| `logos-governance-architecture` | `main` at `43a1679` | W2-0 PR #93 merged and local repo was clean before this W2-14 register update branch was created. |
| `logos-scripture-graph` | detached `origin/main` at `280c73b` in the root checkout | Root checkout was moved off stale `scratch/t423-M4-codex-gpt55` after confirming PR #158 was merged and the branch tip was an ancestor of `origin/main`. Local `main` remains checked out by `_codex_worktrees/logos-scripture-t467-harness-hardening`, so the root checkout was parked detached instead of stealing `main` from that worktree. |
| `logos-boundary-literature` | `main` at `60a8f99` | Root checkout returned to clean `main`; stale merged branch `codex/governance-map-child-gate` was deleted locally/remotely after confirming PR #13 was merged and the branch tip was an ancestor of `origin/main`. An untracked Python cache under the boundary tests folder was removed. |
| `logos-doctrine-genealogy` | `main` at `1e03972` | Already clean on `main`; no branch hygiene action needed. |

## 2026-07-10 Deterministic Family Work Audit

The first generated family audit is
[`reports/FAMILY_WORKTREE_AUDIT_2026-07-10.md`](../../reports/FAMILY_WORKTREE_AUDIT_2026-07-10.md),
with a machine-readable YAML companion. It observed all five configured family
repos and every Git-linked worktree, including dirty, detached, duplicate-task,
open-PR, and merged/superseded candidates. The audit introduces no deletion
authorization. Every unresolved item must be assigned a governed work ID and an
explicit continue, extend, supersede, split, parallel-boundary, or preserved-
abandon decision before cleanup.

## Cleaned Branches

| Repo | Branch | Classification | Evidence | Action |
|---|---|---|---|---|
| `logos-scripture-graph` | `codex/legacy-branch-discovery-audit` | merged_delete_safe | PR #105 merged on 2026-06-22. | Remote branch deleted by merge cleanup. |
| `logos-scripture-graph` | `codex/t390-manuscript-source-catalog-plan` | merged_delete_safe | PR #107 merged on 2026-06-22 as `086b3f5`; the branch was green, non-output-changing, and limited to manuscript source catalog metadata planning surfaces. | Remote branch deleted by merge cleanup; local worktree and local branch deleted after confirming clean state. |
| `logos-scripture-graph` | `scratch/t423-M4-codex-gpt55` | merged_delete_safe | PR #158 merged on 2026-07-07; branch tip `820a20e` was an ancestor of `origin/main` at `280c73b`. | Local branch deleted during W2-14 cleanup on 2026-07-07; remote branch was already gone. Root checkout was parked detached at `origin/main` because local `main` is checked out in a linked worktree. |
| `logos-scripture-graph` | `feat/scale-connection-discovery-codex-5-5` | superseded_archive | T388 audit on main records rediscovery-only use and forbids direct merge. | Local and remote branches deleted after T388 reached main. |
| `logos-scripture-graph` | `t320-t325-boundary-entity-commentary-planning-pack` | superseded_archive | T388 audit on main records useful files and forbids direct merge. | Local-only branch deleted after T388 reached main. |
| `logos-boundary-literature` | `codex/commentary-lineage-placement` | merged_delete_safe | PR #4 merged on 2026-06-22. | Local and remote branches deleted. |
| `logos-boundary-literature` | `t002-three-repo-routing-guardrails` | merged_delete_safe | PR #1 merged on 2026-06-08. | Local and remote branches deleted. |
| `logos-boundary-literature` | `t003-contributor-review-policy` | merged_delete_safe | PR #2 merged on 2026-06-08. | Local and remote branches deleted. |
| `logos-boundary-literature` | `t004-governance-is-constraint-not-obstacle` | merged_delete_safe | PR #3 merged on 2026-06-08. | Local and remote branches deleted. |
| `logos-boundary-literature` | `codex/governance-map-child-gate` | merged_delete_safe | PR #13 merged on 2026-06-29; branch tip `76466e7` was an ancestor of `origin/main` at `60a8f99`. | Local branch deleted; remote branch deleted during W2-14 cleanup on 2026-07-07. |
| `logos-governance-architecture` | `codex/commentary-lineage-placement` | merged_delete_safe | PR #60 merged on 2026-06-22; clean old worktree removed. | Local branch/worktree removed; remote was already gone. |
| `logos-governance-architecture` | `codex/governance-dependency-map` | merged_delete_safe | PR #59 merged on 2026-06-17. | Local and remote branches deleted. |
| `logos-governance-architecture` | `docs/shannon-note-hardening` | merged_delete_safe | PR #49 merged on 2026-05-29; patch equivalent present on main. | Local branch deleted; remote was already gone. |
| `logos-governance-architecture` | `feature/shannon-information-theory-note` | merged_delete_safe | PR #48 merged on 2026-05-29. | Local branch deleted; remote was already gone. |
| `logos-governance-architecture` | `gov-t001-cross-repo-contract` | merged_delete_safe | PR #58 merged on 2026-06-11; clean old worktree removed. | Local, worktree, and remote branches deleted. |
| `logos-governance-architecture` | `governance-boundary-cannot-treat-governance-as-obstacle` | merged_delete_safe | PR #57 merged on 2026-06-08; clean old worktree removed. | Local, worktree, and remote branches deleted. |
| `logos-governance-architecture` | `logos-repo-registry-and-future-architecture` | merged_delete_safe | PR #56 merged on 2026-06-08. | Local and remote branches deleted. |
| `logos-governance-architecture` | `docs/frontier-signal-agent-skill-roadmap` | merged_delete_safe | PR #45 merged on 2026-05-01. | Remote branch deleted. |
| `logos-governance-architecture` | `integrate/logos-scripture-graph-substrate` | merged_delete_safe | PR #51 merged on 2026-06-04. | Remote branch deleted. |
| `logos-governance-architecture` | `claude/review-agent-docs-RfrMC` | merged_delete_safe | Branch was merged into `origin/main`. | Remote branch deleted. |
| `logos-governance-architecture` | `feat/decision-framework-habitat-scaffold` | merged_delete_safe | Branch was merged into `origin/main`. | Remote branch deleted. |
| `logos-governance-architecture` | `feat/phase-3-trinity-network-clean` | merged_delete_safe | Branch was merged into `origin/main`. | Remote branch deleted. |
| `logos-governance-architecture` | `feat/phase-3-trinity-network-commits` | merged_delete_safe | Branch was merged into `origin/main`. | Remote branch deleted. |
| `noesis-atlas` | `docs/shannon-note-hardening` | merged_delete_safe | PR #2 merged on 2026-05-29; branch was stale relative to `origin/main`. | Local branch deleted; remote was already gone. |
| `noesis-atlas` | `feature/shannon-information-theory-note` | merged_delete_safe | PR #1 merged on 2026-05-29. | Local branch deleted; remote was already gone. |

## Cleaned Worktrees

| Repo | Worktree | Classification | Evidence | Action |
|---|---|---|---|---|
| `logos-scripture-graph` | `_codex_worktrees/logos-scripture-t390-manuscript-source-catalog` | merged_delete_safe | PR #107 merged and the worktree was clean with remote branch gone. | Worktree removed; local branch deleted. |
| `logos-scripture-graph` | `_codex_worktrees/logos-scripture-graph-crossrepo` | superseded_archive | Detached HEAD `0dc6280` was clean and already contained in current `main`; no branch or uncommitted work existed. | Worktree removed; no branch deleted. |

## Active Or Preserved Worktrees

| Repo | Worktree | Classification | Why Preserved | Required Next Step |
|---|---|---|---|---|
| `logos-scripture-graph` | `_codex_worktrees/logos-scripture-t391-source-catalog-research-packet` | active_pr_needed | Dirty parallel-agent worktree on local branch `codex/t391-source-catalog-research-packet`; no open PR yet. Local status, tracked diff, and changed/untracked files were copied to the workspace safety backup named `t391-source-catalog-research-packet-20260622-2110`. | Do not delete or overwrite. Let the owning/next agent rebase or merge from `origin/main`, run T391 validators/tests, then open a separate non-output-changing PR or explicitly archive it after review. |

## Preserved Or Docketed Branches

| Repo | Branch | Classification | Why Preserved | Required Next Step |
|---|---|---|---|---|
| `logos-governance-architecture` | `safety/claude-dirty-governance-20260617-142552` | safety_preserve | Explicit Claude safety branch. It points to the same patch lineage as merged Shannon hardening work, but safety branches should not be deleted without an audit/preservation decision. | Audit against `origin/main` and any stash refs, then either preserve as an archive branch or delete with a short audit note. |
| `logos-governance-architecture` | `origin/benchmark-question-corpus-foundation` | unknown_review_required | Remote branch has no open PR and was not proven merged in this pass. | Inspect diff and PR/issue provenance before deciding whether to convert to PR, archive, or delete. |
| `logos-governance-architecture` | `origin/chore/refresh-retrieval-neighborhoods` | unknown_review_required | Remote branch has no open PR and was not proven merged in this pass. | Inspect whether it is scheduled/generated maintenance, still useful, or stale before deletion. |
| `logos-scripture-graph` | `codex/t391-source-catalog-research-packet` | active_pr_needed | Local branch is checked out by the dirty parallel-agent T391 worktree. It is not delete-safe even though its committed tip is behind current `origin/main`, because uncommitted tracked and untracked work exists. | Preserve until the T391 owner/agent turns it into a reviewed PR, rebases it, or archives it with explicit audit evidence. |
| `noesis-atlas` | `master` | unknown_review_required | Local branch is not an ancestor of `origin/main`; deleting it may lose old local-only history. | Audit its diff and history before deletion or archival. |

## Future Agent Instructions

Before branch cleanup:

1. Read this file.
2. Run `git fetch origin --prune --tags`.
3. Confirm `git status --short --branch` is clean.
4. Check open PRs with `gh pr list --state open`.
5. Use GitHub PR state, ancestry, or an explicit audit note as deletion evidence.
6. Preserve safety and unknown branches until they are audited.

Branch cleanup is an auditability task. It is not evidence that theological, graph, retrieval, chunking, source-language, or canonical data decisions are approved.
