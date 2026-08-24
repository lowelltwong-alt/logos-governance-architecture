---
object_type: stewardship_campaign_validation_runbook
trust_zone: proposed
lifecycle_status: active
provenance_note: "Created on 2026-08-23 by Codex root to define deterministic and independent checks for the campaign specification."
reason_for_inclusion: "Tell future maintainers how to validate structure and authority without confusing static validation with runtime qualification."
---

# Validation Runbook

From the repository root, run:

```powershell
python docs/roadmap/logos-stewardship-architecture-buildout/checks/validate_stewardship_campaign.py
```

Also run the current installed `orchestrate-long-run-campaigns` static validator
against `campaign.json` and the current installed task-local mesh validator
against `mesh/agent-mesh.v1.json`. The exact tool revisions belong in the
validation receipt; host-specific paths do not belong in repository files.

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

A passing result means only that the static specification satisfied the checked
contract at the recorded revision. It does not qualify a controller, approve a
human gate, authorize research access, or permit implementation or publication.
