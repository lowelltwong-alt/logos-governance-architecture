---
object_type: prompt_template
trust_zone: governance_instructions
lifecycle_status: draft
review_status: unreviewed
ai_usage_posture: reusable_prompt_header
provenance_note: "Created 2026-04-30 as the universal header for AI-assisted work prompts."
reason_for_inclusion: "Provide a reusable mandatory prompt header so AI-assisted tools declare tool settings, branch, PR title, scope, non-goals, trust zones, work mode, side-effect level, validation, live-main sync, route selection, and routing impact."
---

# Universal AI Prompt Header

Use this header at the top of every Codex, Claude Code, or AI-assisted repository prompt.

## Header

Repository: lowelltwong-alt/logos-governance-architecture

Tool settings:

- Tool:
- Model:
- Reasoning effort:
- Internet:
- Permissions:
- Detail level:

Task declaration:

- Target branch:
- PR title:
- Scope:
- Non-goals:
- Trust zones touched:
- Work mode:
- Side-effect level:
- Expected validation:

Required startup:

- Read AGENTS.md.
- Read AI_WORK_START_HERE.md.
- Read docs/governance/ai-workflow/ai-routing-algorithm.md.
- Treat live origin/main as source of truth for new work.
- Run git status, current branch check, remote check, and fetch origin with prune and tags.
- Fast-forward local main only.
- Create or continue the target branch safely.
- If the target branch already exists locally or remotely, inspect and compare before editing.
- If local state is dirty, divergent, or ambiguous, stop and report.
- Never reset, rebase, force-push, delete, discard, or overwrite local work unless explicitly instructed.

Required route:

- Select exactly one primary route from docs/governance/ai-workflow/ai-task-route-table.yaml.
- Use the matching template from docs/governance/ai-workflow/templates/.
- If multiple routes apply, choose the highest-risk route or split into separate PRs.

Required PR answer:

Does this PR affect AI work routing?

- No.
- Yes, updated AI_WORK_START_HERE.md, route table, settings matrix, or templates.
- Yes, follow-up PR required and listed.
