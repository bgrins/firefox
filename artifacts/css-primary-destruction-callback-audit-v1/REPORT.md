# Primary-frame destruction: callback audit

## Verdict

**Source frontier refined; full native projection remains open.** No reachable
primary-pointer corruption or use-after-free is established. This is a bounded
source audit, with no new Lean theorem, browser run, compilation, or production
edit. The original allocation F1–F16, including F11/F12 and callback/heap
representation obligations, remain in force.

The useful change is a more precise destruction protocol. `nsIFrame::Destroy`
reads the cached primary bit twice. There are synchronous virtual calls before
the first read, and generic property destructors before the second. A proof of
bit/content-pointer coherence only at function entry cannot justify either
read without corresponding effect and lifetime arguments.

## Evidence and source roles

`BINDINGS.json` retains 51 complete selected bodies/classes, their UTF-8 byte
extents and hashes, backed by complete source files. `SOURCE-PINS.json` separates
exact predecessor copies from Searchfox full-file discovery. The latter are not
asserted to be the current worktree or retained upstream Git base. The body
extractor handles the ordinary quoted strings/comments and balanced braces used
by these selected definitions; it is not a C++ parser or translation proof.

`SELECTED-TRANSFER.json` compares 12 selected frozen/indexed definitions: nine
are byte-identical and three differ. In particular the entire `nsIFrame::Destroy`,
display-item deletion, frame-constructor notification, and the generic deletion
helper match. The frozen measurement key includes the padding field absent from
the fetched indexed key; the frozen flex line/item include pending baseline,
position and allocator changes. `INDEXED-DIFFERENCES.patch` preserves these
differences. Property footprint claims below use the **frozen** complete classes.
No copied caption key or newer policy is silently substituted.

The predecessor's primary-bit proof remains conditional. Root independently
found an extra-generated-content construction difference, retained verbatim in
`LOCAL-CONSTRUCTOR-DIFFERENCE.patch`. The ordinary area-suppression result is not
extended to that generated-content lifecycle. The constructor difference is
separate from the matching `NotifyDestroyingFrame` body.

## The two read boundaries

The complete ordered top-level call roster is `CALLBACK-ROSTER.json`. It is an
inventory of selected source paths, **not** an exhaustive transitive callgraph.

1. For a container, `nsContainerFrame::Destroy` first destroys absolute and
   principal children and explicitly drains auxiliary frame lists. The splittable
   base then disconnects continuation links before calling `nsIFrame::Destroy`.
   Therefore child destruction and continuation-cache updates precede both reads.
2. Base destruction schedules non-display SVG text work and invalidates direct
   rendering observers; sticky and placeholder bookkeeping follow. Only then
   does the **first** `IsPrimaryFrame()` guard select query/content-visibility
   cleanup and activity transfer.
3. Scroll-anchor, animation-record, anchor-position and visibility cleanup run.
   `PresShell::NotifyDestroyingFrame` runs, followed by conditional
   `PresShell::ClearFrameRefs`. The **second** `IsPrimaryFrame()` guard then decides
   whether to call `mContent->SetPrimaryFrame(nullptr)`.
4. The final `RemoveAllProperties`, virtual frame destructor and recycler call
   occur afterward. Post-clear callbacks still need a no-republication/lifetime
   argument; success at the second read alone does not close final destruction.

The script-block assertion is retained. It does not establish that native
callbacks cannot reenter layout, destroy frames, or modify another property.

## Property destructors: what is and is not narrowed

### Flex-owned payloads

The frozen `CachedFlexItemData` contains optional measurement/final-metric
records: logical sizes/margins, coordinates and a flag. `PerFragmentFlexData`
contains two coordinates. `SharedFlexData` contains an array of `FlexLine` values;
each line contains an array of `FlexItem` values, and each item's frame member is
an ordinary raw `nsIFrame*`. The complete classes have no custom destructors or
owning frame references.

Their properties expand through `NS_DECLARE_FRAME_PROPERTY_DELETABLE` to
`DeleteValue`, whose body is `delete aPropertyValue`. Under the ordinary C++
value/container destruction contracts, these three payload families release
their storage without calling `Destroy` on the raw referenced frames or writing
a content primary pointer. This is a source-derived **local footprint**, not a
proof about every property attached to a flex frame. The allocator/value-type
implementations and heap alias relation have not been mechanized here.

Deleting `CachedFlexItemData` does invalidate a pointer into that cache. Its
non-owning frame payload does not imply a captured cache survives the property
owner's destruction. The separate cache-lifetime argument remains necessary.

### Auxiliary continuation lists

`OverflowProperty`, `OverflowContainersProperty`, and
`ExcessOverflowContainersProperty` use `WITH_DTOR_NEVER_CALLED`, which supplies an
assertion body; it does not recursively free child frames. The actual cleanup is
`nsContainerFrame::SafelyDestroyFrameListProp`: remove the last child, invoke its
virtual `Destroy`, and **refetch the property on the next iteration**. Only an
empty list is taken from the table and deleted. The source comment explicitly
allows a child callback to remove the property via another route.

Thus child-list cleanup is not a harmless numeric-property deletion, nor is the
list detached before every child callback. A successful-return phase invariant
must establish which properties remain before base destruction. The initial
presence scan and debug assertions do not prove that arbitrary callbacks cannot
add a previously absent list property.

