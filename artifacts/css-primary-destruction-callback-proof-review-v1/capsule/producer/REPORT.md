# Selected destruction footprints and primary coherence

## Result and limit

This component proves a selected property-cleanup phase can preserve a frame's
primary-bit/content-pointer coherence **while freeing that frame's captured cache**.
It therefore separates two previously conflated obligations: owner survival and
cache-allocation survival. It does not prove safe use of an old cache pointer.
No browser defect or actual reentrant cache access is claimed.

The kernel component contains 23 general theorems and 28 concrete witnesses across
three substantive modules, with 51 exact axiom audits. Four alternative-model
witnesses discriminate omitted-root, raw-pointer-following, missing-detach and
missing-role-check behavior; their false correctness claims must fail by `decide`
on a false proposition. They are Lean model mutations, not compiled Gecko edits.

## What is derived

`Deletion.freeMany_complete` derives successful finite execution from allocated
role-correct releases and uniqueness of their addresses. Each execution step reads
the actual modeled heap cell; a frame/content cell or wrong allocation role cannot
be erased. `freeMany_reference` relates that stateful recursion to an independent
address-membership erasure function. `protected_cell`, `primary_preserved` and
`coherent_after_free` derive preservation in one address space, not by adding an
unmodified ownership component to the state.

`PropertyPhase.phase_complete` joins the installed property table, source-shaped
owned-footprint plan, live table detachment, and allocation deletion. `phase_contract`
derives the empty live table, surviving owner, identical primary lookup and freed
owned addresses. `projected_read_after_phase_agrees` is the immediately following
modeled read. It does not include every callback between the two native reads.
`immediate_repeat_empty` applies only to immediate repetition; a compiled witness
shows that adding a new property makes a later cleanup nonempty.

The fixtures retain an allocated empty item-array buffer. They permit repeated and
already-dangling raw frame pointers because selected destructors never dereference
those pointers. Conversely, two separate roots sharing one owned buffer are
rejected even when **all initial allocation roles are correct**. A different witness
rejects the wrong role at a scalar cache root. These are representation/admission
failures, not modeled native error returns.

## Actual source connection

`SOURCE-BINDINGS.json` retains 23 complete bodies/classes/macros, reconstructed from
full source files by a limited lexical selector. The selector supports the retained
ordinary C++ strings/comments/braces and continuation-line macros; it is not a C++
parser or translation proof. Frozen frame/flex sources transfer byte-for-byte from
the authenticated predecessor audit. Newly acquired `nsTArray` files are explicitly
indexed discovery inputs; their version is not silently identified with the frozen
native compilation.

The source chain is:

1. `nsIFrame::Destroy` reaches `PresShell::NotifyDestroyingFrame`; outside its ignore
   branch, this calls `RemoveAllProperties` before the second primary-bit read.
2. `FrameProperties::RemoveAll` moves the ordinary `nsTArray<PropertyValue>` before
   dispatch. Non-auto move uses `TakeHeaderForMove`/`EmptyHdr`, then each descriptor
   invokes the selected destructor, and the detached array storage is released.
3. The three flex descriptors expand through `NS_DECLARE_FRAME_PROPERTY_DELETABLE`,
   `NewWithDestructor` and `Destruct` to `DeleteValue<T>`. They do not use the
   with-frame destructor path. Cache/fragment roots contain inline numeric records;
   shared data owns line storage, whose lines own item storage. Item frame pointers
   are nonowning raw values.
4. Retained array destructors cover element destruction and allocated-buffer release,
   including an empty array that retains capacity.

The model's `Property` already contains decoded nested buffer addresses and raw
frame references. `Cell.allocation` stores only a role, not those payload fields.
Consequently the actual descriptor-to-object-to-buffer decoding relation remains
open. Runtime descriptor identity, implicit member destruction, specialized element
traits, allocator behavior, layout/alignment, finite machine bounds and address
reuse are not kernel-derived. The native implementation does not dynamically check
our roles. No claim is made that a real frame's entire property table belongs to
this three-descriptor roster.

## Remaining full lifecycle obligations

Before/between the native primary-bit reads, SVG notifications can synchronously
invoke virtual reflow and WebRender/refcount/property destruction has other targets.
The selected cleanup does not prove their effects. Later `ClearFrameRefs`, current
event cleanup, added properties, final frame destruction, content/primary setters,
area special cases and callback scheduling still need their actual representation
and lifetime joins. Initial coherence is an explicit input, not inferred from owner
liveness. The parent's complete allocation F1–F16, F11/F12 and native destruction
projection remain open.

The next useful join is actual property installation and generation identity for
captured `CachedFlexItemData`, together with the callbacks that can reach cleanup
between capture and use. Adding an arbitrary callback-preserves-coherence premise
would not resolve that obligation.

## Replay

Run `python3 -I -S check.py --files-sha256 <external FILES hash> --output <new absolute external directory>`.
The controller authenticates a closed regular-file/directory roster before loading
local code, checks predecessor/full-source/body pins, compiles the four modules,
checks exact audit names/allowed axioms, and requires four intended false-claim
rejections. It then reauthenticates sources. Lean executable bytes are pinned;
installed Lean runtime/Std libraries remain the stated toolchain admission.

All replay commands, errors from development, canonical/relocated logs and guard
receipts are retained in sibling owned evidence directories. This capsule contains
only source/replay inputs. No native changes, native compiler calibration, browser
runs or full-project builds are part of this component.
