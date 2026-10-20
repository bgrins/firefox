# Flex cache descriptor access and installation boundary

## Verdict

The cache is **not private by C++ access control**. The inspected named publication sites nevertheless form a useful, small candidate installation roster: both allocate a fresh `CachedFlexItemData` and publish it to the current item's frame. No cache transfer or second-owner publication was found in the inspected sites. This is source evidence for a future installation model, not a closed-world ownership proof or a use-after-free finding.

This follows the immutable capture audit identified in `DEPENDENCIES.json`. Full allocation obligations F1–F16/F11/F12, frame lifetime, actual callback effects, heap decoding and global ownership remain open. No compiler, browser, native-tree or Git operation was performed for this audit.

## Actual access surface

| Surface | Retained definition and consequence |
|---|---|
| Type name | `nsFlexContainerFrame.h` declares `CachedFlexItemData` in its public section. The header provides only a forward declaration. |
| Definition | The complete class is defined in the flex CPP. Constructor, update methods, optional members and `Prop()` are public. The macro does not introduce a private section. |
| Descriptor | `NS_DECLARE_FRAME_PROPERTY_DELETABLE` expands through `NS_DECLARE_FRAME_PROPERTY_WITH_DTOR`: a static function returns the address of a static descriptor with `DeleteValue` destruction. It is not an ownership capability enforced by the property API. |
| Friends | The inspected flex header names its frame factory as a friend. No friend is necessary to access a public nested type; friendship does not establish cache exclusivity. |
| Frame property storage | `nsIFrame::mProperties` is protected. Frame subclasses have a generic access route; ordinary external callers have public typed wrappers. |
| Enumeration | Public `FrameProperties::ForEach` passes an untyped descriptor and raw `uint64_t` payload to its callback. Descriptor identity and payload are therefore observable through a holder with storage access. |
| Typed publication | Public `SetProperty`/`AddProperty` accept a descriptor and raw payload pointer. They do not check that another frame does not already store that pointer. `TakeProperty` removes without destruction. A generic typed holder can therefore express transfer or aliasing if supplied the descriptor and value. |
| Untyped publication | `SetInternal` and `AddInternal` are private. There is no public untyped transfer operation in the complete inspected `FrameProperties` definition. Recovering types/casting an enumerated payload is not a discovered production transfer path. |
| Whole-table copy | Copy construction and assignment are deleted. No whole-table clone/move API is declared in the inspected definition. This does not prohibit copying one raw value through typed setters. |
| Destruction | Public `RemoveAllProperties` requires no named cache descriptor. `RemoveAll` detaches its array and calls each stored destructor. Descriptor hiding would not establish captured-pointer survival. |

A translation unit that sees only the forward declaration does not thereby see the `Prop` member declaration or the payload layout. That is useful visibility friction, not proof that only two installation events can occur in the whole program. No supported API enforces exclusive ownership of a stored pointer.

## Actual generic enumeration callers

The retained Searchfox query for `nsIFrame::mProperties` returned 12 references, and the restricted text query for `mProperties.ForEach` returned two callers. These counts are index observations, not whole-program theorems. Both complete caller bodies are retained, and each is byte-identical between the frozen and indexed container sources:

1. `nsContainerFrame::Destroy` examines descriptor identity only for `OverflowProperty`, `OverflowContainersProperty`, and `ExcessOverflowContainersProperty`. It records three booleans, then destroys those selected auxiliary lists. The enumeration callback ignores payload values and does not publish any property.
2. `nsContainerFrame::GetChildLists` recognizes the same three descriptors and appends their frame lists to an output list. It casts the payload only after the matching descriptor test. It neither removes nor publishes cache properties.

These bodies rule out cache transfer **by these enumeration callbacks**. They do not establish that every callback reached by destruction is harmless, or that arbitrary derived classes cannot enumerate properties. The later base destruction path still performs generic cleanup.

## Candidate installation event roster

The earlier exact identifier query reports 14 references to the cache type. Its result is copied here; the retained complete flex CPP supplies the actual bodies.

* `MeasureBSizeForFlexItem` captures the property pointer before child reflow. If it was null, the later branch allocates a new cache and calls `aItem.Frame()->SetProperty`. There is no intervening native callback between this `new` result and the direct setter, but the earlier reflow interval is material: the null observation is not repeated before installation.
* `ReflowFlexItem` looks up the cache after `FinishReflowChild`. Its null branch also allocates and immediately sets the property on the current item frame.
* The non-null branches update the existing payload in place. `MarkCachedFlexMeasurementsDirty` resets the two optional members without removing the root allocation. Other inspected getters do not install roots.

`FrameProperties::SetInternal` destroys an existing value before replacing its stored pointer. Therefore the measuring null-branch's exclusivity argument still needs a real callback/event relation: a property that appeared during reflow would be replaced, not automatically preserved. No such reentrant installation was established. Similarly, “fresh allocation” requires allocator live-address freshness and a live destination frame; neither follows from the identifier roster.

## Next substantive proof boundary

Use an explicit event family with `AllocateFresh`, `InstallOnCurrentItem`, in-place member updates, and generic property destruction. For the two observed install bodies, derive the fresh root/destination pair from the actual `new` and setter sequence. Given initially disjoint live roots, allocator freshness and **complete publication-event coverage**, installation preserves pairwise owner disjointness. This is stronger than assuming disjointness independently for every cleanup, but its coverage premise must remain named until discharged.

The outstanding native joins are concrete:

1. Establish that all supported publications of this actual descriptor are represented, including generated/platform code, indirect typed helpers and any descriptor recovered through enumeration. An indexed reference count alone cannot do this.
2. Relate frame identities to actual properties through callbacks, frame destruction and continuation ownership. The measuring capture interval remains the principal lifetime seam.
3. Relate descriptor, payload type and nested storage to heap cells. The prior footprint model's nonempty-array-without-buffer witness and cross-owner alias witness remain outside native closure; this audit does not repair them by assuming exclusivity.
4. Track allocation generations/address reuse separately from pointer equality. No native generation counter was found in the cache representation.
5. Include generic cleanup independently of named cache APIs. Neither incomplete-type visibility nor deleted table copying excludes `RemoveAllProperties`.

No new Lean theorem is warranted merely to restate these premises. The next useful model should derive exclusivity from the two source-shaped installation events and then join their actual callback histories, rather than relabel privacy as ownership.

## Source roles and replay

`SOURCE-PINS.json` binds full files. The flex CPP is the previously sealed current-role snapshot (not recaptured from the live timing experiment); frame/container headers and bodies retain their predecessor roles. The flex header is newly indexed discovery evidence. No full indexed-versus-local file identity is claimed. The two container enumeration body comparisons are explicit in `VERSION-COMPARISONS.json`.

`BINDINGS.json` contains complete selected class/function bodies. The lexical brace extractor is a bounded source selector, not a C++ parser or proof of source translation. `check.py EXTERNAL_FILES_SHA256`, invoked with `python3 -I -S`, authenticates the closed regular-file roster, pins, selections and exact comparisons. Passing it establishes artifact consistency, not semantic completeness.
