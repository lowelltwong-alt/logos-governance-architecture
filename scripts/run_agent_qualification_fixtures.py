#!/usr/bin/env python3
"""Run the structural source-safe fixture pack; never invokes a model adapter."""
from __future__ import annotations

import sys

import yaml

from validate_agent_qualification_fixtures import MANIFEST_PATH, validate


def main() -> int:
    failures = validate()
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    print(f"Source-safe qualification fixture pack validated ({len(manifest['fixtures'])} fixtures).")
    print("No model adapter was invoked; all current adapter records remain unqualified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
