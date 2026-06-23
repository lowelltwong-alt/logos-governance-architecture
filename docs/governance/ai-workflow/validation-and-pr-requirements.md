---
object_type: governance_reference
trust_zone: governance_instructions
lifecycle_status: draft
review_status: unreviewed
ai_usage_posture: mandatory_pr_guidance
provenance_note: "Created 2026-04-30 to define validation and PR requirements for AI-assisted work. Updated 2026-06-23 to require premortem/red-team disclosure for generated goal prompts."
reason_for_inclusion: "Define required validation posture, PR governance sections, AI routing impact disclosure, prompt-generation preflight disclosure, and merge discipline for AI-assisted repository changes."
---

# Validation and PR Requirements

## Validation rule

Every AI-assisted PR must run the relevant repo validation commands before merge.

If the correct validation commands are unclear, inspect `.github/workflows/` and existing scripts before guessing.

## Minimum validation posture

At minimum, try to satisfy:

- markdown link/lint checks;
- metadata schema validation;
- trust-zone policy validation;
- cross-reference validation;
- structure validation;
- route-specific schema checks when applicable.

## PR description requirements

Every AI-assisted PR should include:

- Governance change summary;
- Invariant impact statement;
- Trust zone declaration;
- Provenance note update;
- Deprecation plan, if applicable;
- Drift check;
- Old rule preserved;
- Intentional change;
- Unchanged surface;
- Validation;
- AI routing impact answer.
- Prompt-generation impact answer when the PR changes AI prompts, templates,
  routing, slash-style command handling, handoff instructions, or next-agent
  goal prompts.

## AI routing impact answer

Every PR should answer:

Does this PR affect AI work routing?

- No.
- Yes, updated AI_WORK_START_HERE.md, route table, settings matrix, or templates.
- Yes, follow-up PR required and listed.

## Prompt-generation impact answer

When a PR changes prompt workflows, generated prompts, handoff instructions,
slash-style command handling, or next-agent goal prompts, answer:

Does this PR preserve the goal-prompt premortem preflight?

- No prompt-generation impact.
- Yes, premortem/red-team/fix-loop language is present or strengthened.
- Follow-up required, with the missing prompt-generation surface named.

## Validation reporting

The final PR comment or PR body should state:

- validations run;
- validations passed;
- validations skipped and why;
- known failures and whether they are pre-existing or introduced by the PR.

## Scope discipline

If validation fails because of unrelated existing issues, do not broaden the PR. Report the failure and recommend a follow-up.

## Merge discipline

Do not merge until relevant checks pass or the user explicitly accepts the known failure risk.
