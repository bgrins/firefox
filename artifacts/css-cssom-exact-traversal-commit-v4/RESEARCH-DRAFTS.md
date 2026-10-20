# V4 research commit drafts

These are artifact-only recipes for the existing `commit-item.py` schema. Neither recipe is executable as delivered: `expected_head` is a non-hash placeholder. Root must finalize it immediately before each commit after checking the currently staged roster. No Git mutation, compiler, build or browser run was performed to prepare them.

1. **research-source-draft.json — 693 files.** Seven authenticated capsules: proposal (62 payloads), final canonical and relocated extracted replays (154 each), independent source review (241), root source review (3), exact source packaging (40), and runtime-plan review (25), plus each pair of root seals. This retains historical conditional source/experiment decisions; it does not turn them into native approval.
2. **research-runtime-draft.json — 245 files.** Completed shared-build runtime (224 payloads) and independent runtime review (17), plus seals. Includes the root decision snapshots already sealed inside those capsules. The later loose qualified-advancement decision is excluded, as root requested, for a later acceptance/ledger commit.

Each `files` roster equals its explicit `source_pins` map. Every entry comes from a checked closed regular-file manifest or that capsule's seals. The recipes have no overlapping paths and no production native/WPT path. Source snapshots and patches inside `artifacts/` are evidence, not production mutations. All recipe paths were absent from the read-only HEAD snapshot recorded in RESEARCH-DRAFT-AUDIT.json; root must recheck against its later finalized HEAD.

## Dependencies and exclusions

The runtime recipe follows the source recipe. Its analyzer's 351 artifact input pins are covered by these two recipes except the historical DOM-only RUN.json, which was verified byte-identical in the observed committed HEAD. That one dependency is pinned explicitly in the runtime recipe. Non-artifact runtime inputs have retained baseline/candidate snapshots inside the runtime capsule; historical executables are identified by contemporaneous hashes, not included binaries.

The source component retains the v3 source/provider domains and historical calibration qualifications. Source packaging is exact applicability to two bases, not an isolated runtime result. Shared runtime includes DOMRect fix 102. The independent review permits qualified advancement with a disclosed possible deep-root-transform cost; no broad no-regression or standalone-without102 result is introduced here.

Excluded: live standalone and standalone-review work, loose final decision/preflight metadata, the native draft and reviewer log, changing shared ledgers/commit metadata, optional ownership work and all production files. Old nonfinal/development replay sibling directories are not added merely because they exist; the sealed proposal already retains their relevant diagnostic history. `native-draft.json` is untouched.

RESEARCH-DRAFT-AUDIT.json records all capsule seals, recipe hashes, the committed historical dependency, the exact helper hash and exclusions. These draft metadata files themselves are not part of either commit roster; root may finalize them separately.
