# Hidden SVG matrix repair proposal

Unaccepted, unbuilt two-path proposal: `dom/svg/SVGGraphicsElement.cpp` plus one eight-case WPT. `gecko-wpt.patch` applies to the retained HEAD90 source. The working native tree and index were not changed.

## Observation and proposed change

The sealed browser diagnostic on the mixed installed working build observed two stale matrices: after a hidden owner's width changes from 100 to 200px, both matrix APIs retained scale1 instead of scale2 for a percentage-sized outer SVG with a viewBox. The six visible/no-viewBox controls passed; all eight histories calibrated and repeated stably. The first recorded recovered matrix follows getBBox, with twin/host/style reads between repeat and getBBox. Subsequent layout/reveal observations are sequential. This establishes the first-read defect, not an isolated causal proof that getBBox alone caused recovery.

Replace each existing document-only layout flush with `GetPrimaryFrame(FlushType::Layout)`. That helper already performs the document layout flush and additionally forces dirty hidden content, then reacquires the frame. Its return is deliberately unused: the existing matrix provider and singular-result fallback continue to determine the result. Do not add a second document flush or a new null/no-frame/non-display early return.

This preserves the prior disconnected path (the helper returns immediately without a document), the document flush when no primary frame exists, and downstream no-frame/non-display handling. The code which composes transforms and replaces singular matrices is unchanged. For a dirty hidden frame there can be a necessary second layout flush through the forcing path; the proposal does not claim zero additional work. No pointer is kept across that reflow.

[SVG2 SVGGraphicsElement](https://svgwg.org/svg2-draft/types.html#InterfaceSVGGraphicsElement) requires the coordinate-system matrix including the relevant viewport/viewBox transformations. Its unavailable cases and detached matrix creation remain separate. This patch repairs geometry preparation for step3; it does not rewrite all SVG2 availability semantics or assert that existing identity fallback is universally normative. The current WebIDL is nullable even though this native path returns its existing matrix fallback.

## Standalone acceptance gate

The existing hidden-content forcing gate still requires queried-subtree dirtiness. Pending fix107 marks skipped block descendants dirty; the observed working build includes it. Therefore textual patch independence does not establish semantic independence.

Run the new WPT on normalized HEAD90 and HEAD90 plus only this native change, without any pending106–112 overlays/prototypes. Do not assume the recorded working6PASS/2FAIL count transfers automatically. Require calibrated visible controls and all eight candidate tests passing. If either hidden first read remains stale, stop acceptance and investigate provider readiness; do not silently absorb107 or weaken the WPT. A separate installed-working candidate role can diagnose interaction if necessary. HEAD90 itself already contains earlier committed accepted fixes and is not claimed to be clean upstream.

The WPT gives each method/viewBox/visibility combination a fresh DOM tree. Only the owner rectangle is queried between hiding and the viewport resize. The first descendant observation after resize is the matrix assertion. There is no getBBox rescue or prior method sharing. Successful cases then check repeat, reveal and restore. Signed zero is normalized without changing any nonzero or nonfinite value. The diagnostic's twin is omitted from the landing test: exact expected components follow from fixed CSS/attributes, and visible cases independently exercise that same formula.

`CONTROL-ROSTER.json` pins six focused existing WPT files and their direct metadata. Run them in both source roles and retain every outcome/diagnostic; standard fixture support and ancestor metadata must be pinned by the eventual controller. These cover screen transforms/padding, empty viewports, interface types and hidden SVG text. The bounded Searchfox search found no dedicated automated disconnected/display:none CTM WPT, so no such coverage is invented. The separate eight-row `availability-probe.html` captures detached, display:none, defs and singular behavior for each method. Compare complete baseline/candidate observations after validation, without turning historical nonconformance into new normative WPT assertions. This research page is not in the native patch.

## Formal scope and verification

The existing `CssSemantics.ProviderObservation.query` model sequences optional forcing before observation; its `successful_state`/`successful_observation` results describe that supplied transition. This proposal adds the missing native entry into that sequence. Those theorems do not establish Gecko's dirty admission predicate, viewport freshness, native branch reachability or absence of unintended reflow. No new Lean proof, model coverage claim or automated bug-discovery attribution is made here. The concrete lead arose from source/caller audit followed by browser reproduction.

Pinned clang-format on the changed C++ range passes without a delta. Both JS files parse; inert registration obtains exactly eight unique WPT names without running test bodies. The exact two-path patch applies and reverses in a disposable scratch directory; native and test bytes match the retained candidate exactly. No browser, native compiler or WPT lint ran during proposal preparation. Full compilation, lint, isolated correctness, availability preservation and existing controls remain required before acceptance.
