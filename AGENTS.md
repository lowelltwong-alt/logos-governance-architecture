---
object_type: repository_governance_contract
trust_zone: canonical
lifecycle_status: active
provenance_note: "Created on 2026-04-05 from the maintainer's governing contract provided in chat. Updated on 2026-04-30 to add a live-main startup protocol for new Codex work. Updated on 2026-07-10 to require family work-registry and overlap preflight before new work."
reason_for_inclusion: "Keep the working contract on disk at the repo root so future edits follow the same governance rules."
---

# AGENTS.md

## Project intent
This repository is a governed theological ontology project.
Optimize for structural clarity, provenance, and future scalability.
Be strict on structure and light on ceremony.

## Current operating mode
Solo-maintainer mode.
Assume one maintainer currently performs:
- author
- reviewer
- promoter
- publisher

## Live-main startup protocol for new work
Before starting new Codex or AI-assisted repository work, treat the live GitHub `main` branch as the source of truth.

Default startup sequence for new work:

```bash
git status
git branch --show-current
git fetch origin --prune --tags
git checkout main
git pull --ff-only origin main
git status
git log --oneline --decorate -n 8
python scripts/validate_family_work_registry.py
```

Before creating or reusing a branch/worktree, read
`governance/registry/FAMILY_WORK_REGISTRY.yaml` and the latest
`reports/FAMILY_WORKTREE_AUDIT_*.md`. Search for the same task ID, roadmap,
semantic tags, and claimed paths. New work must receive one governed work ID and
claim before non-claim edits begin. Continue, extend, supersede, split, or permit
parallel work only through the controlled coordination policy. Stop for owner
input on dirty-worktree, shared-roadmap, high-risk-tag, or write-path ambiguity.
After adding the claim, run `scripts/audit_family_work.py --check-work-id` against
the live family root before other edits.

For material agent, CI, workflow, worktree, architecture, security, or recurring-
process work, also read `docs/governance/engineering-practice-observatory.md`.
External company practice is evidence, not governance authority.

If the task explicitly continues an existing branch, reviews an old pull request, or inspects historical state, do not blindly switch, reset, rebase, or pull over that work. First report the current branch, working-tree state, and relationship to `origin/main`.

If there is uncommitted work, an untracked-file risk, a non-fast-forward condition, or local/remote divergence, stop and report the blocker before editing files.

Do not create feature, seed, roadmap, or cleanup branches from stale local `main`.

Do not assume a previous chat, local mirror, or deleted branch reflects the current live repo state.

Do not reset, rebase, force-push, discard local work, delete branches, or overwrite files unless explicitly instructed.

## Non-negotiable rules
- Do not invent new top-level folders unless necessary.
- Keep identity separate from labels.
- Do not let inferred or AI-generated material overwrite canonical material.
- Keep doctrine topic, doctrine view, and doctrine assessment separate.
- Preserve history through deprecation rather than deletion.
- Sync from live `origin/main` before starting new repository edits unless explicitly continuing existing branch work.
- Stop and report dirty, divergent, or non-fast-forward local state before editing.
- Do not start duplicate or overlapping work without a validated family work claim and any required owner overlap resolution.

## Required metadata for meaningful additions
Every meaningful addition should declare:
- object type
- trust zone
- lifecycle status
- short provenance note
- reason for inclusion

If a change cannot satisfy those five things, keep it in notes/backlog instead of governed core.

## Trust zones
Allowed trust zones:
- canonical
- tradition-scoped
- proposed
- inferred
- deprecated
- learning-sidecar

Lower-trust zones may reference higher-trust zones.
Higher-trust zones may not depend on lower-trust zones.

## File placement
- Governance docs go in `docs/governance/`
- Phase docs go in `docs/`
- Examples go in `examples/`
- Machine-readable manifests go beside the relevant module or example

## Working style
- Prefer small, reviewable edits
- Prefer explicit file creation over broad rewrites
- Explain why a file belongs before adding it
- Keep commit messages short and concrete

## Definition of done
Before finishing:
- check file placement
- check required metadata
- check trust zone correctness
- check provenance note presence
- leave the worktree clean
