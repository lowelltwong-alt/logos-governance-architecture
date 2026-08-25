#!/usr/bin/env python3
"""Reject machine-local citation and attachment residue in public Git surfaces.

Capability classification: portable_core. The validator is deterministic,
provider-neutral Python backed only by Git and the standard library. By default
it scans blobs from the current Git index, never mutable worktree paths. It can
also scan exact commits or every fetched origin remote-tracking head. Output
contains only target, path, line, and rule identifiers; matched payloads are
never printed.

Unreadable Git state, conflicted index entries, missing refs, unsafe paths, and
undecodable text-like blobs fail closed. Other NUL-bearing or non-text blobs are
counted and skipped. The all-origin-heads mode covers only heads successfully
fetched into refs/remotes/origin; it cannot prove absence from deleted or
unreachable objects, pull-request-only refs, forks, other remotes, or LFS
payloads. This hygiene gate confers no source, theological, review, publication,
remote-mutation, or cleanup authority.
"""
from __future__ import annotations

import argparse
import html
import re
import subprocess
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_CLASS = "portable_core"

PRIVATE_USE_RULE = "unicode_private_use_code_point"
ENCODED_PRIVATE_USE_RULE = "encoded_unicode_private_use_code_point"
CHAT_LOCATOR_RULE = "chat_local_citation_locator"
OBFUSCATED_CHAT_LOCATOR_RULE = "obfuscated_chat_local_citation_locator"
LOCAL_ATTACHMENT_RULE = "local_user_profile_attachment_path"

_LOCATOR_PREFIX = "turn"
_LOCATOR_CHANNELS = (
    "search",
    "fetch",
    "view",
)
CHAT_LOCATOR_RE = re.compile(
    re.escape(_LOCATOR_PREFIX)
    + r"[0-9]+(?:"
    + "|".join(re.escape(channel) for channel in _LOCATOR_CHANNELS)
    + r")[0-9]+",
    re.IGNORECASE,
)
_TRUE_LINE_BOUNDARY_RE = re.compile(r"\r\n|[\n\r\u2028\u2029]")
_BACKSLASH_UNICODE_RE = re.compile(
    re.escape("\\") + r"(?:u([0-9a-fA-F]{4})|U([0-9a-fA-F]{8}))"
)
_TEXT_SUFFIXES = frozenset(
    {
        ".cff",
        ".cfg",
        ".csv",
        ".css",
        ".htm",
        ".html",
        ".ini",
        ".js",
        ".json",
        ".jsonl",
        ".md",
        ".ps1",
        ".py",
        ".rst",
        ".sh",
        ".svg",
        ".toml",
        ".ts",
        ".tsv",
        ".txt",
        ".xml",
        ".yaml",
        ".yml",
    }
)
_MAX_TEXT_BLOB_BYTES = 32 * 1024 * 1024
_MAX_NORMALIZED_LINE_CHARS = 1_000_000


class RepositoryScanError(RuntimeError):
    """Raised when a requested public Git surface cannot be scanned safely."""


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    rule: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.rule}"


@dataclass(frozen=True)
class BlobEntry:
    path: str
    object_id: str
    expected_type: str


@dataclass(frozen=True)
class ScanTarget:
    label: str
    entries: tuple[BlobEntry, ...]


@dataclass(frozen=True)
class ScanResult:
    findings: tuple[Finding, ...]
    tracked_count: int
    scanned_text_count: int
    skipped_non_text_count: int
    targets: tuple[str, ...] = ("index",)


def is_private_use(character: str) -> bool:
    code_point = ord(character)
    return (
        0xE000 <= code_point <= 0xF8FF
        or 0xF0000 <= code_point <= 0xFFFFD
        or 0x100000 <= code_point <= 0x10FFFD
    )


def _combine_surrogates(value: str) -> str:
    combined: list[str] = []
    index = 0
    while index < len(value):
        high = ord(value[index])
        if 0xD800 <= high <= 0xDBFF and index + 1 < len(value):
            low = ord(value[index + 1])
            if 0xDC00 <= low <= 0xDFFF:
                combined.append(chr(0x10000 + ((high - 0xD800) << 10) + low - 0xDC00))
                index += 2
                continue
        combined.append(value[index])
        index += 1
    return "".join(combined)


