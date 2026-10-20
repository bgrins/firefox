# Boundaries

The result is a conditional model/source correspondence with concrete native calibration. Lean checks the mathematical models and the stated arithmetic domains. Extracted C++ is compiled and compared on a finite corpus; neither extraction nor the C++ compiler is formally verified.

## Native entry and providers

The raw border/margin/content/overflow rectangles, frame position, normal position, padding, scroll position, parent-to-scroll offset, viewport size, computed insets, and containing-block writing mode are supplied values. They are not assumed to equal final sticky results. The harness runs the complete selected native functions, actual containing-block selection, rectangle union accumulation, WritingModes helpers, BaseMargin, BaseRect deflation/setters and BaseRectAbsolute. Its visible frame/tree/viewport/transform/length-percentage facades are trusted adapters.

Lean takes the already unioned border and margin rectangles and the selected/transformed containing rectangle. Saturating union, recursive frame traversal, full transform matrices, pointer identity/lifetime, layout's production of these values, anchor/percentage resolution, and scroll-container discovery are not universally proved here. The local scrolled-content padding Deflate arithmetic is separately bounded and proved in WideProviders; transform output remains an explicit provider boundary after that operation. Native calibration covers ordinary content blocks, scrolled content, row-group redirection, and continuation inputs and checks their exact provider-call traces.

The frame passed to the caller theorems is the first continuation selected by the source entry. The source-extracted entry and native adapter perform that canonicalization; continuation input cases and a compiled wrong-continuation mutant test the binding. This is not a proof of Gecko's complete frame graph.

## Numeric domain

InMachine is the complete signed32 storage interval, distinct from the conventional nscoord coordinate interval. WideNormalization accounts for each actual signed64 subtraction and the compound-assignment narrowing. ProviderBounds (nonnegative port and border sizes no greater than nscoord_MAX, and coordinate-bounded insets) suffices for narrowing, but is not asserted to follow from the C++ typedef. Safe can instead directly check the actual normalized result. The kernel rejects a signed32-only size assumption that would narrow -3221225470.

Core, position, translation, optional-range, and absolute-range domains recursively check executed expression intermediates. Some core checks are conservative when a later caller does not read an edge. Range domains include discarded inner assignments, checked FromRect conversion, cross-axis empty intersection, and all executed MoveInsideAndClamp intermediates. The complete repaired wide example is admitted without constructing a signed32 stick extent.

DebugSafe separately describes assertions excluding active edges equal to the finite sentinel and requiring range ordering. These are not a proof that all provider outputs avoid such collisions. GetScrollRanges preserves the existing encoded-sentinel branch behavior. Combined and standalone profiles preserve their different activation, end selection, and positional masks; no claim is made that the standalone profile fixes the separate H1/H2 or positional-sentinel defects.

The retained clamp frame has defined old normalization and old stick storage. Both old and repaired native callers overflow the same outer-height subtraction, 1073801223 - -1073740223. AbsoluteSafe rejects it. Browser reachability remains a separate lead; this artifact claims neither universal range safety nor that this preexisting limitation was repaired.

## Outside this handoff

ComputeStickyOffsets and length/percentage/anchor resolution, scheduling, reflow, continuation movement/update side effects, ViewTimeline Earliest/Latest arithmetic, timeline attachment, CSS parsing/cascade, and full CSS conformance remain outside the changed caller proof. Some unchanged functions are retained in the extracted compilation unit for context but are not counted as new verified paths. Earlier separate proofs and native/WPT evidence remain immutable and are not promoted to new results.

Lean's kernel, approved axioms propext/Classical.choice/Quot.sound, the pinned Lean distribution, compiler/header closure, Python, OS and dynamic runtime are trusted. Source role receipts authenticate the historical local tests; this replay does not rebuild Firefox or rerun WPT. The independent native review retains those browser/build receipts and their limitations.
