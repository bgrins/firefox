# Flex property destruction footprint: implementation scope

Status: local Lean component kernel checked; closed canonical/relocated replay
and independent review are recorded separately. No full native acceptance is claimed.

## Selected real fragment

The target is `FrameProperties::RemoveAll` reached from
`PresShell::NotifyDestroyingFrame`, before the second primary-bit read in the
retained `nsIFrame::Destroy`. The explicit descriptor roster is restricted to
`CachedFlexItemData::Prop`, `SharedFlexData::Prop`, and `PerFragmentFlexData::Prop`.
The real native method accepts other properties; the model refuses to interpret
them. This is a boundary on the local correspondence, not a proposed native
guard and not proof that a complete destruction call has only these properties.

## New mathematical obligation

Use a single address space containing frame, content, and allocation cells.
Do not split primary ownership into an automatically unchanged product field.
Model the actual sequence:

1. Detach the frame-property array, replacing its live table/header with the empty
   state before deleting values.
2. For each admitted descriptor, delete its typed payload and owned array storage.
   Raw `FlexItem::mFrame` pointers are data, never ownership edges.
3. Free the detached property-array buffer after descriptor dispatch.
4. Read the primary bit on the still-live frame.

The executor checks allocation cells before deleting them. The independently
expressed reference erases the union of the planned owned addresses. The target
is executor/reference equality, successful execution from unique typed owned
allocations, preservation of frame/content cells and derived primary coherence,
and invalidation of every freed cache allocation. No callback-preserves-coherence
hypothesis is used for this fragment.

The array-buffer representation is explicit. An empty array may still own a
dynamic buffer; the footprint does not infer allocation absence from zero length.
An optional buffer omits static empty headers and inline/non-owned storage.

## Native source admission

The source-bound class layouts derive the ownership *shape*: inline optional
numeric records for the item cache, two coordinates for per-fragment data, and
shared data owning a line array whose lines own item arrays. All frame references
in these item records are raw pointers. `DeleteValue`, `nsTArray_Impl` destruction,
element `DestructRange`, and base-header freeing are retained for this mapping.
The non-auto array move exchanges the old header with `EmptyHdr()`; it does not
copy ownership into both property tables.

Unproved representation/provider contracts remain:

- decoding the actual installed descriptor and C++ object into the selected
  payload, including its complete optional buffer/address ownership map;
- unique, valid typed allocation addresses, no hidden owning fields/specialized
  element destructor, and the source version of those value types;
- correct C++ implicit member destruction, library/allocator effects, pointer
  bounds, finite machine lengths, alignment, and memory safety;
- the quotient omits numeric payload values because deletion does not read them,
  but does not omit raw frame identities or owned allocation identities;
- the entire actual callback roster before/after the selected pass, including
  SVG virtual reflow, WebRender releases, contain-style/image/visibility cleanup,
  later descriptor additions, and final frame destruction/address reuse.

The executor's `none` is an unsupported/ill-formed model admission, not a native
runtime result. The completeness theorem must supply a structural readiness
condition (unique allocated footprint), not assume successful deletion.

Release tasks carry an address and expected allocation role. The executor checks
that role against the allocation cell before releasing it, distinguishing scalar
cache/fragment/shared roots and line/item/property buffers. Readiness checks both
role agreement and uniqueness of addresses, including across different roles.
These checks express representation validity, not extra native runtime guards.
The decoded footprint still resides in property metadata rather than being read
from C++ payload fields in heap allocation cells: descriptor/payload/heap decoding
and allocator pairing remain a named external correspondence obligation.

## Discrimination

Use a nonempty shared line array with live raw references, an empty but allocated
item array, scalar cache roots, and a dynamic property table. Check that all owned
allocations disappear while both raw-referenced frames and content pointers stay
live. Wrong models omit a cache root, follow a raw frame pointer as ownership, or
forget to detach the table. Include duplicate-owned-address and foreign-descriptor
rejections, plus an explicit intervening property addition showing why the final
native `RemoveAllProperties` is not unconditionally an empty second pass.

These are model counterexamples, not assertions of native producer reachability.
Full frame/heap/lifetime closure and allocation F1–F16/F11/F12 remain open.

Owned-allocation uniqueness is distinct from raw-reference uniqueness. Two
different property roots sharing an owned buffer are rejected; arbitrarily
repeated raw frame references are admitted. A raw reference can already be
dangling when child destruction precedes shared-flex-data destruction. This
component does not dereference such a value or require it to be live.

The concrete successful fixture targets a further distinction: the owner frame
and its primary pointer remain live/coherent after cleanup, but its cache root
has been freed. Frame survival and primary coherence alone therefore do not
justify captured-cache reuse in an interleaved destruction phase. A separate
cache-allocation/property-generation argument is required. Actual reentrant
caller reachability remains unproved; this is not a newly observed bug.
