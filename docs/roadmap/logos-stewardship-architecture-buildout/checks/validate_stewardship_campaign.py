#!/usr/bin/env python3
"""Validate the static, non-authorizing stewardship campaign specification.

The validator is intentionally read-only. It prints one JSON receipt to stdout,
never creates controller state, and never interprets a pass as human approval,
runtime qualification, migration permission, or implementation readiness.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import yaml


SCRIPT = Path(__file__).resolve()
CAMPAIGN_ROOT = SCRIPT.parents[1]
REPO_ROOT = SCRIPT.parents[4]

EXPECTED_ADVISORY_ISSUES = [
    "AB-R02-001", "AB-R02-002", "AB-R02-003", "AB-R02-006",
    "AB-R02-009", "AB-R02-013", "AB-R02-015",
]
EXPECTED_ADVISORY_IDS = [f"ADVISORY-{index:03d}" for index in range(1, 8)]
EXPECTED_ADVISORY_HASHES = [
    "4e179aea2d3620c96d58ee5fcbf8dada52ca9c4960e30e57cc52210ac71c4c1f",
    "9769d0f4453d4ec3f0049031208debc229bdbbfbae3fdf9cd1307c48854d3aad",
    "5235a1607e495b5b7b3b7092bc3dc72a4ff3daaa29b42f9149f5dbc0e27a974b",
    "cac88001f2be264800c79b1c475ee9717a037b22f7bc29a0dba81da85bab8874",
    "50272c5db8975a3072f700d864789f44897d6b7594d7d0428c57ff9e40be027e",
    "db6fcf1baa8788aafbfb3c7f33f489dd02b1ff19743a74fe34fce6f4372f0ddd",
    "8db38fc52aa152a7f3d97e1f299f846a30082edc02a6fd661959448bd6473d62",
]
EXPECTED_P0_ISSUES = ["AB-R02-008", "AB-R02-018"]
EXPECTED_P1_ISSUES = [
    "AB-R02-004", "AB-R02-005", "AB-R02-007", "AB-R02-010", "AB-R02-011",
    "AB-R02-012", "AB-R02-014", "AB-R02-016", "AB-R02-017", "AB-R02-019",
]
EXPECTED_RESIDUALS = [f"AB-R03-DIS-{index:03d}" for index in range(1, 6)]
EXPECTED_PUBLIC_P0 = ["BLOCK-P0-001", "BLOCK-P0-002"]
EXPECTED_PUBLIC_P1 = [f"BLOCK-P1-{index:03d}" for index in range(1, 11)]
EXPECTED_PUBLIC_RESIDUALS = [f"RESIDUAL-{index:03d}" for index in range(1, 6)]
EXPECTED_GATE_IDS = [f"HG-{index:03d}" for index in range(1, 15)]
EXPECTED_JOB_IDS = [
    "J-000", "J-001", "J-002", "J-100", "J-110", "J-120", "J-130", "J-140",
    "J-150", "J-200", "J-210", "J-220", "J-300", "J-310", "J-320", "J-400",
]
EXPECTED_CLAIM_ID = "WORK-GOV-LOGOS-STEWARDSHIP-BUILDOUT-001"
EXPECTED_HEAD = "9a8a0dd4e9c07040d23ceeb3bf1bf10003d45ee4"
EXPECTED_CLAIM_COMMIT = "4424818c40382e52ab9521662ecb0922f61d8430"
EXPECTED_MERGED_BASE = "4f00f6f9d50e870d4e9805f29a69feb33e6f4d12"
EXPECTED_SNAPSHOT = "sha256:d28f522158bb25fd073703a9db376f31e85a1b3c6c3c6dd8bfe468cce9ca633d"
ALLOWED_TRUST_ZONES = {
    "canonical", "tradition-scoped", "proposed", "inferred", "deprecated", "learning-sidecar"
}
METADATA_KEYS = {
    "object_type", "trust_zone", "lifecycle_status", "provenance_note", "reason_for_inclusion"
}


class Recorder:
    def __init__(self) -> None:
        self.checks: list[dict[str, Any]] = []

    def check(self, check_id: str, condition: bool, **details: Any) -> None:
        self.checks.append({
            "id": check_id,
            "status": "pass" if condition else "fail",
            "details": details,
        })

    def guarded(self, check_id: str, operation) -> Any:
        try:
            value = operation()
        except Exception as exc:  # receipt records type only; never echo private payloads
            self.check(check_id, False, error_type=type(exc).__name__)
            return None
        return value


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("top-level YAML value must be a mapping")
    return value


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=True, capture_output=True, text=True,
        encoding="utf-8", errors="strict",
    )
    return completed.stdout.strip()


def metadata_from_markdown(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    value = yaml.safe_load(text[4:end])
    return value if isinstance(value, dict) else None


def duplicate_values(values: Iterable[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def is_acyclic(node_ids: Iterable[str], dependencies: dict[str, set[str]]) -> bool:
    nodes = set(node_ids)
    indegree = {node: 0 for node in nodes}
    followers: dict[str, set[str]] = defaultdict(set)
    for node, required in dependencies.items():
        if node not in nodes or any(target not in nodes for target in required):
            return False
        indegree[node] += len(required)
        for target in required:
            followers[target].add(node)
    ready = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    visited = 0
    while ready:
        node = ready.popleft()
        visited += 1
        for follower in sorted(followers[node]):
            indegree[follower] -= 1
            if indegree[follower] == 0:
                ready.append(follower)
    return visited == len(nodes)


def flatten_campaign_jobs(campaign: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    jobs: list[dict[str, Any]] = []
    phases: dict[str, str] = {}
    for phase in campaign.get("phases", []):
        phase_id = phase.get("id")
        for wave in phase.get("waves", []):
            for subwave in wave.get("subwaves", []):
                for job in subwave.get("jobs", []):
                    jobs.append(job)
                    phases[job.get("id")] = phase_id
    return jobs, phases


def canonical_mesh_digest(mesh: dict[str, Any]) -> str:
    payload = dict(mesh)
    payload.pop("manifest_digest", None)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def main() -> int:
    recorder = Recorder()

    required_files = [
        "README.md", "campaign.md", "campaign.json", "handoff.md", "constitution.yaml",
        "source-lock.yaml", "block-registry.yaml", "human-gates.yaml",
        "jobs/JOB_CATALOG.yaml", "graph/typed-dependency-graph.yaml",
        "mesh/agent-mesh.v1.json", "mesh/repository-metadata-adapter.yaml", "mesh/role-cards.yaml",
        "research/research-docket.yaml", "research/expert-qualification-matrix.yaml",
        "evaluation/evaluation-baseline.yaml", "migration/rollback-spec.yaml",
        "controller/qualification-plan.yaml", "controller/runtime-adapter-contract.yaml",
        "future/implementation-gate.yaml", "checks/README.md", "checks/validate_stewardship_campaign.py",
        "state/README.md",
    ]
    missing = [relative for relative in required_files if not (CAMPAIGN_ROOT / relative).is_file()]
    recorder.check("required-static-artifacts", not missing, required_count=len(required_files), missing=missing)

    metadata_failures: list[str] = []
    governed_files = sorted(
        path for path in CAMPAIGN_ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".yaml", ".yml", ".json"}
    )
    mesh_manifest = CAMPAIGN_ROOT / "mesh/agent-mesh.v1.json"
    for path in governed_files:
        relative = path.relative_to(CAMPAIGN_ROOT).as_posix()
        try:
            if path == mesh_manifest:
                # The portable DAD schema is closed; repository metadata is bound by
                # mesh/repository-metadata-adapter.yaml and validated separately.
                continue
            if path.suffix.lower() == ".md":
                metadata = metadata_from_markdown(path)
            elif path.suffix.lower() in {".yaml", ".yml"}:
                metadata = load_yaml(path).get("metadata")
            else:
                metadata = load_json(path).get("metadata")
            if not isinstance(metadata, dict) or not METADATA_KEYS.issubset(metadata):
                metadata_failures.append(relative)
                continue
            if metadata.get("trust_zone") not in ALLOWED_TRUST_ZONES:
                metadata_failures.append(relative)
        except Exception:
            metadata_failures.append(relative)
    recorder.check(
        "governed-metadata", not metadata_failures,
        checked_files=len(governed_files), failures=sorted(metadata_failures), mesh_metadata_companion=True,
    )

    data = recorder.guarded("parse-static-artifacts", lambda: {
        "campaign": load_json(CAMPAIGN_ROOT / "campaign.json"),
        "source": load_yaml(CAMPAIGN_ROOT / "source-lock.yaml"),
        "blocks": load_yaml(CAMPAIGN_ROOT / "block-registry.yaml"),
        "gates": load_yaml(CAMPAIGN_ROOT / "human-gates.yaml"),
        "catalog": load_yaml(CAMPAIGN_ROOT / "jobs/JOB_CATALOG.yaml"),
        "graph": load_yaml(CAMPAIGN_ROOT / "graph/typed-dependency-graph.yaml"),
        "mesh": load_json(CAMPAIGN_ROOT / "mesh/agent-mesh.v1.json"),
        "adapter": load_yaml(CAMPAIGN_ROOT / "mesh/repository-metadata-adapter.yaml"),
        "roles": load_yaml(CAMPAIGN_ROOT / "mesh/role-cards.yaml"),
        "docket": load_yaml(CAMPAIGN_ROOT / "research/research-docket.yaml"),
        "experts": load_yaml(CAMPAIGN_ROOT / "research/expert-qualification-matrix.yaml"),
        "evaluation": load_yaml(CAMPAIGN_ROOT / "evaluation/evaluation-baseline.yaml"),
        "migration": load_yaml(CAMPAIGN_ROOT / "migration/rollback-spec.yaml"),
        "controller": load_yaml(CAMPAIGN_ROOT / "controller/qualification-plan.yaml"),
        "runtime": load_yaml(CAMPAIGN_ROOT / "controller/runtime-adapter-contract.yaml"),
        "future": load_yaml(CAMPAIGN_ROOT / "future/implementation-gate.yaml"),
        "constitution": load_yaml(CAMPAIGN_ROOT / "constitution.yaml"),
        "public": load_yaml(REPO_ROOT / "docs/governance/logos-convergence-advisory-review.yaml"),
        "family": load_yaml(REPO_ROOT / "governance/registry/FAMILY_WORK_REGISTRY.yaml"),
    })
    if data is None:
        return emit(recorder, None)
    recorder.check("parse-static-artifacts", True, parsed_count=len(data))

    source = data["source"]
    source_failures: list[str] = []
    snapshot_rows: list[dict[str, str]] = []
    for row in source.get("sources", []):
        relative = row.get("path", "")
        candidate = REPO_ROOT / relative
        if not candidate.is_file():
            source_failures.append(relative)
            continue
        actual_sha = sha256_file(candidate)
        try:
            # The lock intentionally binds both checked-out Windows bytes (SHA-256)
            # and the normalized Git object at the pinned HEAD (Git blob identity).
            actual_blob = git("rev-parse", f"HEAD:{relative}")
        except Exception:
            actual_blob = ""
        if actual_sha != row.get("sha256") or actual_blob != row.get("git_blob"):
            source_failures.append(relative)
        snapshot_rows.append({"path": relative, "sha256": row.get("sha256"), "git_blob": row.get("git_blob")})
    snapshot_payload = {
        "repository_head": source.get("repository_head"),
        "origin_main": source.get("origin_main_at_lock"),
        "sources": sorted(snapshot_rows, key=lambda row: row["path"]),
    }
    snapshot_actual = "sha256:" + hashlib.sha256(
        json.dumps(snapshot_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    try:
        head = git("rev-parse", "HEAD")
        parents = git("show", "-s", "--format=%P", "HEAD").split()
        branch = git("branch", "--show-current")
    except Exception:
        head, parents, branch = "", [], ""
    source_ok = (
        not source_failures
        and head == EXPECTED_HEAD == source.get("repository_head")
        and parents == [EXPECTED_CLAIM_COMMIT, EXPECTED_MERGED_BASE]
        and branch == "codex/logos-stewardship-buildout"
        and snapshot_actual == source.get("source_snapshot_digest") == EXPECTED_SNAPSHOT
        and source.get("private_terminal_evidence", {}).get("content_copied_into_campaign") is False
        and source.get("private_terminal_evidence", {}).get("local_path_recorded") is False
    )
    recorder.check(
        "source-lock-replay", source_ok, source_count=len(snapshot_rows), failures=sorted(source_failures),
        head_matches=head == EXPECTED_HEAD, merge_parents_match=parents == [EXPECTED_CLAIM_COMMIT, EXPECTED_MERGED_BASE],
        snapshot_matches=snapshot_actual == EXPECTED_SNAPSHOT,
    )

    claims = [item for item in data["family"].get("work_items", []) if item.get("work_id") == EXPECTED_CLAIM_ID]
    claim = claims[0] if len(claims) == 1 else {}
    expected_claim_paths = [
        "governance/registry/FAMILY_WORK_REGISTRY.yaml",
        "docs/roadmap/logos-stewardship-architecture-buildout/",
    ]
    claim_ok = (
        len(claims) == 1
        and claim.get("status") == "active"
        and claim.get("branch") == "codex/logos-stewardship-buildout"
        and claim.get("claimed_paths") == expected_claim_paths
        and claim.get("authority_ceiling") == "specification_only_non_authorizing_research_campaign_bootstrap"
        and set(claim.get("overlap_resolution_ids", [])) == {
            "OVERLAP-W27-STEWARD-BUILDOUT-001", "OVERLAP-W27-STEWARD-CITATION-001"
        }
        and claim.get("pr_url") is None
    )
    recorder.check("family-claim", claim_ok, claim_count=len(claims), authority_ceiling=claim.get("authority_ceiling"))

    public = data["public"]
    blocks = data["blocks"]
    public_advisories = public.get("advisory_rows", [])
    advisory_ids = [row.get("advisory_id") for row in public_advisories]
    advisory_hashes = [row.get("sha256") for row in public_advisories]
    recomputed_hashes = [
        hashlib.sha256((str(row.get("normalized_text", "")) + "\n").encode("utf-8")).hexdigest()
        for row in public_advisories
    ]
    block_advisories = blocks.get("consensus_advisory_rows", {}).get("rows", [])
    public_block_rows = public.get("blocked_rows", {}).get("rows", [])
    public_p0 = sorted(row.get("block_id") for row in public_block_rows if row.get("priority") == "P0")
    public_p1 = sorted(row.get("block_id") for row in public_block_rows if row.get("priority") == "P1")
    public_residuals = public.get("residuals", {}).get("rows", [])
    exact_boundary_ok = (
        advisory_ids == EXPECTED_ADVISORY_IDS
        and advisory_hashes == EXPECTED_ADVISORY_HASHES == recomputed_hashes
        and [row.get("issue_id") for row in block_advisories] == EXPECTED_ADVISORY_ISSUES
        and [row.get("sha256") for row in block_advisories] == EXPECTED_ADVISORY_HASHES
        and all(row.get("implementation_blocked") is True for row in block_advisories)
        and [row.get("issue_id") for row in blocks.get("blocked_p0_rows", {}).get("rows", [])] == EXPECTED_P0_ISSUES
        and [row.get("issue_id") for row in blocks.get("blocked_p1_rows", {}).get("rows", [])] == EXPECTED_P1_ISSUES
        and [row.get("disagreement_id") for row in blocks.get("residual_rows", {}).get("rows", [])] == EXPECTED_RESIDUALS
        and public_p0 == EXPECTED_PUBLIC_P0
        and public_p1 == EXPECTED_PUBLIC_P1
        and [row.get("residual_id") for row in public_residuals] == EXPECTED_PUBLIC_RESIDUALS
        and all(row.get("implementation_blocked") is True for row in public_block_rows + public_residuals)
        and public.get("blocked_rows", {}).get("invariants", {}).get("findings_closed") == 0
        and public.get("blocked_rows", {}).get("invariants", {}).get("implementation_blocks_cleared") == 0
        and blocks.get("invariants", {}).get("implementation_blocks_cleared") == 0
    )
    recorder.check(
        "exact-convergence-boundary", exact_boundary_ok,
        advisory_count=len(public_advisories), p0_count=len(public_p0), p1_count=len(public_p1), residual_count=len(public_residuals),
    )

    special_public = public.get("special_001", {})
    special_local = blocks.get("special_001", {})
    special_ok = (
        special_public.get("discovery_status") == "UNKNOWN"
        and special_public.get("exact_semantics_identified") is False
        and special_public.get("parent_cardinality_change_allowed") is False
        and special_public.get("substantive_recommendation_allowed") is False
        and special_public.get("experiment_authorized") is False
        and special_local.get("discovery_status") == "UNKNOWN"
        and special_local.get("exact_semantics_identified") is False
        and special_local.get("numeric_parent_constraint_allowed") is False
        and special_local.get("experiment_authorized") is False
        and data["campaign"].get("convergence_boundary", {}).get("special_001") == "UNKNOWN"
    )
    recorder.check("special-001-unknown", special_ok, numeric_constraint_allowed=False, experiment_authorized=False)

    gates = data["gates"].get("gates", [])
    gate_ids = [gate.get("gate_id") for gate in gates]
    gates_ok = (
        gate_ids == EXPECTED_GATE_IDS
        and data["gates"].get("default_status") == "blocked_human"
        and all(gate.get("status") == "blocked_human" and gate.get("receipt_ref") is None for gate in gates)
        and all(value is False for value in data["gates"].get("non_authority_rules", {}).values())
    )
    recorder.check("human-gates-preserved", gates_ok, gate_count=len(gates), receipts_present=0)

    campaign = data["campaign"]
    constitution_auth = data["constitution"].get("current_authority", {})
    boundary = campaign.get("convergence_boundary", {})
    authority_ok = (
        campaign.get("schema_version") == "long_run_campaign.v2"
        and campaign.get("execution", {}).get("mode") == "specification_only"
        and campaign.get("execution", {}).get("launch_command") == "not-authorized"
        and campaign.get("execution", {}).get("authorization_receipt") == "not-authorized"
        and campaign.get("portability", {}).get("activation_blocked") is True
        and boundary.get("implementation_authorized") is False
        and boundary.get("experiment_authorized") is False
        and boundary.get("migration_authorized") is False
        and all(value is False for key, value in constitution_auth.items() if key.endswith("_authorized"))
    )
    recorder.check("specification-only-authority", authority_ok, execution_mode=campaign.get("execution", {}).get("mode"), implementation_authorized=False)

    campaign_jobs, campaign_phases = flatten_campaign_jobs(campaign)
    catalog_jobs = data["catalog"].get("jobs", [])
    campaign_by_id = {job.get("id"): job for job in campaign_jobs}
    catalog_by_id = {job.get("job_id"): job for job in catalog_jobs}
    job_mismatches: list[str] = []
    for job_id in EXPECTED_JOB_IDS:
        left = campaign_by_id.get(job_id, {})
        right = catalog_by_id.get(job_id, {})
        if not left or not right:
            job_mismatches.append(job_id)
            continue
        expected_state = "blocked_human" if job_id in {"J-300", "J-310", "J-320", "J-400"} else "planned"
        if not (
            left.get("title") == right.get("title")
            and left.get("depends_on", []) == right.get("depends_on", [])
            and left.get("effect_class") == right.get("effect_class")
            and left.get("owner_role") == right.get("planned_writer")
            and left.get("checker_role") == right.get("checker")
            and campaign_phases.get(job_id) == right.get("phase")
            and right.get("current_state") == expected_state
        ):
            job_mismatches.append(job_id)
    dependencies = {job_id: set(job.get("depends_on", [])) for job_id, job in catalog_by_id.items()}
    jobs_ok = (
        list(campaign_by_id) == EXPECTED_JOB_IDS
        and list(catalog_by_id) == EXPECTED_JOB_IDS
        and not duplicate_values([job.get("id") for job in campaign_jobs])
        and not duplicate_values([job.get("job_id") for job in catalog_jobs])
        and not job_mismatches
        and is_acyclic(EXPECTED_JOB_IDS, dependencies)
    )
    recorder.check("campaign-job-dag", jobs_ok, job_count=len(campaign_jobs), mismatches=sorted(job_mismatches), acyclic=is_acyclic(EXPECTED_JOB_IDS, dependencies))

    graph = data["graph"]
    graph_nodes = graph.get("nodes", [])
    graph_edges = graph.get("edges", [])
    node_ids = [node.get("node_id") for node in graph_nodes]
    edge_ids = [edge.get("edge_id") for edge in graph_edges]
    node_by_id = {node.get("node_id"): node for node in graph_nodes}
    allowed_relations = set(graph.get("edge_contract", {}).get("allowed_relations", {}))
    endpoint_errors = [
        edge.get("edge_id") for edge in graph_edges
        if edge.get("source_id") not in node_by_id or edge.get("target_id") not in node_by_id
    ]
    relation_errors = [edge.get("edge_id") for edge in graph_edges if edge.get("relation") not in allowed_relations]
    graph_dep_edges = {
        (edge.get("source_id"), edge.get("target_id")) for edge in graph_edges if edge.get("relation") == "depends_on"
    }
    expected_dep_edges = {(job, dep) for job, deps in dependencies.items() for dep in deps}
    graph_dependencies: dict[str, set[str]] = defaultdict(set)
    derivation_dependencies: dict[str, set[str]] = defaultdict(set)
    for edge in graph_edges:
        if edge.get("relation") == "depends_on":
            graph_dependencies[edge.get("source_id")].add(edge.get("target_id"))
        elif edge.get("relation") == "derived_from":
            derivation_dependencies[edge.get("source_id")].add(edge.get("target_id"))
    block_nodes = [node for node in graph_nodes if node.get("node_kind") == "block"]
    block_edges = {
        edge.get("source_id") for edge in graph_edges
        if edge.get("relation") == "blocks" and edge.get("target_id") == "J-400"
    }
    human_gate_nodes = [node for node in graph_nodes if node.get("node_kind") == "human_gate"]
    human_gate_block_sources = {edge.get("source_id") for edge in graph_edges if edge.get("relation") == "blocks"}

    def reaches_source(start: str) -> bool:
        queue = deque([start])
        seen: set[str] = set()
        while queue:
            node_id = queue.popleft()
            if node_id in seen:
                continue
            seen.add(node_id)
            if node_by_id.get(node_id, {}).get("node_kind") == "immutable_source":
                return True
            queue.extend(sorted(derivation_dependencies.get(node_id, set())))
        return False

    conclusions = [node.get("node_id") for node in graph_nodes if node.get("node_kind") == "conclusion"]
    artifact_nodes = [node.get("node_id") for node in graph_nodes if node.get("node_kind") == "artifact"]
    consumer_sources = {
        edge.get("source_id") for edge in graph_edges if edge.get("relation") in {"consumed_by", "validates"}
    }
    graph_ok = (
        graph.get("execution_authority") is False
        and not duplicate_values(node_ids)
        and not duplicate_values(edge_ids)
        and not endpoint_errors
        and not relation_errors
        and not (set(graph.get("edge_contract", {}).get("prohibited_relations", [])) & {edge.get("relation") for edge in graph_edges})
        and graph_dep_edges == expected_dep_edges
        and is_acyclic(EXPECTED_JOB_IDS, {job: graph_dependencies.get(job, set()) for job in EXPECTED_JOB_IDS})
        and is_acyclic(set(derivation_dependencies) | {target for values in derivation_dependencies.values() for target in values}, derivation_dependencies)
        and len(block_nodes) == 25
        and all(node.get("node_id") in block_edges and str(node.get("lifecycle_status", "")).startswith("active") for node in block_nodes)
        and len(human_gate_nodes) == 14
        and all(node.get("node_id") in human_gate_block_sources and node.get("lifecycle_status") == "blocked_human" for node in human_gate_nodes)
        and conclusions and all(reaches_source(node_id) for node_id in conclusions)
        and all(node_id in consumer_sources for node_id in artifact_nodes)
        and not any(edge.get("relation") in {"authorizes", "migrates_to", "implements"} for edge in graph_edges)
    )
    recorder.check(
        "typed-graph", graph_ok, node_count=len(graph_nodes), edge_count=len(graph_edges),
        block_node_count=len(block_nodes), endpoint_errors=sorted(endpoint_errors), relation_errors=sorted(relation_errors),
        provenance_conclusions=len(conclusions), all_conclusions_reach_source=all(reaches_source(node_id) for node_id in conclusions),
    )

    mesh = data["mesh"]
    adapter = data["adapter"]
    role_cards = data["roles"].get("roles", [])
    mesh_roles = mesh.get("roles", [])
    mesh_role_ids = [role.get("role_id") for role in mesh_roles]
    card_role_ids = [role.get("role_id") for role in role_cards]
    role_dependencies = {role.get("role_id"): set(role.get("dependencies", [])) for role in mesh_roles}
    role_reference_errors: list[str] = []
    for role in mesh_roles:
        refs = set(role.get("dependencies", [])) | set(role.get("handoff", {}).get("recipient_role_ids", []))
        if not refs.issubset(mesh_role_ids):
            role_reference_errors.append(role.get("role_id"))
    mesh_digest = canonical_mesh_digest(mesh)
    mesh_ok = (
        mesh.get("schema_version") == "dad.task_local_agent_mesh_manifest.v1"
        and mesh.get("task_id") == EXPECTED_CLAIM_ID
        and mesh.get("source_snapshot_digest") == EXPECTED_SNAPSHOT
        and mesh.get("authority", {}).get("execution_authority") is False
        and mesh.get("authority", {}).get("human_gate_required") is True
        and mesh.get("max_delegation_depth") == 1
        and mesh.get("writer_role_id") == "specification-writer"
        and mesh.get("checker_role_id") == "independent-authority-checker"
        and mesh.get("writer_role_id") != mesh.get("checker_role_id")
        and not duplicate_values(mesh_role_ids)
        and not duplicate_values(card_role_ids)
        and not role_reference_errors
        and is_acyclic(mesh_role_ids, role_dependencies)
        and all(role_id in card_role_ids for role_id in mesh_role_ids)
        and len(role_cards) == adapter.get("role_card_count") == 27
        and mesh_digest == mesh.get("manifest_digest") == adapter.get("portable_manifest_digest")
        and adapter.get("repository_contract", {}).get("max_direct_fanout") == 3
        and adapter.get("repository_contract", {}).get("worker_delegation_allowed") is False
        and adapter.get("repository_contract", {}).get("execution_authorized") is False
        and adapter.get("portability_adapter", {}).get("runtime_adapter_status") == "unbound"
    )
    recorder.check(
        "agent-mesh", mesh_ok, mesh_role_count=len(mesh_roles), role_card_count=len(role_cards),
        canonical_digest=mesh_digest, role_reference_errors=sorted(role_reference_errors), acyclic=is_acyclic(mesh_role_ids, role_dependencies),
    )

    adapter_bindings = data["adapter"].get("job_bindings", [])
    binding_by_job = {binding.get("job_id"): binding for binding in adapter_bindings}
    binding_errors: list[str] = []
    for job_id in EXPECTED_JOB_IDS:
        binding = binding_by_job.get(job_id, {})
        if not binding or binding.get("specification_author") != "specification-writer":
            binding_errors.append(job_id)
            continue
        if job_id != "J-400" and binding.get("checker") != "independent-authority-checker":
            binding_errors.append(job_id)
        if not set(binding.get("human_gate_ids", [])).issubset(EXPECTED_GATE_IDS):
            binding_errors.append(job_id)
    recorder.check(
        "job-role-bindings", set(binding_by_job) == set(EXPECTED_JOB_IDS) and not binding_errors,
        binding_count=len(adapter_bindings), errors=sorted(set(binding_errors)),
    )

    docket = data["docket"]
    research_questions = docket.get("research_questions", [])
    referenced_agent_roles = {role for question in research_questions for role in question.get("research_agents", [])}
    referenced_human_roles = {role for question in research_questions for role in question.get("required_human_experts", [])}
    research_ok = (
        docket.get("execution_authorized") is False
        and docket.get("default_output_status") == "candidate_only"
        and len(research_questions) == 8
        and all(question.get("prohibited_conclusions") for question in research_questions)
        and all(set(question.get("human_gate_ids", [])).issubset(EXPECTED_GATE_IDS) for question in research_questions)
        and referenced_agent_roles.issubset(card_role_ids)
        and referenced_human_roles.issubset(card_role_ids)
        and data["experts"].get("default_on_missing_evidence") == "unqualified"
        and data["experts"].get("selection_rules", {}).get("provider_or_model_name_is_qualification") is False
        and data["experts"].get("selection_rules", {}).get("different_role_id_proves_independence") is False
    )
    recorder.check(
        "research-and-expert-routing", research_ok, question_count=len(research_questions),
        agent_role_count=len(referenced_agent_roles), human_expert_type_count=len(referenced_human_roles),
        missing_agent_roles=sorted(referenced_agent_roles - set(card_role_ids)),
        missing_human_roles=sorted(referenced_human_roles - set(card_role_ids)),
    )

    evaluation = data["evaluation"]
    migration = data["migration"]
    controller = data["controller"]
    runtime = data["runtime"]
    future = data["future"]
    dormant_ok = (
        evaluation.get("experiment_authorized") is False
        and evaluation.get("dataset_selected") is False
        and evaluation.get("protected_fixture_selected") is False
        and evaluation.get("route_selection", {}).get("current_result") == "no_winner"
        and evaluation.get("route_selection", {}).get("selection_authorized") is False
        and migration.get("status") == "dormant"
        and all(migration.get(key) is False for key in ["migration_authorized", "source_selected", "target_selected", "data_copy_authorized", "credentials_authorized"])
        and controller.get("status") == "not_run"
        and all(controller.get(key) is False for key in ["controller_selected", "runtime_adapter_selected", "launch_command_authorized", "shutdown_command_authorized"])
        and runtime.get("binding_status") == "unselected"
        and runtime.get("current_binding") is None
        and future.get("status") == "blocked_human"
        and future.get("implementation_authorized") is False
        and future.get("auto_advance") is False
        and not (CAMPAIGN_ROOT / "future/implementation-decision-receipt.yaml").exists()
    )
    state_payloads = sorted(
        path.relative_to(CAMPAIGN_ROOT).as_posix()
        for path in (CAMPAIGN_ROOT / "state").rglob("*") if path.is_file() and path.name != "README.md"
    )
    dormant_ok = dormant_ok and not state_payloads
    recorder.check("dormant-future-effects", dormant_ok, controller_selected=False, runtime_bound=False, state_payloads=state_payloads)

    # Scope, whitespace, local-path, legacy-label, and secret-like scans never echo matched values.
    try:
        status_lines = git("status", "--porcelain=v1", "--untracked-files=all").splitlines()
    except Exception:
        status_lines = []
    status_paths: list[str] = []
    for line in status_lines:
        path_text = line[3:].split(" -> ")[-1].replace("\\", "/")
        status_paths.append(path_text)
    outside_claim = sorted(
        path for path in status_paths
        if path != "governance/registry/FAMILY_WORK_REGISTRY.yaml"
        and not path.startswith("docs/roadmap/logos-stewardship-architecture-buildout/")
    )
    scan_suffixes = {".md", ".yaml", ".yml", ".json"}
    legacy_label = bytes([104, 97, 98, 105, 116, 97, 116]).decode("ascii")
    absolute_path_pattern = re.compile(r"(?i)(?:[a-z]:\\|/home/|/users/|/tmp/)")
    secret_patterns = [
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        re.compile(r"(?i)\b(?:api[_-]?key|secret|password|bearer[_-]?token|access[_-]?token)\s*[:=]\s*['\"][^'\"]{8,}"),
        re.compile(r"\b(?:ghp|github_pat|sk_live|sk_test)_[A-Za-z0-9_-]{16,}\b"),
    ]
    legacy_hits = 0
    absolute_path_hits = 0
    secret_signal_hits = 0
    whitespace_hits = 0
    for path in sorted(CAMPAIGN_ROOT.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if any(line.endswith((" ", "\t")) for line in text.splitlines()):
            whitespace_hits += 1
        if path.suffix.lower() in scan_suffixes:
            legacy_hits += int(legacy_label in text.casefold())
            absolute_path_hits += int(bool(absolute_path_pattern.search(text)))
            secret_signal_hits += int(any(pattern.search(text) for pattern in secret_patterns))
    try:
        diff_check_ok = subprocess.run(
            ["git", "diff", "--check"], cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8"
        ).returncode == 0
    except Exception:
        diff_check_ok = False
    hygiene_ok = (
        not outside_claim and legacy_hits == 0 and absolute_path_hits == 0
        and secret_signal_hits == 0 and whitespace_hits == 0 and diff_check_ok
    )
    recorder.check(
        "scope-privacy-and-hygiene", hygiene_ok, changed_path_count=len(status_paths), outside_claim=outside_claim,
        legacy_label_hits=legacy_hits, absolute_path_hits=absolute_path_hits,
        secret_signal_hits=secret_signal_hits, whitespace_files=whitespace_hits, git_diff_check=diff_check_ok,
    )

    return emit(recorder, campaign)


def emit(recorder: Recorder, campaign: dict[str, Any] | None) -> int:
    counts = Counter(item["status"] for item in recorder.checks)
    overall = "pass" if counts.get("fail", 0) == 0 else "fail"
    receipt = {
        "metadata": {
            "object_type": "stewardship_architecture_static_validation_receipt",
            "trust_zone": "proposed",
            "lifecycle_status": "validation_evidence",
            "provenance_note": "Generated read-only by the task-local deterministic validator.",
            "reason_for_inclusion": "Report static specification validity without granting human, runtime, migration, implementation, publication, or remote-effect authority.",
        },
        "schema_version": "logos_stewardship_validation_receipt.v1",
        "campaign_id": None if campaign is None else campaign.get("campaign_id"),
        "revision": None if campaign is None else campaign.get("revision"),
        "repository_head": EXPECTED_HEAD,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "checks": recorder.checks,
        "summary": {
            "pass": counts.get("pass", 0),
            "fail": counts.get("fail", 0),
            "blocked": counts.get("blocked", 0),
            "inconclusive": counts.get("inconclusive", 0),
        },
        "overall_status": overall,
        "authorization_state": "blocked_human",
        "non_authorization": {
            "static_pass_is_controller_qualification": False,
            "static_pass_is_research_authorization": False,
            "static_pass_is_human_decision": False,
            "static_pass_is_migration_or_implementation_authority": False,
            "static_pass_is_publication_or_remote_effect_authority": False,
        },
        "mutation_performed": False,
    }
    print(json.dumps(receipt, sort_keys=True, indent=2, ensure_ascii=False))
    return 0 if overall == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
