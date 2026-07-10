from __future__ import annotations

import pathlib

import yaml

from scripts.validate_agent_routing_vocabulary import VOCABULARY_PATH, validate


def test_current_agent_routing_vocabulary_validates() -> None:
    assert validate() == []


def test_human_reserved_gate_fails_closed(tmp_path: pathlib.Path) -> None:
    data = yaml.safe_load(VOCABULARY_PATH.read_text(encoding="utf-8"))
    data["authority_classes"]["A3_human_reserved"]["ai_may_satisfy_gate"] = True
    path = tmp_path / "agent_routing_vocabulary.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    assert any("A3_human_reserved" in failure for failure in validate(path))


def test_missing_specialist_independence_fails_closed(tmp_path: pathlib.Path) -> None:
    data = yaml.safe_load(VOCABULARY_PATH.read_text(encoding="utf-8"))
    data["specialist_domain_requirements"][0]["independence_requirement"] = "I0_not_required"
    path = tmp_path / "agent_routing_vocabulary.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    assert any("independent adapter" in failure for failure in validate(path))
