from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from scripts import validate_machine_citation_artifacts as validator


def locator(channel: str = "search") -> str:
    return "".join(("turn", "17", channel, "4"))


@pytest.mark.parametrize("code_point", [0xE000, 0xF8FF, 0xF0000, 0xFFFFD, 0x100000, 0x10FFFD])
def test_all_private_use_ranges_are_detected(code_point: int) -> None:
    assert validator.is_private_use(chr(code_point))


@pytest.mark.parametrize("code_point", [0xDFFF, 0xF900, 0xEFFFF, 0xFFFFE, 0xFFFFF, 0x10FFFE])
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
    assert validator.CHAT_LOCATOR_RE.search(value) is None


def test_findings_report_location_and_rule_without_payload() -> None:
    private_marker = chr(0xE200)
    sensitive_payload = "do-not-echo-this-payload"
    text = f"{sensitive_payload} {private_marker}\n{sensitive_payload} {locator()}"

    findings = validator.scan_text("example.md", text)
    rendered = [finding.render() for finding in findings]

    assert rendered == [
        f"example.md:1: {validator.PRIVATE_USE_RULE}",
        f"example.md:2: {validator.CHAT_LOCATOR_RULE}",
    ]
    assert all(sensitive_payload not in item for item in rendered)


def test_binary_and_non_utf8_blobs_are_skipped() -> None:
    assert validator.decode_text_blob(b"text\0binary") is None
    assert validator.decode_text_blob(bytes([0xFF])) is None


def test_tracked_symlink_target_is_scanned_without_dereference() -> None:
    path = Mock(spec=Path)
    path.is_symlink.return_value = True
    path.readlink.return_value = Path(locator())

    text = validator.read_tracked_text(path, "public-link")

    assert text is not None
    assert validator.scan_text("public-link", text) == [
        validator.Finding("public-link", 1, validator.CHAT_LOCATOR_RULE)
    ]
    path.read_bytes.assert_not_called()


def test_unreadable_tracked_symlink_fails_closed() -> None:
    path = Mock(spec=Path)
    path.is_symlink.return_value = True
    path.readlink.side_effect = OSError("unreadable")

    with pytest.raises(validator.RepositoryScanError, match="cannot read tracked symlink"):
        validator.read_tracked_text(path, "public-link")


@pytest.mark.parametrize("value", ["", "/absolute", "../escape", "safe/../escape"])
def test_unsafe_git_paths_fail_closed(value: str) -> None:
    with pytest.raises(validator.RepositoryScanError):
        validator._relative_git_path(value)


def test_current_tracked_public_surface_is_clean() -> None:
    root = Path(__file__).resolve().parents[1]

    result = validator.scan_repository(root)

    assert result.findings == ()
    assert result.scanned_text_count > 0
    assert result.tracked_count == result.scanned_text_count + result.skipped_non_text_count


@pytest.mark.parametrize(
    "path",
    [
        Path(validator.__file__),
        Path(__file__),
        Path(__file__).with_name("test_validation_contracts.py"),
    ],
)
def test_new_validator_sources_do_not_self_match_before_commit(path: Path) -> None:
    assert validator.scan_text(path.name, path.read_text(encoding="utf-8")) == []
