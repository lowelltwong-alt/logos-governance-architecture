---
object_type: family_work_coordination_guidance
trust_zone: canonical
lifecycle_status: active
provenance_note: "Created 2026-07-10 by Codex from an owner request for a deterministic, auto-populated scrum view of every worktree, roadmap, dependency, and overlap."
reason_for_inclusion: "Explain the mandatory claim, lease, audit, overlap, and board workflow in human-readable form without making the visual board an authority source."
---

# Family Work Coordination

## Operating Model

The Logos family uses four linked surfaces:

1. `FAMILY_WORK_REGISTRY.yaml` is the governed work identity and claim source.
2. Git branches, worktrees, issues, and pull requests are implementation evidence.
3. `audit_family_work.py` discovers local work that the registry or board missed.
4. the **Logos Family Work** GitHub Project is the scrum/Kanban view.

The board is useful, but it is a projection. A forgotten card move cannot erase a
dirty worktree, close an owner gate, or authorize theology, Scripture, source, or
output changes.

## Before Any New Work

Run the read-only inventory and search for the task, roadmap, tags, and paths:

```powershell
python scripts/audit_family_work.py --family-root "C:\path\to\03_World_View"
python scripts/validate_family_work_registry.py
python scripts/audit_family_work.py --family-root "C:\path\to\03_World_View" --check-work-id WORK-EXAMPLE-001
```

Then choose exactly one result:

- `continue_existing`: return to the existing worktree and work ID;
- `extend_existing`: add the upgraded idea to the existing work claim;
- `supersede_existing`: preserve the old work and record the replacement;
- `split_paths`: allow parallel work with non-overlapping claimed paths;
- `allow_parallel_with_recorded_boundaries`: record why overlap is compatible;
- `abandon_after_preservation`: preserve evidence before closing the old work.

If the choice affects a dirty worktree, a shared roadmap target, a governed
high-risk tag, or overlapping write paths, stop for the owner. Staleness is a
request for reconciliation, never permission to delete.

## Deterministic Overlap

The validator uses structured evidence, not AI intuition:

- duplicate `work_id`, `task_id`, or active roadmap target;
- overlapping normalized path claims in the same repo;
- exclusive versus additive/read-only claim mode;
- shared controlled high-risk semantic tags;
- referenced owner overlap resolutions.

AI semantic similarity may suggest that two differently worded ideas are related,
but it cannot clear or create a conflict. The agent must encode the relationship in
the claim or ask the owner.

## Lease And Age

Active, blocked, and review work has a heartbeat and stale interval. The audit
shows the latest durable commit, dirty state, heartbeat, and age. A stale lease
moves the item to owner reconciliation; it does not mark the work abandoned.

## GitHub Project Projection

Professional teams commonly make issues the durable task identity, link branches
and pull requests to those issues, and use Project workflows to auto-add and move
cards. Logos follows that model with one extra safety property: the local registry
and Git audit can reconstruct state without GitHub access.

Recommended Project fields:

| Field | Source |
|---|---|
| Status | registry status / issue or PR event |
| Repo | work claim |
| Work ID | work claim |
| Task / roadmap | work claim |
| Owner gate | authority ceiling and tags |
| Last heartbeat | work claim |
| Stale | computed from heartbeat |
| Overlap | validator result |
| PR | linked implementation evidence |

Project automation should auto-add family issues and PRs, move linked PRs to
Review, move merged PRs to Done, and archive completed items while retaining field
history. GitHub Actions concurrency should serialize jobs by repo and work ID where
two runs would mutate the same generated or governed surface.

This design follows the stable porcelain interface in the
[Git worktree documentation](https://git-scm.com/docs/git-worktree.html), GitHub's
[automatic Project item addition](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/adding-items-automatically),
[issue/PR linking](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue),
[Project archiving](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/archiving-items-automatically),
and [Actions concurrency groups](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency).
The heartbeat model is analogous to
[Kubernetes leases](https://kubernetes.io/docs/concepts/architecture/leases/):
renewal proves recent activity, while expiry triggers reconciliation rather than
rewriting the underlying state.

## Existing Worktrees

The dated family audit is a reconciliation docket, not a deletion list. Every
dirty, detached, unregistered, unpublished, or stale worktree remains preserved
until its owner chooses a lifecycle action. New agents must consult that audit as
well as the registry until all legacy worktrees are reconciled.
