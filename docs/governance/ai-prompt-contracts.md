---
id: "gov.ai_prompt_contracts"
anchor: "governance.ai_prompt_contracts"
title: "AI Prompt Contracts"
node_type: "governance_contract_catalog"
status: "active"
review_status: "approved"
address: "docs/governance/ai-prompt-contracts.md"
trust_zone: "canonical"
lifecycle_state: "active"
ai_usage_posture: "human_review_required"
object_type: "prompt_contract_catalog"
provenance_note: "Created on 2026-04-08 as controlled task contracts for AI-assisted ontology operations. Updated 2026-06-23 to require premortem, red-team, and fix-loop language when task contracts are turned into generated goal prompts."
reason_for_inclusion: "Standardize prompts so common automation tasks remain bounded, reviewable, promotion-safe, and protected against optimistic goal prompts."
---


# AI Prompt Contracts

## Global contract clauses

All task prompts should include:
- operation_class: suggest | draft | normalize
- trust_zone_output: proposed | inferred | learning-sidecar (never canonical by default)
- promotion_policy: "never promote without explicit human review"
- provenance_note
- reason_for_inclusion
- route_and_scope_preflight
- premortem: "assume the work failed after merge and list plausible causes"
- red_team: "attack the plan for authority leaks, source weakness, trust-zone contamination, prompt-injection risk, validation blind spots, and stale-branch/PR hazards"
- fix_loop: "convert each P0/P1 risk into a prevention, validator, stop condition, or owner-decision gate"

Generated goal prompts and prompt sequences must follow
[`docs/governance/ai-workflow/goal-prompt-premortem-preflight.md`](ai-workflow/goal-prompt-premortem-preflight.md).

---

## Contract: node creation (draft)

**Intent:** Create a draft node in quarantine.

**Required input fields:**
- node_type
- candidate_label
- parent_context
- trust_zone_output
- source_references

**Required output fields:**
- draft_node_id
- draft_anchor
- metadata (object_type, trust_zone, lifecycle_status, provenance_note, reason_for_inclusion)
- reviewer_required: true

**Hard constraints:**
- do not overwrite canonical nodes
- do not assign canonical trust zone
- preserve doctrine topic/view/assessment separation

---

## Contract: edge suggestion (suggest)

**Intent:** Suggest candidate edges for reviewer triage.

**Required input fields:**
- source_node
- candidate_targets
- allowed_relationship_verbs

**Required output fields:**
- candidate_edge_id
- source
- verb
- target
- confidence_band (low|medium|high)
- evidence_summary
- reviewer_required: true

**Hard constraints:**
- suggestions only; no graph promotion
- do not invent new relationship verbs

---

## Contract: mapping ingestion (normalize + draft)

**Intent:** Ingest external mapping files into deterministic, reviewable proposals.

**Required input fields:**
- mapping_source
- schema_version
- record_batch_id

**Required output fields:**
- normalized_records
- validation_warnings
- draft_objects_written_to_quarantine
- reviewer_required: true

**Hard constraints:**
- quarantine lane only
- preserve source lineage
- no canonical writes

---

## Contract: migration drafting (draft)

**Intent:** Draft migration plans when IDs or anchors need change.

**Required input fields:**
- migration_scope
- from_identifiers
- to_identifiers
- compatibility_expectations

**Required output fields:**
- migration_plan_id
- deterministic rename table
- impact summary
- rollback notes
- reviewer_required: true

**Hard constraints:**
- produce plan only; no execution by default
- do not delete historical objects; deprecate instead
