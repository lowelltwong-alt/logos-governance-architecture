from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts import validate_internal_links as links


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools" / "logos_governance_fast_validators" / "Cargo.toml"


def run_rust_internal_links(root: Path, *paths: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "cargo",
            "run",
            "--quiet",
            "--manifest-path",
            str(MANIFEST),
            "--",
            "internal-links",
            "--root",
            str(root),
            *paths,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_rust_internal_links_matches_python_pass_fixture(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").write_text(
        "[ok](docs/target.md)\n`docs/config.yaml`\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "target.md").write_text("target\n", encoding="utf-8")
    (tmp_path / "docs" / "config.yaml").write_text("key: value\n", encoding="utf-8")

    python_failures = links.check_markdown_files(tmp_path, [tmp_path / "README.md"])
    rust = run_rust_internal_links(tmp_path)

    assert python_failures == []
    assert rust.returncode == 0
    assert "Internal link validation passed (1 markdown files)." in rust.stdout


def test_rust_internal_links_matches_python_failure_fixture(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("[missing](docs/missing.md)\n", encoding="utf-8")

    python_failures = links.check_markdown_files(tmp_path, [tmp_path / "README.md"])
    rust = run_rust_internal_links(tmp_path)

    assert python_failures == ["README.md: missing local target 'docs/missing.md'"]
    assert rust.returncode == 1
    assert "FAIL README.md: missing local target 'docs/missing.md'" in rust.stdout


def test_python_wrapper_require_rust_uses_fast_validator() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/validate_internal_links.py", "--require-rust"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "Internal link validation passed (1 markdown files)." in completed.stdout


def test_python_wrapper_fallback_runs_python_when_rust_unavailable() -> None:
    env = os.environ.copy()
    env["LOGOS_GOVERNANCE_FAST_VALIDATORS_MANIFEST"] = str(
        ROOT / "tools" / "missing_fast_validators" / "Cargo.toml"
    )
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/validate_internal_links.py",
            "--python-fallback",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "Internal link validation passed (1 markdown files)." in completed.stdout


def test_python_wrapper_require_rust_fails_when_rust_unavailable() -> None:
    env = os.environ.copy()
    env["LOGOS_GOVERNANCE_FAST_VALIDATORS_MANIFEST"] = str(
        ROOT / "tools" / "missing_fast_validators" / "Cargo.toml"
    )
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/validate_internal_links.py",
            "--require-rust",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 2
    assert "Rust fast validator unavailable" in completed.stderr
