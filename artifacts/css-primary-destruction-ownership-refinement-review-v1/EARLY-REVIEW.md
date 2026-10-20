# Early independent ownership review

Status: **source-only draft review; no acceptance verdict**. The five mathematical modules are uncompiled. No compiler, browser, native build, Git operation or main-source edit was run. The current timing hold is respected. The retained draft snapshot is a reading checkpoint, not an authoritative producer seal.

## The four prior witnesses

| Prior observation | Added constraint and effect |
| --- | --- |
| The successful sample has a nonempty item list with no item buffer. | `ArrayShape capacity none length` requires zero length. `PropertyShape` applies this to every line's item list. The offending entry now fails `TableShape`; the executor itself is intentionally unchanged. |
| Cleanup accepts that incomplete buffer encoding. | `represented_cleanup_executes` starts from `World`, whose local representation includes the new table/line/item shape. It excludes that input before invoking the unchanged completeness theorem. It does not add a native runtime check. |
| A distinct live owner survives while its aliased cache is freed. | `OwnersSeparated` compares the actual addresses of both selected plans. Sharing root30 violates this relation even though each local plan has distinct addresses and correct roles. |
| Cleanup of the second owner then fails. | `other_allocations_survive` uses separation plus the actual erased address set to preserve its allocations. `world_after_cleanup` derives local representation and separation for all surviving modeled owners, and the second cleanup theorem derives successful execution. |

These are substantive pre-state restrictions followed by a preservation derivation, not a premise that arbitrary callbacks preserve the desired postcondition. No immediate logical mismatch was found in the source reading. Kernel elaboration and fresh final replay remain pending.

## What the state really contains

`Cell.allocation role` has no capacity, array payload, byte extent, generation or allocator identity. `Capacity : Address → Nat` is external. The same heap/table may satisfy the shape relation with a large supplied capacity and fail it with a small one. This is acceptable as a parameterized representation contract; it is not a proof that native headers encode those capacities.

A complete native decoder must relate the property payload, nested line/item arrays, ordinary array headers, lengths/capacities and deallocated base pointers. It must also justify occupied byte ranges, element size/layout, overflow-free allocation-size arithmetic and selected destructor identity. Merely showing `length ≤ capacity(address)` in a separately supplied function does not perform this decoding. Address inequality is not byte-range disjointness or generation identity.

`World` quantifies over every live frame cell in the selected-descriptor projection. `PropertyShape .foreign = False` and `tablePlan .foreign = none` explicitly exclude foreign properties. Hidden owners outside this projection are not constrained by `OwnersSeparated`. Therefore the theorem is global within that modeled world, not across all native frame properties or all heap roots. A source proof must establish projection completeness for the claimed ownership universe before transferring that wording to Gecko.

## Liveness and phase boundaries

World representation/separation does not imply `Coherent`: primary bits and content pointers need their own initial relation. The predecessor cleanup theorem preserves coherence when supplied. It does not infer it from allocation ownership.

The selected frame survives with an empty table, but its selected cache is freed. A captured pointer to that cache is therefore not justified by owner survival or by `World` preservation. Raw frame references in line arrays remain unrestricted and are ignored by the destructor footprint. That is appropriate for the selected raw-pointer destructor path, but does not prove that those references can later be dereferenced safely. Allocation reuse and pointer generations remain outside the model.

The modeled phase clears the table and performs finite releases, with no allocator callback that installs a new property midway. The retained `FrameProperties::RemoveAll` moves storage and then invokes descriptor destruction; its final assertion that the live table is empty does not establish arbitrary destructor effects. Selected numeric records, raw references and ordinary-array destruction supply the intended restricted path, subject to the explicit trait/allocator/destructor contracts. Other callback targets and actual installation histories remain open.

## Source check and nonvacuity requests

The predecessor manifests and every listed payload hash were authenticated. All 23 retained complete source-body slices were matched to source bytes. Deletion and PropertyPhase are unchanged copies. The source confirms ordinary `nsTArray` property/line/item storage, non-auto move to `EmptyHdr`, allocated empty-buffer destruction, and nonowning raw frame references. Indexed array providers retain the predecessor's revision-transfer limitation.

The draft already has full two-owner nonvacuity for separate scalar caches and shape-only positive tests for nested arrays. Suggested additions, sent to the producer before freeze:

1. A full `World` example with shared lines, item buffers, an allocated empty array and repeated/dangling raw references. This jointly exercises shape, local role allocation, local uniqueness and global separation; separate `PropertyShape` examples do not establish their conjunction.
2. A `World` plus initial `Coherent` example whose successful cleanup preserves the owner/coherence while freeing the captured cache. This keeps the intended lifetime boundary visible under the stronger invariant.
3. When composing the two theorem families, preserve `Coherent` as an explicit premise rather than presenting it as a consequence of `World`.

These are nonvacuity/claim-clarity requests, not findings of a false theorem or an observed native defect. Full allocation F1–F16/F11/F12, actual descriptor/heap decoding, installation coverage, callback scheduling and captured-pointer liveness remain open. Final review waits for compiled, frozen producer inputs and authoritative pins.
