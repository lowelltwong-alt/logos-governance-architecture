#!/usr/bin/env python3
"""Run the V3 high-risk aggregate sentinel from fresh copied roots.

This runner is an assurance adapter, not a runtime or doctrine implementation.
It invokes ``validate_all('draft')`` directly so findings retain validator
emission order.  It never parses the presentation-sorted CLI output.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CATALOG = HERE / "fixtures" / "aggregate-sentinel-cases.json"
sys.path.insert(0, str(HERE))

import validate_doctrine_marathon as validator  # noqa: E402


SOURCE_SENTINELS = (
    "constitution.yaml",
    "mesh/agent-mesh.v3.json",
    "DOCTRINE_MARATHON_MASTER_PROMPT.md",
    "checks/validate_doctrine_marathon.py",
    "checks/run_adversarial_harness.py",
)


def file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def finding_identity(value: str) -> dict[str, str]:
    rule = value.split(":", 1)[0]
    return {"rule": rule, "identity": value}


def ordered_findings(values: list[str]) -> list[dict[str, str]]:
    result = [finding_identity(value) for value in values]
    keys = [(row["rule"], row["identity"]) for row in result]
    if len(keys) != len(set(keys)):
        raise AssertionError("aggregate validator emitted duplicate finding identities")
    return result


def load_catalog() -> list[dict[str, Any]]:
    value = json.loads(CATALOG.read_text(encoding="utf-8"))
    if set(value) != {"metadata", "schema_version", "assurance_scope", "cases"}:
        raise AssertionError("aggregate sentinel catalog root keys drifted")
    if value["schema_version"] != "logos.doctrine-marathon.aggregate-sentinel-catalog.v1":
        raise AssertionError("aggregate sentinel catalog schema drifted")
    if value["assurance_scope"] != "aggregate_sentinel_only_not_full_legacy_migration":
        raise AssertionError("aggregate sentinel assurance boundary drifted")
    cases = value["cases"]
    if not isinstance(cases, list) or not cases:
        raise AssertionError("aggregate sentinel catalog is empty")
    ids = [row.get("case_id") for row in cases]
    if len(ids) != len(set(ids)):
        raise AssertionError("aggregate sentinel case IDs are not unique")
    return cases


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def tree_digests(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): file_digest(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }


def reseal_assignment_dependencies(root: Path, target_ref: str, digest: str) -> None:
    assignment_path = root / "mesh/examples/design-time-independence-fixture.json"
    assignment = json.loads(assignment_path.read_text(encoding="utf-8"))
    replacements = 0
    for row in assignment["assignments"]:
        basis = row["qualification_basis"]
        if basis["ref"] == target_ref:
            basis["digest"] = digest
            replacements += 1
        for source in row["source_order"]:
            if source["source_ref"] == target_ref:
                source["source_digest"] = digest
                replacements += 1
        row["source_order_digest"] = validator.object_digest(row["source_order"])
    if replacements < 1:
        raise AssertionError(
            f"{target_ref} has no assignment dependency binding"
        )
    assignment["bundle_digest"] = validator.object_digest(
        assignment, omit=("bundle_digest",)
    )
    write_json(assignment_path, assignment)


def reseal_checkpoint_controls(root: Path, updates: dict[str, str]) -> None:
    checkpoint_path = root / "state/examples/initial-resume-checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    unknown = set(updates) - set(checkpoint)
    if unknown:
        raise AssertionError(f"checkpoint reseal fields are unknown: {sorted(unknown)}")
    checkpoint.update(updates)
    write_json(checkpoint_path, checkpoint)
    checkpoint_digest = validator.file_digest(checkpoint_path)

    for relative in (
        "state/examples/terminal-handoff-blocked.json",
        "state/examples/initial-weekly-fresh-context-gate.json",
    ):
        dependent_path = root / relative
        dependent = json.loads(dependent_path.read_text(encoding="utf-8"))
        dependent["checkpoint_digest"] = checkpoint_digest
        write_json(dependent_path, dependent)


def reseal_constitution_dependencies(root: Path, digest: str) -> None:
    reseal_assignment_dependencies(root, "constitution.yaml", digest)

    graph_path = root / "graph/example-graph.json"
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    for node in graph["nodes"]:
        if node.get("content_ref") == "constitution.yaml":
            node["content_digest"] = digest
    for edge in graph["edges"]:
        for index, ref in enumerate(edge.get("basis_refs", [])):
            if ref == "constitution.yaml":
                edge["basis_digests"][index] = digest
    graph["graph_digest"] = validator.object_digest(graph, omit=("graph_digest",))
    write_json(graph_path, graph)
    graph_digest = validator.file_digest(graph_path)

    debt_path = root / "debt/initial-review-debt.json"
    debts = json.loads(debt_path.read_text(encoding="utf-8"))
    for row in debts:
        row["dependency_graph_digest"] = graph_digest
        if row.get("human_gate_registry_ref") == "constitution.yaml":
            row["human_gate_registry_digest"] = digest
        if row.get("acceptance_rubric_ref") == "constitution.yaml":
            row["acceptance_rubric_digest"] = digest
    write_json(debt_path, debts)
    reseal_checkpoint_controls(
        root,
        {
            "constitution_digest": digest,
            "dependency_graph_digest": validator.file_digest(graph_path),
            "review_debt_digest": validator.file_digest(debt_path),
        },
    )


def reseal_mesh_dependencies(root: Path, digest: str) -> None:
    reseal_assignment_dependencies(root, "mesh/agent-mesh.v3.json", digest)


def reseal_prompt_dependencies(root: Path, digest: str) -> None:
    reseal_assignment_dependencies(root, "DOCTRINE_MARATHON_MASTER_PROMPT.md", digest)
    reseal_checkpoint_controls(root, {"prompt_digest": digest})


def apply_mutation(root: Path, case: dict[str, Any]) -> None:
    target = root / case["target_ref"]
    mutation = case["mutation_id"]
    if case["case_id"] == "AGG-DMV3-AUTHORITY-RUNTIME":
        value = validator.yaml.safe_load(target.read_text(encoding="utf-8"))
        value["authority"]["runtime_activation_authorized"] = True
        target.write_text(
            validator.yaml.safe_dump(value, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        reseal_constitution_dependencies(root, validator.file_digest(target))
    elif case["case_id"] == "AGG-DMV3-MESH-META-CHECKER":
        value = json.loads(target.read_text(encoding="utf-8"))
        value["roles"] = [
            row
            for row in value["roles"]
            if row["role_id"] != "role-qualification-and-independence-auditor"
        ]
        write_json(target, value)
        reseal_mesh_dependencies(root, validator.file_digest(target))
    elif case["case_id"] == "AGG-DMV3-MESH-WRITER-INDEPENDENCE":
        value = json.loads(target.read_text(encoding="utf-8"))
        value["roles"][0]["checked_by"] = [value["roles"][0]["role_id"]]
        write_json(target, value)
        reseal_mesh_dependencies(root, validator.file_digest(target))
    elif case["case_id"] == "AGG-DMV3-PROMPT-NEUTRALITY":
        target.write_text(
            target.read_text(encoding="utf-8")
            + "\nYour job is to prove the preferred conclusion.\n",
            encoding="utf-8",
        )
        reseal_prompt_dependencies(root, validator.file_digest(target))
    else:
        raise AssertionError(f"unknown aggregate case: {case['case_id']}")
    if mutation not in {"authorize_runtime", "remove_meta_checker", "writer_self_checks", "desired_conclusion"}:
        raise AssertionError(f"unexpected mutation ID: {mutation}")


def run_case(case: dict[str, Any], *, observe: bool) -> dict[str, Any]:
    source_root = validator.ROOT
    before_source = {
        relative: file_digest(ROOT / relative) for relative in SOURCE_SENTINELS
    }
    validator._QUALIFICATION_VALIDATION_CACHE.clear()
    validator._ROLE_ASSIGNMENT_VALIDATION_CACHE.clear()
    try:
        with tempfile.TemporaryDirectory(prefix=f"dmv3-{case['case_id'].lower()}-") as temporary:
            copied_root = Path(temporary) / "doctrine-marathon-v3"
            shutil.copytree(ROOT, copied_root)
            validator.ROOT = copied_root
            baseline_errors, _ = validator.validate_all("draft")
            if baseline_errors:
                raise AssertionError(
                    f"{case['case_id']} baseline was not clean: {baseline_errors}"
                )
            target = copied_root / case["target_ref"]
            baseline_target_digest = file_digest(target)
            baseline_tree = tree_digests(copied_root)
            apply_mutation(copied_root, case)
            candidate_target_digest = file_digest(target)
            if candidate_target_digest == baseline_target_digest:
                raise AssertionError(f"{case['case_id']} mutation was a byte no-op")
            candidate_tree = tree_digests(copied_root)
            changed_paths = sorted(set(baseline_tree) | set(candidate_tree))
            changed_files = [
                {
                    "path": relative,
                    "baseline_digest": baseline_tree.get(relative),
                    "candidate_digest": candidate_tree.get(relative),
                    "change_role": (
                        "intended_target"
                        if relative == case["target_ref"]
                        else "derived_reseal"
                    ),
                }
                for relative in changed_paths
                if baseline_tree.get(relative) != candidate_tree.get(relative)
            ]
            if not changed_files or changed_files[0]["path"] is None:
                raise AssertionError(f"{case['case_id']} has no exact changed-path proof")
            validator._QUALIFICATION_VALIDATION_CACHE.clear()
            validator._ROLE_ASSIGNMENT_VALIDATION_CACHE.clear()
            candidate_errors, _ = validator.validate_all("draft")
            observed = ordered_findings(candidate_errors)
            if not observed:
                raise AssertionError(f"{case['case_id']} produced no aggregate finding")
            if observed[0]["rule"] != case["intended_rule"]:
                raise AssertionError(
                    f"{case['case_id']} intended {case['intended_rule']} but primary was "
                    f"{observed[0]['rule']}: {candidate_errors}"
                )
            expected = case["expected_findings_ordered"]
            if not observe and observed != expected:
                raise AssertionError(
                    f"{case['case_id']} exact ordered findings drifted: "
                    f"expected={expected}; observed={observed}"
                )
            return {
                "case_id": case["case_id"],
                "source_case_id": case["source_case_id"],
                "target_ref": case["target_ref"],
                "baseline_target_digest": baseline_target_digest,
                "candidate_target_digest": candidate_target_digest,
                "changed_files": changed_files,
                "baseline_findings": [],
                "candidate_findings": observed,
                "intended_rule": case["intended_rule"],
                "primary_rule": observed[0]["rule"],
                "aggregate_validator_executed": True,
                "component_only": False,
                "candidate_changed": True,
            }
    finally:
        validator.ROOT = source_root
        validator._QUALIFICATION_VALIDATION_CACHE.clear()
        validator._ROLE_ASSIGNMENT_VALIDATION_CACHE.clear()
        after_source = {
            relative: file_digest(ROOT / relative) for relative in SOURCE_SENTINELS
        }
        if after_source != before_source:
            raise AssertionError("source-root sentinel changed during aggregate replay")


def run_catalog(cases: list[dict[str, Any]], *, observe: bool) -> dict[str, Any]:
    forward = [run_case(case, observe=observe) for case in cases]
    reverse_runs = [run_case(case, observe=observe) for case in reversed(cases)]
    reverse = {row["case_id"]: row for row in reverse_runs}
    for row in forward:
        other = reverse[row["case_id"]]
        if row != other:
            raise AssertionError(
                f"{row['case_id']} changed between forward and reverse replay"
            )
    return {
        "schema_version": "logos.doctrine-marathon.aggregate-sentinel-result.v1",
        "status": "observation_only" if observe else "pass",
        "assurance_scope": "aggregate_sentinel_only_not_full_legacy_migration",
        "case_count": len(forward),
        "forward": forward,
        "reverse_case_order": [row["case_id"] for row in reverse_runs],
        "source_root_mutation_performed": False,
        "runtime_authority": "none",
        "publication_authority": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--observe",
        action="store_true",
        help="Print raw aggregate findings without treating the catalog as frozen evidence.",
    )
    args = parser.parse_args()
    try:
        result = run_catalog(load_catalog(), observe=args.observe)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "fail",
                    "error": f"{type(exc).__name__}: {exc}",
                    "runtime_authority": "none",
                    "publication_authority": "none",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
