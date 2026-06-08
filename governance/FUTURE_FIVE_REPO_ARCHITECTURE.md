---
object_type: logos_future_repo_architecture
trust_zone: proposed
lifecycle_status: active
provenance_note: "Created 2026-06-08 to record the planned five-repo Logos topology without creating future repos."
reason_for_inclusion: "Separate current repo authority from planned future execution and doctrine-lineage surfaces."
---

# Future Five Repo Architecture

This document records the intended future topology. The planned repos listed
here are not created by this document.

```mermaid
flowchart TD
  GOV["logos-governance-architecture<br/>governance / registry / contracts"]
  SCRIPT["logos-scripture-graph<br/>canonical Scripture data plane"]
  BOUND["logos-boundary-literature<br/>boundary / reception support plane"]
  CHUNK["logos-chunking-harness<br/>planned execution/evaluation plane"]
  DOCTRINE["logos-doctrine-genealogy<br/>planned doctrine lineage/profile plane"]

  GOV --> SCRIPT
  GOV --> BOUND
  GOV --> CHUNK
  GOV --> DOCTRINE

  CHUNK -->|"read-only adapter: canonical mode"| SCRIPT
  CHUNK -->|"read-only adapter: boundary mode"| BOUND
  CHUNK -->|"read-only adapter: doctrine mode"| DOCTRINE

  DOCTRINE -->|"Scripture refs only; scoped claims"| SCRIPT
  DOCTRINE -->|"boundary/reception references"| BOUND

  BOUND -. "not canonical authority" .-> SCRIPT
  CHUNK -. "not semantic authority" .-> SCRIPT
  DOCTRINE -. "not canonical authority" .-> SCRIPT
```

## Planned Repo Responsibilities

### logos-chunking-harness

Future execution/evaluation plane for chunking across corpora. It may read
Scripture, boundary, or doctrine repos through source-mode adapters, but it must
not own canonical truth, mix output namespaces, or transfer boundary claims into
Scripture.

### logos-doctrine-genealogy

Future doctrine/concept lineage and profile-comparison plane. It may track
doctrine development over time, source basis, ethical implications,
alignment/disalignment, and tradition/profile scope. It must not rewrite
canonical Scripture or collapse contested doctrine into universal truth.

## Creation Gate

Each planned repo remains `planned_not_created` until:

1. a registration issue is opened in this repo;
2. authority and data-flow direction are approved;
3. an initial scaffold PR creates an `AI_FRONT_DOOR.md`;
4. the registry is updated in this governance repo first or in the same
   coordinated PR.
