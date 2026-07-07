---
object_type: logos_family_map
trust_zone: canonical
lifecycle_status: active
provenance_note: "Created 2026-07-06 by Codex as PR-1r of the Fable kernel implementation sequence, summarizing active, planned, and advisory Logos-family repo roles without restating all authority rules."
reason_for_inclusion: "Give humans and AI agents a short root-level map of how Logos repos should work together before they choose a repo or implementation lane."
---

# Logos Family Map

This is the short repo-selection map for the Logos project family. It summarizes where work belongs; governing authority remains in the repo registry, dependency map, link contracts, and front-door files.

| Repo | Job | Front door / routing surface | Must not do |
|---|---|---|---|
| `logos-governance-architecture` | Cross-repo governance, ontology discipline, repo registry, contracts, theological architecture roadmaps, Fable kernels, and owner decision records. | [`AI_FRONT_DOOR.md`](AI_FRONT_DOOR.md) | Store Scripture data-plane outputs, import source corpora, or hold doctrine-genealogy data records. |
| `logos-scripture-graph` | Canonical 66-book Scripture data plane, passage records, chunking decisions, metadata, validators, review packets, and Scripture release artifacts. | [logos-scripture-graph AI front door](https://github.com/lowelltwong-alt/logos-scripture-graph/blob/main/AI_FRONT_DOOR.md) | Import boundary/commentary/doctrine material as Scripture authority or treat AI/vector output as truth. |
| `logos-boundary-literature` | Boundary, reception, patristic, commentary, theologian-writing, and source-metadata support plane. | [logos-boundary-literature AI front door](https://github.com/lowelltwong-alt/logos-boundary-literature/blob/main/AI_FRONT_DOOR.md) | Equal or outrank Scripture, become the doctrine plane, or import texts without source-governance controls. |
| `logos-doctrine-genealogy` | Active scaffold for doctrine-lineage, theologian, tradition, and profile-comparison work after D7 and Issue #83 gates were satisfied. | [logos-doctrine-genealogy AI front door](https://github.com/lowelltwong-alt/logos-doctrine-genealogy/blob/main/AI_FRONT_DOOR.md) | Add doctrine-lineage records, import sources, rewrite Scripture, own commentary corpora, mint verbs or entity IDs, or collapse contested doctrine without later authorization. |
| `logos-chunking-harness` | Planned execution/evaluation plane for future cross-corpus chunking harnesses after readiness is met. | Planned; use [`governance/ADDING_NEW_LOGOS_REPOS.md`](governance/ADDING_NEW_LOGOS_REPOS.md) before creation. | Exist yet, supply semantic authority, or generalize chunking behavior without reviewed gates. |
| `noesis-atlas` | External advisory comparison context only. | [Noesis boundary policy](docs/governance/noesis-boundary.md) | Govern, gate, promote, demote, derive, or modify any Logos repo. |

Read next:

- [`AI_TABLE_OF_CONTENTS.md`](AI_TABLE_OF_CONTENTS.md) for discovery surfaces.
- [`DATA_FLOW_MAP.md`](DATA_FLOW_MAP.md) for current and future data flow.
- [`docs/roadmap/fable-kernels/README.md`](docs/roadmap/fable-kernels/README.md) for Fable architecture kernels and D1-D10 owner decisions.
- [`governance/GOVERNANCE_DEPENDENCY_MAP.yaml`](governance/GOVERNANCE_DEPENDENCY_MAP.yaml) for machine-readable governance dependencies.
