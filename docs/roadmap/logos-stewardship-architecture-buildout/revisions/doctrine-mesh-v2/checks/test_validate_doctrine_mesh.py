#!/usr/bin/env python3
"""
object_type: doctrine_mesh_validator_negative_test
trust_zone: proposed
lifecycle_status: active
provenance_note: Created on 2026-08-24 by Codex root.
reason_for_inclusion: Prove the audit harness fails closed for missing,
duplicate, stale, out-of-order, self-checked, reused, and corrupted receipts.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = Path(__file__).with_name("validate_doctrine_mesh.py")
SPEC = importlib.util.spec_from_file_location("validate_doctrine_mesh", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("validator module unavailable")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class DoctrineMeshAuditNegativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        required = [ROOT / "evidence/event-ledger.json", ROOT / "evidence/timeline.json"]
        if not all(path.is_file() for path in required) or not list((ROOT / "evidence/receipts").glob("*.json")):
            raise unittest.SkipTest("pending final audit evidence")
        cls.events = VALIDATOR.load_data(ROOT / "evidence/event-ledger.json")["events"]
        cls.receipts = [VALIDATOR.load_data(path) for path in sorted((ROOT / "evidence/receipts").glob("*.json"))]
        cls.attempts = VALIDATOR.load_data(ROOT / "evidence/execution-attempts.json")["attempts"]
        cls.timeline = VALIDATOR.load_data(ROOT / "evidence/timeline.json")
        cls.cases = json.loads((ROOT / "checks/fixtures/negative-cases.json").read_text(encoding="utf-8"))["cases"]

    def test_positive_audit_bundle(self) -> None:
        self.assertEqual([], VALIDATOR.validate_audit_bundle(ROOT))

    def test_negative_cases_fail_closed(self) -> None:
        for case in self.cases:
            with self.subTest(case=case["case_id"]):
                events = copy.deepcopy(self.events)
                receipts = copy.deepcopy(self.receipts)
                attempts = copy.deepcopy(self.attempts)
                timeline = copy.deepcopy(self.timeline)
                action = case["action"]
                if action == "remove_postflight_receipt":
                    receipts = [item for item in receipts if item["phase"] != "postflight"]
                elif action == "duplicate_midflight_receipt":
                    duplicate = copy.deepcopy(next(item for item in receipts if item["phase"] == "midflight"))
                    duplicate["receipt_id"] += "-DUP"
                    receipts.append(duplicate)
                elif action == "stale_input_digest":
                    next(item for item in receipts if item["phase"] == "midflight")["input_manifest_digest"] = "sha256:" + ("f" * 64)
                elif action == "out_of_order_sequence":
                    next(item for item in events if item["phase"] == "midflight")["sequence"] = 9
                elif action == "auditor_checker_collision":
                    next(item for item in receipts if item["phase"] == "preflight")["checker_role_id"] = "doctrine-mesh-completeness-auditor"
                elif action == "reused_attempt":
                    mids = next(item for item in receipts if item["phase"] == "midflight")
                    mids["auditor_attempt_id"] = next(item for item in receipts if item["phase"] == "preflight")["auditor_attempt_id"]
                elif action == "corrupt_receipt_digest":
                    next(item for item in receipts if item["phase"] == "postflight")["receipt_digest"] = "sha256:" + ("a" * 64)
                elif action == "corrupt_event_digest":
                    next(item for item in events if item["phase"] == "midflight")["event_digest"] = "sha256:" + ("b" * 64)
                elif action == "break_receipt_chain":
                    next(item for item in receipts if item["phase"] == "midflight")["previous_receipt_digest"] = "sha256:" + ("c" * 64)
                elif action == "wrong_output_digest":
                    next(item for item in receipts if item["phase"] == "preflight")["coverage_plan_digest"] = "sha256:" + ("d" * 64)
                elif action == "wrong_event_predecessor":
                    next(item for item in events if item["phase"] == "postflight")["required_before_event_id"] = None
                elif action == "missing_attempt":
                    attempts = [item for item in attempts if item["event_id"] != "DMA-MIDFLIGHT-001"]
                elif action == "attempt_actor_mismatch":
                    next(item for item in attempts if item["event_id"] == "DMA-PREFLIGHT-001")["actor_role_id"] = "bounded-domain-researcher"
                elif action == "preflight_after_writer":
                    timeline["first_writer_lease_at"] = "2026-08-24T15:29:00Z"
                elif action == "postflight_before_worker":
                    timeline["last_worker_or_checker_receipt_at"] = "2099-01-01T00:00:00Z"
                else:
                    self.fail(f"unknown fixture action {action}")
                failures = VALIDATOR.validate_audit_bundle(ROOT, events, receipts, attempts, timeline)
                self.assertTrue(failures, f"negative case passed unexpectedly: {case['case_id']}")
                self.assertTrue(any(case["expected_signal"] in failure for failure in failures), failures)

    def test_non_horizontal_graph_cycle_fails(self) -> None:
        node_ids = {"A", "B"}
        edges = [
            {"type": "derived_from", "from": "A", "to": "B"},
            {"type": "stored_in", "from": "B", "to": "A"},
        ]
        self.assertFalse(VALIDATOR.graph_acyclic(node_ids, edges, {"checks", "challenges"}))

    def test_horizontal_challenge_cycle_is_ignored(self) -> None:
        node_ids = {"A", "B"}
        edges = [
            {"type": "checks", "from": "A", "to": "B"},
            {"type": "challenges", "from": "B", "to": "A"},
        ]
        self.assertTrue(VALIDATOR.graph_acyclic(node_ids, edges, {"checks", "challenges"}))

    def test_risk_floor_uses_highest_tag(self) -> None:
        self.assertEqual(
            "frontier",
            VALIDATOR.compute_risk_floor(["bounded_descriptive_history", "systemic_autonomy_or_controller_change"]),
        )

    def test_risk_floor_rejects_unknown_tag(self) -> None:
        with self.assertRaises(ValueError):
            VALIDATOR.compute_risk_floor(["model_says_low"])


class DoctrineMeshStaticContractTests(unittest.TestCase):
    def test_file_digest_is_checkout_newline_stable(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            lf_path = root / "lf.txt"
            crlf_path = root / "crlf.txt"
            binary_path = root / "binary.bin"
            binary_crlf_path = root / "binary-crlf.bin"
            lf_path.write_bytes(b"alpha\nbeta\n")
            crlf_path.write_bytes(b"alpha\r\nbeta\r\n")
            binary_path.write_bytes(b"\xffalpha\nbeta\n")
            binary_crlf_path.write_bytes(b"\xffalpha\r\nbeta\r\n")

            self.assertEqual(VALIDATOR.file_digest(lf_path), VALIDATOR.file_digest(crlf_path))
            self.assertNotEqual(
                VALIDATOR.file_digest(binary_path), VALIDATOR.file_digest(binary_crlf_path)
            )

    def test_interpreter_cache_is_not_a_freeze_payload(self) -> None:
        self.assertTrue(VALIDATOR.is_volatile_runtime_file(Path("checks/__pycache__/validator.pyc")))
        self.assertFalse(VALIDATOR.is_volatile_runtime_file(Path("checks/validate_doctrine_mesh.py")))

    def test_job_path_contract_rejects_noncanonical_repository_paths(self) -> None:
        schema = VALIDATOR.load_data(ROOT / "mesh/job-binding.schema.json")
        path_schema = schema["$defs"]["repositoryRelativePath"]
        validator = VALIDATOR.Draft202012Validator(path_schema)
        valid_paths = [
            "claimed/unit-1",
            "claimed/unit-1/nested/result.json",
            "claimed/unit-1/.keep",
        ]
        invalid_paths = [
            "",
            ".",
            "..",
            "../claimed/file.json",
            "claimed/./file.json",
            "claimed/unit-1/../../other/file.json",
            "claimed/unit-1//file.json",
            "claimed/unit-1/",
            "/absolute/file.json",
            "//server/share/file.json",
            "C:/absolute/file.json",
            "C:relative/file.json",
            "claimed\\unit-1\\file.json",
            "claimed/unit-1/line\nbreak.json",
        ]
        for path in valid_paths:
            with self.subTest(valid=path):
                self.assertEqual([], list(validator.iter_errors(path)))
        for path in invalid_paths:
            with self.subTest(invalid=path):
                self.assertTrue(list(validator.iter_errors(path)), path)

    def test_qualified_role_cannot_have_deterministic_failures(self) -> None:
        schema = VALIDATOR.load_data(ROOT / "research/qualification-receipt.schema.json")
        instance = {
            "status": "qualified_exact_revision",
            "deterministic_results": {"failed": 1},
            "meets_all_thresholds": True,
        }
        errors = VALIDATOR.schema_errors(schema, instance, "qualification")
        self.assertTrue(any("deterministic_results.failed" in error for error in errors), errors)

    def test_approved_source_use_requires_approved_access(self) -> None:
        schema = VALIDATOR.load_data(ROOT / "research/evidence-source-manifest.schema.json")
        instance = {
            "use_state": "approved_exact_descriptive_use",
            "rights_and_access": {"access_state": "unknown", "credentials_required": False},
            "verification_states": {"rights_exact_use": "approved"},
        }
        errors = VALIDATOR.schema_errors(schema, instance, "source")
        self.assertTrue(any("rights_and_access.access_state" in error for error in errors), errors)

    def test_checked_influence_requires_known_contact_and_reception(self) -> None:
        schema = VALIDATOR.load_data(ROOT / "graph/influence-bridge.schema.json")
        instance = {
            "status": "checked_descriptive_only",
            "contact_mechanism": "unknown",
            "reception_state": "unknown",
        }
        errors = VALIDATOR.schema_errors(schema, instance, "influence")
        self.assertTrue(any("contact_mechanism" in error for error in errors), errors)
        self.assertTrue(any("reception_state" in error for error in errors), errors)

    def test_manual_audit_cannot_bind_controller_runtime_receipt(self) -> None:
        schema = VALIDATOR.load_data(ROOT / "mesh/audit-receipt.schema.json")
        instance = {
            "execution_class": "manual_specification_coverage_review",
            "controller_runtime_receipt_ref": "evidence/runtime/controller.json",
            "controller_runtime_receipt_digest": "sha256:" + ("1" * 64),
        }
        errors = VALIDATOR.schema_errors(schema, instance, "manual receipt")
        self.assertTrue(any("controller_runtime_receipt_ref" in error for error in errors), errors)

    def test_risk_floor_uses_highest_tag_without_model_vote(self) -> None:
        self.assertEqual(
            "frontier",
            VALIDATOR.compute_risk_floor(["bounded_descriptive_history", "systemic_autonomy_or_controller_change"]),
        )
        with self.assertRaises(ValueError):
            VALIDATOR.compute_risk_floor(["model_says_low"])

    def test_non_horizontal_graph_cycle_fails(self) -> None:
        self.assertFalse(
            VALIDATOR.graph_acyclic(
                {"A", "B"},
                [
                    {"type": "derived_from", "from": "A", "to": "B"},
                    {"type": "stored_in", "from": "B", "to": "A"},
                ],
                {"checks", "challenges"},
            )
        )

    def test_expired_qualified_receipt_fails_semantic_check(self) -> None:
        receipt = {
            "receipt_id": "DQR-EXPIRED-TEST",
            "status": "qualified_exact_revision",
            "observed_at": "2026-01-01T00:00:00Z",
            "expires_at": "2026-02-01T00:00:00Z",
            "deterministic_results": {"passed": 1, "failed": 0},
            "meets_all_thresholds": True,
            "receipt_digest": "",
        }
        receipt["receipt_digest"] = VALIDATOR.object_digest(receipt, ("receipt_digest",))
        failures = VALIDATOR.validate_qualification_semantics(receipt, datetime(2026, 8, 24, tzinfo=timezone.utc))
        self.assertTrue(any("expired" in failure for failure in failures), failures)

    def test_normative_source_rejects_explicit_contradictions(self) -> None:
        schema = VALIDATOR.load_data(ROOT / "research/evidence-source-manifest.schema.json")
        instance = {
            "use_state": "approved_exact_normative_use_after_human_gate",
            "source_class": "SC-DISCOVERY-ONLY",
            "normative_christian_doctrine_authority": "candidate_tradition_scoped",
            "edition_or_witness": {"identity": "x", "revision": "x", "fitness_state": "not_fit"},
            "locator": {"exact_value": ""},
            "custody_and_provenance": {"provenance_state": "unprovenanced", "authenticity_state": "forged"},
            "freshness": {"state": "stale"},
            "rights_and_access": {"access_state": "approved_exact_use", "credentials_required": False},
            "verification_states": {
                "identity": "blocked", "edition_fitness": "not_fit", "locator": "not_found",
                "translation": "disputed", "source_quality": "rejected",
                "rights_exact_use": "approved", "custody_provenance": "unprovenanced_blocked",
            },
            "human_authorization_receipt_ref": "evidence/human/receipt.json",
            "human_authorization_receipt_digest": "sha256:" + ("1" * 64),
        }
        errors = VALIDATOR.schema_errors(schema, instance, "source")
        for signal in ("source_class", "edition_or_witness.fitness_state", "locator.exact_value", "freshness.state", "verification_states.source_quality"):
            self.assertTrue(any(signal in error for error in errors), (signal, errors))

    def test_multiple_surfaces_may_share_one_required_risk_tag(self) -> None:
        record = {
            "identity": {"decision_id": "D-TEST"},
            "scope": {
                "risk_tags": ["doctrine_interpretation"],
                "protected_surfaces": ["scripture_interpretation", "doctrine_interpretation"],
                "materiality_triggers": ["downstream_doctrine_effect"],
                "downstream_consumers": [],
                "material": True,
            },
            "risk": {"computed_minimum_floor": "high", "slicing_check_status": "pass_bundle_complete"},
            "review": {
                "writer_actor_instance_id": "writer-1",
                "checker_actor_instance_ids": ["checker-1"],
                "challenger_actor_instance_ids": ["challenger-1"],
            },
            "authority": {"valid_receipt_refs": ["human-receipt-1"]},
        }
        failures = VALIDATOR.validate_decision_semantics(record)
        self.assertFalse(any("protected-surface" in failure for failure in failures), failures)

    def test_budget_ledger_reconciles_and_rejects_duplicate_debits(self) -> None:
        zero = {dimension: 0 for dimension in VALIDATOR.BUDGET_DIMENSIONS}
        ceiling = {dimension: 10 for dimension in VALIDATOR.BUDGET_DIMENSIONS}
        consumed = zero
        reserved = {dimension: 2 for dimension in VALIDATOR.BUDGET_DIMENSIONS}
        remaining = {dimension: 8 for dimension in VALIDATOR.BUDGET_DIMENSIONS}
        entry = {
            "debit_id": "debit-1", "entry_type": "reservation", "idempotency_key": "idempotency-key-0001", "attempt_id": "attempt-1",
            "work_unit_id": "unit-1", "assignment_id": "DMJ-TEST", "consumed_delta": consumed,
            "reserved_delta": reserved, "receipt_ref": "receipt-1", "receipt_digest": "sha256:" + ("1" * 64),
            "lease_fence": 1, "observed_at": "2026-08-24T00:00:00Z",
        }
        ledger = {
            "ledger_id": "ledger-1", "campaign_id": "campaign-1", "campaign_revision": "r1", "sequence": 1,
            "previous_ledger_digest": None, "authorized_ceiling": ceiling, "consumed": consumed,
            "reserved": reserved, "remaining": remaining, "journal_entries": [entry],
            "work_units": [{"work_unit_id": "unit-1", "consumed": consumed, "reserved": reserved}],
            "attempt_receipt_chain_digest": "sha256:" + ("2" * 64), "observed_at": "2026-08-24T00:00:00Z",
            "ledger_digest": "",
        }
        ledger["ledger_digest"] = VALIDATOR.object_digest(ledger, ("ledger_digest",))
        self.assertEqual([], VALIDATOR.validate_budget_ledger_semantics(ledger))
        duplicate = copy.deepcopy(ledger)
        duplicate_entry = copy.deepcopy(entry)
        duplicate_entry["debit_id"] = "debit-2"
        duplicate["journal_entries"].append(duplicate_entry)
        duplicate["ledger_digest"] = VALIDATOR.object_digest(duplicate, ("ledger_digest",))
        failures = VALIDATOR.validate_budget_ledger_semantics(duplicate)
        self.assertTrue(any("idempotency_key" in failure for failure in failures), failures)
        self.assertTrue(any("attempt_id" in failure for failure in failures), failures)

        later = copy.deepcopy(ledger)
        later["sequence"] = 2
        later["previous_ledger_digest"] = ledger["ledger_digest"]
        later["reserved"] = {dimension: 4 for dimension in VALIDATOR.BUDGET_DIMENSIONS}
        later["remaining"] = {dimension: 6 for dimension in VALIDATOR.BUDGET_DIMENSIONS}
        later["work_units"][0]["reserved"] = later["reserved"]
        later["ledger_digest"] = VALIDATOR.object_digest(later, ("ledger_digest",))
        failures = VALIDATOR.validate_budget_ledger_semantics(later, ledger, ledger["journal_entries"])
        self.assertTrue(any("across snapshots" in failure for failure in failures), failures)

    def test_job_output_must_be_bound_inside_claimed_scope(self) -> None:
        digest = "sha256:" + ("3" * 64)
        role = lambda actor, group, scope: {"actor_instance_id": actor, "independence_group": group, "write_scope": scope}
        binding = {
            "assignment_id": "DMJ-TEST", "campaign_id": "campaign-1", "work_unit_id": "unit-1", "claimed_scope_ref": "claimed/unit-1",
            "work_claim_digest": digest,
            "controller": {"lease_fence": 7},
            "roles": {
                "writer": role("writer-1", "g1", ["claimed/unit-1"]),
                "checkers": [role("checker-1", "g2", [])],
                "challengers": [role("challenger-1", "g3", [])],
            },
            "data_and_effects": {"write_scope": ["claimed/unit-1"]},
            "outputs": [{"canonical_path": "claimed/unit-1/result.json", "work_claim_digest": digest}],
            "budget_binding": {
                "campaign_id": "campaign-1", "ledger_id": "ledger-1", "ledger_sequence": 1,
                "ledger_snapshot_ref": "evidence/budgets/test.json", "ledger_snapshot_digest": digest,
                "reservation_idempotency_key": "reservation-key-0001",
                "reservation_receipt_ref": "receipt/reservation-1.json", "reservation_receipt_digest": digest,
                "debit_receipt_ref": None, "debit_receipt_digest": None,
            },
        }
        self.assertEqual([], VALIDATOR.validate_job_binding_semantics(binding))
        ledger = {
            "ledger_id": "ledger-1", "campaign_id": "campaign-1", "sequence": 1, "ledger_digest": digest,
            "journal_entries": [{
                "entry_type": "reservation", "assignment_id": "DMJ-TEST", "work_unit_id": "unit-1",
                "lease_fence": 7, "receipt_ref": "receipt/reservation-1.json", "receipt_digest": digest,
                "idempotency_key": "reservation-key-0001",
            }],
        }
        self.assertEqual([], VALIDATOR.validate_job_binding_semantics(binding, {"evidence/budgets/test.json": ledger}))
        bad_budget = copy.deepcopy(binding)
        bad_budget["budget_binding"]["ledger_snapshot_digest"] = "sha256:" + ("4" * 64)
        failures = VALIDATOR.validate_job_binding_semantics(bad_budget, {"evidence/budgets/test.json": ledger})
        self.assertTrue(any("ledger identity or digest" in failure for failure in failures), failures)
        bad_fence = copy.deepcopy(binding)
        bad_fence["controller"]["lease_fence"] = 8
        failures = VALIDATOR.validate_job_binding_semantics(bad_fence, {"evidence/budgets/test.json": ledger})
        self.assertTrue(any("reservation journal" in failure for failure in failures), failures)
        missing_ledger = copy.deepcopy(binding)
        missing_ledger["budget_binding"]["ledger_snapshot_ref"] = "evidence/budgets/missing.json"
        failures = VALIDATOR.validate_job_binding_semantics(missing_ledger, {"evidence/budgets/test.json": ledger})
        self.assertTrue(any("missing budget ledger" in failure for failure in failures), failures)
        binding["outputs"][0]["canonical_path"] = "another/unit/result.json"
        failures = VALIDATOR.validate_job_binding_semantics(binding)
        self.assertTrue(any("output does not descend" in failure for failure in failures), failures)

        invalid_outputs = [
            "claimed/unit-1",
            "claimed/unit-10/result.json",
            "claimed/unit-1/../../other/file.json",
            "claimed/./unit-1/result.json",
            "claimed/unit-1//result.json",
            "claimed\\unit-1\\result.json",
        ]
        for path in invalid_outputs:
            with self.subTest(output=path):
                invalid = copy.deepcopy(binding)
                invalid["outputs"][0]["canonical_path"] = path
                failures = VALIDATOR.validate_job_binding_semantics(invalid)
                self.assertTrue(
                    any(
                        "invalid output canonical path" in failure
                        or "output does not descend" in failure
                        for failure in failures
                    ),
                    failures,
                )

        invalid_claim = copy.deepcopy(binding)
        invalid_claim["claimed_scope_ref"] = "claimed/../other"
        invalid_claim["roles"]["writer"]["write_scope"] = ["claimed/../other"]
        invalid_claim["data_and_effects"]["write_scope"] = ["claimed/../other"]
        invalid_claim["outputs"][0]["canonical_path"] = "claimed/../other/result.json"
        failures = VALIDATOR.validate_job_binding_semantics(invalid_claim)
        self.assertTrue(any("invalid claimed scope path" in failure for failure in failures), failures)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
