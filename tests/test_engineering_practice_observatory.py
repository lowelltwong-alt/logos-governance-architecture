from copy import deepcopy
from datetime import date

from scripts import run_engineering_practice_watch as watch
from scripts import validate_engineering_practice_observatory as validator


def test_current_observatory_validates() -> None:
    assert validator.validate() == []


def test_current_date_has_no_due_research() -> None:
    report = watch.build_report(date(2026, 7, 10), "weekly", [])
    assert report["due_sources"] == []
    assert report["due_recommendations"] == []


def test_future_date_surfaces_due_work() -> None:
    report = watch.build_report(date(2026, 8, 10), "weekly", [])
    assert "EPS-OPENAI-001" in report["due_sources"]
    assert "EPR-005" in report["due_recommendations"]


def test_event_paths_route_research_topics() -> None:
    report = watch.build_report(date(2026, 7, 10), "event", [".github/workflows/new-agent.yml"])
    assert "agent_or_orchestration" in report["triggered_topics"]
    assert "workflow_or_ci" in report["triggered_topics"]


def test_unknown_evidence_source_fails_closed(monkeypatch) -> None:
    original = validator.load
    def mutant(path):
        data = original(path)
        if path == validator.RECOMMENDATIONS:
            data = deepcopy(data)
            data["recommendations"][0]["evidence_source_ids"] = ["EPS-UNKNOWN"]
        return data
    monkeypatch.setattr(validator, "load", mutant)
    assert any("unknown sources" in failure for failure in validator.validate())
