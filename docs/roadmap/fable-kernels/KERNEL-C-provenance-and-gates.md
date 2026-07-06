---
object_type: fable_architecture_kernel
trust_zone: proposed
lifecycle_status: draft
provenance_note: "Created 2026-07-06 by Fable. Kernel for HP4 (evidence and provenance standard) and HP6 (original-language and textual-critical dependency gates)."
reason_for_inclusion: "Define the minimum proof before any theology-lineage object becomes machine-readable at asserted status, and the gates that block promotion on language-sensitive or variant-sensitive claims."
---

# Kernel C — Provenance Standard and Review Gates

Design goal: extend the existing anti-guessing discipline to doctrine-lineage objects with one
reusable provenance block and two promotion-blocking gates. No new philosophy — the Scripture
plane already solved this pattern; this kernel gives it jurisdiction over theology-across-time.

## C1. The provenance block (`doctrine_provenance.v1`)

Required on every `claim`, `doctrine_view`, `assessment`, and `genealogy_edge` at
`proposed_relationship` status or above. Candidates may be sparse; promotion may not.

```yaml
doctrine_provenance:
  source_basis:                 # >=1 entry; each names its rung
    - ref: work/... | scripture:... | instrument/...
      ladder_rung: S0..S7
      citation_locator: ""      # book/chapter/section/column
      citation_mode: quotation | paraphrase | allusion | summary
  claim_role: historical_description | normative_position | comparative_note
  authority_zone: S0..S7        # highest rung actually cited
  tradition_scope: <profile-registry value or orthodox_core-exempt per V-ORTH-2>
  orthodoxy_status: <Kernel B enum>
  orthodoxy_basis_refs: []      # required for orthodox_core and heterodox
  asserted_or_inferred: asserted | inferred
  method: human_authored | ai_staged | derived_from_assessment | crosswalk
  lifecycle_status: draft | proposed | active | deprecated
  review_status: unreviewed | in_review | reviewed
  reviewer_or_owner_decision_ref: null | <ref>
  upstream_deps: []             # object refs this depends on
  known_counterclaims: []       # refs; empty allowed only with review attestation
  contested_status: uncontested | contested | historically_settled_scoped
  original_language_review: not_required | required_pending | complete
  original_language_review_ref: null | <review record>
  textual_critical_review: not_required | required_pending | complete
  textual_critical_review_ref: null | <review record>
  downstream_risk_note: ""
  provenance_note: ""
```

**Promotion ladder** (reuses the anti-guessing edge ladder semantics):

| Status | Entry requirement |
|---|---|
| `retrieval_candidate` | none — machine suggestions land here and stay here |
| `derived_view` | computed only from already-governed objects; labeled |
| `proposed_relationship` | full provenance block present; every basis cited; gates evaluated (may be `required_pending`) |
| `asserted_relationship` | human review recorded; scope checks pass; **both gates `not_required` or `complete`**; validators pass |

**`reviewed_lineage` set (owner decision D9):** the doctrine-plane analog of chunking
reviewed-gold — a small, owner-gated set of exemplar lineage subgraphs (e.g. one pilot slice)
promoted as reference-quality. Same discipline as chunking gold: promotion is explicit,
per-object, owner-authorized, and never generalizes ("this slice is reviewed" never means "the
method is auto-trusted elsewhere").

**AI staging rule:** AI-produced objects always enter as `method: ai_staged`,
`asserted_or_inferred: inferred`, `review_status: unreviewed`, at candidate or proposed status.
No projection policy exists in this plane yet; the Scripture repo's owner-projection pattern is
**not** inherited (owner decision required before any analog is created here).

## C2. Original-language gate (HP6)

**Trigger registry** — `original_language_review: required_pending` is forced when a claim or
edge materially hinges on:

- a specific lemma, term, or grammatical construction (the classic list: homoousios vs
  homoiousios, hypostasis/persona, monogenēs, theotokos, physis/natura,
  sacramentum/mystērion, dikaioō, presbyteros/episkopos …);
- a translation-polemic passage — by reference to the Scripture repo's
  orthodox original-language pressure dossier queue
  (`logos-scripture-graph:.ai/control/orthodox_original_language_pressure_dossier_queue.yaml`);
- an argument from word rarity, root, article, tense, or word order.

**Completion requires** a human review record naming: reviewer role
(original-language reviewer), the term in phrase/clause/discourse/genre/canonical context, and
compliance with the Scripture repo's original-language phrase/context policy
(`logos-scripture-graph:.ai/control/original_language_phrase_context_policy.yaml`) — referenced,
not forked. Governance owns the pointer; the policy text stays where it lives. An isolated
lemma, gloss, Strong's tag, or AI parse never satisfies the gate (root-fallacy,
semantic-range-transfer, and interlinear-gloss guards apply here with full force).

## C3. Textual-critical gate (HP6)

`textual_critical_review: required_pending` is forced when a claim's basis passage appears in
the Scripture repo's textual-variant/source-tradition dossier queue
(`logos-scripture-graph:.ai/control/textual_variant_source_tradition_dossier_queue.yaml`) or the
claim itself argues from a disputed reading (Comma Johanneum is the canonical example: any
Trinity-lineage claim resting on 1 John 5:7 is structurally blocked until the gate records the
variant status — which will, correctly, prevent that verse from ever silently grounding an
`orthodox_core` classification).

Completion follows the already-selected case-by-case owner policy pattern (`TCP-T378-B`
lineage): exact variants named, dependency or non-dependency recorded, owner confirmation where
the Scripture repo's policy requires it. The gate never selects a preferred reading and never
creates source-tradition preference — it only records whether the doctrine claim *depends* on
one.

## C4. Validators (Codex implements)

| ID | Rule |
|---|---|
| V-PROV-1 | Promotion to `proposed_relationship`+ with any missing required field fails. |
| V-PROV-2 | `asserted_relationship` with either gate at `required_pending` fails. |
| V-PROV-3 | `authority_zone` must equal the max rung present in `source_basis` (no inflation). |
| V-PROV-4 | `method: ai_staged` + `review_status: unreviewed` above proposed status fails. |
| V-PROV-5 | Empty `known_counterclaims` at asserted status requires reviewer attestation flag. |
| V-GATE-1 | Trigger-registry passages/terms force `required_pending` mechanically (list-driven). |

## C5. Stop rules

Stop and report if a task would: promote with an open gate; satisfy a gate with AI-generated
language analysis; fork (rather than reference) the Scripture repo's language or
textual-critical policies; treat gate completion as a preferred-reading or source-tradition
decision; or create a `reviewed_lineage` entry without an explicit owner promotion record.
