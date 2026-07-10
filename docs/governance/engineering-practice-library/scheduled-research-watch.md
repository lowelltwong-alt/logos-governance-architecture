---
object_type: engineering_practice_card
trust_zone: proposed
lifecycle_status: active
provenance_note: "Created 2026-07-10 from EPR-005 and GitHub scheduling documentation."
reason_for_inclusion: "Teach why recurring work needs redundant triggers, visible overdue state, and proof of completion."
---

# Scheduled Research Watch

**Problem:** Humans forget recurring research, and automation schedules can be
delayed, disabled, or mistaken for completed work.

**Professional pattern:** Combine event triggers, a scheduled check, manual
dispatch, and an overdue queue. Schedule away from the top of the hour.

**Logos adaptation:** Pull requests receive a cheap sentinel. GitHub runs the due
check Monday at minute 17. A weekly Codex automation performs actual primary-source
research. Monthly and quarterly work is selected from explicit due dates. No clock
may automatically adopt a recommendation.

**Evidence:** `EPS-GITHUB-001`, `EPS-GITHUB-002`; recommendation `EPR-005`.

