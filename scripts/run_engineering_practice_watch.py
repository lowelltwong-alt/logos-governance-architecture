#!/usr/bin/env python3
"""Produce a deterministic due/trigger report; never adopt a practice."""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import json
import os
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES = ROOT / "governance/registry/ENGINEERING_PRACTICE_SOURCE_REGISTRY.yaml"
RECOMMENDATIONS = ROOT / "governance/registry/ENGINEERING_PRACTICE_RECOMMENDATION_REGISTRY.yaml"

TRIGGERS = {
    "agent_or_orchestration": ("agent", "routing", "worktree", "family_work"),
    "workflow_or_ci": (".github/workflows", "validation", "validator", "scripts/"),
    "architecture_or_schema": ("governance/", "schemas/", "architecture", "dependency"),
    "security_rights_or_authority": ("security", "license", "rights", "source_authorization", "authority"),
    "postmortem_or_lesson": ("postmortem", "lesson", "dad-lesson"),
}


def load(path: pathlib.Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def build_report(as_of: date, run_kind: str, changed_files: list[str]) -> dict:
    sources = load(SOURCES).get("sources", [])
    recs = load(RECOMMENDATIONS).get("recommendations", [])
    due_sources = sorted(s["source_id"] for s in sources if date.fromisoformat(s["next_review_due"]) <= as_of)
    due_recs = sorted(r["practice_id"] for r in recs if date.fromisoformat(r["next_review_due"]) <= as_of)
    lowered = [path.lower().replace("\\", "/") for path in changed_files]
    topics = sorted(topic for topic, needles in TRIGGERS.items() if any(needle in path for path in lowered for needle in needles))
    actions: list[str] = []
    if due_sources:
        actions.append("research_due_sources_using_current_primary_official_evidence")
    if due_recs:
        actions.append("review_due_recommendations_for_logos_fit_and_owner_gates")
    if topics:
        actions.append("assess_triggered_topics_against_existing_recommendations")
    if not actions:
        actions.append("no_research_action_due")
    return {
        "object_type": "engineering_practice_watch_report",
        "trust_zone": "proposed",
        "lifecycle_status": "generated_report",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_kind": run_kind,
        "due_sources": due_sources,
        "due_recommendations": due_recs,
        "triggered_topics": topics,
        "actions": actions,
    }


def markdown(report: dict) -> str:
    lines = ["# Engineering Practice Watch", "", f"Run kind: `{report['run_kind']}`", ""]
    for label, key in (("Due sources", "due_sources"), ("Due recommendations", "due_recommendations"), ("Triggered topics", "triggered_topics"), ("Actions", "actions")):
        values = report[key]
        lines.extend([f"## {label}", ""] + ([f"- `{value}`" for value in values] if values else ["- None"]) + [""])
    lines.append("This report is evidence-only and cannot adopt practices or satisfy owner gates.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--run-kind", choices=["event", "weekly", "monthly", "quarterly", "manual"], default="manual")
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    parser.add_argument("--github-output")
    args = parser.parse_args()
    report = build_report(date.fromisoformat(args.as_of), args.run_kind, args.changed_file)
    json_text = json.dumps(report, indent=2) + "\n"
    md_text = markdown(report)
    if args.output_json:
        pathlib.Path(args.output_json).write_text(json_text, encoding="utf-8")
    if args.output_md:
        pathlib.Path(args.output_md).write_text(md_text, encoding="utf-8")
    output = args.github_output or os.environ.get("GITHUB_OUTPUT")
    if output:
        action_required = bool(report["due_sources"] or report["due_recommendations"])
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"action_required={str(action_required).lower()}\n")
    print(json_text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
