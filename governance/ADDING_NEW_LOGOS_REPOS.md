---
object_type: logos_repo_registration_process
trust_zone: governance_instructions
lifecycle_status: active
provenance_note: "Created 2026-06-08 to define the issue-based process for adding future Logos repos."
reason_for_inclusion: "Make repo onboarding intentional, reviewable, and tied to registry updates."
---

# Adding New Logos Repos

No new repository is part of the Logos project family until it has a registration
issue and a registry entry in `logos-governance-architecture`.

## Required Process

1. Open a repository registration issue using
   `.github/ISSUE_TEMPLATE/register_new_logos_repo.yml`.
2. Identify the proposed repo role, authority level, owned data, forbidden data,
   upstream governance repo, downstream supported repos, and validation commands.
3. Review contamination, source, trust, security, and authority-direction risks.
4. Add or update `governance/LOGOS_REPO_REGISTRY.yaml` in this repo.
5. Add the child repo scaffold only after the registry entry is accepted.
6. Ensure the child repo has an `AI_FRONT_DOOR.md`.
7. Ensure the child repo has a table of contents, data map, or documented
   exception.
8. Ensure any repo that touches source, tradition, denomination, or profile data
   has source-trust rules, scope rules, and validation commands before adding
   real corpus or lineage records.
9. Ensure any repo that touches chunking, vector indexes, retrieval
   neighborhoods, graph edge generation, or doctrine-lineage links has
   anti-guessing and evidence-discipline rules before generated structure is
   treated as governed.
10. Link child-repo issues back to the governance registration issue.

## Relationship Updates

Any repo relationship change requires an issue using
`.github/ISSUE_TEMPLATE/update_repo_relationship.yml`.

Relationship changes include:

- authority direction changes;
- data-flow direction changes;
- routing changes;
- new cross-repo references;
- new adapters or promotion gates;
- any change that could affect contamination controls.

## Boundary-Originated Requests

A boundary-originated request may not become an automated permission request,
automated approval route, bundled governance change, or direct edit to a
higher-authority repo.

If boundary/reception/noncanonical work conflicts with governance policy, the
agent must stop and produce the human-readable warning required by
[`BOUNDARY_GOVERNANCE_CONSTRAINTS.md`](BOUNDARY_GOVERNANCE_CONSTRAINTS.md).

Only Lowell Wong, as project owner, may authorize a boundary-originated request
to change higher-authority governance, canonical Scripture authority,
repository-link contracts, canonical scope, trust hierarchy, or cross-repo
policy. Contributor consensus, contributor volume, automated recommendation,
agent routing, or boundary-layer operational need is not sufficient authority.

## Planned Repos

Planned repos may appear in the registry with `status: planned_not_created`.
That status does not create the repo, authorize source text ingestion, or
authorize runtime integration.

Creating a planned repo requires a new issue and scaffold PR.

Do not create `logos-chunking-harness` or `logos-doctrine-genealogy` directly
from chat or local convenience. The scaffold PR must preserve the planned repo's
authority limits from `LOGOS_REPO_REGISTRY.yaml` before any implementation,
runtime adapter, source import, commentary corpus, or doctrine-lineage data is
added.

For planned repos that will generate chunks, vectors, retrieval neighborhoods,
or graph candidates, the scaffold must also preserve the anti-guessing rule:
semantic similarity, embedding closeness, generated confidence, and graph rank
may create candidates, but not authority.

## Readiness Threshold

A planned repo is no longer premature only when its first concrete task cannot
be safely handled by an existing active repo. The registration issue must name
the first task, owned data, forbidden data, upstream governance, downstream
consumers, authority level, source/trust risks, and validation commands.
If the repo touches chunking, vectorizing, retrieval, or graph edges, it must
also name the anti-guessing controls and what validator would fail if generated
structure were promoted without evidence.

For `logos-doctrine-genealogy`, the threshold is met only when doctrine lineage,
denomination/profile comparison, or theologian-to-theologian development needs
records that would distort either `logos-governance-architecture` or
`logos-boundary-literature`.

For `logos-chunking-harness`, the threshold is met only when cross-corpus
execution/evaluation needs runtime or adapter behavior that would distort
`logos-scripture-graph`, `logos-boundary-literature`, or
`logos-doctrine-genealogy`. Semantic search, embeddings, or graph ideas alone
are not enough; the first task must need separate source-mode adapters,
namespace separation, anti-guessing controls, and validation commands.

## AI Rule

If an AI cannot determine which repo owns the task, it must stop and report the
missing routing information. It must not guess by moving data across repos.

If an AI cannot name the source basis, authority owner, scope, method, review
status, and provenance for a chunk, vector-derived neighborhood, graph edge, or
doctrine-lineage link, it must keep the output as a candidate or stop and
report the missing evidence. It must not promote generated structure by vibes.
