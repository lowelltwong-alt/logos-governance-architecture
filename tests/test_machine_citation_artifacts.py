from __future__ import annotations

import subprocess
import unicodedata
from pathlib import Path

import pytest

from scripts import validate_machine_citation_artifacts as validator


def locator(channel: str = "search") -> str:
    return "".join(("turn", "17", channel, "4"))


def percent_encode(value: str) -> str:
    return "".join(f"%{byte:02X}" for byte in value.encode("utf-8"))


def attachment_path() -> str:
    return "/".join(
        ("C:", "Users", "person", ".codex", "attachments", "id", "pasted-text.txt")
    )


def run_git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return completed.stdout.strip()


def initialize_repository(root: Path) -> None:
    run_git(root, "init")
    run_git(root, "config", "user.name", "Validator Test")
    run_git(root, "config", "user.email", "validator@example.invalid")


@pytest.mark.parametrize(
    "code_point",
    [0xE000, 0xF8FF, 0xF0000, 0xFFFFD, 0x100000, 0x10FFFD],
)
def test_all_private_use_ranges_are_detected(code_point: int) -> None:
    assert validator.is_private_use(chr(code_point))


@pytest.mark.parametrize(
    "code_point",
    [0xDFFF, 0xF900, 0xEFFFF, 0xFFFFE, 0xFFFFF, 0x10FFFE],
)
def test_private_use_boundaries_do_not_expand(code_point: int) -> None:
    assert not validator.is_private_use(chr(code_point))


@pytest.mark.parametrize("channel", ["search", "fetch", "view", "SEARCH"])
def test_chat_local_locator_family_is_detected(channel: str) -> None:
    assert validator.CHAT_LOCATOR_RE.search(locator(channel))


@pytest.mark.parametrize(
    "value",
    [
        "turning search results",
        "turn-search-4",
        "search17turn4",
        "turn17query4",
    ],
)
def test_nearby_safe_text_is_not_detected(value: str) -> None:
    assert validator.scan_text("example.md", value) == []


@pytest.mark.parametrize(
    "value",
    [
        "".join(("\\", "u", "E200")),
        "".join(("&#", "xE200;")),
        percent_encode(chr(0xE200)),
        "".join(("\\", "U", "000F0000")),
        "".join(("\\", "u", "DB80", "\\", "u", "DC00")),
    ],
)
def test_encoded_private_use_markers_are_detected(value: str) -> None:
    assert validator.scan_text("example.md", value) == [
        validator.Finding("example.md", 1, validator.ENCODED_PRIVATE_USE_RULE)
    ]


@pytest.mark.parametrize(
    "value",
    [
        "turn17" + chr(0x200B) + "search4",
        "turn17" + chr(0x202E) + "search4",
        "turn17" + chr(0x1F) + "search4",
        percent_encode("turn17" + chr(0x1F) + "search4"),
        "".join(("t", "&#x75;", "rn17search4")),
        percent_encode(locator()),
        "".join(
            chr(ord(character) + 0xFEE0)
            if "!" <= character <= "~"
            else character
            for character in locator()
        ),
    ],
)
def test_encoded_or_invisible_locators_are_detected(value: str) -> None:
    assert validator.scan_text("example.md", value) == [
        validator.Finding(
            "example.md",
            1,
            validator.OBFUSCATED_CHAT_LOCATOR_RULE,
        )
    ]


@pytest.mark.parametrize(
    "value",
    [
        attachment_path(),
        "file:///" + attachment_path(),
        "file:///" + percent_encode(attachment_path()),
        attachment_path().replace("/", "\\"),
    ],
)
def test_local_profile_attachment_paths_are_detected(value: str) -> None:
    assert validator.scan_text("example.md", value) == [
        validator.Finding("example.md", 1, validator.LOCAL_ATTACHMENT_RULE)
    ]


@pytest.mark.parametrize(
    "value",
    [
        "local-only attachment 84c88835-597b-49f3-9f21-791be3bd6e6e "
        "(path redacted; original retained offline)",
        "external_attachment_ref: governed-asset-id",
        "https://example.com/attachments/public-evidence.json",
    ],
)
def test_governed_attachment_references_do_not_match(value: str) -> None:
    assert validator.scan_text("example.md", value) == []


def test_findings_report_location_and_rule_without_payload() -> None:
    sensitive_payload = "do-not-echo-this-payload"
    text = f"{sensitive_payload} {chr(0xE200)}\n{sensitive_payload} {locator()}"

    rendered = [
        finding.render() for finding in validator.scan_text("example.md", text)
    ]

    assert rendered == [
        f"example.md:1: {validator.PRIVATE_USE_RULE}",
        f"example.md:2: {validator.CHAT_LOCATOR_RULE}",
    ]
    assert all(sensitive_payload not in item for item in rendered)


def test_binary_and_non_utf8_non_text_blobs_are_skipped() -> None:
    assert validator.decode_text_blob(b"text\0binary") is None
    assert validator.decode_text_blob(bytes([0xFF])) is None


