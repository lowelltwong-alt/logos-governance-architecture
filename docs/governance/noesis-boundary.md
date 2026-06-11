---
object_type: governance_boundary_policy
trust_zone: canonical
lifecycle_status: active
provenance_note: "Created 2026-05-27 to make the Noesis-cannot-govern-Logos invariant explicit and machine-enforced on the Logos side, complementing the Noesis-side LOGOS_COMPATIBILITY contract."
reason_for_inclusion: "Authority direction between Noesis and Logos must be a hard, checkable invariant, not an implicit convention that holds only because no cross-reference happens to exist yet."
---

# Noesis Boundary Policy (Logos side)

## The invariant

> Noesis may inform Logos. Noesis may never govern Logos.

Information may flow `Noesis -> Logos` only as **advisory, non-authoritative comparison data** that Logos re-evaluates under its own theological authority. **Governance and authority never flow `Noesis -> Logos` in any form.**

Noesis Atlas classifies worldviews, authority structures, and truth modes across many traditions. Logos is a specifically Christian theological architecture. The two are separate repositories that may interact, but their authority relationship is strictly one-directional and asymmetric.

## What this forbids

A Logos artifact must never:

- treat a Noesis object as the **authority, source, or derivation basis** of any Logos doctrine, claim, ordering, weighting, or governance rule;
- import a Noesis classification, coherence score, or branch ruling as if it settled a Christian theological question;
- let a Noesis profile, registry, lifecycle state, or constitutional rule override, gate, promote, demote, or veto any Logos artifact;
- depend (in any governed trust zone) on a Noesis file being present, valid, or approved.

In short: nothing in Logos's authority chain may trace back to Noesis.

## What this permits

Logos may, under Logos review, *read* reviewed Noesis exports as **external comparison material** — for contrast, public-reason bridging, or mapping how another worldview frames a question. Such material:

- must be confined to a non-canonical trust zone (`proposed`, `inferred`, or a dedicated advisory lane) and never `canonical` or `tradition-scoped`;
- must be tagged explicitly as external (see "Advisory reference field" below);
- must never appear in an authority or derivation field;
- carries no binding force; Logos reaches its own conclusion under its own authority.

## Allowed connection shape

Noesis may connect to Logos repos only through reviewed, read-only advisory
comparison surfaces. A Noesis connector or export must not write to, modify,
gate, promote, demote, approve, or govern `logos-governance-architecture`,
`logos-scripture-graph`, or `logos-boundary-literature`.

Connections may carry comparison context. They must not carry authority.

## Comment and paste backdoor

Noesis may connect only through reviewed, read-only, advisory comparison
references. Noesis may not modify, gate, govern, promote, demote, derive, or
indirectly authorize any Logos change through comments, PR reviews, issues,
handoffs, task files, generated notes, hidden advisory text, or pasted
rationale.

Noesis-origin analysis pasted into a Logos PR, issue, review comment, chat
transcript, handoff, generated note, copied summary, task note, or committed
file remains external advisory material. It must be quarantined, labeled
non-authoritative, marked advisory only, and re-authored as a Logos-native task
with explicit owner authorization in the appropriate Logos repo before it may
affect canonical Scripture, chunking, claims, routes, evaluators, retrieval
defaults, governance, or source scope.

## Authority direction (one line)

`Noesis (classify) -> reviewed export -> Logos-side review -> Logos (decide under Christian authority)`

There is no return arrow on authority. Logos owes Noesis no deference.

## Advisory reference field

If and when Logos ever needs to cite Noesis comparison material, it goes in an explicitly external field and nowhere else:

```yaml
external_advisory_refs:        # advisory only; never authority/derivation
  - noesis:branch.<id>:<object>
```

Authority/derivation fields — `subject`, `object` (under authority predicates such as `grounds`, `derived_from`, `constrains`, `anchors`), `lineage`, `source_basis`, and node frontmatter `parents`/`source`/`authority`/`derived_from` — must never contain a Noesis-namespaced reference.

## Enforcement

`scripts/validate_noesis_boundary.py` is a tripwire validator. Today Logos contains zero references to Noesis, so it passes trivially. It exists so that the first time anyone wires a Noesis reference into a Logos authority or derivation field — or into a canonical/tradition-scoped artifact at all — the build fails. Run it locally and in CI alongside the other structure validators.

## Relationship to the Noesis-side contract

This policy is the Logos-side mirror of Noesis's `LOGOS_COMPATIBILITY.md`. The two are intentionally redundant: each repository enforces the boundary from its own side so the guarantee does not depend on the other repository behaving correctly.
