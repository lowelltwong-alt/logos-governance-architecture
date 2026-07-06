---
object_type: fable_architecture_kernel
trust_zone: proposed
lifecycle_status: draft
provenance_note: "Created 2026-07-06 by Fable. Kernel for HP1 (doctrine-genealogy object model + relationship vocabulary) and HP8 (cross-repo entity identity)."
reason_for_inclusion: "The doctrine-genealogy plane needs a typed object model before the repo exists, so records can never predate their own guardrails."
---

# Kernel A — Doctrine-Genealogy Object Model and Relationship Vocabulary

Design goal: trace what derived from what, across time, without (a) flattening theology into
one timeline, (b) letting a later systematic framework silently govern earlier sources, or
(c) letting semantic similarity or generated confidence create lineage.

## A1. The core separation

The model refuses to store "doctrine" as one object. It splits five things that projects
usually conflate:

| Concept | Object | Time-bearing? | Example |
|---|---|---|---|
| The question | `doctrine_topic` | no | "How do divinity and humanity relate in Christ?" |
| A position | `doctrine_view` | no | Chalcedonian dyophysitism; miaphysitism |
| A historical expression of a position | `formulation` | **yes** | Leo's Tome (449); Cyril's Second Letter to Nestorius |
| A judgment about a position | `assessment` | **yes** | Chalcedon condemns Eutychianism (451) |
| Who spoke or judged | `agent` / `instrument` | yes | Athanasius; the Chalcedonian Definition |

Heresy is therefore never a bare property of a view. It is always
*assessed-as-heterodox-by-X-with-scope-Y-at-time-Z*, plus a separate project-boundary
classification (Kernel B). This is the structural answer to "later systematics governing
earlier sources": judgments and readings are dated acts by identified agents, never silent
edits to earlier objects.

## A2. Node types (v1 — closed set)

1. **`doctrine_topic`** — stable theological locus. Fields: `id`, `title`, `locus`
   (controlled: theology_proper, christology, pneumatology, trinity, bibliology, anthropology,
   hamartiology, soteriology, ecclesiology, sacraments, eschatology, ethics), `scripture_refs[]`
   (passage IDs only, from `logos-scripture-graph`; never text), `status`.
2. **`doctrine_view`** — a distinguishable position on exactly one topic. Fields: `topic_ref`,
   `summary`, `distinguishing_claims[]` (claim refs), `orthodoxy_status` + basis (Kernel B),
   `tradition_scope`, `first_attested_formulation_ref`.
3. **`formulation`** — a concrete, dated, sourced expression of a view by an agent in a work.
   Fields: `view_ref`, `agent_ref`, `source_work_ref` (boundary-literature work ID; never text),
   date block (A4), `original_language`, `key_terms[]` (original-language lemmas, evidence-only,
   gated per Kernel C), review flags.
4. **`agent`** — subtype required: `theologian`, `council`, `school_or_tradition`, `movement`.
   Fields: date block, `affiliations[]` (each affiliation is *time-scoped*: tradition + from/to —
   agents change traditions; Newman exists). Source metadata about an agent's writings stays in
   `logos-boundary-literature`; the agent node holds identity + genealogy role only.
5. **`instrument`** — creed, conciliar definition/canon, confession, catechism: a normative
   document adopted by an authority. Distinct from `formulation` because an instrument **binds a
   scope**. Fields: `adopting_authority_ref`, `binding_scope[]` (tradition + adopted/revised/
   rejected + dates — per-tradition reception is first-class), `source_work_ref`, `recensions[]`
   (e.g. Nicene creed with and without filioque are recensions of one instrument),
   `ladder_rung` (Kernel B).
6. **`claim`** — atomic subject–predicate–object theological assertion with the full provenance
   block (Kernel C). Views are composed of claims; claims are where evidence attaches.
7. **`assessment`** — a dated judgment by an agent or instrument about a view/formulation.
   `verdict` (controlled: affirmed, clarified, tolerated, disputed, condemned, anathematized),
   `assessor_ref`, `scope` (whose judgment binds whom), date block, `basis_refs[]`.
8. **`controversy`** — a bounded historical dispute episode (e.g. the Arian controversy) that
   groups topics, agents, formulations, assessments. Exists to prevent timeline-flattening:
   disputes are contexts, not points on one line.

One edge object: **`genealogy_edge`** — subject, verb (A3), object, direction, plus the full
anti-guessing evidence block from
[`../../governance/anti-guessing-and-evidence-discipline.md`](../../governance/anti-guessing-and-evidence-discipline.md):
evidence basis, scope, method, asserted/inferred, review status, provenance. Edge statuses reuse
the existing ladder verbatim: `retrieval_candidate` → `derived_view` → `proposed_relationship` →
`asserted_relationship`. Nothing in this plane can ever be `canonical_scripture_record`.

