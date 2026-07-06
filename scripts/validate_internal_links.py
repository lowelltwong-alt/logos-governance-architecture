#!/usr/bin/env python3
"""Validate local markdown internal links and backtick path references.

Default scope is README.md so local validation, CI validation, and semantic
merge all measure the same bounded baseline in Wave B. Pass --all-markdown to
run the broader manual audit that will be normalized in Wave C.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
BACKTICK_RE = re.compile(r"`([^`]+)`")

SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "data:", "#")
VALID_BACKTICK_SUFFIXES = (".md", ".yaml", ".yml", ".json", ".py", ".sh", "/")
ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_RUST_MANIFEST = ROOT / "tools" / "logos_governance_fast_validators" / "Cargo.toml"


def looks_like_local_path(text: str) -> bool:
    candidate = text.strip().strip('"').strip("'")
    if not candidate or " " in candidate or '<' in candidate or '>' in candidate:
        return False
    if candidate.startswith(SKIP_PREFIXES):
        return False
    if candidate.startswith("<") and candidate.endswith(">"):
        candidate = candidate[1:-1].strip()
    if candidate.startswith(("./", "../")):
        return True
    if "/" not in candidate:
        return False
    return candidate.endswith(VALID_BACKTICK_SUFFIXES)


def normalize_target(raw: str) -> str:
    target = raw.strip().strip('"').strip("'")
    if target.startswith('<') and target.endswith('>'):
        target = target[1:-1].strip()
    if '#' in target:
        target = target.split('#', 1)[0]
    if '?' in target:
        target = target.split('?', 1)[0]
    return target.strip()


def iter_targets(text: str):
    yield from MARKDOWN_LINK_RE.findall(text)
    for ref in BACKTICK_RE.findall(text):
        if looks_like_local_path(ref):
            yield ref


def path_exists(base_file: pathlib.Path, raw_target: str, root: pathlib.Path) -> bool:
    target = normalize_target(raw_target)
    if not target or target.startswith(SKIP_PREFIXES):
        return True

    candidates = []
    if target.startswith('/'):
        candidates.append(root / target.lstrip('/'))
    else:
        candidates.append(base_file.parent / target)
        candidates.append(root / target)
    return any(c.exists() for c in candidates)


def check_markdown_files(root: pathlib.Path, files: list[pathlib.Path]) -> list[str]:
    failures: list[str] = []
    for md in files:
        text = md.read_text(encoding='utf-8')
        for target in iter_targets(text):
            if not path_exists(md, target, root):
                failures.append(f"{md.relative_to(root).as_posix()}: missing local target '{target}'")
    return failures


def rust_manifest_path() -> pathlib.Path:
    override = os.environ.get("LOGOS_GOVERNANCE_FAST_VALIDATORS_MANIFEST")
    if override:
        return pathlib.Path(override)
    return DEFAULT_RUST_MANIFEST


def run_rust_validator(args: argparse.Namespace, root: pathlib.Path) -> int | None:
    manifest = rust_manifest_path()
    cargo = shutil.which("cargo")
    if cargo is None or not manifest.exists():
        return None

    command = [
        cargo,
        "run",
        "--quiet",
        "--manifest-path",
        str(manifest),
        "--",
        "internal-links",
        "--root",
        str(root),
    ]
    if args.all_markdown:
        command.append("--all-markdown")
    command.extend(args.paths)

    try:
        completed = subprocess.run(command, text=True)
    except FileNotFoundError:
        return None
    return completed.returncode


def run_python_validator(args: argparse.Namespace, root: pathlib.Path) -> int:
    if args.paths:
        files = [root / p for p in args.paths]
    elif args.all_markdown:
        files = sorted(root.rglob('*.md'))
    else:
        files = [root / 'README.md']

    markdown_files = [p for p in files if p.suffix == '.md' and p.exists()]
    failures = check_markdown_files(root, markdown_files)

    if failures:
        for failure in failures:
            print('FAIL', failure)
        return 1

    print(f'Internal link validation passed ({len(markdown_files)} markdown files).')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='*', help='Optional markdown files to validate.')
    parser.add_argument(
        '--all-markdown',
        action='store_true',
        help='Validate all markdown files in repository (broader manual audit scope).',
    )
    parser.add_argument(
        '--python-fallback',
        action='store_true',
        help='Try the Rust fast validator when available; fall back to Python only if Rust is unavailable.',
    )
    parser.add_argument(
        '--require-rust',
        action='store_true',
        help='Require the Rust fast validator and fail if it is unavailable.',
    )
    args = parser.parse_args()

    if args.python_fallback and args.require_rust:
        parser.error("--python-fallback and --require-rust are mutually exclusive")

    root = ROOT

    if args.python_fallback or args.require_rust:
        rust_returncode = run_rust_validator(args, root)
        if rust_returncode is not None:
            return rust_returncode
        if args.require_rust:
            print(
                f"Rust fast validator unavailable: expected cargo and {rust_manifest_path()}",
                file=sys.stderr,
            )
            return 2

    return run_python_validator(args, root)


if __name__ == '__main__':
    raise SystemExit(main())
