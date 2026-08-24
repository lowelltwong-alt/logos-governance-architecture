---
object_type: stewardship_campaign_controller_state_boundary
trust_zone: proposed
lifecycle_status: inactive
provenance_note: "Created on 2026-08-23 by Codex root to reserve and explain the controller-owned state boundary without creating runtime state."
reason_for_inclusion: "Make it explicit that workers cannot edit controller state and that no lease, receipt log, or execution state currently exists."
---

# Controller State Boundary

This directory is intentionally empty of runtime state. No controller is
selected or qualified, no launch is authorized, and no receipt log or lease is
active.

If a later exact campaign revision is authorized for a qualified dry run, only
the selected controller may create append-only state here. Workers may submit
evidence but may not edit controller state. Repository content, source records,
and human approval receipts must never be fabricated in this directory.
