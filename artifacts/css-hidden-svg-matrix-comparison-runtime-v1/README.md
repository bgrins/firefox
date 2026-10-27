# Disabled standalone SVG matrix comparison

The draft is disabled. No source, index, WPT, browser or build mutation has run. It reuses the reviewed integer-client comparison driver and its WPT execution/parser, plus the existing owned browser capture/cleanup helper. The executable delta is retained in `run.py.diff` and `tests.py.diff`.

## Source roles and ownership

Initial role: the successful restored OOF trace epoch `0bbbfcb6…`, including expanded112 and older working prototypes. Its 49 sources/337 pins/current rebuilt binaries and installed-test identities are authenticated through the existing epoch gate. Add clean `SVGGraphicsElement.cpp` as guard50. Preserve the exact HEAD90, 925 staged research payloads, and current 26-path native inventory.

Baseline: normalize all 26 tracked native differences to their exact HEAD90 bodies. Candidate: that same baseline plus only the proposed SVGGraphicsElement.cpp body. The normalized source roster is27 including the initially clean candidate target. The baseline must have no tracked native differences; candidate must have exactly the one SVG native difference. Pending107 is absent in both roles. HEAD90 already contains earlier committed fixes and is not described as pristine upstream.

The two installed112 WPTs remain untouched, with exact bytes/inodes and untracked ownership preserved. Exclusively create the proposed eight-case SVG WPT, using its final test filename. Six existing WPT controls remain unchanged. Phase inputs consist of303 non-source resource/metadata pins,50 source pins and the owned test, plus both freshly built binary hashes. Historical resources are transferred without adopting a new unnoticed support version. The selected XML fixtures' harness scripts are explicitly pinned in `support_paths`; normal linked support and ancestor metadata are discovered by the existing helper. This is bounded fixture discovery, not a general transitive-loader claim.

## Execution and outcome gates

Root activates a fresh runtime copy and reseals DRAFT-FILES, then uses:

```
python3 -I -S artifacts/<runtime>/run.py --draft-sha <activated-manifest-sha256>
```

The driver checks ownership before mutation, installs the one WPT, runs its exact WPT lint gate, then builds/tests HEAD90 and the sole SVG candidate sequentially. All seven files and34 unique subtest identities must complete without infrastructure faults or source/resource/binary drift. The existing WPT runner and infrastructure parser are AST-identical to the reviewed base; names are compared as exact unique sets, without incidental report-order dependence.

Baseline visible/no-viewBox controls must pass. The two hidden viewBox rows may either pass or fail at the first post-resize matrix assertion; their actual results and messages are retained. No predetermined baseline failure count is required. Candidate must pass all8 main assertions. Existing26 control assertions must respect expected metadata, retain every baseline pass and preserve diagnostics for any continuing FAIL. A failure of the candidate's hidden histories stops acceptance;107 is not silently added.

After each phase's WPT gate, a fresh owned browser/profile captures the proposal's8 availability rows (detached, display:none, defs and singular, both methods). Require all8 repeat-stable, complete finite/null/exception schemas, exact identities and connectivity, source/binary/resource joins and cleanup. The entire baseline/candidate payload must match; historical availability is not recast as a new normative assertion. A coverage correction to the sealed proposal README: existing `SVGGraphicsElement.svg` already checks detached return types, because its rect is never attached. The research capture adds full matrix/null/exception observations rather than claiming detached coverage was wholly absent.

Restoration is in `finally`: independently attempt every original source restoration using recorded owned inode/body pairs, remove only the owned WPT inode, and rebuild only if all original source bodies were restored. Unknown edits are refused. Preserve both installed112 WPTs, all metadata/support guards and the exact index. The restoration tail matches the reviewed base after only the temporary-file suffix substitution and added `FINAL-PINS.json` receipt. Build commands retain the base driver's process/timeout limitations; this is not arbitrary interruption recovery.

No acceptance, bug number or native installation is automatic. The standalone result, availability comparison, restoration and independent review are required before a landing decision.

## Static verification

`check.py` authenticates the archived epoch/proposal, compiles Python, validates50/27/26 source roles and7/34 test scope, verifies exact fixture copies, confirms unchanged WPT runner/fault-parser AST and restoration tail, and exercises four negative outcome gates. It performs no browser/build/lint or live native/index validation. `STATIC-CHECK.json` is the receipt. Root activation must recheck actual current state through the driver's preflight.
