---
object_type: validator_lifecycle_note
trust_zone: canonical
lifecycle_status: active
provenance_note: "Added 2026-07-06 to adopt the modular Rust fast-validator standard from logos-scripture-graph T462 for deterministic governance validation hot paths."
reason_for_inclusion: "Future agents need a deterministic record of which validation work may be accelerated in Rust and which governance authority remains in Python and owner-controlled review."
---

# T462 Governance Rust Fast Validators

This note records the governance repo adoption of the modular Rust fast-validator
standard first used in `logos-scripture-graph` T462.

## Scope

Rust may accelerate deterministic, structure-only validation hot paths:

- Markdown internal-link and local path scans.
- Duplicate identifier scans.
- Machine-readable manifest and checksum checks.
- Canonical scope, path, or reference-shape checks that do not select authority.
- Large deterministic comparison passes.

Rust must not own or infer governance authority:

- owner gates;
- theology, canon, or source-tradition authority;
- reviewed-gold or promotion decisions;
- route, evaluator, or policy decisions;
- broad semantic policy interpretation;
- anything that needs human theological judgment.

## Current Migration

The first migrated hot path is `scripts/validate_internal_links.py`.

- Stable agent-facing command remains `python scripts/validate_internal_links.py`.
- Default behavior remains the existing Python implementation.
- Rust lives under `tools/logos_governance_fast_validators/`.
- Rust can be required with `--require-rust` for parity checks.
- Rust can be attempted with `--python-fallback`; fallback only occurs when the
  Rust toolchain or manifest is unavailable, not when Rust finds failures.
- `scripts/validate_all.py` is a compatibility alias for
  `scripts/run_validation_suite.py`.

The Rust path is shadow/opt-in in this PR. It is not enabled as the default path
inside the validation suite until parity fixtures and review history justify that
change.

## Rust Module Contract

The crate follows the T462 modular standard:

- `main.rs` parses CLI arguments and dispatches.
- `reports.rs` defines `CheckReport` with check name, status, elapsed time,
  message, detail lines, and JSON serialization.
- Each check module exposes `run_check(input) -> CheckReport`.
- Bundled commands may be added later only if each check keeps its own identity,
  elapsed time, failure message, and JSON report.

## Lifecycle

`scripts/validate_internal_links.py` remains the canonical wrapper and the
current validation-suite entry point. The Rust implementation is a governed
acceleration surface, not a new authority surface.

Any later PR that replaces default Python execution with Rust must:

- keep Python command ergonomics stable;
- keep or document Python fallback behavior;
- prove parity on fixtures and representative repo scans;
- update this lifecycle note and `governance/GOVERNANCE_DEPENDENCY_MAP.yaml`;
- run the full validation suite and focused wrapper tests.

## DAD

This repo does not currently expose a DAD outbox workflow. No DAD outbox report
is required for this migration. If a DAD workflow is later added, validator
acceleration changes should emit an outbox entry naming the accelerated check,
the wrapper command, the parity fixture set, and the authority boundaries above.
