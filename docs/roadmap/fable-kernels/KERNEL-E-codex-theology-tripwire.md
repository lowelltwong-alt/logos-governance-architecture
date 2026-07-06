---
object_type: fable_architecture_kernel
trust_zone: proposed
lifecycle_status: draft
provenance_note: "Created 2026-07-06 by Fable during the follow-up gap pass, after owner selections FABLE-D1-D10-2026-07-06 were recorded and the kernel packet merged (PR #71)."
reason_for_inclusion: "Codex must implement schemas, validators, seeds, and examples that contain theological terms without ever making a theological judgment; the boundary between transcription and decision needs a mechanical test, not vigilance."
---

# Kernel E — Codex Theology Tripwire

## Problem

PRs 2–8 require Codex to write files full of theological vocabulary: enum values, seed
entities, the Chalcedon exemplar, validator messages. The failure mode is silent theology —
an enum default, an example classification, or an error-message phrasing that asserts a
doctrinal position nobody decided. Stop rules alone don't catch this because Codex won't
recognize the judgment *as* a judgment.

## Why it is hard

"Transcribe the recorded decision" and "decide theology" look identical at implementation
time. Classifying miaphysitism as `heterodox` relative to the project boundary is legal
transcription (it follows mechanically from D1 + Kernel B2); classifying Apollinarianism the
same way — not named in any decided surface — would be Codex doing theology, even though both
feel equally "obvious."

## The mechanical test

A Codex action is theology, and must stop, **iff** it would assign any of:

- `orthodoxy_status` other than `unclassified_candidate`
- `ladder_rung`, `tradition_scope`, `verdict`, or `claim_role: normative_position`
- a relationship verb chosen between plausible candidates

…to a **real** historical entity, text, or view **without a citable determinative basis** in:
Kernels A–D, decision record `FABLE-D1-D10-2026-07-06`, or a later explicit owner record.

Derivable-by-citation is allowed and required to show its work: the value plus a
`decision_basis:` field citing the exact kernel section or decision ID that determines it.
No citation ⇒ use the ladder floor (`unclassified_candidate` / `historical_description` /
`retrieval_candidate`) or stop and ask.

## Rules

1. **Citation rule:** every non-floor classification value in any example, seed, or test
   fixture carries `decision_basis`. (The PR-5 Chalcedon exemplar cites D1/D2/Kernel B for
   every status it assigns.)
2. **Floor-only defaults:** schema defaults may only be the lowest rung of each ladder
   (`unclassified_candidate`, `historical_description`, `retrieval_candidate`,
   `review_status: unreviewed`). No schema default may encode a theological position.
3. **Neutral validator voice:** error messages state rule violations, never doctrine —
   "`orthodox_core` requires a cited S1 basis (V-ORTH-1)", never "this view is heretical."
4. **Invented fixtures:** test fixtures use invented placeholder entities (the boundary repo's
   existing convention), except the PR-5 exemplar, which exists precisely to test the citation
   rule on real material.
5. **Seed scope:** seed data (entity registry, vocab docs) is limited to entities and values
   named in Kernels A–D or D1–D10, identity fields only.

## Validators / audit surfaces

- **V-CODEX-1** (add to PR-4): lint examples/seeds — any non-floor classification field
  without `decision_basis` fails.
- **Audit surface:** every PR in the 2–8 queue lists, in its description, each theological
  term/value it introduces and its basis citation (extends the GD-014 impact-statement
  pattern).

## Stop rules

Stop and ask the owner if a task needs: a new enum value; a classification with no citable
basis; a choice between relationship verbs on real material; or original wording of any
doctrinal statement not quoted from a decided surface.

## Codex handoff tasks

1. PR-4: implement V-CODEX-1.
2. PR-2/PR-5: apply the citation rule to all seeds and the exemplar.
3. PRs 2–8: add the "theological terms introduced + basis" section to each PR report.
