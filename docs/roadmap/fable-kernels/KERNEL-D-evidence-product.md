---
object_type: fable_architecture_kernel
trust_zone: proposed
lifecycle_status: draft
provenance_note: "Created 2026-07-06 by Fable. Kernel for HP5 (cross-repo evidence product shape)."
reason_for_inclusion: "Define the only shape in which Scripture, boundary, and doctrine data may appear together, so joined views can never blur authority."
---

# Kernel D — Cross-Repo Evidence Packet (`evidence_packet.v1`)

Design goal: answer queries like *"show the development of Trinitarian doctrine from Scripture
through councils, theologians, confessions, and modern disputes"* without a single
authority-blurred row. A packet is a **derived, read-only report** — never a data plane, never
truth.

## D1. Packet structure

```yaml
evidence_packet:
  packet_id: ""
  query: ""                       # the human question answered
  generated_by: ""                # tool/agent + date
  generated_from:                 # exact upstream versions/commits
    scripture_graph_release: ""
    boundary_snapshot: ""
    doctrine_snapshot: ""
  non_authority_block:            # machine-readable, mandatory, uneditable by generators
    is_derived_artifact: true
    creates_scripture_authority: false
    creates_doctrine_authority: false
    creates_graph_or_retrieval_truth: false
    advisory_material_authority: none
  sections:
    scripture_refs: []            # passage IDs + release-artifact pointers ONLY
    boundary_sources: []          # work/source rows, each with trust tier
    doctrine_objects: []          # topics/views/formulations/assessments/edges
    advisory_notes: []            # rare; the only place a Noesis-namespaced ref may appear
  timeline_view: []               # optional presentation layer, see D3
```

**Row contract — every row in every section carries:**
`namespace` (`scripture_` | `boundary_` | `doctrine_` | `advisory_`), `authority_rung` (S0–S7,
Kernel B), `trust_tier` (boundary rows), `review_status`, `orthodoxy_status` + `claim_role`
(doctrine rows), and a provenance ref. A row missing any of these is a linter failure, not a
warning.

## D2. Hard rules

1. **Join by ID only.** No merged cross-namespace rows, ever. A packet cell never contains
   Scripture text copied through the boundary or doctrine planes — Scripture renderings come
   only from `logos-scripture-graph` validated release artifacts, cited by pointer.
2. **Namespace prefixes are load-bearing** (existing registry rule applied): a `canonical_*`
   labeled section may contain only S0 Scripture rows. Boundary/commentary/patristic/
   theologian/profile rows in a canonical section are a fail-closed linter error.
3. **Advisory quarantine:** `advisory_notes` is the only legal location for external-advisory
   refs; an advisory ref in any other section fails (extends the Noesis tripwire pattern to
   packets).
4. **Packets are disposable.** They live in the generating repo's `reports/` (or an
   `evidence_packets/` dir), never under any `data/` canonical path, and regeneration must be
   deterministic from `generated_from`.
5. **No packet feedback loop:** a packet may never be cited as `source_basis` for any claim
   (V-PKT-3). Evidence flows into packets; authority never flows out of them.

## D3. The timeline view

The flattening danger concentrates here, so the presentation layer gets its own rules:

- a timeline row is always a dated `formulation`, `assessment`, or instrument-adoption event —
  never a topic or view (topics/views are atemporal; putting them on a timeline invents dates);
- rows keep full row-contract fields; a condensed display must still carry rung + scope;
- parallel traditions render as parallel tracks, not merged sequence — the packet schema
  requires `track: <tradition_scope>` on timeline rows so one-timeline flattening is a schema
  violation, not a style choice;
- date-precision must be displayed (a `century`-precision date shown as a year is a linter error).

## D4. Example (shape only, invented refs)

A Trinity-development query returns: `scripture_refs` (John 1, Phil 2 passage IDs + release
pointers) → `boundary_sources` (Ignatius, Tertullian, Arius' Thalia [S7, adversarial],
Athanasius works — each with trust tier) → `doctrine_objects` (topic `trinity/consubstantiality`,
views Arian/Nicene, formulations dated with precision, Nicaea-325 and Constantinople-381
assessments with scope, `counters`/`derives_from` edges with evidence basis) →
timeline view on parallel tracks (Alexandrian, Antiochene, conciliar). At no point does a
patristic quotation acquire rung above S4, and Arius is fully represented at S7 with
`claim_role: historical_description`.

## D5. Validators (Codex implements)

| ID | Rule |
|---|---|
| V-PKT-1 | Row contract completeness; unknown namespace fails. |
| V-PKT-2 | Canonical-section purity; advisory-location rule. |
| V-PKT-3 | No packet ref may appear in any `source_basis` anywhere. |
| V-PKT-4 | Timeline rows must be dated event objects with `track`; precision must survive rendering. |
| V-PKT-5 | `non_authority_block` present, exact, unmodified. |
