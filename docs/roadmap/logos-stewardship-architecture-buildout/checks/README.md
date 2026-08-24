---
object_type: stewardship_campaign_validation_runbook
trust_zone: proposed
lifecycle_status: active
provenance_note: "Created on 2026-08-23 by Codex root to define deterministic and independent checks for the campaign specification; revised on 2026-08-24 to distinguish the frozen V1 checkpoint replay from current V2 release gates."
reason_for_inclusion: "Tell future maintainers which revision each validator governs without confusing historical replay, current static validation, or runtime qualification."
---

# Validation Runbook

## Current Doctrine Mesh V2 and portfolio gates

The current public release candidate is governed by the revision-specific V2
validator and tests plus the portfolio and repository-wide gates:

```powershell
python docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/checks/validate_doctrine_mesh.py --mode final
python docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2/checks/test_validate_doctrine_mesh.py
python scripts/validate_portfolio_front_door.py
python scripts/run_validation_suite.py
python -m pytest -q
```

The release receipt records the exact results, bounded limitations, candidate
fingerprint, and independent review. These static gates do not activate the
mesh, ingest sources, implement doctrine, or grant theological authority.

## Historical V1 checkpoint replay

The command below is the frozen V1 campaign validator. Its passing receipt binds
the exact staged candidate validated while repository `HEAD` was
`9a8a0dd4e9c07040d23ceeb3bf1bf10003d45ee4`; those staged bytes were then
committed as artifact commit `410c7e429290d34013c1dbf23c0335ebfe68e45f`.
An ordinary checkout of either commit is not an exact replay: the earlier tree
lacks the candidate files, while the later checkout has a different `HEAD`.
Consult `validation-receipt.json` and `final-independent-review.json` for the
recorded historical result. An exact forensic replay would require a separately
authorized disposable workspace with the artifact tree staged over the locked
parent without moving `HEAD`. This command is not a current V2 or portfolio
release gate:

From the repository root, run:

```powershell
python docs/roadmap/logos-stewardship-architecture-buildout/checks/validate_stewardship_campaign.py
```

At the V1 checkpoint, also run the then-recorded
`orchestrate-long-run-campaigns` static validator
against `campaign.json` and the current installed task-local mesh validator
against `mesh/agent-mesh.v1.json`. The exact tool revisions belong in the
validation receipt; host-specific paths do not belong in repository files.

Replaying this V1 command on the expanded V2/portfolio working tree is expected
to report four changed-revision failures, not a V2 validation result:

- `governed-metadata`: the V1 scanner recursively encounters V2 metadata shapes;
- `source-lock-replay`: the V1 source lock predates current navigation and registry changes;
- `family-claim`: the V1 assertion encodes its historical claim shape and status;
- `scope-privacy-and-hygiene`: the V1 scope/parser contract predates the public-release surface.

Required checks:

- source SHA-256 and Git-blob replay;
- exact seven advisory hashes and 2/10/5/SPECIAL exclusion replay;
- no cleared implementation or human gate;
- JSON/YAML parsing and required metadata;
- campaign and role dependency acyclicity;
- one writer, distinct checker, depth-one delegation, and valid job-role bindings;
- typed graph endpoints, no load-bearing catch-all edge, and reverse provenance path;
- disjoint write paths and controller-state separation;
- provider-neutral core and unbound runtime adapter;
- dormant migration and implementation gates;
- no absolute workstation path, secret, private payload, or hidden authority claim;
- `git diff --check` and exact claimed-path scope.

A passing result means only that the selected static specification satisfied
the checks for its recorded revision. It does not qualify a controller, approve
a human gate, authorize research access, or permit implementation or
publication.
