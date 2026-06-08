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
8. Link child-repo issues back to the governance registration issue.

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

## Planned Repos

Planned repos may appear in the registry with `status: planned_not_created`.
That status does not create the repo, authorize source text ingestion, or
authorize runtime integration.

Creating a planned repo requires a new issue and scaffold PR.

## AI Rule

If an AI cannot determine which repo owns the task, it must stop and report the
missing routing information. It must not guess by moving data across repos.
