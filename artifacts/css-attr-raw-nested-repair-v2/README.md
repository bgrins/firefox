# Raw nested attribute repair, version 2

This version retains exactly the version 1 native postimages and adds a third explicit correction to attr-cycle.html plus seven parser-boundary controls. The first comparison repaired all 13 original disagreements and passed all 29 new tests, 329 regression assertions and six reftests, but failed the old EOF oracle. That failed acceptance gate remains recorded. Version 2 has not run in a browser.

The current CSS Syntax function consumer returns its function object on EOF. For data-foo=`attr(data-foo`, the inner bare read therefore returns the unchanged attribute text as a CSS string. The existing expectation abc is obsolete; the corrected expected string contains no added parenthesis. The versioned EOF audit and independent trace supply fresh primary evidence. This is the same raw-versus-typed distinction as the native repair, not a separate native fix or a new bug count.

The patch still has exactly three paths: cascade.rs, attr-cycle.html and attr-raw-nested-cycle.html. It depends on the accepted used-fallback repair's helper. The current live and committed-base equivalent native postimages are byte-identical to version 1; no prototype changes are added. The exact patch applies, reverses and reapplies to both captured bases with exact three-path postimages.

The new fixture contains 36 tests: all prior 26 fixed cases and three mutation tests unchanged, plus seven fixed cases listed in EOF-CONTROLS.json. TEST-CHECK.json verifies all original29 identities and data remain, helper/mutation bodies are unchanged, all 37 existing helper calls remain, and only the EOF call changes relative to version1. The two earlier oracle corrections and both resolution-order variants are retained.

## Acceptance gates

First complete the separate used-fallback comparison. Then run the corrected attr-cycle fixture and the new fixture on both the used-fallback baseline and raw candidate; require all new assertions to pass and exactly the documented old-oracle changes. Preserve the 34-test used-fallback fixture, numeric-token, typed-preparation/eligibility, namespace-cache/namespace variants, non-custom-cycle, all-types, no-type-fallback and existing order regressions. Retain the root's native demand-resolver regression gates as applicable. No unexplained regression may be hidden by changing expected metadata.

For this version, a newly frozen capsule must run all 73 target assertions (37 existing and 36 new) on both original and candidate sources; candidate targets must all pass. The 329 regression assertions and six reftests remain mandatory. Existing raw capsule versions remain immutable and do not represent this third correction or the seven added cases. A fresh original observation is required; the earlier failed candidate run cannot be relabeled as successful.

Only cascade.rs and the two WPT files belong in an eventual standalone fix after the used-fallback prerequisite. All snapshots, normative traces and transport tooling are research material. Preparation did not change native/live WPT sources, existing capsules/runtime evidence, canonical Lean, index, HEAD or epochs, and did not launch a browser/build. EOF parsing is outside the normalized Lean guard model's proof boundary.
