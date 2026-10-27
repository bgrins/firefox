# Raw nested attribute WPT comparison

This capsule runs genuine WPT against two explicitly corrected target pages in both original and candidate phases. It does not install test files or change live metadata. Native fix acceptance remains a separate review decision.

The targets are `attr-cycle.html` (37 assertions, including two explicitly corrected historical oracles) and `attr-raw-nested-cycle.html` (29 assertions). Both phases use exactly the proposal bytes. The candidate must pass all 66 assertions. `ORACLE-ADJUDICATION.md` in the sealed raw repair proposal explains both changed expectations; the original phase may record these and other target failures without being classified as infrastructure failure.

The unchanged regression roster has 329 assertions across eight pages, including all 34 used-fallback assertions and 178 attr-all-types assertions, plus six reftests. `ROSTER-COUNTS.json` independently derives counts and identities from the completed used-fallback candidate run and saved ordinary WPT run. Every phase must retain those exact identities. Candidate status, explicit/default expectation fields, intermittent fields and test-end outcomes must match the new original observation. Regression failures remain visible; no expectations or metadata are rewritten.

`POLICY.json` pins original native sources to used-fallback repair v3 candidate-live and candidate sources to the raw-nested proposal, with the used-fallback custom-properties helper unchanged. The initial original requires `attribute_fallback_transition` with role `candidate`, `compiled: true`, and `accepted: true`. Restored originals and raw candidates require `raw_attribute_transition` with their own matching role and `compiled: true`. Source and binary hashes must independently match the supplied epoch. No epoch is fabricated here.

HEAD is bound at launch to the caller-supplied epoch and must remain identical across the comparison. Each phase binds actual WPT `browser_build_id` to its own application.ini BuildID, resolved regular target, bytes and entry/target identities before and after the run. Only that independently bound BuildID may differ between phases. All other run_info fields must match. The application.ini symlink exception remains limited to that specific resource.

The inherited runner preserves full epoch/index/nested/native/research state, resource/header/metadata pins, profile inputs, real manifest/config and owned copied inputs. It generates an owned WPT configuration and copied manifest root, uses ephemeral server ports and a separate temporary profile root, and requires owned process-group absence and temporary-root removal. The live historical attr-cycle file stays pinned to its original oracle; the new raw test must remain absent from live WPT during the experiment. The signed used-fallback fixture is pinned to its accepted bytes.

The real in-tree Manifest API generated and reloaded `SUBSET-MANIFEST.json`: ten testharness pages and six reftests with the original reference relationships. All 15 selected manifest entries from capsule v1 are unchanged. The added attr-all-types entry matches the saved genuine manifest for its authenticated bytes. Captured testharness scripts, four reference documents, inherited headers and metadata are retained. No external fonts or images are needed.

## Order acceptance gate

`ORDER-GATE.md` maps the proposal's existing-order requirement to the unchanged opposite-resolution-order pair already in attr-cycle. Both are target assertions and therefore must pass, not merely retain a baseline status. The used-fallback mutual/reordered controls remain additional unchanged regression assertions. The sealed proposal's acceptance wording is retained without modification.

## Commands (root execution only)

Compute and externally record the current epoch SHA after the root controller finishes each native transition. Use fresh absent output directories. `CAPSULE_SHA` is the SHA256 of this directory's FILES.json; the caller also supplies the original assessment digest. Do not substitute a mutable or stale epoch without recomputing and recording its digest.

```sh
python3 -I -S -B artifacts/css-attr-raw-nested-wpt-capsule-v2/run.py CAPSULE_SHA original-1 ABS_EPOCH_PATH EPOCH_SHA /Users/bgrins/code/firefox/artifacts/css-attr-raw-nested-wpt-runtime-original-1
python3 -I -S -B artifacts/css-attr-raw-nested-wpt-capsule-v2/run.py CAPSULE_SHA candidate-1 ABS_EPOCH_PATH EPOCH_SHA /Users/bgrins/code/firefox/artifacts/css-attr-raw-nested-wpt-runtime-candidate-1 /Users/bgrins/code/firefox/artifacts/css-attr-raw-nested-wpt-runtime-original-1/ASSESSMENT.json ORIGINAL_ASSESSMENT_SHA
```

Redirect outer output to separate owned artifact logs and record actual tool sessions and terminal exits. The runner records child WPT exit separately; an original WPT assertion exit of 1 is allowed only when lifecycle, identities, infrastructure and preservation checks establish a complete observation.

## Version 2

Version 1 omitted the proposal's explicit attr-all-types gate. This version adds that unchanged fixture, its exact 178 saved identities, live source/header/metadata pins and genuine manifest entry. It retains all 66 target identities, the prior 151 regression identities and six reftests. There are 395 total subtest assertions. No original raw browser run occurred with version 1; it remains immutable historical preparation.

## Preparation evidence

`ASSESSMENT-TESTS.json` records synthetic assessor controls, including missing/failing assertions or pages for each target, unchanged regression drift, lifecycle faults, BuildID/revision drift and compiled-role/acceptance guards. `APPLICATION-METADATA-TESTS.json` covers regular and symlink application metadata plus replacement, retargeting, broken-link and non-regular-target controls. These are harness tests, not browser observations. `PREPARATION-CHECK.json`, `MANIFEST-GENERATION.json` and `MANIFEST-ROUNDTRIP.json` authenticate captured resources and the genuine WPT manifest. No browser, Mach, build or live-file mutation was performed while preparing this capsule.
