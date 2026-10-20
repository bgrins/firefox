# Exact app-unit translation through the existing traversal

Status: **ARTIFACT_PROPOSAL_PENDING_INDEPENDENT_REVIEW_AND_FULL_BUILD**. This is a successor to the held duplicate-walk integer rectangle repair. It has not been installed, built as Gecko, run in a browser, or measured for performance. The independent DOMRect precision fix is preserved as an unchanged source role.

## Candidate

`proposal.patch` changes four native files: nsIFrame.cpp/.h and nsLayoutUtils.cpp/.h. Original/current and candidate snapshots are retained. The patch applies to those retained originals and reverses byte-exactly in an isolated directory. Main native files, browser/build, Git and index were not modified. Root supplied HEAD fb6c1b5cc7f2 and DOMRect commit c0e8c7fd1deb as context; source SHA-256 identities, not a new Git lookup, bind this artifact.

`GetTransformMatrix` optionally returns `mozilla::AppUnitTranslation`, with signed-64 x/y fields. The ordinary traversal uses checked signed-64 offset/docOffset state when this result is requested. Existing callers with a null result pointer retain their original nsPoint additions and scaling. The new carrier is defined in nsIFrame.h and forward-declared in nsLayoutUtils.h, which only forward-declares nsIFrame; no nested type of an incomplete class is required.

`GetTransformToAncestor` passes the optional result only to its first segment. If that segment does not reach the requested ancestor, exact metadata is cleared and the original subsequent matrix multiplication/project-to-2D sequence continues. Every method entry clears stale metadata, including self/root early returns. No later segment can restore a discarded exact result.

A CPP-local `TransformClientRectToAncestor` opts in only from the existing root-relative, non-outer-SVG BoxToRect branch. It checks the frame/context/SVG and rectangle prerequisites, obtains the matrix once, and uses checked integer translation when available. On ordinary transformed fallback it passes that same matrix to the existing rectangle API as a populated cache, avoiding a second ancestry traversal. Same-frame identity is handled explicitly by the wrapper as zero translation; this preserves the earlier helper's zero-length exact route despite the metadata methods' conservative early returns.

## Arithmetic and domain

Two real source-arithmetic omissions in the first draft are preserved in development evidence and fixed here:

1. Leaf position −2,000,000,000 followed by +1,400,000,000,+1,400,000,000 gives rectangle-relative prefixes within signed32 and final800,000,000. The old separately grouped docOffset reaches2,800,000,000 and overflows. Checked64 ordinary accumulation now returns the exact rectangle without executing the overflowing nsPoint operation.
2. Rectangle x=−2,000,000,000 followed by positions+1,500,000,000,+1,000,000,000 gives valid prefixes and final500,000,000, while translation alone2,500,000,000 does not fit nsPoint. The carrier and final rectangle additions remain64-bit until checked endpoints justify narrowing.

The imported `numeric-bounds-v2` component has nine Lean results: differences between any two signed32 rectangle-relative prefixes are within ±4,294,967,295. Thus all v1-admitted ordinary translation and ancestor-subtotal prefixes fit signed64 without a frame-count bound. This is a mathematical bound plus a manual source correspondence: same-context ordinary traversal visits the same positions, with offset initially the first position and docOffset accumulating subsequent positions. It is not a kernel proof of frame construction, native traversal, CheckedInt, graphics, or complete CSSOM behavior.

Preserving v1's admitted domain means **inclusion**, not identical acceptance. Example x=1,000,000,000 with positions+1,500,000,000,−2,000,000,000 is rejected by v1 at its first signed32 rectangle prefix but returns exact500,000,000 here. The larger checked64 domain is deliberate: no intermediate rectangle clipping exists on the admitted ordinary translation route, and final coordinates/edges and dimensions still satisfy the original nscoord-range clipping prerequisites. This does not promise identical final rectangle output on every formerly rejected route.

## Old-defined matrix behavior and numerical fallback

For each old-defined path, wide offset/docOffset additions have the same integer values as the original grouped additions. At an APD change, the code uses the existing `nsPoint::ScaleToOtherAppUnits` with the same narrowed docOffset arguments; it does not replace its rounding/clamping with a new formula. The same offset flushes, resets, cross-document additions, ancestor choices and matrix composition remain. Equal-APD conversion is the existing identity branch. Final wide integer-to-float conversion uses the same cast/divide value for representable old operands. This is a source argument supported by extracted differential checks, not exhaustive native/provider verification.