def test_invalid_text_like_blob_fails_closed() -> None:
    with pytest.raises(validator.RepositoryScanError, match="not valid UTF-8"):
        validator.decode_text_blob(bytes([0xFF]), "evidence.md")
    with pytest.raises(validator.RepositoryScanError, match="contains NUL"):
        validator.decode_text_blob(b"text\0binary", "evidence.yaml")


def test_utf16_text_like_blob_is_scanned() -> None:
    decoded = validator.decode_text_blob(locator().encode("utf-16"), "evidence.txt")

    assert decoded is not None
    assert validator.scan_text("evidence.txt", decoded) == [
        validator.Finding("evidence.txt", 1, validator.CHAT_LOCATOR_RULE)
    ]


@pytest.mark.parametrize("value", ["", "/absolute", "../escape", "safe/../escape"])
def test_unsafe_git_paths_fail_closed(value: str) -> None:
    with pytest.raises(validator.RepositoryScanError):
        validator._relative_git_path(value)


def test_default_scan_reads_index_not_mutable_worktree(tmp_path: Path) -> None:
    initialize_repository(tmp_path)
    evidence = tmp_path / "evidence.md"
    evidence.write_text("safe evidence\n", encoding="utf-8")
    run_git(tmp_path, "add", "evidence.md")

    evidence.write_text(locator() + "\n", encoding="utf-8")
    clean_index = validator.scan_repository(tmp_path)

    assert clean_index.findings == ()
    run_git(tmp_path, "add", "evidence.md")
    contaminated_index = validator.scan_repository(tmp_path)
    assert [finding.rule for finding in contaminated_index.findings] == [
        validator.CHAT_LOCATOR_RULE
    ]


def test_exact_ref_scan_does_not_read_worktree(tmp_path: Path) -> None:
    initialize_repository(tmp_path)
    evidence = tmp_path / "evidence.md"
    evidence.write_text("safe evidence\n", encoding="utf-8")
    run_git(tmp_path, "add", "evidence.md")
    run_git(tmp_path, "commit", "-m", "safe")
    safe_commit = run_git(tmp_path, "rev-parse", "HEAD")

    evidence.write_text(locator() + "\n", encoding="utf-8")
    run_git(tmp_path, "add", "evidence.md")
    run_git(tmp_path, "commit", "-m", "contaminated")
    bad_commit = run_git(tmp_path, "rev-parse", "HEAD")
    evidence.write_text("untracked mutable state\n", encoding="utf-8")

    assert validator.scan_refs(tmp_path, (safe_commit,)).findings == ()
    bad_result = validator.scan_refs(tmp_path, (bad_commit,))
    assert [finding.rule for finding in bad_result.findings] == [
        validator.CHAT_LOCATOR_RULE
    ]
    with pytest.raises(validator.RepositoryScanError, match="failed"):
        validator.scan_refs(tmp_path, ("missing-ref",))


def test_all_origin_heads_scan_every_non_symbolic_remote_head(tmp_path: Path) -> None:
    initialize_repository(tmp_path)
    evidence = tmp_path / "evidence.md"
    evidence.write_text("safe evidence\n", encoding="utf-8")
    run_git(tmp_path, "add", "evidence.md")
    run_git(tmp_path, "commit", "-m", "safe")
    safe_commit = run_git(tmp_path, "rev-parse", "HEAD")

    evidence.write_text(locator() + "\n", encoding="utf-8")
    run_git(tmp_path, "add", "evidence.md")
    run_git(tmp_path, "commit", "-m", "contaminated")
    bad_commit = run_git(tmp_path, "rev-parse", "HEAD")
    run_git(tmp_path, "update-ref", "refs/remotes/origin/main", safe_commit)
    run_git(tmp_path, "update-ref", "refs/remotes/origin/bad", bad_commit)

    result = validator.scan_origin_heads(tmp_path)

    assert len(result.targets) == 2
    assert [finding.rule for finding in result.findings] == [
        validator.CHAT_LOCATOR_RULE
    ]
    assert "refs/remotes/origin/bad@" in result.findings[0].path


def test_all_origin_heads_fails_when_no_heads_are_fetched(tmp_path: Path) -> None:
    initialize_repository(tmp_path)

    with pytest.raises(validator.RepositoryScanError, match="fetch them first"):
        validator.scan_origin_heads(tmp_path)


def test_current_tracked_index_is_clean() -> None:
    root = Path(__file__).resolve().parents[1]

    result = validator.scan_repository(root)

    assert result.findings == ()
    assert result.scanned_text_count > 0
    assert result.tracked_count == (
        result.scanned_text_count + result.skipped_non_text_count
    )


@pytest.mark.parametrize(
    "path",
    [
        Path(validator.__file__),
        Path(__file__),
        Path(__file__).with_name("test_validation_contracts.py"),
    ],
)
def test_validator_sources_do_not_self_match(path: Path) -> None:
    assert validator.scan_text(path.name, path.read_text(encoding="utf-8")) == []


def test_fullwidth_normalization_is_bounded_to_detection() -> None:
    value = "".join(
        chr(ord(character) + 0xFEE0) if "!" <= character <= "~" else character
        for character in locator()
    )

    assert unicodedata.normalize("NFKC", value) == locator()
