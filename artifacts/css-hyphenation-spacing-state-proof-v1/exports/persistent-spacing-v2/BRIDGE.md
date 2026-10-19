# Persistent spacing source binding and remaining obligations

This supplement preserves the approved full ownership scope. It proves a stateful component that the earlier completeSpacing interface did not supply. It does not claim full native ownership, consumer or Firefox correctness.

## Native association

Sixteen complete native definitions are pinned in SOURCE-BINDING.json and reproduced from the retained candidate4 nsTextFrame.cpp/.h. The source bytes come from the authenticated full-scope dossier, not live source. Reflow construction initializes mTabWidths to null, mTabWidthsAnalyzedLimit to zero and mOffsetFromBlockOriginForTabs to its constructor argument. Display construction also starts without a local cache, with zero offset, and later borrows the frame property. The header explicitly says a non-null mTabWidths points to that frame's TabWidthProperty.

PersistentTabs.frontier corresponds to startOffset plus either mTabWidths->mLimit or mTabWidthsAnalyzedLimit. CalcTabWidths uses precisely that frontier, computes previously unvisited indices in increasing order, and retains the running numerical offset. Its before/advance-or-nextTab/after ordering is preserved for arbitrary arithmetic operations; no floating-point associativity is assumed. The existing native-shaped TabValues step is related to a separate numerical fold whose state contains only offset and tab entries. Arbitrary query sequences now derive their states from construction, rather than supplying unrelated states for each query.

PropertySession records the cache/property association across the exact branch structure: disabled calculation preserves everything; intrinsic reflow with no cache and no line container returns without deleting even a stale property; non-reflow with no cache loads the current frame property; normal computation publishes/reuses the cache or removes a stale property when no tabs exist. A non-null local cache remains associated with the same modeled property. Frame/run/content-offset labels are preserved. This is a value-level alias relation, not a proof of C++ pointer validity, deletion semantics or concurrent/external mutation. Property replacement/removal is abstracted to the source's Get/Set/RemoveProperty operations.

SpacingAssociation derives each saved-property context and tab state from the preceding session and proves exact agreement with the existing complete calculateAndApply values. It retains ordinary, tab and justification phases and ignore-tabs recursion through the existing joinedProviders theorem. Arbitrary request histories preserve the local association and answer count. It does not invent a separate valid cache for every query.

## What is newly universal

- Constructor-derived cache frontier is the maximum endpoint of an arbitrary valid reflow query history, including decreasing, overlapping and repeated ends.
- Singleton no-tab spacing requests visit each newly covered source index once and in order.
- Final offset and complete cached tab-width entries equal an independent numerical fold over the covered prefix. Equal coverage yields equal values and singleton request sequences, without reordering numerical operations.
- Current-property loading and cache/property association persist through modeled request sequences.
- The stateful query returns exactly the existing complete spacing result from its derived context.

Model witnesses distinguish proper persistence, repeatedly resetting state (duplicate provider requests) and independently seeding an incompatible offset/frontier (width 8 versus 7). They show why the interface needs an invariant; they do not establish a browser bug or assert native reachability of the bad seed.

## Still open

1. Native object/source readiness: actual frame/run identity, source text and style epoch, positive numeric tab width, original/transformed coordinate bounds and defined machine arithmetic must admit these fields. A mathematical contentOffset token is not source epoch validation. EnsureTextRun only explicitly drops a cached property with mismatched content offset on its reconstruction branch; broader lifecycle freshness remains a caller obligation.
2. Provider stability: the prefix theorem requires the same numerical/Unicode/font/spacing providers and start coordinate during the history. InitializeForDisplay/InitializeForMeasure change mStart/mLength; SetStartOfLine affects spacing. They are retained full source, not assumed harmless. A history must start after the relevant preparation, or model a justified reset/epoch change. External mutation of a borrowed frame property is excluded by the still-required native lifetime association.
3. Measurement request admission: connect the actual constructor/refill and nested ligature calls to this history, including actual GetSpacing's HasTab gating, and derive each range/phase input. V2 proves constructed-cache binary-search/ApplySpacing clipping stability, but full Result.present remains history-dependent and must be preserved or projected only by the actual consumer.
4. Native numeric/heap/font/FFI limits remain the explicit original trusted or open boundaries. There is no native build in this supplement and no new finite matrix. Original LF/nowrap/Ahom and mask-loss counterexamples remain unchanged.

## Additional v2 joins

CacheQueryStability proves the native strict binary-search result equals an independent linear selection, then proves later tab entries cannot change an earlier query's applied writes. CacheConstructionBridge derives sortedness, strictness and bounds from constructor numerical-prefix execution; it does not assume those properties independently. Its final theorem compares arbitrary two histories with sufficient coverage and derives exact equality of applied tab writes.

SpacingPresence retains a concrete limitation on abstraction: GetSpacing's complete Result is not pure in its range. A prior query that constructs a cache for a later tab makes an earlier tab-free query return present=true, while a fresh provider returns false with identical zero spacing. The kernel witness checks both flags and every index/side of the zero store. This is allowed: the complete gfxTextRun::PropertyProvider contract explicitly permits true if spacing may be present. BreakAndMeasureText ignores GetAdjustedSpacing's return value at initial/refill requests; ComputeLigatureData checks it before adding spacing. The example's Nat zero-add observation is proved; no universal IEEE signed-zero/NaN theorem is inferred. All complete native methods are pinned. This is an interface counterexample, not a Firefox defect.

The next useful join is actual measurement request admission, including nested partial-ligature spacing queries, followed by the consumer-specific projection of the present flag. Preserve the flag in full provider traces; use array equality only where the native consumer justifies it. Actual ordinary-spacing input formation, source/style epochs, shared property lifetime and display-after-reflow readiness remain open.
