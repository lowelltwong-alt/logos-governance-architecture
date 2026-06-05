# Graph and Concordance Layer

## Purpose

This folder is the entry point for the repository's graph-oriented and machine-readable concordance work. This graph layer also now supports a future primary-sources domain, including witness objects, fragment objects, transcriptions, passage reconstructions, lexical evidence objects, and translation comparison objects. That future domain should remain governed by the same identity, trust, provenance, and validation rules as the rest of the graph architecture.

It exists to support governed, machine-readable representations of:
- verse connections
- topic and doctrine connections
- relationship objects
- edge provenance
- graph-ready structures that can later aggregate into larger concordance systems

## Why this layer exists

The repository should not rely only on human-readable prose to preserve important connections.

Some relationships need to become explicit machine-readable objects so they can be:
- reviewed
- extended
- validated
- reused across many nodes
- read by concordance or graph systems without hidden drift

This graph layer also now supports a future primary-sources domain, including witness objects, fragment objects, transcriptions, passage reconstructions, lexical evidence objects, and translation comparison objects. That future domain should remain governed by the same identity, trust, provenance, and validation rules as the rest of the graph architecture.

## Relation to the rest of the repository

This layer should not operate as a separate project.

It should remain downstream of and aligned with:
- governance files
- canon, doctrine, concept, and scripture nodes
- translation and manuscript control layers
- noncanonical and boundary rules

The companion `logos-scripture-graph` repo is the downstream data-plane
implementation for Scripture graph and concordance artifacts. Its link to this
repo is a governance contract, not a submodule or runtime dependency. This repo
defines upstream relationship discipline; the downstream data-plane emits
validated artifacts under that discipline.

## Good uses for this layer

- governed verse-to-verse edge objects
- reusable doctrine or topic links
- relationship objects with provenance and trust status
- future concordance datasets built from approved node and edge vocabularies

## Coherence rule

Anything added here should still follow the repository's broader architecture:
- stable identifiers
- controlled relation types
- provenance where needed
- warning and trust controls where needed
- no silent override of the human-readable architecture

## Recommended companion files

This layer should be read together with:
- `docs/governance/README.md`
- `docs/governance/relationship-registry.md`
- `docs/governance/anchor-conventions-scripture-and-graph-extension.md`
- `docs/roadmap/repository-integration-map.md`

## Summary principle

Important connections should become explicit where needed.

That is how the repository grows from a strong document architecture into a governed concordance and graph architecture without losing coherence.
