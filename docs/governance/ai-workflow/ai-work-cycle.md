---
object_type: governance_process
trust_zone: governance_instructions
lifecycle_status: draft
review_status: unreviewed
ai_usage_posture: mandatory_process_guidance
provenance_note: "Created 2026-04-30 to define the repeatable cycle for AI-assisted repository work. Updated 2026-06-23 to require premortem/red-team/fix-loop handling for generated goal prompts."
reason_for_inclusion: "Define the required orient, sync, classify, route, goal-prompt preflight, validate, PR, report, and router-update cycle for AI-assisted repository work."
---

# AI Work Cycle

Every AI-assisted contribution must follow this cycle.

## 1. Orient

Read the required entry files in order:

1. `AGENTS.md`
2. `AI_WORK_START_HERE.md`
3. `docs/governance/ai-workflow/ai-routing-algorithm.md`
4. `docs/governance/ai-workflow/ai-task-route-table.yaml`

Then identify the task type, target branch, trust zone, expected changed paths, and non-goals.

## 2. Sync safely

Treat live `origin/main` as source of truth for new work.

Before editing, inspect local state and fetch remote state. If local state is dirty, divergent, or ambiguous, stop and report before editing.

Do not reset, rebase, force-push, delete, discard, or overwrite local work unless explicitly instructed.

## 3. Classify the task

Select exactly one primary route from the route table.

Examples:

- staged research addition;
- governance bridge;
- concept promotion;
- source profile cards;
- source registry;
- claim object;
- graph object;
- ingestion pilot;
- validation infrastructure;
- runtime-agent planning;
- chat handoff.

If the task spans multiple routes, choose the highest-risk route or split the work into separate PRs.

## 4. Choose work mode

Modes:

| Mode | Meaning | Default permissions |
|---|---|---|
| Explore | Read-only investigation | read/list/search only |
| Plan | Draft plan, prompt, or PR proposal | read/list/search plus no repo edits unless explicitly requested |
| Edit | Modify repository files inside scope | file edits allowed inside declared paths |
| Execute | Push, merge, deploy, send, delete, or external mutation | explicit authorization and approval required |

Default mode is Explore or Plan unless the task explicitly requests edits.

## 5. Choose tool settings

Use the settings matrix.

Default to:

- conservative permissions;
- internet off;
- reasoning effort based on route risk;
- no side effects unless explicitly authorized.

## 6. Choose route template

Use the route-specific template under `docs/governance/ai-workflow/templates/`.

The template controls mandatory prompt fields, scope, non-goals, validation, and PR language.

## 7. Apply goal-prompt preflight when generating prompts

When the task is to generate a goal prompt, next-agent prompt, handoff prompt,
slash-style command prompt, roadmap prompt, or prompt sequence, follow
`docs/governance/ai-workflow/goal-prompt-premortem-preflight.md`.

The generated prompt must include:

- route and scope preflight;
- premortem before execution;
- red-team before execution;
- fix loop before execution;
- validation and PR/merge policy;
- post-work red-team and fix loop;
- residual-risk reporting.

Slash-style commands such as `/plan`, `/goal`, `/research`, `/review`,
`/red-team`, `/fix-ci`, `/implement`, `/merge`, or `/cleanup` are intent hints.
They do not override repo front doors, route selection, validation, trust zones,
or owner permission.

## 8. Work inside scope

Only modify allowed paths. Do not opportunistically improve unrelated files. If a required change falls outside scope, stop and report or create a follow-up recommendation.

## 9. Validate

Run the repository's relevant validation commands. If a validation command is unclear, inspect workflows before guessing.

If validation fails because of existing unrelated issues, report that clearly and avoid broadening the PR.

## 10. Open PR

Open a PR with the required governance sections.

The PR must state:

- invariant impact;
- trust zones touched;
- provenance notes updated;
- deprecation plan if applicable;
- drift check;
- validation status;
- whether AI routing is affected.

## 11. Report outcome

Report branch, PR number, changed files, validation state, and any follow-up items.

## 12. Check router update impact

Every PR must ask whether it affects AI routing. If yes, update the route table, templates, settings matrix, or AI entry points in the same PR or list a follow-up PR.
