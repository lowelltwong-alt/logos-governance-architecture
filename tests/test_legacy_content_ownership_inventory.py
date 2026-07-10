from __future__ import annotations

from copy import deepcopy

from scripts import validate_legacy_content_ownership_inventory as validator


def test_current_inventory_validates() -> None:
    assert validator.validate_inventory(validator.ROOT, validator._load(validator.INVENTORY)) == []


def test_unclassified_legacy_paths_fail_closed() -> None:
    inventory = validator._load(validator.INVENTORY)
    inventory["entries"] = [entry for entry in inventory["entries"] if entry["entry_id"] != "LCOI-001"]

    failures = validator.validate_inventory(validator.ROOT, inventory)

    assert any("data/claims/" in failure and "exactly one ownership disposition" in failure for failure in failures)


def test_overlapping_path_classifications_fail_closed() -> None:
    inventory = validator._load(validator.INVENTORY)
    duplicate = deepcopy(inventory["entries"][0])
    duplicate["entry_id"] = "LCOI-999"
    inventory["entries"].append(duplicate)

    failures = validator.validate_inventory(validator.ROOT, inventory)

    assert any("data/claims/" in failure and "found 2" in failure for failure in failures)
