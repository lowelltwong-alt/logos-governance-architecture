from __future__ import annotations

from pathlib import Path

from scripts.validation_contracts import default_validation_commands


def test_machine_citation_validator_is_registered_once() -> None:
    commands = default_validation_commands("python")
    matches = [item for item in commands if item["name"] == "machine_citation_artifacts"]

    assert matches == [
        {
            "name": "machine_citation_artifacts",
            "command": ["python", "scripts/validate_machine_citation_artifacts.py"],
        }
    ]


def test_structure_workflow_runs_machine_citation_validator_once() -> None:
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github" / "workflows" / "validate-logos-structure.yml").read_text(
        encoding="utf-8"
    )

    assert workflow.count("python scripts/validate_machine_citation_artifacts.py") == 1