def _decode_backslash_unicode(value: str) -> str:
    def replace(match: re.Match[str]) -> str:
        encoded = match.group(1) or match.group(2)
        code_point = int(encoded, 16)
        if code_point > 0x10FFFF:
            return match.group(0)
        return chr(code_point)

    return _combine_surrogates(_BACKSLASH_UNICODE_RE.sub(replace, value))


def normalize_obfuscation(value: str) -> str:
    """Decode bounded textual encodings and remove invisible format controls."""

    if len(value) > _MAX_NORMALIZED_LINE_CHARS:
        raise RepositoryScanError("text line exceeds the normalization safety limit")
    normalized = value
    for _ in range(2):
        previous = normalized
        normalized = _decode_backslash_unicode(normalized)
        normalized = html.unescape(normalized)
        normalized = unquote(normalized, encoding="utf-8", errors="replace")
        if normalized == previous:
            break
    normalized = unicodedata.normalize("NFKC", normalized)
    return "".join(
        character
        for character in normalized
        if unicodedata.category(character) not in {"Cc", "Cf"}
    )


def has_local_attachment_path(value: str) -> bool:
    normalized = value.replace("\\", "/").lower()
    attachment_root = "/".join((".codex", "attachments")) + "/"
    profile_roots = (
        "/".join(("", "users", "")),
        "/".join(("", "home", "")),
        "/".join(("", "root", "")),
    )
    return "/".join(("~", attachment_root)) in normalized or (
        attachment_root in normalized
        and any(root in normalized for root in profile_roots)
    )


