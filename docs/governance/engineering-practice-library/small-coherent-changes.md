---
object_type: engineering_practice_card
trust_zone: proposed
lifecycle_status: active
provenance_note: "Created 2026-07-10 from EPR-006 and its primary source record."
reason_for_inclusion: "Teach how change size affects reviewability without encouraging unsafe fragmentation."
---

# Small Coherent Changes

**Problem:** Large mixed pull requests hide defects, couple unrelated work, and
make rollback difficult.

**Professional pattern:** Make one self-contained, reviewable change at a time.

**Logos adaptation:** A small change still includes every companion schema,
validator, decision register, lesson, handoff, and migration surface needed to keep
its invariant true. Do not split an atomic safety contract merely to reduce line
count.

**Evidence:** `EPS-GOOGLE-002`; recommendation `EPR-006`.

