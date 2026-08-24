#!/usr/bin/env python3
"""Validate the public Logos portfolio, evidence packet, and frozen design boundary.

Capability classification: ``portable_core``. This deterministic validator reads
only repository files and imports the doctrine-mesh static validator from the
same revision. It performs no network or model call and writes no files. A pass
proves only the schema, evidence-reference, privacy-pattern, navigation, diagram,
mesh-manifest, and frozen-specification contracts implemented here. It does not
prove semantic or theological correctness, runtime readiness, source authority,
publication authority, or complete security coverage.

Unreadable or malformed inputs fail closed. Material changes to the portfolio,
evidence schema, doctrine-mesh freeze, authority rules, or validation runtime
require a fresh run and review. Rollback consists of removing this command from
the validation contract together with the public packet; rollback cannot erase a
release already fetched by another party.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Any, Iterable

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
PACKET_ROOT = ROOT / "docs/portfolio/logos-trust-layer"
MANIFEST_PATH = PACKET_ROOT / "project-evidence.yaml"
SCHEMA_PATH = PACKET_ROOT / "project-evidence.schema.json"
PORTFOLIO_PATH = ROOT / "PORTFOLIO.md"
DOCTRINE_ROOT = (
    ROOT
    / "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2"
)
DOCTRINE_VALIDATOR_PATH = DOCTRINE_ROOT / "checks/validate_doctrine_mesh.py"
ARTIFACT_CLASS = "portable_core"

EXPECTED_REPOSITORIES = {
    "logos-governance-architecture",
    "logos-scripture-graph",
    "logos-boundary-literature",
    "logos-doctrine-genealogy",
}
EXPECTED_NAVIGATION_FILES = (
    "README.md",
    "AI_FRONT_DOOR.md",
    "AI_TABLE_OF_CONTENTS.md",
    "AI_WORK_START_HERE.md",
)
EXPECTED_PUBLIC_FILES = (
    "PORTFOLIO.md",
    "docs/portfolio/logos-trust-layer/README.md",
    "docs/portfolio/logos-trust-layer/AI-INTERROGATION-PROMPT.md",
    "docs/portfolio/logos-trust-layer/project-evidence.schema.json",
    "docs/portfolio/logos-trust-layer/project-evidence.yaml",
    "docs/portfolio/logos-trust-layer/agent-mesh-manifest.json",
    "docs/portfolio/logos-trust-layer/validation-receipt.json",
    "scripts/validate_portfolio_front_door.py",
    "tests/test_portfolio_front_door.py",
)
REQUIRED_BOUNDARY_TEXT = (
    "validated design, not a running system",
    "not a completed doctrine corpus",
    "not qualified theological authority",
)
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".txt"}

CHAT_LOCAL_LOCATOR = re.compile(r"turn[0-9]+(?:search|fetch|view)[0-9]+", re.I)
WINDOWS_PRIVATE_PATH = re.compile(
    r"(?i)(?:[a-z]:[\\/](?:users|wt|tmp|git)(?:[\\/]|$)|c:/users/)"
)
PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
GITHUB_TOKEN = re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")
AWS_ACCESS_KEY = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
GENERIC_SECRET = re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")


class PortfolioValidationError(RuntimeError):
    """Raised when a required portfolio input cannot be validated safely."""


@dataclass(frozen=True, order=True)
class Finding:
    rule: str
    path: str
    detail: str

    def render(self) -> str:
        return f"{self.rule}: {self.path}: {self.detail}"


@dataclass(frozen=True)
class ValidationResult:
    findings: tuple[Finding, ...]
    metrics: dict[str, int]

    @property
    def passed(self) -> bool:
        return not self.findings


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PortfolioValidationError(f"cannot load JSON {path}: {exc}") from exc


def _load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise PortfolioValidationError(f"cannot load YAML {path}: {exc}") from exc


def _canonical_digest(value: dict[str, Any], omitted: Iterable[str] = ()) -> str:
    payload = {key: item for key, item in value.items() if key not in set(omitted)}
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _safe_repo_path(value: str) -> Path:
    if not isinstance(value, str) or not value:
        raise PortfolioValidationError("evidence path is missing")
    posix = PurePosixPath(value)
    if posix.is_absolute() or any(part in {"", ".", ".."} for part in posix.parts):
        raise PortfolioValidationError(f"unsafe repository path: {value!r}")
    if re.match(r"^[A-Za-z]:", value) or "\\" in value:
        raise PortfolioValidationError(f"non-portable repository path: {value!r}")
    return Path(*posix.parts)


def _is_private_use(character: str) -> bool:
    code_point = ord(character)
    return (
        0xE000 <= code_point <= 0xF8FF
        or 0xF0000 <= code_point <= 0xFFFFD
        or 0x100000 <= code_point <= 0x10FFFD
    )


def scan_public_text(path: str, text: str) -> list[Finding]:
    """Return privacy/sensitive-pattern findings without echoing matched content."""

    findings: list[Finding] = []
    rules = (
        ("windows_private_path", WINDOWS_PRIVATE_PATH),
        ("file_uri", re.compile(r"file://", re.I)),
        ("chat_local_locator", CHAT_LOCAL_LOCATOR),
        ("private_key_marker", PRIVATE_KEY),
        ("github_token_shape", GITHUB_TOKEN),
        ("aws_access_key_shape", AWS_ACCESS_KEY),
        ("generic_secret_shape", GENERIC_SECRET),
    )
    for line_number, line in enumerate(text.splitlines(), start=1):
        if any(_is_private_use(character) for character in line):
            findings.append(Finding("unicode_private_use", path, f"line {line_number}"))
        for rule, pattern in rules:
            if pattern.search(line):
                findings.append(Finding(rule, path, f"line {line_number}"))
    return findings


def _public_text_paths(root: Path, packet_root: Path, doctrine_root: Path) -> list[Path]:
    paths = [root / name for name in EXPECTED_NAVIGATION_FILES]
    paths.append(root / "PORTFOLIO.md")
    for directory in (packet_root, doctrine_root):
        for path in directory.rglob("*"):
            if (
                path.is_file()
                and path.suffix.lower() in TEXT_SUFFIXES
                and "__pycache__" not in path.parts
                and path.suffix.lower() != ".pyc"
            ):
                paths.append(path)
    return sorted(set(paths))


def _load_doctrine_validator(validator_path: Path) -> ModuleType:
    try:
        spec = importlib.util.spec_from_file_location(
            "logos_doctrine_mesh_static_validator", validator_path
        )
        if spec is None or spec.loader is None:
            raise PortfolioValidationError("cannot create doctrine validator module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except (OSError, ImportError, AttributeError) as exc:
        raise PortfolioValidationError(
            f"cannot import doctrine validator: {exc}"
        ) from exc


def _check_manifest_schema(
    manifest: dict[str, Any], schema: dict[str, Any], manifest_path: Path, root: Path
) -> list[Finding]:
    findings: list[Finding] = []
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    for error in sorted(validator.iter_errors(manifest), key=lambda item: list(item.path)):
        location = "/".join(str(part) for part in error.absolute_path) or "<root>"
        findings.append(Finding("manifest_schema", str(manifest_path.relative_to(root)), f"{location}: {error.message}"))
    return findings


def _check_evidence_references(manifest: dict[str, Any], root: Path) -> list[Finding]:
    findings: list[Finding] = []
    references: list[dict[str, Any]] = []
    for repository in manifest.get("repositories", []):
        references.extend(repository.get("evidence", []))
    for capability in manifest.get("capabilities", []):
        references.extend(capability.get("evidence", []))
    references.extend(manifest.get("doctrine_mesh_specification", {}).get("evidence", []))

    for reference in references:
        if reference.get("kind") == "github_url":
            target = reference.get("target", "")
            if not target.startswith("https://github.com/lowelltwong-alt/"):
                findings.append(Finding("external_evidence_url", "project-evidence.yaml", "GitHub evidence URL is outside the allowlisted owner"))
            continue
        try:
            relative = _safe_repo_path(reference.get("target", ""))
        except PortfolioValidationError as exc:
            findings.append(Finding("local_evidence_path", "project-evidence.yaml", str(exc)))
            continue
        candidate = root / relative
        if not candidate.exists():
            findings.append(Finding("local_evidence_missing", relative.as_posix(), "referenced evidence does not exist"))

    for route in manifest.get("evidence_routes", []):
        for value in [route.get("start_at", ""), *route.get("then_read", [])]:
            if value.startswith("https://"):
                continue
            try:
                relative = _safe_repo_path(value)
            except PortfolioValidationError as exc:
                findings.append(Finding("route_path", "project-evidence.yaml", str(exc)))
                continue
            if not (root / relative).exists():
                findings.append(Finding("route_target_missing", relative.as_posix(), "route target does not exist"))
    return findings


def _check_repository_inventory(manifest: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    repositories = manifest.get("repositories", [])
    ids = [item.get("repository_id") for item in repositories]
    if set(ids) != EXPECTED_REPOSITORIES or len(ids) != len(set(ids)):
        findings.append(Finding("repository_inventory", "project-evidence.yaml", "repository IDs must equal the four unique Logos public repositories"))

    fields = (
        "tracked_files",
        "json_paths",
        "yaml_paths",
        "schema_like_paths",
        "validator_like_paths",
        "test_like_paths",
    )
    declared_totals = manifest.get("snapshot", {}).get("totals", {})
    for field in fields:
        actual = sum(int(item.get("counts", {}).get(field, 0)) for item in repositories)
        if declared_totals.get(field) != actual:
            findings.append(Finding("repository_total", "project-evidence.yaml", f"{field} total does not equal repository rows"))
    return findings


def _check_agent_mesh(root: Path) -> list[Finding]:
    relative = Path("docs/portfolio/logos-trust-layer/agent-mesh-manifest.json")
    mesh = _load_json(root / relative)
    findings: list[Finding] = []
    if mesh.get("schema_version") != "dad.task_local_agent_mesh_manifest.v1":
        findings.append(Finding("mesh_schema", relative.as_posix(), "unexpected schema version"))
    roles = mesh.get("roles", [])
    role_ids = [role.get("role_id") for role in roles]
    if len(role_ids) != len(set(role_ids)):
        findings.append(Finding("mesh_roles", relative.as_posix(), "duplicate role IDs"))
    if mesh.get("writer_role_id") == mesh.get("checker_role_id"):
        findings.append(Finding("mesh_independence", relative.as_posix(), "writer and checker are identical"))
    if mesh.get("max_delegation_depth") != 1:
        findings.append(Finding("mesh_depth", relative.as_posix(), "delegation depth must remain one"))
    if mesh.get("manifest_digest") != _canonical_digest(mesh, ("manifest_digest",)):
        findings.append(Finding("mesh_digest", relative.as_posix(), "canonical digest mismatch"))
    relation_by_id = {role.get("role_id"): role.get("writer_checker_relation") for role in roles}
    if relation_by_id.get(mesh.get("writer_role_id")) != "writer":
        findings.append(Finding("mesh_writer", relative.as_posix(), "writer role relation is invalid"))
    if relation_by_id.get(mesh.get("checker_role_id")) != "checker":
        findings.append(Finding("mesh_checker", relative.as_posix(), "checker role relation is invalid"))
    return findings


def _check_doctrine_freeze(
    manifest: dict[str, Any], doctrine_root: Path, validator_path: Path, root: Path
) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    doctrine = manifest.get("doctrine_mesh_specification", {})
    managed_files = [
        path
        for path in doctrine_root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    ]
    if len(managed_files) != doctrine.get("release_file_count"):
        findings.append(Finding("doctrine_release_count", str(doctrine_root.relative_to(root)), "managed file count does not match public evidence"))

    revision = _load_yaml(doctrine_root / "revision-manifest.yaml")
    final_saved = _load_yaml(doctrine_root / "FINAL-SAVED-VERSION.yaml")
    receipt = _load_json(doctrine_root / "checks/validation-receipt.json")
    review = _load_json(doctrine_root / "checks/independent-review.json")

    comparisons = {
        "payload_file_count": revision.get("payload_file_count"),
        "payload_digest": revision.get("payload_digest"),
        "revision_manifest_digest": revision.get("manifest_digest"),
        "final_saved_version_digest": final_saved.get("final_digest"),
        "independent_review_status": review.get("status"),
        "independence_status": review.get("independence_status"),
        "cross_provider_verified": review.get("cross_provider_verified"),
    }
    for field, observed in comparisons.items():
        if doctrine.get(field) != observed:
            findings.append(Finding("doctrine_freeze_value", "project-evidence.yaml", f"{field} disagrees with frozen evidence"))

    expected_flags = {
        "runtime_activation_authorized": False,
        "source_ingestion_authorized": False,
        "substantive_doctrine_implementation_authorized": False,
        "completed_doctrine_corpus": False,
        "qualified_theological_authority": False,
    }
    for field, expected in expected_flags.items():
        if doctrine.get(field) is not expected:
            findings.append(Finding("doctrine_authority_boundary", "project-evidence.yaml", f"{field} must remain false"))

    if final_saved.get("publication_authorized") is not doctrine.get("freeze_publication_authorized"):
        findings.append(Finding("doctrine_freeze_publication", "project-evidence.yaml", "freeze-time publication flag disagrees with saved artifact"))
    if receipt.get("status") != "pass_artifact_specification_only":
        findings.append(Finding("doctrine_receipt", "checks/validation-receipt.json", "unexpected specification receipt status"))
    if receipt.get("test_result", {}).get("test_count") != doctrine.get("adversarial_test_count"):
        findings.append(Finding("doctrine_test_count", "checks/validation-receipt.json", "test count disagrees with public evidence"))

    module = _load_doctrine_validator(validator_path)
    try:
        doctrine_failures, checks = module.validate_revision(doctrine_root, "final")
    except Exception as exc:  # fail closed around the revision-owned validator
        raise PortfolioValidationError(f"doctrine validator failed to execute: {exc}") from exc
    for failure in doctrine_failures:
        findings.append(Finding("doctrine_static_validator", str(validator_path.relative_to(root)), str(failure)))

    expected_metrics = {
        "parsed_structured_files": "structured_file_count",
        "mesh_roles": "capability_role_count",
        "domain_profiles": "expert_profile_count",
        "graph_nodes": "graph_node_count",
        "graph_edges": "graph_edge_count",
    }
    for check_key, manifest_key in expected_metrics.items():
        if checks.get(check_key) != doctrine.get(manifest_key):
            findings.append(Finding("doctrine_metric", "project-evidence.yaml", f"{manifest_key} disagrees with static replay"))

    return findings, {
        "doctrine_managed_files": len(managed_files),
        "doctrine_static_failures": len(doctrine_failures),
    }


def _check_portfolio_prose(root: Path) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    try:
        text = (root / "PORTFOLIO.md").read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise PortfolioValidationError(f"cannot read PORTFOLIO.md: {exc}") from exc
    lowered = text.lower()
    for required in REQUIRED_BOUNDARY_TEXT:
        if required not in lowered:
            findings.append(Finding("portfolio_boundary_text", "PORTFOLIO.md", f"missing required boundary: {required}"))
    mermaid_count = text.count("```mermaid")
    prose_count = text.count("Plain-language reading:")
    if mermaid_count < 5:
        findings.append(Finding("portfolio_diagrams", "PORTFOLIO.md", "at least five Mermaid diagrams are required"))
    if prose_count != mermaid_count:
        findings.append(Finding("portfolio_diagram_accessibility", "PORTFOLIO.md", "each Mermaid diagram needs one plain-language reading"))
    return findings, {"mermaid_diagrams": mermaid_count, "diagram_prose_readings": prose_count}


def _check_navigation(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for relative in EXPECTED_NAVIGATION_FILES:
        try:
            text = (root / relative).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise PortfolioValidationError(f"cannot read navigation file {relative}: {exc}") from exc
        if "PORTFOLIO.md" not in text:
            findings.append(Finding("portfolio_navigation", relative, "missing root portfolio link"))
    return findings


def _check_receipt(root: Path) -> list[Finding]:
    relative = Path("docs/portfolio/logos-trust-layer/validation-receipt.json")
    receipt = _load_json(root / relative)
    findings: list[Finding] = []
    required = {
        "schema_version": "logos.portfolio_validation_receipt.v1",
        "status": "pass_release_candidate",
        "work_id": "WORK-GOV-LOGOS-STEWARDSHIP-BUILDOUT-001",
        "doctrine_mesh_status": "validated_specification_only",
    }
    for field, expected in required.items():
        if receipt.get(field) != expected:
            findings.append(Finding("portfolio_receipt", relative.as_posix(), f"{field} must equal {expected}"))
    if receipt.get("runtime_activation_authorized") is not False:
        findings.append(Finding("portfolio_receipt_authority", relative.as_posix(), "runtime activation must remain false"))
    if receipt.get("receipt_digest") != _canonical_digest(receipt, ("receipt_digest",)):
        findings.append(Finding("portfolio_receipt_digest", relative.as_posix(), "canonical digest mismatch"))
    return findings


def validate_repository(root: Path = ROOT) -> ValidationResult:
    root = root.resolve()
    packet_root = root / "docs/portfolio/logos-trust-layer"
    manifest_path = packet_root / "project-evidence.yaml"
    schema_path = packet_root / "project-evidence.schema.json"
    doctrine_root = root / "docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-mesh-v2"
    doctrine_validator_path = doctrine_root / "checks/validate_doctrine_mesh.py"

    for relative in EXPECTED_PUBLIC_FILES:
        if not (root / relative).is_file():
            raise PortfolioValidationError(f"required public file is missing: {relative}")

    manifest = _load_yaml(manifest_path)
    schema = _load_json(schema_path)
    if not isinstance(manifest, dict) or not isinstance(schema, dict):
        raise PortfolioValidationError("manifest and schema must be objects")

    findings: list[Finding] = []
    findings.extend(_check_manifest_schema(manifest, schema, manifest_path, root))
    findings.extend(_check_evidence_references(manifest, root))
    findings.extend(_check_repository_inventory(manifest))
    findings.extend(_check_agent_mesh(root))
    doctrine_findings, doctrine_metrics = _check_doctrine_freeze(
        manifest, doctrine_root, doctrine_validator_path, root
    )
    findings.extend(doctrine_findings)
    prose_findings, prose_metrics = _check_portfolio_prose(root)
    findings.extend(prose_findings)
    findings.extend(_check_navigation(root))
    findings.extend(_check_receipt(root))

    scanned_count = 0
    for path in _public_text_paths(root, packet_root, doctrine_root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        except OSError as exc:
            raise PortfolioValidationError(f"cannot read public text {path}: {exc}") from exc
        scanned_count += 1
        findings.extend(scan_public_text(path.relative_to(root).as_posix(), text))

    metrics = {
        "manifest_repositories": len(manifest.get("repositories", [])),
        "manifest_capabilities": len(manifest.get("capabilities", [])),
        "public_text_files_scanned": scanned_count,
        **doctrine_metrics,
        **prose_metrics,
    }
    return ValidationResult(tuple(sorted(set(findings))), metrics)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = validate_repository(args.root)
    except PortfolioValidationError as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, sort_keys=True))
        return 1
    payload = {
        "status": "pass" if result.passed else "fail",
        "artifact_class": ARTIFACT_CLASS,
        "metrics": result.metrics,
        "findings": [finding.render() for finding in result.findings],
        "mutation_performed": False,
        "authority_granted": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