## A3. Relationship-verb registry v1 (Fable decision; owner approval D4)

Twelve verbs, four families. The registry lives in **this governance repo** as an extension of
[`../../governance/relationship-registry.md`](../../governance/relationship-registry.md);
`logos-doctrine-genealogy` may not mint verbs.

**Derivation family** (requires temporal-ordering validation, A4):

| Verb | Meaning | Evidence floor |
|---|---|---|
| `derives_from` | B developed from A | citation showing B's use/knowledge of A |
| `depends_on` | logical dependency (atemporal) | stated inferential dependence |
| `clarifies` | B makes A more precise without changing content | side-by-side content basis |
| `modifies` | B alters A's content | side-by-side content basis |
| `systematizes` | B organizes A and others into a system — explicitly a **later act by B** | cited organization |
| `reads_back_into` | B retrospectively interprets earlier A — the anachronism-safe verb | cited interpretive act |

**Citation family** (cross-plane; reference verbs):

| Verb | Meaning | Note |
|---|---|---|
| `interprets_passage` | formulation → Scripture passage ID | records interpretation *history*; never creates Scripture meaning |
| `cites_source` | formulation → boundary work ID | carries `citation_mode: quotation \| paraphrase \| allusion \| summary` (reuses boundary repo's patristic-reception distinctions rather than new top-level verbs) |

**Response family:**

| Verb | Meaning | Note |
|---|---|---|
| `receives` | affirmative uptake | |
| `rejects` | agent rejects a view/formulation | |
| `counters` | formulation constructed against another | |

**Comparative family** (lowest evidence class; may not exceed `proposed_relationship` without cited comparison basis):
`partially_aligns_with`, `tensions_with`.

**Decisions recorded:**

- `condemns` / `is_condemned_by` are **not hand-authored edges**. Condemnation is an
  `assessment` object (with assessor, scope, instrument basis, date); condemnation edges are
  machine-derived `derived_view` projections of assessments. This blocks scope-free
  "X is a heresy" edges permanently.
- `requires_original_language_review` and `requires_textual_critical_review` (roadmap
  candidates) are **not verbs**. They are promotion-blocking gate fields in the provenance
  block (Kernel C). Verbs are for traversal; gates are for promotion.
- **Forbidden verbs:** `related_to`, `influences` (too vague — use a stronger verb or keep the
  pair as `retrieval_candidate`). This extends the existing boundary contamination rule.
- New verbs enter only through the governance vocabulary process, owner-gated.

## A4. Time discipline

- No global timeline object exists. Time lives only on `formulation`, `assessment`,
  `instrument.binding_scope`, and `agent`.
- Every date is a block: `date_earliest`, `date_latest`, `date_precision`
  (year/decade/quarter_century/century), `date_basis` (cited). This reuses the date discipline
  already drafted in `logos-boundary-literature/schemas/reliability_evidence_early_traditions.md`.
- **Anachronism validator (V-TIME-1):** a derivation-family edge whose subject's
  `date_earliest` postdates its object's `date_latest` fails closed — unless the verb is
  `reads_back_into` or `systematizes`, which are defined as later acts. Later→earlier influence
  is inexpressible except as an explicit, dated interpretive act.

## A5. Cross-repo entity identity (HP8)

Problem found during the scout pass: Augustine will exist as a canon-thinker node (this repo,
theological buildout), as source-work metadata (boundary repo), and as an `agent`
(doctrine-genealogy). Without one ID, the three planes silently fork.

**Decision:** this governance repo owns a shared entity-ID registry for persons, councils,
schools/movements, and instruments — one slug per entity, kebab-case, disambiguated:
`person/augustine-of-hippo`, `council/chalcedon-451`, `instrument/nicene-constantinopolitan-381`,
`school/antiochene`. Rules:

- `logos-boundary-literature` continues to own `work/` IDs; `logos-scripture-graph` owns passage IDs.
- Other repos **reference** registry IDs; they never mint person/council/instrument IDs locally.
- An ID must be registered before any `asserted_relationship` may reference it
  (candidates may use provisional IDs flagged `unregistered`).
- Registry location: `governance/registry/entity_ids.yaml` (Codex scaffolds; owner D10 confirms
  ownership).

## A6. Stop rules for this plane

Stop and report if a task would:

- create any doctrine-genealogy data record **anywhere** before the repo exists and is
  registered — no "temporary" records in governance, boundary, or Scripture repos;
- author a condemnation edge directly instead of an assessment;
- assign heresy status without an assessment basis and a Kernel B boundary classification;
- create an edge from embedding similarity, co-occurrence, or generated confidence;
- mint a verb, node type, or entity ID outside the governance process;
- let a genealogy object modify, or supply meaning defaults for, any Scripture record.
