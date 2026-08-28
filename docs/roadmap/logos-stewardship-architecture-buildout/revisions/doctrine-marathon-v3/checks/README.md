---
object_type: doctrine_marathon_validation_runbook
trust_zone: proposed
lifecycle_status: active
provenance_note: "Created on 2026-08-27 by Codex root as the deterministic V3 replay route."
reason_for_inclusion: "Let reviewers reproduce schema, graph, authority, prompt, manifest, fixture, and public-boundary checks without activating the campaign."
---

# Doctrine Marathon V3 checks

From the repository root:

```powershell
python -B docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/validate_doctrine_marathon.py --mode prefinal
python -B docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/validate_doctrine_marathon.py --mode final
python -B docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/test_validate_doctrine_marathon.py
python -B docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/run_adversarial_harness.py
python -B -m pytest -q --assert=plain -p no:cacheprovider docs/roadmap/logos-stewardship-architecture-buildout/revisions/doctrine-marathon-v3/checks/test_run_adversarial_harness.py
python -B scripts/validate_portfolio_front_door.py
python -B scripts/validate_internal_links.py
python -B scripts/validate_governance_dependency_map.py
python -B scripts/validate_family_work_registry.py
```

These checks validate the saved specification and public projection. They do not
prove that an expert taxonomy is complete, a source is true, a model is an
expert, a runtime enforces the contracts, or a doctrine claim is correct.
The four-case aggregate sentinel is a non-authorizing subset regression, not a
substitute for the still-missing V4 repository registry, receipt index,
clean-checkout adapter, provider CI execution, or full 197-case disposition.
Consequently the public V3 maturity is `blocked_specification_only` and final
mode must retain the exact `adversarial_harness_release_gate` until those gates
are closed and independently reviewed.

The V3 harness separately exercises event-chain continuity and ordering,
changed-input midflight barriers, pairwise role-assignment lineage, the seven-day
fresh-context ceiling, resolvable terminal handoffs, evidence and translation
lineage, exact-scope review and qualification receipts, typed ExpertPacks,
authority-registry and human-decision boundaries, full reverse-closure event
barriers, transitive context-taint and weakest-premise rules, semantically gated
campaign completion, latest-requirement provenance, qualified producer and
entry/midflight/exit completeness-auditor bindings, exact two-reviewer decision
receipts, reviewer capability/freshness coverage, typed graph basis resolution,
and ledger-reachable correlation-exception consumption, Jewish-context non-flattening,
influence-hypothesis structure, prompt neutrality, public nonclaims, and the
administrative freeze and owner-release-authorization chain. The negative fixture count is derived from the
fixture file; a passing count is not hard-coded evidence of semantic quality.
The strict prefinal mode validates final-strength payload rules before the
receipt exists. Final mode additionally validates the exact manifest, receipt,
independent-review record, terminal saved-version index, their cross-digests,
and the absence of symlinks or junctions. The harness uses recomputed-checksum
tamper cases so a valid hash cannot conceal a semantically invalid admin record.
Run Python with `-B`: ignored local bytecode is never evidence, and any generated
cache path that becomes Git-tracked is a hard public-release failure.

The fully sealed positive completion fixture deliberately bootstraps synthetic
generation-zero qualification through an explicit synthetic human decision.
That proves deterministic contract composition only. Hashes do not prove real
identity, scholarly competence, or authority; production use remains blocked
until a separately protected or signed human trust anchor exists.
