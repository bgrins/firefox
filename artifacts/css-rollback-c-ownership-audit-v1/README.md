# Cold C declaration ownership audit

No shared-entry/different-block or owned-temporary counterexample was found in the bounded paths inspected. The ownership premise used by `css-rollback-c-membership-bridge-lean-v1` is supported by concrete container and caller behavior; it remains a source argument, not a Rust memory proof or native execution result.

The authority is immutable checkout snapshot `a6f39620516a4cf76a5dbf5208960adc79068cf1` plus the exact copied cold-C candidate. `SOURCES.json` records nine file hashes and relevant excerpts. Searchfox supplied discovery; its indexed source differs from this checkout in some unrelated function bodies, so conclusions use the pinned local objects. `CHECK.json` records eight structural checks from actual invocation `4d0097`, exit 0. No browser, build, Lean replay, Git mutation or native edit occurred.

## Distinct cloned blocks have distinct nonempty entry storage

`PropertyDeclarationBlock` owns `ThinVec<PropertyDeclaration>`. Its manual `Clone` invokes `self.declarations.clone()`. The current `ThinVec::clone` allocates `with_capacity(len)` and writes each cloned element into that new array. For nonzero capacity and a non-zero-sized element, `with_capacity` reaches `header_with_capacity`, which calls the allocator for a new header/data allocation. This is not an Arc-style shallow copy of the entry array.

`PropertyDeclaration` has `#[repr(u16)]`; it cannot be a zero-sized type. The ThinVec zero-sized-element shortcut therefore cannot merge these entry addresses. Empty blocks may use shared singleton storage, but their slices have no entries, so `block_contains` cannot find a declaration there. Cloned declaration payloads may themselves contain shared Arcs; membership compares the address of the outer `PropertyDeclaration`, not a shared payload.

The shared-memory path does not provide a counterexample either. `PropertyDeclarationBlock::to_shmem` calls the ThinVec serializer. That serializer allocates a new header plus entry region with `builder.alloc`, then serializes entries into it. `SharedMemoryBuilder::alloc` advances its checked cursor past each reserved region. The generic Arc serializer serializes the underlying value and creates a new static Arc around it. This path does not manufacture different block objects sharing a nonempty entry slice. These conclusions rely on the allocator/builder and valid-container contracts; their unsafe implementations were not formally verified.

## Read guards keep original entries stable

`StyleSource::read` returns a block reference borrowing both the source and its `SharedRwLockReadGuard`. `Locked::read_with` checks guard identity, except for read-only locks; its return lifetime cannot outlive either borrow. Rule-tree sources retain the owning Arcs along the borrowed ancestor chain.

`SharedRwLock::read` holds an `AtomicRef`, while `write` requests an `AtomicRefMut`. The inspected `AtomicBorrowRefMut::try_new` only succeeds when its borrow count is zero and otherwise rejects the write. `Locked::write_with` additionally requires the matching writable guard. Read-only shared-memory locks cannot acquire a write guard. Thus the inspected sanctioned paths cannot mutate or reallocate the declarations ThinVec while the cascade retains those read borrows. Updating the atomic `immutable` marker does not move the entry array.

The direct-block caller, `Stylist::compute_for_declarations`, owns the `Arc<Locked<PropertyDeclarationBlock>>` for the call, reads it with the author guard, and passes that exact block both to the declaration iterator and as `Some(block)` to `apply_declarations`. It does not substitute its deliberately empty rule-tree root for the source owner.

## Every inspected cold lookup uses a covered original entry

`DeclarationIterator::update_for_node` obtains its declaration iterator from `source.read(guard)`. `DeclarationImportanceIterator` yields references from that block's declarations slice. `Declarations::note_declaration` stores the reference unchanged; moving or growing the separate declaration-record buffer does not move the referenced block entries.

Both calls to `apply_one_longhand` pass those stored references: the prioritary linked walk and ordinary longhand iteration. Ordinary logical mapping changes the physical property ID, not the declaration reference. The cold lookup walks the same rule-tree ancestor/source domain, or checks the direct block described above. Repeated nodes sharing a block may yield the same owner through different nodes, but lookup returns only the block and retains the triggering event's priority.

`apply_one_longhand` tests exclusions against its input reference and saves `original_declaration` before substitution. `substitute_variables_if_needed` returns a `Cow`; its borrowed or owned result determines the action, but Rule lookup explicitly receives the saved original reference. Neither an owned substituted keyword nor a shorthand-cache replacement is used as the membership needle. Temporary inheritance declarations in the zoom-recompute path call `do_apply_declaration` directly, bypassing cold lookup. The custom-only constructor does not populate a longhand stream.

## Remaining trusted boundary

The small remaining ownership assumptions are ordinary live-allocation disjointness for non-zero-sized entries; validity of ThinVec/slice/Arc and shared-memory layout contracts; Rust borrow/lifetime enforcement plus the inspected lock/AtomicRefCell unsafe implementation; and absence of outside unsafe/FFI mutation violating those contracts. This bounded audit does not claim to examine every unsafe write in Firefox.

No additional semantic CSS assumption is needed merely to establish that the cold search recovers the original block allocation in these callers. Whether grouping repeated semantic rule occurrences by that allocation and full normalized priority preserves all cascade observations is still the separate ordered-block/observation obligation. The cold-C generic `apply_declarations` API must also retain its caller contract: any future supplied iterator must agree with its Rules/Block source view. Current inspected producers agree; an arbitrary iterator of owned temporaries would violate that contract and hit the candidate's membership assertion.
