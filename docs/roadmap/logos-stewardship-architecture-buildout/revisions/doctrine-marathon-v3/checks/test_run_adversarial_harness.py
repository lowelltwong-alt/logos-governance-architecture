#!/usr/bin/env python3
"""Regression tests for the copied-root V3 aggregate sentinel."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys

import pytest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "dmv3_aggregate_harness", HERE / "run_adversarial_harness.py"
)
assert SPEC and SPEC.loader
harness = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = harness
SPEC.loader.exec_module(harness)


def test_complete_aggregate_sentinel_replays_both_orders() -> None:
    result = harness.run_catalog(harness.load_catalog(), observe=False)
    assert result["status"] == "pass"
    assert result["case_count"] == 4
    assert result["source_root_mutation_performed"] is False
    assert result["runtime_authority"] == "none"
    assert result["publication_authority"] == "none"
    for row in result["forward"]:
        assert row["aggregate_validator_executed"] is True
        assert row["component_only"] is False
        assert row["candidate_changed"] is True
        assert row["primary_rule"] == row["intended_rule"]
        assert row["baseline_findings"] == []
        assert row["candidate_findings"]
        assert any(
            change["change_role"] == "intended_target"
            for change in row["changed_files"]
        )


def test_noop_candidate_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    case = copy.deepcopy(harness.load_catalog()[0])
    monkeypatch.setattr(harness, "apply_mutation", lambda root, selected: None)
    with pytest.raises(AssertionError, match="byte no-op"):
        harness.run_case(case, observe=False)


def test_primary_rule_mismatch_fails_closed() -> None:
    case = copy.deepcopy(harness.load_catalog()[-1])
    case["intended_rule"] = "not_the_observed_primary_rule"
    with pytest.raises(AssertionError, match="intended not_the_observed_primary_rule"):
        harness.run_case(case, observe=False)


def test_raw_finding_order_is_not_presentation_sorted() -> None:
    observed = harness.ordered_findings(
        ["z_rule: emitted first", "a_rule: emitted second"]
    )
    assert [row["rule"] for row in observed] == ["z_rule", "a_rule"]


def test_duplicate_finding_identity_fails_closed() -> None:
    with pytest.raises(AssertionError, match="duplicate finding identities"):
        harness.ordered_findings(["same_rule: same", "same_rule: same"])
