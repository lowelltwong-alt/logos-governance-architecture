#!/usr/bin/env python3
"""Validate the Logos cross-repo governance contract surface."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_MARKERS = {
    "README.md": [
        "logos-scripture-graph",
        "upstream governance",
        "governance_contract",
        "Noesis Atlas",
        "non-governing",
        "non-mutating",
    ],
    "AI_FRONT_DOOR.md": [
        "Cross-repo governance",
        "logos-scripture-graph",
        "agent-hostile",
        "Noesis Atlas",
        "must not modify",
        "must not modify, gate, govern",
    ],
    "AI_TABLE_OF_CONTENTS.md": [
        "DATA_FLOW_MAP.md",
        "logos-cross-repo-governance-contract.md",
        "agent-hostile-protection.md",
        "noesis-boundary.md",
    ],
    "DATA_FLOW_MAP.md": [
        "governance_contract",
        "logos-scripture-graph",
        "future runtime consumers",
        "Noesis Atlas",
        "read-only advisory comparison",
    ],
    "governance/LOGOS_REPO_REGISTRY.md": [
        "External Advisory Connections",
        "Noesis Atlas",
        "must not modify, govern",
    ],
    "governance/LOGOS_REPO_REGISTRY.yaml": [
        "external_advisory_connections",
        "noesis-atlas",
        "modify_logos_repos",
    ],
    "governance/REPOSITORY_LINK_CONTRACTS.md": [
        "external_advisory_link",
        "noesis-atlas",
        "must not modify, gate, govern",
    ],
    "docs/roadmap/repository-integration-map.md": [
        "logos-scripture-graph",
        "governance_contract",
        "data-plane",
    ],
    "data/graph/README.md": [
        "logos-scripture-graph",
        "downstream data-plane",
        "governance contract",
    ],
    "docs/governance/logos-cross-repo-governance-contract.md": [
        "logos-governance-architecture",
        "logos-scripture-graph",
        "governance_contract",
        "lowelltwong-alt/logos-scripture-graph#7",
        "Noesis Atlas",
        "must not modify, gate, govern",
    ],
    "docs/governance/agent-hostile-protection.md": [
        "agent-hostile",
        "Fail-Closed",
        "generated model content",
        "logos-scripture-graph",
        "Noesis",
    ],
    "docs/governance/noesis-boundary.md": [
        "Allowed connection shape",
        "read-only advisory",
        "must not write to, modify",
        "logos-boundary-literature",
    ],
}


def main() -> int:
    failures: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        path = ROOT / rel
        if not path.exists():
            failures.append(f"Missing required file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        missing = [marker for marker in markers if marker not in text]
        if missing:
            failures.append(f"{rel} missing marker(s): {', '.join(missing)}")

    if failures:
        print("Cross-repo governance contract validation failed.")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Cross-repo governance contract validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
