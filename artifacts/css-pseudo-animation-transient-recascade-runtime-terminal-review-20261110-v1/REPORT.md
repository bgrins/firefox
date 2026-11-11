# Transient recascade failed-build terminal review

The live hold can be released. Independent raw-result and restoration checks pass. The candidate build failed, and no candidate WPT, query-driver or recascade-driver suite executed. This run provides no native semantic acceptance.

The frozen runtime manifest is `218eef805552d4d1911efdeb686b819ddf9beacbdd37ec0505ab50e60abf54f0` at HEAD `ec467c0219d3d5daf70f42fcc53677cf8a262173`. Every frozen input was authenticated. The baseline raw stream has exactly 130 records: 99 PASS, 19 expected FAIL and 12 OK harness endings. Full callback identities, statuses, messages and expected classifications match the frozen baseline vector; suite lifecycle is complete, with no raw crash/error event.

Candidate WPT lint, both installed ESLint checks and manifest lint passed. The real binaries build returned 2. The retained build log contains one actual compiler error: the temporary driver spells the generated enum member `PseudoStyleType::after`, where the compiler identifies `After`. The build stopped before candidate sampling and tests; the source and binary hashes in BUILD.json are failure-time evidence, not a successful candidate executable. Other code may still contain compile issues not reached by this build.

A targeted source follow-up found the same lowercase naming mistake in the production helper's Before/After/Marker guard. The author has retained the original capsule and prepared capitalization amendments separately. `BUILD-LOG-SUMMARY.json` distinguishes the actual compiler diagnostic from an unrelated SDK method name containing the text `error:`.

Restoration was checked against both transaction snapshots and the retained browser receipt, not only wrapper booleans:

- All 9,378 app entries and 42,811 installed Mochitest entries match, including the helper's semantic file/link/mode representation.
- All six extras/metadata files, 14 source roles, existing test/config pins and retained executable hashes match.
- HEAD and staged-index identity are unchanged; tracked worktree/index are clean. All 527 unrelated untracked paths match the retained inventory.
- Temporary fixtures, backup directories and runtime lock are absent. All seven recorded lint/build/test process groups are absent from an independent process snapshot.

`review.py` derives raw records independently and performs the complete live restoration scan. `INPUTS.json` binds retained raw/build/process/result receipts. Build intermediates were not promoted to an accepted browser; a follow-up requires another real build and fresh successful executable receipts.

## Additional marker assertion finding

The capitalization correction alone does not establish the declared Marker support. At the pinned revision, `PseudoElement::is_eager` reads `IS_EAGER`; the generator defaults that field to false, and the Marker definition supplies only tree-abiding status. However, the newly admitted Marker request calls `StyleResolverForElement::cascade_style_and_visited_for_pseudo_with_default_parents`, whose underlying cascade method asserts that a supplied pseudo is eager. The matching source pins are retained in MARKER-PINS.json and marker-source/. This is a concrete debug-assertion hazard found by source review, not an observed debug crash or another Firefox bug count.

The earlier source-only review left compilation/debug gates open but missed this specific restriction. The newly established condition supersedes its no-blocker conclusion for the eager Marker route.

The existing `Stylist::compute_pseudo_element_style_with_inputs` is the appropriate narrow route to investigate for Marker: it forwards both rule paths and the explicit pseudo/origin to the common cascade without the eager assertion. It preserves the native lazy-pseudo convention of using the supplied primary style as both inheritance and layout parent, including that helper's documented layout-parent limitation. Before/After should retain their existing pseudo-aware default-parent route. The author is preparing this as a substantive separate follow-up, not altering the failed evidence.

Full public CSSOM integration, provider/sample coherence, visited exposure and the final missing-pseudo debug regression gate remain open.
