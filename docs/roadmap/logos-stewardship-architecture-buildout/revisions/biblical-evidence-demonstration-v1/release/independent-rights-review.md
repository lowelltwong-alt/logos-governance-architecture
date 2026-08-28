---
schema_version: logos.biblical-evidence.independent-review-receipt.v1
object_type: independent_rights_release_review_receipt
trust_zone: proposed
lifecycle_status: draft
provenance_note: "Recorded from a read-only independent rights, provenance, and public-boundary review completed 2026-08-28 against the exact canonical UTF-8/LF freeze; a preliminary raw-versus-canonical hash false alarm was independently corrected and invalidated before this result."
reason_for_inclusion: "Bind the exact Cologne P66 verso JPEG, attribution, license scope, object-versus-image distinction, translation separation, and public boundary to an independent non-author review without presenting AI review as legal, historical, doctrinal, or release authority."
review_id: urn:logos:review:biblical-evidence-rights-v1
review_class: rights_provenance_and_release
reviewer_role: source-rights-reviewer
reviewer_identity: codex-subagent-independent-rights-release-review
reviewer_attempt_id: REVIEW-RIGHTS-006
reviewer_independence: true
independence_basis: read_only_non_author_no_candidate_mutation
result: pass
frozen_manifest_sha256: "sha256:7671341b23c70e806a05acba23d9721eb4762e3104c8ead104756adacdce1e9f"
frozen_aggregate_sha256: "sha256:9791fc26beebdf90f13e22f0f56f9bc631a57b20a7ef379bc657328bead8ea81"
reviewed_scope:
  - docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/assets/p66-cologne-john19-verso.jpg
  - docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/frozen-digests.json
  - docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/release/asset-attribution.yaml
  - docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/release/public-release-manifest.yaml
  - docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/sources/p66-source-and-rights.yaml
reviewed_scope_digests:
  - {path: docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/assets/p66-cologne-john19-verso.jpg, sha256: "sha256:f7453af8d2523cc358148c7d26072d87b53c991aa03df667f8c5c54c7beef040"}
  - {path: docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/frozen-digests.json, sha256: "sha256:7671341b23c70e806a05acba23d9721eb4762e3104c8ead104756adacdce1e9f"}
  - {path: docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/release/asset-attribution.yaml, sha256: "sha256:87d30f7fc9fc0b4dad5fcd4177092b21aeb38c37bdf05f9cd867619fc6c840ed"}
  - {path: docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/release/public-release-manifest.yaml, sha256: "sha256:172f8b0634260ef347282e1e1fc096574337890fb4f3681a4b5705ca81a5c150"}
  - {path: docs/roadmap/logos-stewardship-architecture-buildout/revisions/biblical-evidence-demonstration-v1/sources/p66-source-and-rights.yaml, sha256: "sha256:bb27df5fe6a0cfb485e0d17f5934a6f584bf3f3126964b4c128439464b003663"}
blocking_findings: []
residual_nonclaims:
  - "This review is not legal advice and does not establish every non-copyright permission, including moral, privacy, publicity, trademark, or culturally sensitive-use rights."
  - "The Cologne CC BY 4.0 rights statement covers the image and public object metadata; it does not license or establish a diplomatic transcription, critical edition, transliteration, English translation, preferred reading, historical conclusion, or doctrinal claim."
  - "The official catalog coverage belongs to the combined recto-and-verso object record; the exact passage content of the reviewed verso JPEG remains unresolved, and no catalog segment is assigned to that side."
  - "The World English Bible text has a separate public-domain source basis and trademark notice; it does not derive rights or textual authority from the P66 image license."
  - "The Cologne object-record URL is the persistent locator; the direct JPEG URL is a delivery locator and is not asserted to be persistent or continuously available."
  - "The source archive digest for the World English Bible was relied upon as pinned package evidence and was not independently re-downloaded in this rights-review lane."
  - "No private payload or absolute machine path was found in the reviewed P66 public package; a disclosed repo-relative non-durable M7 observation locator and digest remain subject to the named human public-release gate."
  - "Repository-wide privacy output included one sensitive-pattern candidate outside this package, and Git history was not scanned; those broader checks remain separate human and independent release gates."
  - "Publication grants no legal, historical, canonical, doctrinal, theological, promotion, runtime-activation, or release authority."
mutation_performed: false
authority_granted: false
qualified_human_approval: false
observed_at: "2026-08-28T15:35:42Z"
---

# Independent rights and release-boundary review

Result: **PASS**

The reviewer independently checked the exact 1,083,773-byte, 1802 × 1921 P66
verso JPEG at SHA-256
`f7453af8d2523cc358148c7d26072d87b53c991aa03df667f8c5c54c7beef040`
against the University of Cologne source.

The Cologne object record identifies Inv. 04274+004298 / TM 61627 and publishes
`P.inv. 04274_04298v.jpg`. It presents the object-level John 19 coverage as
combined recto-and-verso metadata and licenses its public metadata and images
under CC BY 4.0:

- Persistent object record: https://papyri.uni-koeln.de/stueck/tm61627
- Direct image locator: https://papyri.uni-koeln.de/stueck/DS_d1e18043/img/04274_04298/orig/P.inv.%2004274_04298v.jpg
- License terms: https://creativecommons.org/licenses/by/4.0/

A successful direct-image retrieval during this review returned HTTP 200,
`image/jpeg`, 1,083,773 bytes, and the exact governed SHA-256. Later automated
retries received HTTP 500 or an environment-level 403, so the direct image URL
is treated only as a delivery locator; the object-record URL remains the
persistent source locator.

The attribution record supplies the institution, object and image identifiers,
persistent source link, license link, and the filename-only modification
disclosure. It also prohibits implied institutional endorsement. These satisfy
the applicable CC BY 4.0 credit, license-link, change-indication, and
no-endorsement duties for the declared unchanged image content.

The English verses remain separately sourced from the public-domain World
English Bible Classic:

- https://ebible.org/details.php?id=eng-web
- https://ebible.org/eng-web/copr.htm

The package does not copy or claim rights to a P66 transcription, critical
edition, transliteration, or restricted translation. The image node has no
coverage-segment or English-translation edge; all four discontinuous John 19
coverage edges originate from the combined physical-object node. Exact
verso-side mapping remains prohibited pending the listed papyrology,
transcription/source, independent-fidelity, and named-human gates.

The canonical freeze was replayed using the validator's UTF-8 newline
normalization for text and raw bytes for opaque binary. All 21 rows matched, and
the recomputed aggregate was exactly
`sha256:9791fc26beebdf90f13e22f0f56f9bc631a57b20a7ef379bc657328bead8ea81`.

## Reviewer-tooling correction

A preliminary review message incorrectly treated raw CRLF checkout hashes as
canonical frozen hashes and reported false drift. The raw manifest hash was
subsequently confirmed to equal the freeze-time raw hash. Two stable snapshots
and an exact replay of `canonical_file_bytes` produced the tasked canonical
manifest and aggregate with zero mismatches. The preliminary fail-closed message
is invalidated and is not evidence of repository mutation.

No repository, Git, cache, registry, receipt, or remote state was modified by
this review.
