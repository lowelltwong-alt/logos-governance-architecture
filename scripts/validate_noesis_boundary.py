#!/usr/bin/env python3
"""Enforce the Noesis-cannot-govern-Logos invariant from the Logos side.

Policy: docs/governance/noesis-boundary.md

Noesis may inform Logos (as advisory comparison material) but may never govern
it. Concretely, no Logos artifact may carry a Noesis-namespaced reference in an
authority or derivation field, and no canonical/tradition-scoped artifact may
reference Noesis at all.

This validator is a tripwire. Logos currently contains zero Noesis references,
so it passes trivially today. It fails the first time someone wires Noesis into
a place that would let Noesis govern Logos.

Detection is deliberately broad: any token matching the Noesis namespace
(``noesis:``, ``noesis.``, ``noesis/``, or a bare ``noesis`` segment) found in a
guarded field is a violation.

Exit non-zero on any violation.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLAIMS_DIR = ROOT / "data" / "claims"
GRAPH_DIR = ROOT / "data" / "graph"
DOCS_DIR = ROOT / "docs"

# A reference is "Noesis-namespaced" if it names the noesis system as a source.
NOESIS_REF = re.compile(r"(?i)(^|[\s:/.\"'\[])noesis([:./]|$|[\s\"'\]])")

# Trust zones that may never reference Noesis in any field.
GOVERNED_ZONES = {"canonical", "tradition-scoped"}

# Predicates that make a claim's object an authority/derivation basis.
AUTHORITY_PREDICATES = {"grounds", "derived_from", "constrains", "anchors", "informs", "renders", "attests"}

# Claim fields that express authority/derivation (never advisory).
CLAIM_AUTHORITY_FIELDS = {"subject", "object", "lineage", "source_basis", "evidence_refs"}

# Frontmatter keys that express authority/derivation.
FRONTMATTER_AUTHORITY_KEYS = {"parents", "source", "source_basis", "authority", "derived_from", "grounds", "lineage"}

# The single field where advisory Noesis references are tolerated.
ADVISORY_FIELD = "external_advisory_refs"

# Free-text fields legitimately discuss Noesis (e.g. policy prose). The
# "governed zones may not reference Noesis at all" rule skips these; the
# authority/derivation rule does not depend on them.
FREE_TEXT_FIELDS = {
    "notes", "provenance_note", "reason_for_inclusion", "title", "slug",
    "description", "summary", "purpose", "object_type",
}

# Files whose job is to document the boundary itself; they must name Noesis.
SELF_EXEMPT = {"docs/governance/noesis-boundary.md"}


def has_noesis(value) -> bool:
    if isinstance(value, str):
        return bool(NOESIS_REF.search(value))
    if isinstance(value, (list, tuple)):
        return any(has_noesis(v) for v in value)
    if isinstance(value, dict):
        return any(has_noesis(v) for v in value.values())
    return False


def parse_simple_yaml(text: str) -> dict:
    data: dict = {}
    current = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and current:
            data.setdefault(current, [])
            data[current].append(line[4:].strip())
            continue
        if line.startswith(" "):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if value == "":
            current = key
            data[key] = []
        else:
            current = None
            data[key] = value
    return data


def extract_frontmatter(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else None


def check_claims(failures: list[str]) -> None:
    if not CLAIMS_DIR.exists():
        return
    for path in sorted(CLAIMS_DIR.glob("*.yaml")):
        data = parse_simple_yaml(path.read_text(encoding="utf-8"))
        zone = str(data.get("trust_zone", ""))
        predicate = str(data.get("predicate", ""))
        rel = path.relative_to(ROOT).as_posix()
        if rel in SELF_EXEMPT:
            continue

        for field in CLAIM_AUTHORITY_FIELDS:
            if field == "object" and predicate not in AUTHORITY_PREDICATES:
                # object only counts as authority basis under an authority predicate
                pass
            if has_noesis(data.get(field)):
                failures.append(
                    f"{rel}: Noesis reference in authority/derivation field '{field}' "
                    f"(predicate '{predicate}') — Noesis may not govern Logos"
                )
        if zone in GOVERNED_ZONES:
            for field, value in data.items():
                if field == ADVISORY_FIELD or field in FREE_TEXT_FIELDS:
                    continue
                if has_noesis(value):
                    failures.append(
                        f"{rel}: governed claim (trust_zone={zone}) references Noesis in '{field}' "
                        f"— governed zones may not reference Noesis at all"
                    )


def check_node_frontmatter(failures: list[str]) -> None:
    if not DOCS_DIR.exists():
        return
    for path in sorted(DOCS_DIR.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm = extract_frontmatter(text)
        if fm is None:
            continue
        data = parse_simple_yaml(fm)
        zone = str(data.get("trust_zone", ""))
        rel = path.relative_to(ROOT).as_posix()
        if rel in SELF_EXEMPT:
            continue

        for key in FRONTMATTER_AUTHORITY_KEYS:
            if has_noesis(data.get(key)):
                failures.append(
                    f"{rel}: Noesis reference in authority field '{key}' — Noesis may not govern Logos"
                )
        if zone in GOVERNED_ZONES:
            for key, value in data.items():
                if key == ADVISORY_FIELD or key in FREE_TEXT_FIELDS:
                    continue
                if has_noesis(value):
                    failures.append(
                        f"{rel}: governed node (trust_zone={zone}) references Noesis in '{key}' "
                        f"— governed zones may not reference Noesis at all"
                    )


def check_graph(failures: list[str]) -> None:
    if not GRAPH_DIR.exists():
        return
    for path in sorted(GRAPH_DIR.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        rel = path.relative_to(ROOT).as_posix()
        zone = str(data.get("trust_zone", "")) if isinstance(data, dict) else ""
        for key in FRONTMATTER_AUTHORITY_KEYS | {"from", "to", "subject", "object"}:
            if isinstance(data, dict) and has_noesis(data.get(key)):
                failures.append(
                    f"{rel}: Noesis reference in authority field '{key}' — Noesis may not govern Logos"
                )
        if zone in GOVERNED_ZONES and isinstance(data, dict):
            for key, value in data.items():
                if key == ADVISORY_FIELD:
                    continue
                if has_noesis(value):
                    failures.append(
                        f"{rel}: governed graph object (trust_zone={zone}) references Noesis in '{key}'"
                    )


def main() -> int:
    failures: list[str] = []
    check_claims(failures)
    check_node_frontmatter(failures)
    check_graph(failures)

    if failures:
        for f in failures:
            print(f"FAIL {f}")
        print(
            f"\nNoesis boundary violated: {len(failures)} reference(s). "
            "See docs/governance/noesis-boundary.md. Noesis may inform Logos but never govern it."
        )
        return 1

    print("Noesis boundary OK: no Noesis reference governs or derives any Logos artifact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
