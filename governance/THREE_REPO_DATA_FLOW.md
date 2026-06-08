---
object_type: logos_current_repo_data_flow_map
trust_zone: canonical
lifecycle_status: active
provenance_note: "Created 2026-06-08 to document the current active three-repo Logos topology."
reason_for_inclusion: "Show current repo authority and data-flow direction without relying on chat context."
---

# Three Repo Data Flow

This map describes the current active Logos repository topology.

```mermaid
flowchart TD
  GOV["logos-governance-architecture<br/>cross-repo policy / registry / contracts"]
  SCRIPT["logos-scripture-graph<br/>canonical 66-book Scripture graph"]
  BOUND["logos-boundary-literature<br/>supporting boundary / reception literature"]

  GOV -->|"defines repo policy"| SCRIPT
  GOV -->|"defines repo policy"| BOUND

  SCRIPT -->|"canonical Scripture refs / IDs"| BOUND
  BOUND -->|"scoped background / reception / comparison claims"| SCRIPT

  BOUND -. "cannot override / equal / mutate" .-> SCRIPT
  SCRIPT -. "does not import boundary texts" .-> BOUND
```

## Directional Meaning

`logos-governance-architecture` defines repo policy, registry entries, authority
contracts, and update rules.

`logos-scripture-graph` owns canonical 66-book Scripture records, chunks, and
reviewed Scripture evaluation surfaces.

`logos-boundary-literature` may provide scoped background, reception,
comparison, and refutation material. It is supporting context, not canonical
authority.

## Forbidden Flow

- Boundary claims must not become canonical Scripture claims.
- Noncanonical material must not become default Scripture meaning.
- Commentary and reception claims must not mutate canonical Scripture records.
- Canonical Scripture source text must not be imported into the boundary repo.
- Cross-repo links must preserve authority, trust level, tradition/profile
  scope, and provenance.
