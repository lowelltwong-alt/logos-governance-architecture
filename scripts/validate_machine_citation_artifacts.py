#!/usr/bin/env python3
"""Reject non-resolvable machine citation artifacts in tracked public text.

Capability classification: ``portable_core``. The validator is deterministic,
provider-neutral Python backed only by Git and the local filesystem. Its input is
the repository's tracked-file index and UTF-8 text content; its output is a
stable pass/fail result plus path, line, and rule identifiers. It never prints
matched payloads, calls a network or model, writes files, changes Git state, or
confers source, theological, review, publication, or cleanup authority.

Unreadable Git state and missing tracked files fail closed. Tracked symlink
targets are scanned as public text without following the link. NUL-bearing or
non-UTF-8 regular blobs are treated as non-text and skipped. Stop and investigate
if the tracked surface cannot be enumerated or a finding represents an
intentionally governed identifier rather than chat-local residue. Evaluate
changes with the focused tests and a clean scan of the current tracked surface.
Rollback consists of removing this validator from the existing validation
contracts and CI step; rollback does not restore prohibited artifacts.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_CLASS = "portable_core"

PRIVATE_USE_RULE = "unicode_private_use_code_point"
CHAT_LOCATOR_RULE = "chat_local_citation_locator"

_LOCATOR_PREFIX = "turn"
_LOCATOR_CHANNELS = ("search", "fetch", "view")
CHAT_LOCATOR_RE = re.compile(
    re.escape(_LOCATOR_PREFIX)
    + r"[0-9]+(?:"
    + "|".join(re.escape(channel) for channel in _LOCATOR_CHANNELS)
    + r")[0-9]+",
    re.IGNORECASE,
)


class RepositoryScanError(RuntimeError):
    """Raised when the tracked public surface cannot be scanned safely."""


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    rule: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.rule}"


@dataclass(frozen=True)
class ScanResult:
    findings: tuple[Finding, ...]
    tracked_count: int
    scanned_text_count: int
    skipped_non_text_count: int


def is_private_use(character: str) -> bool:
    code_point = ord(character)
    return (
        0xE000 <= code_point <= 0xF8FF
        or 0xF0000 <= code_point <= 0xFFFFD
        or 0x100000 <= code_point <= 0x10FFFD
    )


def scan_text(path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if any(is_private_use(character) for character in line):
            findings.append(Finding(path, line_number, PRIVATE_USE_RULE))
        if CHAT_LOCATOR_RE.search(line):
            findings.append(Finding(path, line_number, CHAT_LOCATOR_RULE))
    return findings


def _relative_git_path(value: str) -> Path:
    parts = value.split("/")
    if (
        not value
        or value.startswith("/")
        or any(part in {"", ".", ".."} for part in parts)
    ):
        raise RepositoryScanError(f"Git returned an unsafe tracked path: {value!r}")
    return Path(*parts)


def tracked_paths(root: Path) -> list[tuple[str, Path]]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RepositoryScanError(
            "cannot enumerate tracked files" + (f": {detail}" if detail else "")
        )
    try:
        output = completed.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RepositoryScanError("tracked paths are not valid UTF-8") from exc

    values = [value for value in output.split("\0") if value]
    return [(value, root / _relative_git_path(value)) for value in values]


def decode_text_blob(data: bytes) -> str | None:
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def read_tracked_text(path: Path, relative: str) -> str | None:
    if path.is_symlink():
        try:
            return str(path.readlink())
        except OSError as exc:
            raise RepositoryScanError(
                f"cannot read tracked symlink {relative}: {exc}"
            ) from exc
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise RepositoryScanError(f"cannot read tracked file {relative}: {exc}") from exc
    return decode_text_blob(data)


def scan_repository(root: Path = ROOT) -> ScanResult:
    root = root.resolve()
    findings: list[Finding] = []
    tracked = tracked_paths(root)
    scanned_text_count = 0
    skipped_non_text_count = 0

    for relative, path in tracked:
        text = read_tracked_text(path, relative)
        if text is None:
            skipped_non_text_count += 1
            continue
        scanned_text_count += 1
        findings.extend(scan_text(relative, text))

    return ScanResult(
        findings=tuple(sorted(findings)),
        tracked_count=len(tracked),
        scanned_text_count=scanned_text_count,
        skipped_non_text_count=skipped_non_text_count,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)

    try:
        result = scan_repository(args.root)
    except RepositoryScanError as exc:
        print("Machine citation artifact validation failed.")
        print(f"FAIL repository_scan: {exc}")
        return 1

    if result.findings:
        print("Machine citation artifact validation failed.")
        for finding in result.findings:
            print(f"FAIL {finding.render()}")
        return 1

    print(
        "Machine citation artifact validation passed "
        f"({result.scanned_text_count} UTF-8 tracked text files scanned; "
        f"{result.skipped_non_text_count} non-text files skipped)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
