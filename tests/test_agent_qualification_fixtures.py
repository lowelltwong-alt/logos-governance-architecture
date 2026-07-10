from __future__ import annotations

import pathlib

import yaml

from scripts.validate_agent_qualification_fixtures import MANIFEST_PATH, REGISTER_PATH, validate


def _copy(path: pathlib.Path, destination: pathlib.Path) -> pathlib.Path:
    destination.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return destination


def test_current_fixture_pack_and_register_validate() -> None:
    assert validate() == []


def test_adapter_cannot_become_eligible_without_evidence(tmp_path: pathlib.Path) -> None:
    manifest = _copy(MANIFEST_PATH, tmp_path / "manifest.yaml")
    register_data = yaml.safe_load(REGISTER_PATH.read_text(encoding="utf-8"))
    register_data["adapter_records"][0]["eligible_work_classes"] = ["W0_mechanical"]
    register = tmp_path / "register.yaml"
    register.write_text(yaml.safe_dump(register_data, sort_keys=False), encoding="utf-8")
    assert any("eligible_work_classes" in failure for failure in validate(manifest, register))


def test_missing_fixture_fails_closed(tmp_path: pathlib.Path) -> None:
    manifest_data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest_data["fixtures"].pop()
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    register = _copy(REGISTER_PATH, tmp_path / "register.yaml")
    assert any("fixed qualification pack" in failure for failure in validate(manifest, register))
