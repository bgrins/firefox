# Selected cleanup: array representation and ownership refinement

## Result and scope

The mathematical component strengthens the pre-state model exposed by the four independent cleanup challenges. It derives preservation of every untouched modeled owner's allocation claims through the existing stateful deletion executor. It does not establish that native installations and callbacks satisfy the new representation invariant.

The exact audit roster contains **74 declarations**: 23 unchanged predecessor results; 18 new general representation/ownership results; and 33 concrete, inhabitation and semantic-boundary results. Eight modules include the axiom driver. Five falseclaim files must fail because Lean's `decide` proves the stated proposition false. These are model controls, not compiled Gecko mutations. Replay accepts only the standard `propext`, `Quot.sound`, and `Classical.choice` axiom set; the actual printed roster is retained in the receipts.

## What is derived

`ArrayShape` disallows a nonempty ordinary array without owned storage, permits shared-empty and allocated-empty representations, and bounds length by a separate capacity input. `Represented` also checks that the selected table has a destructor plan, each owned address occurs once, and every release reads a live allocation of its expected role. `World` quantifies those constraints over every live frame in the modeled heap and requires address separation between distinct owners, including aliases across different allocation roles.

`Ownership.lean` joins this pre-state invariant to the unchanged executor. `removeAll` detaches the selected table before following its actual release list. `other_frame_was_present` rules out invented post-state frames. `other_allocations_survive` derives survival using pre-state separation and the executor's independently expressed erased-address reference. The selected owner becomes empty; all other tables and their live role-correct allocations survive. Hence `world_after_cleanup` preserves the global modeled invariant, and `untouched_owner_cleanup_remains_executable` derives readiness for a later cleanup of another owner.

This is not an assumption that callbacks preserve ownership. It is a theorem about this selected cleanup phase from an explicit pre-state representation. It neither constrains nor models intervening arbitrary callbacks.

## Distinguishing examples

The full `nested_world` fixture jointly inhabits the representation: two live owners, two coherent content-primary relationships, a shared-flex root, a line-array buffer, a nonempty item-array buffer, an allocated-empty item-array buffer, and property-table buffers. Item references include repeated identities and the absent address `999`. These nonowning values do not add ownership claims or require unique references.

The fixture executes cleanup and derives the final World and primary coherence. The selected frame remains, its cache and allocated-empty buffer are freed, and the second owner's table and cache survive. Thus **World plus primary coherence does not imply a captured cache pointer remains live**.

Additional controls reject missing nonempty storage at each of the three array levels, capacity overflow, shared roots, shared buffers, and root/buffer aliases. A locally represented aliasing owner still loses its cache after the other owner cleans up; its later cleanup fails in the model. The cross-owner precondition excludes this witness. This failure is a mathematical executor result, not evidence that a native operation reports failure or that a browser can create the state.

`BoundaryMutants.lean` compiles the changed semantic definitions and counterobservations first. Separate falseclaims then detect omitted array-length validation, role-sensitive rather than address-only separation, omitted detachment, assuming local ownership is sufficient for another owner's cleanup, and assuming captured-pointer survival. No syntax or missing-import error counts as discrimination.

## Source correspondence and open admissions

The unchanged `Deletion` and `PropertyPhase` bytes are authenticated against the sealed predecessor. Five complete source files are copied unchanged. Twenty-one inherited class/helper/macro bindings and ten additional storage declarations are checked against exact byte slices. They retain actual declarations of `FrameProperties::mProperties`, `SharedFlexData::mLines`, `FlexLine::mItems`, the ordinary array header/length/capacity/shared-empty representation, and complete selected destruction helpers. The checker confirms source consistency; it is not a C++ translation checker or a proof that these slices are the full native call graph.

The `nsTArray` files retain the predecessor's indexed-discovery identity. The flex/frame files retain their explicitly frozen identities. There is no assertion that all files are a single currently compiled Gecko source revision.

| Boundary | Explicit obligation left open |
| --- | --- |
| Array decoding | The heap stores only allocation roles. `Capacity : Address → Nat` is an external input, not a decoded field in that heap. Native header, backing-buffer address, payload, length and capacity must be related to the model. |
| Ordinary array kinds | `none` denotes no owned buffer/shared-empty header, not a null native header. AutoTArray inline storage and custom element relocation/destruction are outside this selected relation. |
| Item payload | The item list projects each actual `FlexItem` to its raw frame pointer. Its other value fields and destructor behavior require the selected-descriptor source admission; the native buffer is an array of FlexItem values, not an array of raw pointers. |
| Global ownership | `World` covers all decoded live frames' selected descriptors. Foreign properties and owners outside that projection must not be hidden. Supported installer/transfer/event completeness has not been proved. |
| Primary identity | Existing abstract content/primary coherence is preserved by this phase. Cached-bit versus actual native pointer/setter ordering remains governed by the predecessor's separate admission. |
| Lifetime | No captured pointer or raw frame reference is proved live; address reuse, generation identity, callback reachability and native allocator lifetime remain open. |
| Machine/compiler | Addresses/capacities are unbounded naturals. Native bounds, alignment, heap validity and compiler/library correspondence are not established. |

Full allocation F1–F16/F11/F12 and the destruction callback/heap representation goal remain open. No native bug, UAF, native repair, performance result or browser claim follows from this capsule.

## Replay and integrity

Authenticate the externally supplied `FILES.json` and `FREEZE.json` hashes before executing:

```text
python3 -I -S /absolute/capsule/check.py --files-sha256 EXTERNAL_FILES_SHA256 --output /absolute/new-external-output
```

The controller rejects nonisolated, site-enabled or optimized invocation immediately after importing builtin `sys`, before other imports. It rejects symlinks, unexpected files/directories, duplicate JSON keys, unsafe manifest paths and changed/missing inputs. It authenticates inherited transfers and source slices, pins the Lean executable, compiles each module afresh, checks the exact theorem/axiom roster and intended falseclaim failures, then reauthenticates the source tree. The supplied Lean distribution, its runtime/Std libraries, Python, OS and compiler implementation remain trusted tooling; only the executable hash is checked here.

The canonical and manifest-only relocated runs, guard challenges, development failures and cleanup inventories are retained in the separate replay sibling. Only completed owned compiler products are removed after retaining those receipts. The preliminary indentation failure and deprecated-name warnings were corrected before freeze; no theorem premise was weakened for compilation. There are no proof holes or custom axioms.
