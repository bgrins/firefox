# Empty ArcSlice layout arithmetic

`EmptyArcSlice.lean` proves the layout portion of the narrow empty-singleton repair. It models the current sized zero-tail representation, not the separate true-DST rewrite.

For every Rust element alignment `2^k <= 8`, `compatibleFieldsAndExtent` derives equality with the `u64` singleton's complete layout: refcount, optional allocation-size field, header, length and zero-tail offsets; alignment; full typed referent size; and constructor allocation size. Both `track_alloc_size` configurations are covered. `baseAndTailAligned` additionally derives element alignment of the allocation base and empty-tail address from an eight-aligned source base.

The results are derived from padding calculations, not assumed field equality. `smallExponent` proves the bound permits exactly exponents 0 through 3, then the kernel checks their layout calculations.

The align-64 counterexample changes the header/length/tail offsets to 64/72/128 and the referent extent to 128 bytes. The original singleton allocation is only 24 bytes without tracking or 32 with it. Even choosing base address 4096, divisible by 64, cannot repair the insufficient allocation extent. This supports the decision to allocate a typed empty owner for larger alignments.

## Source correspondence and premises

The [Rust Reference](https://doc.rust-lang.org/reference/type-layout.html#reprc-structs) specifies declaration-order placement, field-alignment padding, maximum field alignment and final size rounding for `repr(C)`. Its [array-layout rule](https://doc.rust-lang.org/reference/type-layout.html#array-layout) gives `[T; 0]` zero size with `T`'s alignment. Rust alignments are positive powers of two.

The model instantiates the observed 64-bit target premises: `u64`, `usize` and `AtomicUsize` each have size and alignment eight. `target-layout.rs` checks these primitive premises with the recorded native Rust toolchain; its log is retained and its executable was removed. This is explicit target scope, not a universal Rust ABI claim. The modeled source declarations are `ArcInner<T>` (refcount, optional `alloc_size`, data) and `HeaderSlice<u64,T>` (header, length, `[T;0]`), both `repr(C)`. `SOURCE-MAPPING.json` pins their complete source file and the repaired constructor. These declarations are identical across the old and repaired current-library bodies.

`shape` applies those layout rules first to `HeaderSlice`, then to the outer `ArcInner`. Its last alignment operation represents `Layout::extend(Layout::array::<T>(0))` in `from_header_and_iter_alloc`. The relevant computed sizes are small, so mathematical-natural arithmetic does not hide a machine overflow for the proved cases.

This arithmetic does **not** prove provenance, initialization, lifetime, static-refcount discipline, aliasing, destruction or allocator correctness. It does not establish browser reachability, a C++ ABI on other targets, compatibility for nonempty tails, or soundness of the whole Arc library. Existing Miri and C++ observations remain separate evidence.

## Replay

Run the command in `RESULT.json` with the recorded Lean version. Only Lean's bundled `Std` library is needed. The five public theorem axiom reports contain no `sorryAx`; the proofs use neither `native_decide` nor external axioms. No canonical CSS model or production source was modified.
