---
object_type: governance_standard
trust_zone: canonical
lifecycle_status: active
review_status: owner_authorized
ai_usage_posture: non_authorizing_adapter_qualification
provenance_note: "Created 2026-07-10 under AGENT-W7-A."
reason_for_inclusion: "Specify how adapter evidence is collected and how missing evidence remains visibly unqualified."
---

# Adapter Qualification Fixtures

The fixture pack and current register are canonical controls:

- [`agent_qualification_fixture_manifest.yaml`](../../../governance/registry/agent_qualification_fixture_manifest.yaml)
- [`current_adapter_qualification_register.yaml`](../../../governance/registry/current_adapter_qualification_register.yaml)

## Qualification Rule

Every adapter must run the whole fixed fixture pack under a captured, auditable
runtime before it may receive a durable role assignment. Record total cost,
elapsed time, defects, escalation quality, completed fixture IDs, and an expiry
date. A result expires after the register's stated window; expired and missing
evidence are both unqualified.

The current records intentionally contain `not_run`, null metrics, no eligible
work classes, and no specialist-domain eligibility. This workspace can validate
the fixture pack but cannot call the Sol, Terra, Luna, low, high, or ultra
adapters. Null does not mean zero cost or zero defects. It means no evidence was
captured.

## Running The Structural Pack

Run `python scripts/run_agent_qualification_fixtures.py` to validate the fixed,
source-safe pack and the current no-evidence posture. This is not a model run.

When a callable adapter exists, the execution environment must capture the raw
fixture inputs and outputs outside canonical governance content, then update the
register through a separately reviewed PR. It must not use Scripture, licensed
sources, doctrine records, or real source imports as qualification material.

## Stop Rules

- A model/effort name is never qualification evidence.
- A passing software fixture does not establish Greek, Hebrew/Aramaic, textual
  criticism, archaeology/history, theology/hermeneutics, or architecture
  qualification.
- An implementer cannot self-certify an independent review fixture.
- A qualification result cannot satisfy a human or owner gate.
- Failed, expired, incomplete, or unavailable runs leave the adapter ineligible.
