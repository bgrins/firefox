# Standalone nowrap patch: review and formatter check

**GO for the isolated paired native experiment.** No concrete correctness blocker was found in the three native hunks or the unchanged 169-callback WPT. Publication still requires the fresh original/candidate target and regression results; historical combined-worktree results are not substituted for that gate.

`fix.patch` is the exact two-file publication payload: `dom/base/nsLineBreaker.cpp` plus `testing/web-platform/tests/css/css-text/white-space/nowrap-inline-break-policies.html`. The native preimage is `c8b2d4f7`, candidate `a87f4210`, patch `b499d2a2`, and WPT `3c390a8c`. Full hashes are in FORMAT/RESOURCES. The test is already an untracked recovered file in the working checkout; the installer must verify/adopt its exact bytes rather than overwrite it blindly.

The configured `.mozbuild/clang/bin/clang-format` 22.1.8, with repository and `dom/` configuration, produces **no changes**. The initial description of this candidate as unformatted was not confirmed. Both changed-range idempotence and a full-file replacement check succeed; `FORMAT-DELTA.patch` is empty. No native source was edited. FORMAT records the actual executable/configuration hashes and commands. The exact forward/reverse patch check uses an owned temporary tree, removes it, and checks both postimages without offsets or fuzz.

Native review:

- At chunk offset zero, INITIAL alone controls the first byte. INSIDE starts at the next byte. This preserves a permitted boundary before a nowrap inline inside wrapping text.
- At a positive chunk offset, every byte in the published span is interior, including a span following a buffered contribution. The helper correctly uses the callback's chunk offset, not a word-relative offset.
- Length zero returns before dereference, pointer advancement or subtraction. Length one at offset zero advances only to the one-past pointer with a zero remaining length. Both callbacks retain their existing allocation, sink and `noBreaksNeeded` guards and bounds.
- Both immediate AppendText paths apply the mask after all break producers and before SetBreaks. Buffered FlushCurrentWord already applies the same positional flag rule. Its first-word skip is preserved, so the immediate first-byte decision is not overwritten later.
- Unflagged bytes, callback ranges/order, buffering, language/hyphenation providers, capitalization and mutable stream state are unchanged. This prevents new forbidden break bits; it does not claim to clear arbitrary stale glyph bits or repair unrelated invalidation.

The WPT waits for the pinned Ahem face and calibrates its five-character width. Its matrix covers normal/break-all/keep-all/anywhere, whole/adjacent/nested text, wrapping and nowrap containers, capitalization delegation, min-content sizes and an allowed initial boundary. The source constructs `ABC D` without a forced break or markup whitespace. Geometry observations are assertions, not timing measurements. No test bytes or oracle changes were necessary. The five required resources are pinned in RESOURCES; fresh underlying WPT path/content lint returns zero, the manifest is genuine, and all 169 names are unique. No expected-failure metadata is introduced.

Current primary spec review supports the fixture's narrow oracle (SPEC.md). Searchfox supplied the chunk suppression contract from its cached header. Network retrieval of the cpp/permalink failed with DNS errors; exact admitted cpp bytes were reviewed directly. The spec-index query failed with a read-only database error, so no successful indexed anchor trace is claimed.

Validation receipts: formatting/roundtrip/resources `a93bac/0`; WPT static success is retained in `static-check.log` (the combined shell receipt `71aab3` exits one only because the subsequent spec-index query failed). No native build, browser execution, Git write or live checkout mutation occurred. The paired owner must preserve all fresh-baseline passing outcomes and endings, require all 169 target callbacks PASS, and preserve exact fresh regression signatures without assuming the historical combined baseline's counts.
