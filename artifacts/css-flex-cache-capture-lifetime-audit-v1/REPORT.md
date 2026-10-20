# Flex cache capture and lifetime audit

## Verdict

**No reachable use-after-free or cache-replacement defect established.** The narrow
unclosed interval is real: `MeasureBSizeForFlexItem` captures the cache before
`ReflowChild` and `FinishReflowChild`, then updates the captured pointer. The final
reflow path instead looks the property up after both calls. This audit identifies
the actual generation-changing operations and narrows one synchronous observer
route; it does not replace callback reachability with a generic unsafe callback.

The next tractable obligation is to derive exclusive cache-root ownership from the
two native fresh-allocation installers, then combine it with the actual
continuation-deletion target set and the selected `DidReflow` observer domain.
The full allocation F1–F16/F11/F12 and frame/heap/callback projection remain open.

## Source roles and search bounds

`SOURCE-PINS.json` records each full retained input. The current flex snapshot was
copied before the parent's subsequent native experiment; it is not recaptured
from the temporarily modified tree. The prior frozen flex source remains separate.
All ten selected cache/consumer bodies compare **byte-identically** across frozen,
current and newly indexed flex snapshots (20 comparisons). The three selected
container reflow/deletion bodies also compare exactly frozen versus indexed.
`VERSION-COMPARISONS.json` records all 23 comparisons; no whole-file identity is
inferred. The measurement key class itself is not among these ten comparisons.

Searchfox returned 14 `CachedFlexItemData` references, all in the flex CPP, and four
`MarkCachedFlexMeasurementsDirty` references. Frame `RemoveAllProperties` has two
discovered call sites: `PresShell::NotifyDestroyingFrame` and `nsIFrame::Destroy`.
Other similarly named DOM-property operations are different tables. Searches are
indexed discovery evidence, not a closed-world compiler call graph. Initial
sandbox DNS failure and successful escalated retries are retained. No browser,
compiler or build runs were made for this audit.

`BINDINGS.json` retains complete selected bodies; `bind.py` regenerates them from
full snapshots with the same limited lexical selector used previously. Remaining
small override discoveries are preserved as complete Searchfox definition output.
They are not silently promoted to frozen-native source identity.

## Actual installation and generations

There are two discovered installations of this descriptor. Both allocate with
`new CachedFlexItemData(...)` and immediately install that new pointer on
`aItem.Frame()` via `SetProperty`. Existing-cache branches call `Update` on the
same root. No discovered named call site transfers the cache to another frame,
uses `TakeProperty`, explicitly `RemoveProperty`s it, or installs a borrowed cache
pointer. `FrameProperties` disables copying, and `GetInternal` returns the stored
payload value: a pointer to the separately allocated cache, not a pointer into the
resizable property-table buffer. Unrelated table growth therefore does not by
itself invalidate this payload pointer.

`FrameProperties::SetInternal` destroys an existing value before storing a
replacement. `RemoveInternal` destroys the value; `TakeInternal` detaches it without
destruction; `RemoveAll` detaches the whole table before descriptor dispatch.
These APIs have no generation counter. Root allocation identity, property binding
identity, and inline `Maybe` member lifetime are distinct:

- `MarkCachedFlexMeasurementsDirty` resets both members but leaves the root alive.
- Measuring `Update` reconstructs measurement and clears final metrics.
- Final `Update` reconstructs final metrics while retaining measurement.
- Measured-reuse `Update(item,size)` reconstructs final metrics in place.
- Replacement/destruction ends the cache-root lifetime. Address equality after
  allocator reuse would not establish generation equality.

Native `new` supplies a fresh allocation under the ordinary allocator/lifetime
contract. Starting with no cache bindings, the two installation bodies therefore
provide a concrete basis for an ownership induction: each successful install owns
its newly allocated root, updates do not alias it into another table, and cleanup
removes ownership. This has **not yet been joined to every generic property API,
frame construction/destruction event, or callback**. It is a proposed producer
invariant, not an assertion that arbitrary initial tables are globally exclusive.

This also addresses two independent-review boundaries in the preceding deletion
model. Its selected-table address uniqueness does not exclude a second live owner
aliasing the same root. Its successful fixture includes a nonempty abstract raw
frame list with no item buffer, which is not a representable ordinary `nsTArray`.
A subsequent source representation must derive nonempty-array storage and global
exclusive installation; no frozen theorem or fixture is changed here.

