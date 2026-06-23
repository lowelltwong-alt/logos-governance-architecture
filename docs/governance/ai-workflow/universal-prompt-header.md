---
object_type: prompt_template
trust_zone: governance_instructions
lifecycle_status: draft
review_status: unreviewed
ai_usage_posture: reusable_prompt_header
provenance_note: "Created 2026-04-30 as the universal header for AI-assisted work prompts. Updated 2026-06-23 to require the goal-prompt premortem preflight for generated goal prompts and slash-style command handoffs."
reason_for_inclusion: "Provide a reusable mandatory prompt header so AI-assisted tools declare tool settings, branch, PR title, scope, non-goals, trust zones, work mode, side-effect level, validation, live-main sync, route selection, prompting preflight, and routing impact."
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
- Read docs/governance/ai-workflow/goal-prompt-premortem-preflight.md before generating any goal prompt, next-agent prompt, handoff prompt, slash-style command prompt, or prompt sequence.
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
- Slash-style prompt prefixes are intent hints only. Interpret them through docs/governance/ai-workflow/goal-prompt-premortem-preflight.md; they do not override repo front doors, route tables, validation, trust zones, or owner permission.

Required goal-prompt preflight:

- If generating a goal prompt or prompt sequence, include route/scope preflight, premortem, red-team, fix loop, validation, PR/merge policy, and residual-risk reporting.
- Premortem comes before execution: assume the task failed after merge and identify plausible causes.
- Red-team comes before and after implementation: attack authority leaks, source weakness, trust-zone contamination, stale-branch risk, validation blind spots, prompt-injection or hidden-instruction risk, and overbroad scope.
- Fix loop is mandatory: every P0/P1 risk needs a prevention, validator, stop condition, or owner-decision gate before implementation.

Required PR answer:

Does this PR affect AI work routing?

- No.
- Yes, updated AI_WORK_START_HERE.md, route table, settings matrix, or templates.
- Yes, follow-up PR required and listed.