def scan_text(path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    # Split only on true newline boundaries. Other Cc/Cf controls—including
    # separators recognized by str.splitlines()—must remain in the line so the
    # obfuscation normalizer can remove them before locator matching.
    for line_number, line in enumerate(_TRUE_LINE_BOUNDARY_RE.split(text), start=1):
        raw_private_use = any(is_private_use(character) for character in line)
        raw_locator = CHAT_LOCATOR_RE.search(line) is not None
        if raw_private_use:
            findings.append(Finding(path, line_number, PRIVATE_USE_RULE))
        if raw_locator:
            findings.append(Finding(path, line_number, CHAT_LOCATOR_RULE))

        normalized = normalize_obfuscation(line)
        if not raw_private_use and any(
            is_private_use(character) for character in normalized
        ):
            findings.append(Finding(path, line_number, ENCODED_PRIVATE_USE_RULE))
        if not raw_locator and CHAT_LOCATOR_RE.search(normalized):
            findings.append(
                Finding(path, line_number, OBFUSCATED_CHAT_LOCATOR_RULE)
            )
        if has_local_attachment_path(normalized):
            findings.append(Finding(path, line_number, LOCAL_ATTACHMENT_RULE))
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


def _run_git(root: Path, *arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        command = " ".join(arguments)
        raise RepositoryScanError(
            f"git {command} failed" + (f": {detail}" if detail else "")
        )
    return completed.stdout


def _decode_git_output(data: bytes, description: str) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RepositoryScanError(f"{description} is not valid UTF-8") from exc


def index_target(root: Path) -> ScanTarget:
    output = _run_git(root, "ls-files", "--stage", "-z")
    entries: list[BlobEntry] = []
    seen_paths: set[str] = set()
    for record in (item for item in output.split(b"\0") if item):
        try:
            metadata, encoded_path = record.split(b"\t", 1)
            mode, object_id, stage = metadata.decode("ascii").split()
        except (ValueError, UnicodeDecodeError) as exc:
            raise RepositoryScanError("Git returned a malformed index entry") from exc
        path = _decode_git_output(encoded_path, "tracked index path")
        _relative_git_path(path)
        if stage != "0":
            raise RepositoryScanError(
                f"index contains an unresolved stage-{stage} entry: {path}"
            )
        if path in seen_paths:
            raise RepositoryScanError(f"index returned duplicate path: {path}")
        seen_paths.add(path)
        expected_type = "commit" if mode == "160000" else "blob"
        entries.append(BlobEntry(path, object_id, expected_type))
    return ScanTarget("index", tuple(entries))


def _validate_revision(value: str) -> None:
    if (
        not value
        or value.startswith("-")
        or any(character.isspace() or character == "\0" for character in value)
    ):
        raise RepositoryScanError(f"unsafe Git revision: {value!r}")


def ref_target(root: Path, revision: str) -> ScanTarget:
    _validate_revision(revision)
    resolved = _run_git(
        root,
        "rev-parse",
        "--verify",
        "--end-of-options",
        f"{revision}^{{commit}}",
    ).decode("ascii").strip()
    output = _run_git(root, "ls-tree", "-r", "-z", "--full-tree", resolved)
    entries: list[BlobEntry] = []
    seen_paths: set[str] = set()
    for record in (item for item in output.split(b"\0") if item):
        try:
            metadata, encoded_path = record.split(b"\t", 1)
            _mode, object_type, object_id = metadata.decode("ascii").split()
        except (ValueError, UnicodeDecodeError) as exc:
            raise RepositoryScanError(
                f"Git returned a malformed tree entry for {revision}"
            ) from exc
        path = _decode_git_output(encoded_path, f"tree path for {revision}")
        _relative_git_path(path)
        if path in seen_paths:
            raise RepositoryScanError(
                f"tree {revision} returned duplicate path: {path}"
            )
        seen_paths.add(path)
        entries.append(BlobEntry(path, object_id, object_type))
    return ScanTarget(f"{revision}@{resolved[:12]}", tuple(entries))


def origin_head_revisions(root: Path) -> tuple[str, ...]:
    output = _run_git(
        root,
        "for-each-ref",
        "--format=%(refname)%09%(symref)",
        "refs/remotes/origin",
    )
    revisions: list[str] = []
    for line in _decode_git_output(output, "origin ref inventory").splitlines():
        refname, separator, symref = line.partition("\t")
        if not separator:
            raise RepositoryScanError("Git returned a malformed origin ref entry")
        if symref or refname == "refs/remotes/origin/HEAD":
            continue
        revisions.append(refname)
    revisions = sorted(set(revisions))
    if not revisions:
        raise RepositoryScanError(
            "no live origin remote-tracking heads are available; fetch them first"
        )
    return tuple(revisions)


class GitObjectReader:
    """Read Git objects through one fail-closed cat-file --batch process."""

    def __init__(self, root: Path):
        self.root = root
        self.process: subprocess.Popen[bytes] | None = None
        self.cache: dict[str, tuple[str, bytes]] = {}

    def __enter__(self) -> "GitObjectReader":
        self.process = subprocess.Popen(
            ["git", "cat-file", "--batch"],
            cwd=self.root,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return self

    def read(self, object_id: str) -> tuple[str, bytes]:
        if object_id in self.cache:
            return self.cache[object_id]
        if (
            self.process is None
            or self.process.stdin is None
            or self.process.stdout is None
        ):
            raise RepositoryScanError("Git object reader is not active")
        self.process.stdin.write(object_id.encode("ascii") + b"\n")
        self.process.stdin.flush()
        header = self.process.stdout.readline().rstrip(b"\n")
        fields = header.split()
        if len(fields) != 3:
            raise RepositoryScanError(
                f"cannot read required Git object {object_id}"
            )
        returned_id, encoded_type, encoded_size = fields
        if returned_id.decode("ascii", errors="replace") != object_id:
            raise RepositoryScanError(
                f"Git returned the wrong object for {object_id}"
            )
        try:
            object_type = encoded_type.decode("ascii")
            size = int(encoded_size)
        except (UnicodeDecodeError, ValueError) as exc:
            raise RepositoryScanError(
                f"Git returned malformed metadata for {object_id}"
            ) from exc
        data = self.process.stdout.read(size)
        delimiter = self.process.stdout.read(1)
        if len(data) != size or delimiter != b"\n":
            raise RepositoryScanError(f"Git truncated object {object_id}")
        result = (object_type, data)
        self.cache[object_id] = result
        return result

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self.process is None:
            return
        if self.process.stdin is not None:
            self.process.stdin.close()
        stderr = (
            self.process.stderr.read()
            if self.process.stderr is not None
            else b""
        )
        return_code = self.process.wait()
        if exc_type is None and return_code != 0:
            detail = stderr.decode("utf-8", errors="replace").strip()
            raise RepositoryScanError(
                "git cat-file --batch failed" + (f": {detail}" if detail else "")
            )


def _is_text_like_path(path: str) -> bool:
    return Path(path).suffix.lower() in _TEXT_SUFFIXES


def decode_text_blob(data: bytes, path: str = "") -> str | None:
    if len(data) > _MAX_TEXT_BLOB_BYTES:
        if _is_text_like_path(path):
            raise RepositoryScanError(f"text-like blob exceeds size limit: {path}")
        return None
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        try:
            return data.decode("utf-16")
        except UnicodeDecodeError as exc:
            raise RepositoryScanError(
                f"text-like blob is invalid UTF-16: {path}"
            ) from exc
    if b"\0" in data:
        if _is_text_like_path(path):
            raise RepositoryScanError(f"text-like blob contains NUL bytes: {path}")
        return None
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        if _is_text_like_path(path):
            raise RepositoryScanError(
                f"text-like blob is not valid UTF-8: {path}"
            ) from exc
        return None


def scan_targets(root: Path, targets: tuple[ScanTarget, ...]) -> ScanResult:
    findings: list[Finding] = []
    tracked_count = 0
    scanned_text_count = 0
    skipped_non_text_count = 0
    decoded_cache: dict[tuple[str, str], str | None] = {}

    with GitObjectReader(root) as reader:
        for target in targets:
            for entry in target.entries:
                tracked_count += 1
                object_type, data = reader.read(entry.object_id)
                if object_type != entry.expected_type:
                    raise RepositoryScanError(
                        f"object type mismatch for {target.label}:{entry.path}"
                    )
                if object_type != "blob":
                    skipped_non_text_count += 1
                    continue
                cache_key = (entry.object_id, Path(entry.path).suffix.lower())
                if cache_key not in decoded_cache:
                    decoded_cache[cache_key] = decode_text_blob(data, entry.path)
                text = decoded_cache[cache_key]
                if text is None:
                    skipped_non_text_count += 1
                    continue
                scanned_text_count += 1
                display_path = (
                    entry.path
                    if target.label == "index"
                    else f"{target.label}:{entry.path}"
                )
                findings.extend(scan_text(display_path, text))

    return ScanResult(
        findings=tuple(sorted(findings)),
        tracked_count=tracked_count,
        scanned_text_count=scanned_text_count,
        skipped_non_text_count=skipped_non_text_count,
        targets=tuple(target.label for target in targets),
    )


def scan_repository(root: Path = ROOT) -> ScanResult:
    root = root.resolve()
    return scan_targets(root, (index_target(root),))


def scan_refs(root: Path, revisions: tuple[str, ...]) -> ScanResult:
    root = root.resolve()
    if not revisions:
        raise RepositoryScanError("at least one exact Git revision is required")
    return scan_targets(
        root,
        tuple(ref_target(root, revision) for revision in revisions),
    )


def scan_origin_heads(root: Path = ROOT) -> ScanResult:
    root = root.resolve()
    return scan_refs(root, origin_head_revisions(root))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--index",
        action="store_true",
        help="scan the current Git index (the default when no ref mode is selected)",
    )
    parser.add_argument(
        "--ref",
        action="append",
        default=[],
        help="scan one exact commit-ish; repeat for multiple refs",
    )
    parser.add_argument(
        "--all-origin-heads",
        action="store_true",
        help="scan every fetched non-symbolic refs/remotes/origin head",
    )
    args = parser.parse_args(argv)
    if sum((bool(args.index), bool(args.ref), args.all_origin_heads)) > 1:
        parser.error("--index, --ref, and --all-origin-heads are mutually exclusive")

    try:
        if args.all_origin_heads:
            result = scan_origin_heads(args.root)
        elif args.ref:
            result = scan_refs(args.root, tuple(args.ref))
        else:
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
        f"({len(result.targets)} target(s); "
        f"{result.scanned_text_count} UTF text blobs scanned; "
        f"{result.skipped_non_text_count} non-text objects skipped; "
        f"{result.tracked_count} tracked entries)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