### Generic cleanup and the two calls

`PresShell::NotifyDestroyingFrame` calls `aFrame->RemoveAllProperties()` when
`!mIgnoreFrameDestruction`, **before the second primary read**. `FrameProperties`
moves its table to a local array, then synchronously dispatches each descriptor's
destructor (optionally with the frame pointer). A debug assertion checks that
callbacks did not repopulate the table; release execution does not enforce that
condition.

The final `nsIFrame::Destroy` call is empty/idempotent only if the first pass ran,
its callbacks did not repopulate, and intervening callbacks did not add entries.
When `mIgnoreFrameDestruction` is true, the first pass is skipped. None of these
cases permits ignoring the first callback phase. The generic with-frame
descriptor's teardown warning is also retained: its pointer is not universally
safe to dereference during pres-shell destruction.

`RemoveDisplayItemDataForDeletion` runs even when `mIgnoreFrameDestruction` is
true. It takes the WebRender table out of the properties before releasing it.
Its existing bug 1530657 comment explicitly describes destructors that can
remove other frame properties. The table contains refcounted polymorphic
WebRender payloads; retained destructors call resource/manager operations and
release owning members. This branch is **not** included in the numeric-flex
footprint. No direct primary-pointer write was found in the inspected wrapper
bodies, but the transitive release graph is open.

## SVG: immediate work before the first read

The element overload of `InvalidateDirectRenderingObservers` reads the element's
current primary frame, which need not be the frame being destroyed. The
`FrameBeingDestroyed` flag prevents bounding-box-property deletion in this
overload; it does not suppress observer notification. The selected observer set
is detached first, all observers are notified of eviction, and then all receive
`OnNonDOMMutationRenderingChange`, a direct virtual dispatch.

The concrete `SVGTextPathObserver` branch is important. With a valid target and
frame, an SVG-text ancestor, neither text-in-reflow nor correspondence-dirty flag,
and an outer SVG already calling reflow, it directly calls `ReflowSVG` or
`ReflowSVGNonDisplayText`; otherwise it schedules reflow. Therefore the statement
"all SVG invalidation here is queued" is false at the source level.

The source does **not** establish that this conjunction occurs during the flex
destruction case under study, or that its reflow destroys an owner or changes a
primary pointer. Other concrete observer targets retained in the full file
include image/mpath notifications, paint invalidation, filter/canvas update and
recursive template invalidation. Their transitive effects and the allocation/
registration provenance of the observer set are unresolved. No bug is inferred
from arbitrary virtual dispatch alone.

## ClearFrameRefs: a smaller local result

The weak-frame portion removes matching tracking objects from pres-shell lists/
sets and nulls their stored pointers. These complete bodies contain no call to
frame destruction or content `SetPrimaryFrame`.

The EventStateManager branch also registers a managed post-refresh action for a
link frame. Registration is not unconditionally deferred:
`RegisterManagedPostRefreshObserver` synchronously calls `Cancel` if detached
from its pres shell. `Cancel` calls the action with `true`; that action reaches
`MaybeLeavePendingLink(true)`, whose first conditional returns before `LeaveLink`.
This bounds the specific immediate cancellation action. Strong-reference release,
managed-observer bookkeeping and future refresh delivery are separate effects;
the audit does not equate registration with eventual delivery or prove a general
observer non-reentrancy theorem.

## Remaining joins, in priority order

1. **Actual callback roster to heap relation.** Derive which descriptors and
   observer objects can be installed on the selected flex/child/continuation
   frames, and connect their concrete reads/writes/deletions to the earlier
   content-pointer/bit/frame-aliveness model. A conjunction of independent
   callback and heap predicates is not that relation.
2. **Before the first read.** Establish or refute the destruction-time SVG-text
   guard conjunction using real registration/caller state, then bound the
   resulting reflow if reachable. Include prior child destruction and actual
   continuation setter dispatch, rather than assuming a two-frame chain.
3. **Before the second read.** Close the specific property families actually
   present, WebRender releases, contain-style quote/counter cleanup, image-load
   unblocking and remaining anchor/visibility callbacks. `DropRequestsForFrame`
   reaches `UnblockOnload(false)` and image deregistration; no no-callback
   contract is inferred from the method name.
4. **Stable point and final release.** At each primary-bit read, derive that the
   frame is alive and its bit agrees with its own content pointer. Permit genuine
   coherent ownership changes; do not require every callback to leave all state
   unchanged. After the final clear, rule out republishing a soon-freed frame and
   establish cache-owner disjointness before captured-cache dereference.

These are necessary source/representation frontiers, not new premises claimed
to be established by this report. No broad callback-no-op Lean model is added.

## Replay

Run `python3 -I -S check.py --files-sha256 <external FILES.json hash>`. It checks
the closed regular-file roster, full-source pins, exact selected slices,
frozen/indexed transfer, read/callback order, and the explicit branch markers.
It does not prove the human effect classification or C++ semantics. `../css-primary-destruction-callback-audit-replay-v1/CHECKS.json`
records the source-only replay and negative controls. There are no generated
compiler outputs or active sessions to clean.
