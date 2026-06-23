---
object_type: governance_process
trust_zone: governance_instructions
lifecycle_status: draft
review_status: unreviewed
ai_usage_posture: mandatory_prompt_preflight
provenance_note: "Created 2026-06-23 after maintainer instruction to require premortem, red-team, and fix-loop blocks in generated goal prompts."
reason_for_inclusion: "Make goal-prompt generation deterministic so AI agents do not create optimistic, underspecified, route-ambiguous, or slash-command-confused prompts."
---

# Goal Prompt Premortem Preflight

This file governs any AI-assisted drafting of a goal prompt, handoff prompt,
slash-command prompt, roadmap prompt, PR work prompt, or next-agent prompt in
the Logos repository family.

## Research anchors

This preflight uses these stable source anchors:

- Gary Klein's project premortem pattern: imagine that the project has already
  failed, then generate plausible reasons for the failure before work begins.
  Source: https://hbr.org/2007/09/performing-a-project-premortem
- Atlassian's premortem play: identify risks and opportunities before starting,
  customize questions to expose what stakeholders are nervous about, and assign
  actions before execution. Source:
  https://www.atlassian.com/team-playbook/plays/pre-mortem
- NIST generative AI risk guidance: AI red-teaming is a structured probing
  exercise used to find flaws and vulnerabilities. Source:
  https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
- OWASP LLM guidance: prompt injection can alter model behavior or output in
  unintended ways, so prompts that create agents, ingestion, retrieval, or
  external-tool work must include adversarial review. Source:
  https://genai.owasp.org/llmrisk/llm01-prompt-injection/

## Mandatory sequence

Every generated goal prompt must include this sequence in order:

1. **Route and scope preflight.**
   - Identify target repo, live-main status, work mode, route-table route,
     allowed paths, forbidden paths, side-effect level, validation commands,
     PR/merge permission, and non-goals.

2. **Premortem before implementation.**
   - Imagine the work is finished and failed.
   - List plausible failure modes before execution.
   - Include governance failure, source failure, validation failure, merge
     failure, scope creep, authority leak, and stale-branch failure where
     relevant.

3. **Red-team pass before implementation.**
   - Attack the plan as if trying to make it overclaim, contaminate trust
     zones, import protected material, bypass source rules, misuse a slash
     command, or pass tests while still being wrong.
   - For AI, retrieval, graph, vector, source ingestion, or prompt work, include
     prompt-injection, source-poisoning, hidden-instruction, and tool-side-effect
     checks.

4. **Fix loop before execution.**
   - Convert each P0/P1 risk into a concrete prevention, validator, stop
     condition, or owner-decision requirement.
   - If a P0 risk has no prevention, the generated goal prompt must block the
     work or reduce scope.

5. **Implementation and validation.**
   - Run the scoped work.
   - Run route-appropriate validation.
   - Do not treat passing tests as authority if source, provenance, trust zone,
     or owner scope is missing.

6. **Post-work red-team and fix loop.**
   - Re-run a smaller red-team after implementation.
   - Fix discovered issues before final PR/merge recommendation.
   - Report residual risks explicitly.

## Required block for goal prompts

Any prompt generated for a future agent must include a block equivalent to:

```text
Premortem/red-team requirement:
- Before editing, run a premortem: assume this task failed after merge and list
  the most plausible causes.
- Run a red-team pass against the plan: look for authority leaks, source
  weakness, trust-zone contamination, stale-branch risk, validation blind spots,
  prompt-injection or hidden-instruction risk, overbroad scope, and merge/PR
  hazards.
- Fix loop: for each P0/P1 risk, add a prevention, validator, stop condition,
  or owner-decision requirement before implementation.
- After implementation, run a post-work red-team and fix any concrete issue
  before PR/merge.
```

## Slash-style intent routing

Slash-style prefixes in chat are intent hints, not authority overrides. They do
not bypass AGENTS.md, AI_WORK_START_HERE.md, route selection, live-main sync,
trust zones, validation, or owner permission.

| Slash-style intent | Default mode | Required interpretation |
|---|---|---|
| `/plan` | Plan | Produce a plan or prompt. No repository edits unless the user also asks to implement. Include premortem, red-team, and fix-loop requirements if the plan becomes a goal prompt. |
| `/goal` | Plan | Generate a goal prompt or goal sequence. Must include route/scope preflight, premortem, red-team, fix loop, validation, PR policy, and next-agent handoff language. |
| `/research` | Explore/Plan | Gather source anchors, separate confirmed facts from candidate claims, and define what would block later implementation. Use internet when current/source verification is needed. |
| `/review` | Review | Use review posture: findings first, severity ordered, file/line grounded, with tests and residual risks. Do not rewrite unless asked. |
| `/red-team` | Review | Attack an existing plan, prompt, branch, PR, or architecture. Produce failure modes and fixes; edit only when explicitly asked to fix. |
| `/premortem` | Plan/Review | Assume failure after completion, name plausible causes, and produce preventive changes. Pair with red-team before execution. |
| `/fix` | Edit | Fix a scoped issue. Read context first, keep edits minimal, run validation, and include a post-fix red-team for high-risk surfaces. |
| `/fix-ci` | Edit/Review | Inspect CI logs, identify root cause, fix only the failing scope, rerun relevant checks, and update the PR. |
| `/implement` | Edit | Execute the already-scoped plan. If the plan lacks premortem/red-team/fix-loop language, add that preflight before editing. |
| `/merge` | Execute | Requires explicit owner authorization, clean branch state, live checks, PR review status, and no unresolved P0/P1 premortem or red-team findings. |
| `/cleanup` | Edit/Execute | Use branch/repo cleanup runbooks. Preserve valuable work before deletion. Destructive cleanup requires explicit authorization. |

If an unfamiliar slash-style command appears, infer only the safest work mode,
state the inferred meaning, and ask or stop if the command would authorize
side effects, deletion, merge, publication, source ingestion, or trust-zone
promotion.

## Deterministic prompt-generation checklist

Before returning any generated goal prompt, verify:

- Target repo and branch strategy are explicit.
- Route-table route and work mode are explicit.
- Allowed paths and forbidden actions are explicit.
- Source policy and trust-zone policy are explicit.
- Premortem block is present.
- Red-team block is present.
- Fix loop is present.
- Validation commands or validation-discovery instructions are present.
- PR/merge permission is explicit.
- Stale-branch, dirty-worktree, and parallel-agent coordination are covered.
- Slash-style command meaning is either explicit or safely inferred.

## Stop rules

Stop and report instead of generating an execution prompt when:

- the requested goal would change governance, Scripture authority, trust-zone
  hierarchy, repository routing, or canon scope without explicit owner
  authorization;
- the prompt would import source text, protected text, private prompts, or
  unreviewed external material outside a governed source policy;
- slash-style intent conflicts with repo front-door instructions;
- the requested prompt cannot name validations or a route-table route;
- a P0 premortem or red-team risk has no prevention, validator, stop condition,
  or owner-decision gate.
