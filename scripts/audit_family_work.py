#!/usr/bin/env python3
"""Discover Logos-family worktrees and reconcile them with governed work claims."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.validate_family_work_registry import ACTIVE_STATUSES, REGISTRY, load_yaml, paths_overlap
except ModuleNotFoundError:  # Direct script execution places scripts/ on sys.path.
    from validate_family_work_registry import ACTIVE_STATUSES, REGISTRY, load_yaml, paths_overlap

REPOS = {
    "logos-governance-architecture": "logos-governance-architecture",
    "logos-scripture-graph": "logos-scripture-graph-repo",
    "logos-boundary-literature": "logos-boundary-literature",
    "logos-doctrine-genealogy": "logos-doctrine-genealogy",
    "noesis-atlas": "noesis-atlas",
}
TASK_RE = re.compile(r"(?i)(?:^|[-_/])(T\d+)(?:$|[-_/])")


def run(command: list[str], cwd: Path, *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=check)


def git(cwd: Path, *args: str) -> str:
    completed = run(["git", *args], cwd)
    return completed.stdout.strip() if completed.returncode == 0 else ""


def parse_worktrees(repo_root: Path) -> list[dict[str, Any]]:
    raw = subprocess.run(
        ["git", "worktree", "list", "--porcelain", "-z"], cwd=repo_root,
        capture_output=True, check=True,
    ).stdout.decode("utf-8", errors="replace")
    records: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for token in raw.split("\0"):
        if not token:
            if current:
                records.append(current)
                current = {}
            continue
        key, _, value = token.partition(" ")
        current[key] = value if value else True
    if current:
        records.append(current)
    return records


def dirty_paths(worktree: Path) -> list[str]:
    raw = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z"], cwd=worktree,
        capture_output=True, check=False,
    ).stdout.decode("utf-8", errors="replace")
    paths: list[str] = []
    tokens = [token for token in raw.split("\0") if token]
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if len(token) >= 4:
            paths.append(token[3:].replace("\\", "/"))
            if token[:2] in {"R ", "C ", "RM", "CM"} and index + 1 < len(tokens):
                index += 1
        index += 1
    return sorted(set(paths))


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def latest_dirty_edit(worktree: Path, paths: list[str]) -> datetime | None:
    mtimes = []
    for value in paths:
        path = worktree / value
        try:
            if path.is_file():
                mtimes.append(path.stat().st_mtime)
        except OSError:
            continue
    return datetime.fromtimestamp(max(mtimes), timezone.utc) if mtimes else None


def open_prs(repo_root: Path) -> dict[str, dict[str, Any]]:
    completed = run([
        "gh", "pr", "list", "--state", "open", "--limit", "200", "--json",
        "number,title,headRefName,url,isDraft,updatedAt",
    ], repo_root)
    if completed.returncode != 0:
        return {}
    try:
        return {item["headRefName"]: item for item in json.loads(completed.stdout)}
    except (json.JSONDecodeError, KeyError, TypeError):
        return {}


def classify(*, primary: bool, branch: str | None, dirty: bool, detached: bool, ancestor: bool, tree_equivalent: bool, ahead: int, pr: dict[str, Any] | None) -> str:
    if dirty:
        return "preserve_dirty_owner_reconciliation"
    if primary and branch == "main":
        return "active_base_or_current_checkout"
    if pr:
        return "open_pr_review"
    if detached:
        return "detached_review_required"
    if ancestor or tree_equivalent:
        return "merged_or_superseded_cleanup_candidate"
    if ahead > 0:
        return "unpublished_or_unmerged_commits"
    return "stale_branch_review_required"


def registered_matches(registry: dict[str, Any], repo: str, branch: str | None, tasks: list[str]) -> list[str]:
    matches = []
    for item in registry.get("work_items", []):
        if item.get("repo") != repo:
            continue
        if branch and item.get("branch") == branch:
            matches.append(item["work_id"])
        elif str(item.get("task_id", "")).upper() in tasks:
            matches.append(item["work_id"])
    return sorted(set(matches))


def observe_repo(repo: str, root: Path, registry: dict[str, Any], observed_at: datetime) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    prs = open_prs(root)
    for index, raw in enumerate(parse_worktrees(root)):
        worktree = Path(str(raw["worktree"]))
        branch_ref = raw.get("branch")
        branch = str(branch_ref).removeprefix("refs/heads/") if isinstance(branch_ref, str) else None
        head = str(raw.get("HEAD", ""))
        dirty = dirty_paths(worktree) if worktree.exists() else []
        last_commit = git(worktree, "log", "-1", "--format=%cI") if worktree.exists() else ""
        commit_time = parse_time(last_commit)
        dirty_edit_time = latest_dirty_edit(worktree, dirty)
        activity_candidates = [value for value in (commit_time, dirty_edit_time) if value]
        last_activity = max(activity_candidates) if activity_candidates else None
        activity_age_days = (
            round((observed_at - last_activity.astimezone(timezone.utc)).total_seconds() / 86400, 2)
            if last_activity else None
        )
        behind = ahead = 0
        counts = git(worktree, "rev-list", "--left-right", "--count", "origin/main...HEAD") if worktree.exists() else ""
        if counts:
            try:
                behind, ahead = map(int, counts.split())
            except ValueError:
                pass
        ancestor = run(["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"], worktree).returncode == 0 if worktree.exists() else False
        tree_equivalent = run(["git", "diff", "--quiet", "origin/main", "HEAD"], worktree).returncode == 0 if worktree.exists() else False
        committed_paths = (
            git(worktree, "diff", "--name-only", "origin/main...HEAD").splitlines()
            if worktree.exists() and not tree_equivalent else []
        )
        branch_or_path = f"{branch or ''}/{worktree.name}"
        tasks = sorted({match.upper() for match in TASK_RE.findall(branch_or_path)})
        pr = prs.get(branch or "")
        classification = classify(
            primary=index == 0, branch=branch, dirty=bool(dirty), detached=bool(raw.get("detached")),
            ancestor=ancestor, tree_equivalent=tree_equivalent, ahead=ahead, pr=pr,
        )
        records.append({
            "repo": repo,
            "worktree_name": worktree.name,
            "is_primary_checkout": index == 0,
            "head": head,
            "branch": branch,
            "detached": bool(raw.get("detached")),
            "locked": raw.get("locked", False),
            "prunable": raw.get("prunable", False),
            "dirty": bool(dirty),
            "dirty_paths": dirty,
            "committed_paths_not_on_main": sorted(set(committed_paths))[:200],
            "committed_path_count_not_on_main": len(set(committed_paths)),
            "last_commit_at": last_commit or None,
            "last_local_dirty_edit_at": dirty_edit_time.isoformat().replace("+00:00", "Z") if dirty_edit_time else None,
            "last_observed_activity_at": last_activity.isoformat().replace("+00:00", "Z") if last_activity else None,
            "last_observed_activity_age_days": activity_age_days,
            "activity_note": "Local dirty-file mtimes are observational and may be affected by checkout or sync operations; they are not lifecycle authority.",
            "behind_origin_main": behind,
            "ahead_of_origin_main": ahead,
            "head_is_ancestor_of_origin_main": ancestor,
            "tree_matches_origin_main": tree_equivalent,
            "task_candidates": tasks,
            "registered_work_ids": registered_matches(registry, repo, branch, tasks),
            "open_pr": pr,
            "classification": classification,
            "observed_at": observed_at.isoformat().replace("+00:00", "Z"),
        })
    return records


def markdown(payload: dict[str, Any]) -> str:
    lines = [
        "---",
        "object_type: family_worktree_audit",
        "trust_zone: proposed",
        "lifecycle_status: audit_snapshot",
        f'provenance_note: "Generated {payload["observed_at"]} by scripts/audit_family_work.py from Git worktree, branch, status, PR, and governed registry evidence."',
        'reason_for_inclusion: "Preserve a rediscoverable snapshot of every observed family worktree and its reconciliation state without treating age as deletion authority."',
        "---",
        "",
        "# Family Worktree Audit",
        "",
        f"Observed: `{payload['observed_at']}`",
        "",
        "This is a reconciliation docket, not a deletion authorization. Dirty, detached, unknown, or stale work stays preserved until owner review.",
        "",
        "## Summary",
        "",
        f"- Repositories scanned: {payload['summary']['repo_count']}",
        f"- Worktrees observed: {payload['summary']['worktree_count']}",
        f"- Dirty worktrees: {payload['summary']['dirty_count']}",
        f"- Detached worktrees: {payload['summary']['detached_count']}",
        f"- Unregistered worktrees: {payload['summary']['unregistered_count']}",
        "",
        "## Worktrees",
        "",
        "| Repo | Worktree | Branch / task | Dirty | Age days | Ahead / behind | Registered | Classification |",
        "|---|---|---|---:|---:|---:|---|---|",
    ]
    for row in payload["worktrees"]:
        identity = row["branch"] or "detached"
        if row["task_candidates"]:
            identity += " / " + ", ".join(row["task_candidates"])
        registered = ", ".join(row["registered_work_ids"]) or "NO"
        lines.append(
            f"| `{row['repo']}` | `{row['worktree_name']}` | `{identity}` | "
            f"{'yes' if row['dirty'] else 'no'} | {row['last_observed_activity_age_days']} | "
            f"{row['ahead_of_origin_main']} / {row['behind_origin_main']} | "
            f"{registered} | `{row['classification']}` |"
        )
    duplicates = payload["summary"]["duplicate_task_candidates"]
    lines.extend(["", "## Duplicate Task Signals", ""])
    if duplicates:
        for task, names in duplicates.items():
            lines.append(f"- `{task}` appears in {len(names)} worktrees: " + ", ".join(f"`{name}`" for name in names))
    else:
        lines.append("- None observed.")
    lines.extend([
        "",
        "## Required Reconciliation",
        "",
        "1. Preserve every dirty or unpublished worktree.",
        "2. Match each unfinished item to a governed work ID and roadmap/task.",
        "3. Record continue, extend, supersede, split, parallel-boundary, or preserved-abandon decision.",
        "4. Remove a worktree only after clean-state, merge/ancestry, and preservation evidence agree.",
        "",
    ])
    return "\n".join(lines)


def claim_blockers(payload: dict[str, Any], registry: dict[str, Any], work_id: str) -> list[str]:
    claims = {item.get("work_id"): item for item in registry.get("work_items", [])}
    claim = claims.get(work_id)
    if not claim:
        return [f"unknown governed work ID {work_id}"]
    if claim.get("status") not in ACTIVE_STATUSES:
        return [f"{work_id} is not active and cannot claim new work"]
    blockers: list[str] = []
    claim_resolutions = set(claim.get("overlap_resolution_ids", []))
    for row in payload["worktrees"]:
        if row["repo"] != claim["repo"] or work_id in row["registered_work_ids"]:
            continue
        row_claims = [claims[item] for item in row["registered_work_ids"] if item in claims]
        if any(claim_resolutions & set(item.get("overlap_resolution_ids", [])) for item in row_claims):
            continue
        if (
            row["classification"] == "active_base_or_current_checkout"
            and not row["dirty"]
            and row["ahead_of_origin_main"] == 0
        ):
            continue
        task_match = str(claim["task_id"]).upper() in set(row["task_candidates"])
        observed_paths = row["dirty_paths"] + row["committed_paths_not_on_main"]
        overlaps = [
            (claimed, observed) for claimed in claim["claimed_paths"] for observed in observed_paths
            if paths_overlap(claimed, observed)
        ]
        if task_match or overlaps:
            reason = []
            if task_match:
                reason.append(f"same task candidate {claim['task_id']}")
            if overlaps:
                reason.append(f"path overlap {overlaps[0][0]} <-> {overlaps[0][1]}")
            blockers.append(
                f"{row['repo']}:{row['worktree_name']} ({row['branch'] or 'detached'}) - "
                + "; ".join(reason)
            )
    return blockers


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-root", type=Path, default=os.environ.get("LOGOS_FAMILY_ROOT"))
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--output-yaml", type=Path)
    parser.add_argument("--output-md", type=Path)
    parser.add_argument("--fail-on-unregistered-dirty", action="store_true")
    parser.add_argument("--check-work-id", help="Fail when this governed claim overlaps another observed worktree without a recorded resolution.")
    args = parser.parse_args(argv)
    if args.family_root is None:
        parser.error("--family-root or LOGOS_FAMILY_ROOT is required")
    family_root = args.family_root.resolve()
    registry = load_yaml(args.registry)
    observed_at = datetime.now(timezone.utc).replace(microsecond=0)
    worktrees: list[dict[str, Any]] = []
    missing_repos: list[str] = []
    for repo, directory in REPOS.items():
        root = family_root / directory
        if not (root / ".git").exists():
            missing_repos.append(repo)
            continue
        worktrees.extend(observe_repo(repo, root, registry, observed_at))
    classes = Counter(row["classification"] for row in worktrees)
    task_groups: dict[str, list[str]] = {}
    for row in worktrees:
        for task in row["task_candidates"]:
            task_groups.setdefault(task, []).append(f"{row['repo']}:{row['worktree_name']}")
    duplicate_tasks = {
        task: sorted(names) for task, names in sorted(task_groups.items()) if len(names) > 1
    }
    payload = {
        "object_type": "family_worktree_audit",
        "trust_zone": "proposed",
        "lifecycle_status": "audit_snapshot",
        "provenance_note": "Generated by scripts/audit_family_work.py from local Git worktree, branch, status, PR, and governed registry evidence.",
        "reason_for_inclusion": "Preserve a machine-readable reconciliation snapshot without treating age or generated classification as deletion authority.",
        "observed_at": observed_at.isoformat().replace("+00:00", "Z"),
        "family_root_name": family_root.name,
        "missing_repos": missing_repos,
        "summary": {
            "repo_count": len(REPOS) - len(missing_repos),
            "worktree_count": len(worktrees),
            "dirty_count": sum(row["dirty"] for row in worktrees),
            "detached_count": sum(row["detached"] for row in worktrees),
            "unregistered_count": sum(not row["registered_work_ids"] for row in worktrees),
            "classifications": dict(sorted(classes.items())),
            "duplicate_task_candidates": duplicate_tasks,
        },
        "worktrees": worktrees,
    }
    rendered_yaml = yaml.safe_dump(payload, sort_keys=False, allow_unicode=False)
    rendered_md = markdown(payload)
    if args.output_yaml:
        args.output_yaml.write_text(rendered_yaml, encoding="utf-8")
    if args.output_md:
        args.output_md.write_text(rendered_md, encoding="utf-8")
    if not args.output_yaml and not args.output_md:
        print(rendered_md)
    if args.check_work_id:
        blockers = claim_blockers(payload, registry, args.check_work_id)
        if blockers:
            print(f"WORK PREFLIGHT BLOCKED for {args.check_work_id}:")
            print("\n".join(f"- {blocker}" for blocker in blockers))
            return 3
        print(f"Work preflight passed for {args.check_work_id}.")
    risky = [row for row in worktrees if row["dirty"] and not row["registered_work_ids"]]
    return 2 if args.fail_on_unregistered_dirty and risky else 0


if __name__ == "__main__":
    raise SystemExit(main())