## Capture-to-use intervals

`CAPTURE-ROSTER.json` lists the exact owners and intervals. The measuring hit path
only performs dirty/key checks, logs and an immediate return. Its two callers
consume `measurement.BSize()` immediately; one returns the scalar and the other
passes it to `SetCrossSize`, a plain field assignment. There is no additional
callout between that returned reference and its use in these bodies.

The measuring miss path is different: it retains `cachedData` across virtual
`Reflow`, possible next-in-flow destruction, size commit and virtual `DidReflow`.
After these calls it does not re-read the property before `Update`. If the capture
was null, it also does not recheck whether a callback installed a cache before
performing its own allocation/SetProperty. No actual same-owner recursive installer
has been found, so neither pattern is reported as a defect.

`MeasuredBSize` reads `FirstInFlow()` and returns a copied optional scalar. Other
cache paths use the actual item frame. First-in-flow routing is not a substitute
for content-primary identity, frame liveness or ownership-generation evidence.

## Concrete callback/deletion narrowing

1. `ReflowChild` invokes virtual child `Reflow`, then, under its fully-complete /
   no-inline-break / no-suppression guards, deletes `child->GetNextInFlow()` through
   that later flow's parent. The base deletion implementation walks further flows
   backwards, steals the selected frame and calls its `Destroy`. The block
   override uses `DoRemoveFrame` for its normal case. This can reach the selected
   property cleanup on deleted continuations/descendants. Under proper acyclic,
   disjoint continuation/tree ownership, that target set excludes the measured
   current frame. The native producer/readiness and destructor callback effects
   needed for that exclusion are still open; an arbitrary graph does not suffice.
2. `FinishReflowChild` commits size/position and calls `DidReflow`. In base
   `nsIFrame::DidReflow`, SVG observer invalidation runs **before** clearing the
   current frame's `NS_FRAME_IN_REFLOW` bit. However, the invalidation helper reads
   the content's **primary frame** and tests that frame's bit. If the measured
   current frame is that primary and is in reflow, `InvalidateAll(true)` selects
   only observers with `ObservesReflow()==true`.
3. This excludes `SVGTextPathObserver`'s synchronous `ReflowSVG` path in that
   admitted state: it inherits the default false `ObservesReflow`. In the retained
   implementation the two true overrides are `SVGMozElementObserver` and
   `BackgroundClipRenderingObserver`, whose rendering-change bodies invalidate
   paint. Their eviction/unregistration, inherited helper and painting effects
   remain explicit transitive boundaries. If primary differs or its bit is clear,
   this restriction does not follow. Thus the previous generic SVG reflow route
   cannot simply be inserted into this capture interval without proving its guards.
4. The table percentage observer's selected `NotifyPercentBSize` /
   `RequestSpecialBSizeReflow` path marks relative-block-size bits; it does not
   immediately reflow or remove the cache. Later table passes are separate work.
   `ReflowedFrame()` itself increments a counter.
5. The discovered scroll DidReflow override invokes the base then posts resnap or
   scroll-anchor work. The tree override manages a posted reflow callback then
   invokes its base. Posting and delivery are distinct: retained
   `PostReflowCallback` only links a request; `HandlePostedReflowCallbacks` invokes
   callbacks from `DidDoReflow`, after `DoReflow` returns in the retained `ProcessReflowCommands` path. That
   path keeps a script blocker around reflow and processes posted callbacks after
   leaving that scope. No universal
   no-reentrancy theorem follows merely from those names; lifecycle entry guards
   and undisclosed virtual Reflow targets still require their own closure.

## Recommended next bounded join

Build an installation-derived relation with allocation tokens (not just numeric
addresses), frame/descriptor bindings and separate measurement/final member
versions. Derive global uniqueness from an empty initial binding map and these
actual fresh-new/Update/destruction events. Represent the property payload/buffer
relation separately, including nonempty ordinary-array allocation requirements.
Then prove the selected continuation-deletion set is disjoint from the captured
owner using actual native phase construction, and instantiate the primary/in-reflow
observer filter before analyzing its two selected targets. These results would
remove concrete representation/callback premises; assuming a callback preserves
the cache would not.

No native change is proposed. Reacquiring the cache after callbacks might be a
local defensive design, but without a demonstrated reachable replacement it is
not justified as a bug repair, and it would not establish item-frame liveness or
measurement freshness. Source-derived closure or a calibrated reachable sequence
must come first.
