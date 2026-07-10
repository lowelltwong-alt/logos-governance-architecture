from __future__ import annotations

import pathlib

import yaml

from scripts.validate_independent_study_source_authorization import AUTHORIZATION_PATH, CANDIDATE_PATH, validate


def _write_yaml(path: pathlib.Path, data: object) -> pathlib.Path:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def test_current_authorization_and_candidates_validate() -> None:
    assert validate() == []


def test_institutional_gate_fails_closed(tmp_path: pathlib.Path) -> None:
    authorization = yaml.safe_load(AUTHORIZATION_PATH.read_text(encoding="utf-8"))
    authorization["institutional_requirements"]["university_required"] = True
    path = _write_yaml(tmp_path / "authorization.yaml", authorization)
    assert any("institutional affiliation" in failure for failure in validate(path, CANDIDATE_PATH))


def test_source_import_authority_fails_closed(tmp_path: pathlib.Path) -> None:
    authorization = yaml.safe_load(AUTHORIZATION_PATH.read_text(encoding="utf-8"))
    authorization["content_authority"]["source_text_import_authorized"] = True
    path = _write_yaml(tmp_path / "authorization.yaml", authorization)
    assert any("source content" in failure for failure in validate(path, CANDIDATE_PATH))


def test_institutional_credentials_cannot_be_shared(tmp_path: pathlib.Path) -> None:
    authorization = yaml.safe_load(AUTHORIZATION_PATH.read_text(encoding="utf-8"))
    authorization["optional_institutional_access_escalation"]["credential_sharing_authorized"] = True
    path = _write_yaml(tmp_path / "authorization.yaml", authorization)
    assert any("credential_sharing_authorized" in failure for failure in validate(path, CANDIDATE_PATH))


def test_candidate_text_presence_fails_closed(tmp_path: pathlib.Path) -> None:
    candidates = yaml.safe_load(CANDIDATE_PATH.read_text(encoding="utf-8"))
    candidates["candidates"][0]["source_text_present"] = True
    path = _write_yaml(tmp_path / "candidates.yaml", candidates)
    assert any("source_text_present" in failure for failure in validate(AUTHORIZATION_PATH, path))
