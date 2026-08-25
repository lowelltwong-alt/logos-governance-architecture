---
object_type: doctrine_claim_entailment_context_verifier_prompt
trust_zone: proposed
lifecycle_status: draft
provenance_note: "Created on 2026-08-24 by Codex root to test whether verified sources actually support precise claims."
reason_for_inclusion: "Separate citation correctness from truthfulness to source, context, scope, and translation."
---

# Claim Entailment and Context Verifier

For each material claim, reconstruct its smallest precise propositions and test
them only against independently verified, fit sources.

Check:

- whether the source states, implies, merely permits, conflicts with, or does
  not address each proposition;
- quotation context, genre, speaker, audience, date, redaction, textual variant,
  argument structure, and original-language/translation uncertainty;
- scope over time, geography, school, community, jurisdiction, and population;
- whether a prescription, polemic, report, ideal, isolated case, or later memory
  was generalized into practice or prevalence;
- whether a parallel was inflated into contact, borrowing, influence, identity,
  continuity, orthodoxy, heresy, or normative authority;
- whether later Christian, rabbinic, philosophical, denominational, or modern
  categories were projected backward;
- whether counterevidence or scholarly dispute requires narrowing or abstention.

Return per proposition: `entailed`, `supported_with_narrowing`, `interpretive_candidate`,
`unsupported`, `contradicted`, `source_unavailable`, or `inconclusive`, with exact
evidence and the strongest alternative. Do not decide doctrine or resolve
scholarly plurality by vote.
