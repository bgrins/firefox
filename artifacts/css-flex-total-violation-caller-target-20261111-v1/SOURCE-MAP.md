# Source map and remaining realization joins

Pinned native.snapshot.cpp SHA cc649bb12d69438bcc84f67e77dcafa25f58a574475f8235211cc6da3de9822c includes the accepted prior two fixes and root total-violation candidate. Searchfox discovery logs retain the upstream baseline; no silent claim that indexed upstream contains the local candidate is made.

| Actual source | Model | Outstanding native/provider join |
| --- | --- | --- |
| Normal FlexItem defaults and SetFlexBaseSizeAndMainSize | normal Seed/seedItem | effective bounds, resolved base, hypothetical identity after all setup providers |
| Strut constructor; early inflexible Freeze; CloneFor | retainedFrozen/strutSeed | actual settled frozen state and copied lifetime/frame identity |
| FlexLine count0; AddLastItemToMainSizeTotals | initialLine/appendItem | exactly-once bookkeeping after line placement; valid array/lifetime/count31 |
| FreezeItemsEarly | earlyItem/earlyWalk/early | zero-test observations, chosen grow mode, preserved map and exhausted counter |
| ResolveFlexibleLengths base reset and distribution | resetBase/suppliedItems/ProviderValid | floating arithmetic, preferred bound, full positional provider output |
| Min/max violation loop | clampItem/clampWalk | source flag freshness and scalar V2 acquired bridge, derived from history |
| Freeze/ClearViolationFlags/SetWasMinClamped/SetWasMaxClamped | freeze/freezeWalk | frozen flags mean clamp history; survivor flags mean current violation |
| FreezeOrRestoreEachFlexibleSize final fallback | explicit finalIteration branch/fallback bit | prove unreachable from actual generated history, not remove branch |
| NumItems for-loop and post-pass break | LoopState/advance/History | current control-state abstraction excludes no optional-info pass |
| aLineInfo base/growth/delta writes | wantsInfo + external non-mutating-output provider | valid buffers/index, narrow diagnostic delta arithmetic, observer semantics |

The scalar target/proof and its independent review are frozen predecessors. This target does not redefine their clamped/difference/selection meanings. The fresh survivor invariant is narrower than all-flags-false: frozen min/max flags are intentionally retained as clamping observations.

The actual Source has valid-array count assertions and counter-based early exits. We do not replace those counters by filtering in the executable; filtering supplies the independently stated remaining/count and scalar subset relations. Likewise the positional clamp relation checks complete list length/order through Aligned, not a truncating zip alone. The provider's explicit equal-length premise protects the executable zip.

## Initial-count producer audit

The source snapshot's `GenerateFlexLines` is the producer on the inspected `ResolveFlexibleLengths` call path: `DoFlexLayout` constructs a fresh result, generates its lines, and invokes the resolver once on each generated line. The `Reflow` first-in-flow branch selects that path. Its collapse restart clears the previous lines and calls fresh `DoFlexLayout` again. `PRODUCER-EXCERPTS.json` binds exact snapshot slices; the Searchfox producer lookup pins upstream discovery separately.

Within `GenerateFlexLines`, normal and strut creation append a pending item before wrap selection. When wrapping, `PopLastElement` moves that pending item to a newly constructed destination line **before** either line counts it. The sole `AddLastItemToMainSizeTotals` call follows final placement and increments the destination count iff the item is frozen. Moving/reallocating an entire FlexLine retains its field values; correct container/move/lifetime semantics remain a native refinement obligation. This supports an abstract append fold for each finalized fresh line without requiring a decrement on the previous line.

`GenerateFlexLayoutResult`, used on continuations, instead appends `CloneFor` results without invoking `AddLastItemToMainSizeTotals`. `CloneFor` copies the item, changes its frame and resets measuring-reflow state. Thus a continuation line's count is not established by this append-fold argument and can remain zero despite frozen cloned items. The inspected `Reflow` continuation branch bypasses `DoFlexLayout` and its resolver call, reusing computed sizes/positions. This is source call-path evidence, not a theorem that every native FlexLine satisfies CountAgrees or that no future caller can pass a reconstructed line to the resolver.

The abstract Seed interface includes retained frozen states for generality; that inclusion does not assert that continuation reconstruction feeds this solver. Establishing the complete native entry relation still requires normal/inflexible/strut setup providers, actual list ownership and array-count bounds, frame identity and move semantics, and the fresh-layout call-path join. The finite Lean witnesses demonstrate abstract reachable histories only.
