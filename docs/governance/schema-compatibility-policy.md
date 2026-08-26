# Schema Compatibility Policy

## Purpose

This file defines how machine-readable structures in the repository should evolve without creating silent breakage, drift, or incompatible side architectures.

The repository increasingly includes structured objects such as:
- governed node headers
- graph or concordance objects
- relationship objects
- translation classification objects
- manuscript and witness objects
- boundary-source classification objects

These structures should be treated as governed schemas rather than casual formatting choices.

## Core principle

A schema is a contract.

If a machine-readable structure is meant to be reused by humans, tools, or future automations, then changes to that structure should be:
- intentional
- reviewable
- documented
- compatibility-aware

## What counts as a schema here

For this repository, a schema includes any repeatable machine-readable shape such as:
- top-of-file governed metadata blocks
- JSON concordance objects
- graph node objects
- graph edge objects
- classification object templates
- import or normalization object formats

## Preferred change order

When a new need appears, prefer this order:

1. reuse the existing schema if it can carry the new use without distortion
2. add optional fields before changing required structure
3. document the extension before broad use
4. version the schema if the change is meaningfully breaking
5. avoid parallel shadow schemas unless the object type is truly different

## Compatibility categories

### Backward-compatible additive change
A change is usually compatible when it:
- adds a new optional field
- adds a new optional controlled value
- adds a new documented extension file
- adds a new object subtype that still conforms to existing base rules

These are the safest changes.

### Compatibility-sensitive change
A change needs more review when it:
- changes the meaning of an existing field
- repurposes an existing controlled value
- changes expected field shape or type
- changes required relationship semantics
- changes trust or boundary semantics in ways that could affect downstream interpretation

### Breaking change
A change is usually breaking when it:
- removes an expected field
- renames a field without transition support
- changes a required field into a new incompatible structure
- changes a controlled value in a way that would invalidate existing objects
- creates a second competing shape for the same object type without clear governance

Breaking changes should be rare and explicit.

## Versioning rule

If a schema change is meaningfully breaking, the schema should be versioned rather than silently replaced.

Versioning may happen through:
- explicit schema version fields
- new template files
- new documented object versions
- migration notes where needed

The repository should prefer evolutionary growth over abrupt hidden replacement.

## Base schema vs extension schema rule

Where possible, use this pattern:
- a stable base schema for the common object type
- extension documents for branch-specific expansions

Examples:
- base node-type registry plus scripture/boundary extension
- base tag registry plus scripture/boundary extension
- base anchor conventions plus scripture/graph extension

This pattern keeps the shell stable while still allowing growth.

## One object type, one primary grammar rule

Avoid having several incompatible grammars for what is functionally the same object type.

If the repository has:
- a governed node header
- a graph concept object
- a graph edge object

then each should have one primary grammar, even if specialized subtypes exist.

Differences should be expressed through:
- node type
- classification
- optional fields
- subtype docs

not through uncontrolled reinvention.

## Provenance rule for schema evolution

When a schema changes meaningfully, the repository should be able to say:
- what changed
- why it changed
- who changed it
- whether the change is additive or breaking
- whether older objects need migration

That does not require bureaucratic overhead for every tiny update.
It does require discipline for structural changes.

## Migration rule

When changing a machine-readable shape in a way that affects existing objects, prefer one of these approaches:
- keep the old field and add a new one for a transition period
- add a compatibility note and update objects gradually
- create a versioned successor shape if the change is truly breaking

Do not silently leave the repository with mixed incompatible object grammars if avoidable.

## Review triggers

Additional review is recommended when a proposed change affects:
- node identity fields
- provenance fields
- trust or boundary classifications
- translation or heresy status fields
- graph edge semantics
- concordance object shape
- machine-readable import or export assumptions

## Fractal rule for schemas

Schema discipline should itself be fractal.

That means:
- the same compatibility logic should apply at multiple levels
- local branches may extend carefully, but should not casually fork the grammar
- branches can specialize, but should still feel like the same repository architecture

## Recommended contributor questions

Before changing a schema, ask:
1. is this really a new object type, or just a new example of an existing one?
2. can an optional field solve this instead of a structural fork?
3. is this change additive, compatibility-sensitive, or breaking?
4. will future humans and machines still read the object the same way?
5. does this preserve one coherent grammar across the repository?

## Summary principle

Machine-readable growth should be governed like architecture, not treated like decoration.

Stable schemas let the repository grow recursively without becoming incompatible with itself.

## Academic Extension Contract profile

The [Academic Extension Contract](academic-extension-contract.md) applies the
base-versus-extension rule to future academic disciplines. Pack-only changes
must preserve the recorded kernel bytes, place unknown data in a lossless
`extension_payload`, version pack schemas explicitly, default external mappings
to non-exact, and register every known downstream consumer. An unknown consumer,
namespace collision, missing migration, or source-digest drift blocks a
compatibility claim.