If a checked64 operation fails, or differing-APD scaling requires a docOffset already outside signed32, the method calls its original null-metadata path. Such a restart is outside both the old-defined arithmetic domain and v1's admitted same-context exact domain. Exact metadata remains empty and cannot recover from that failure. There is no early saturation, guessed frame-count limit, or newly invented approximate-coordinate policy.

**The legacy restart can still execute legacy undefined arithmetic.** The retained cross-document/APD witness deliberately reaches this gate, prints the extraction's restart marker and triggers UBSan in the original addition. It is an expected negative result, not a candidate pass or a universal arithmetic-safety claim. Every tested old-defined configuration has the same method-entry count with metadata as without; ordinary deep transformed paths do not restart. This does not establish the absence of all numerical restarts in all browser frame graphs.

## Source and provider boundaries

The opt-in exact route requires a single ordinary same-context layout segment, no transform/SVG-text/SVG-layout frame on the traversed route, empty transform flags, and a reached nonnull target. The target's own transform is correctly outside its relative coordinate system. Initial outer-SVG substitution and source SVG-text recursion remain on the original path. Non-root BoxToRect requests, cross-context roots, visual viewport/APZ requests, explicit matrix caches and other public rectangle callers retain their existing APIs and routes.

For a rejected ordinary candidate, the precomputed matrix is handed to the original rectangle conversion with the same frame/APD, null axis-preservation pointer and null out-ancestor pointer used by this caller. Source SVG-text requests are rejected before precomputation so their original geometry conversion/recursion is preserved. Getter purity, stable frame lifetimes after layout flushing, actual context/frame topology and platform graphics providers remain native admissions.

Actual 3D transforms, perspective, SVG geometry, cross-document/APD conversion, zoom/APZ clipping, and complete cache/caller behavior have **not** been executed against a full Gecko build here. The source inspection preserves these fallback paths; the extracted facade is not a substitute for their implementation. Current main header/include integration and all caller compilation remain full-build gates.

## Retained checks

- Full extracted original and candidate GetTransformMatrix/GetTransformToAncestor methods plus the exact new wrapper compile with actual Mozilla CheckedInt headers at O0/O2 under UBSan.
- 168 old-defined configurations per optimization compare original/candidate matrix values, operation grouping traces, ancestor outputs and method-entry counts. Cases include depths1/8/128, early/late transforms, SVG rejection, context/cross-document transitions, APD29/61, layout/visual routing, scrolling flags and stopping flags. Candidate null-metadata behavior is also compared.
- 2,048 generated v1-admitted finite chains match the exact v1 helper per optimization. Targeted controls cover zero-length identity, clipping/extents, both missing wide-domain witnesses and the expanded-domain example.
- Five semantic mutants fail at both optimizations: wrong translation, missing SVG guard, missing flag guard, dropping cached fallback and dropping exact self handling.
- Both wide-domain witnesses trigger original UBSan and pass candidate checks. The separate cross-document restart witness intentionally triggers original and candidate legacy UBSan.
- Canonical and relocated closed-capsule replays agree. Six controls reject wrong manifest pins, extra cache files, modified source, output inside the capsule, optimized Python and nonisolated Python before compiling or creating output.
- Changed ranges were formatted using clang-format22.1.8. This is artifact formatting, not a main-tree lint or full build.

The facade models frames, transforms, scaling and rectangle fallback. Its matrix is a deliberately limited affine provider with an operation trace; it does not implement Gecko's full 3D GFX machinery. Source snippets are bound before adding a method-entry counter and restart stderr marker. Development includes an initial restart fixture that did not reach the intended gate; that failed hypothesis is retained and excluded from accepted replay evidence.

## Handoff and remaining gates

Run `python3 -I -S -B verify.py --files-sha256 OUTER_PIN` to verify the closed artifact and retained result consistency. For a fresh native extraction replay:

```
python3 -I -S -B capsule/replay.py --files-sha256 ccfc2946ea8a71b25f1c14edf3eb2022be3984f6b1019a79b8a145cbd0909da1 /tmp/NEW-UNUSED-OUTPUT
```

The existing standalone four-case integer WPT is referenced in `WPT-REFERENCE.json`; no production test was edited or weakened. Before acceptance: independent source/capsule review, full caller/header build, paired exact-geometry and transform/SVG/iframe/scroll/zoom regression tests, then the focused six-case performance comparison. Avoiding a duplicate traversal does not prove the added checked arithmetic is cheap enough. The full safe-origin and CSS specification projects remain open.
