# Empty ArcSlice layout candidate validation

Both frozen Rust candidates pass the complete requested empty-slice matrix: current `servo_arc` with a typed empty fallback, and the final integrated DST representation with the same ArcSlice fallback. Tree Borrows and Stacked Borrows pass with debug assertions enabled and disabled. Leak checking remains enabled in every run.

Actual execution was `ddf897 / session 23901 / a1a35f`, exit 0. Each of the eight configurations executes these cases:

- `Default` and `from_iter(empty)` for `u64`, a 64-byte-aligned nonzero-sized type, an ordinary zero-sized type, and a 64-byte-aligned zero-sized type.
- Every empty case checks one-word owner size, zero length, aligned slice pointer, cloning while a shared slice borrow is live, pointer agreement, dropping the original owner, reading the clone and dropping it.
- Nonempty ordinary and high-alignment zero-sized inputs remain rejected. Each refusal catches the intended panic and checks that all three input values were dropped exactly once. Empty cases instantiate no element values and cause no element drops.

That is 64 executions of the eight empty cases and 16 executions of the two refusal controls, not 80 distinct tests. `main.rs` is safe caller code. It verifies and prints the actual debug-assertion configuration. Expected panic-hook messages in successful logs belong to the two caught nonempty-ZST controls; no UB or leak diagnostic occurs. `CHECK.json`, `CHECK.log`, the eight logs and `RECEIPT.json` retain the actual results.

`SOURCE-ROLES.json` pins the producer's frozen candidates. The current library is `b594817200227041aee54a2be707a17cf6e0864f8df037a150dede2f35e37976`, the DST module is `c45eed580b63b2703dfaae0f82364211bfada9bb1d5b52b58fa1c76b0b57d281`, and the shared ArcSlice body is `7e4181d75352ab21cc2e33df1c3f92445312d6ec444294013c2a63103a6e791e`. Other DST integration roles are exactly the full generated-FFI snapshot. The unchanged real selectors, ToShmem, style_traits and support crates are compiled in each workspace; no extracted ArcSlice model replaces production code.

The producer retains the common `u64` singleton only for the compatible alignment envelope. Because the header and count/length prefix are fixed and the tail is empty, the smaller-or-equal element alignment preserves this prefix layout. Other element types get an allocation of their own empty layout. Both constructors allow zero-sized element types only when length is zero; nonempty behavior is unchanged. These tests check complete reference validity and deallocation through Miri, rather than assuming a suitably aligned address alone is enough.

The original failures remain separately preserved in `css-arcslice-empty-alignment-current-v1`: ordinary controls pass, high-alignment calls panic with debug assertions, and disabled-assertion read/drop calls form an out-of-bounds ArcInner reference. This capsule does not rewrite those results or reinterpret assertion panics as UB.

Two provenance corrections supersede earlier sealed prose. Exact immutable `git show a6f39620516a:servo/components/servo_arc/lib.rs` hashes to `6fb0d15828b928fa637d499a1d3f3ceaa678fd970bb32861d9d4f62bcde6167a`, so the witness is against committed branch source; describing it as merely an uncommitted local change was inaccurate. This says nothing new about upstream ancestry or browser reachability. Also, root's final integrated Miri capsule tests static ownership and alias paths without enabling `gecko_refcount_logging`; logging-counter checks belong to the earlier DST-core source variant. This matrix likewise does not enable logging. `PROVENANCE-CORRECTIONS.json` records both qualifications.

All candidate and vendor hashes were checked before and after execution. Offline vendor copies only refresh their private checksum metadata, following the already recorded client-check setup. The retained Miri toolchain was reused; the owned temporary target/vendor tree was removed. No live native source, index, application, browser, network or toolchain-install operation occurred.

This is bounded Rust API validation. It does not certify the remaining current-library allocator/provenance defects, C++ empty factories, fresh generated bindings, shared-memory roundtrips, every platform/layout or production reachability. The separate full style/gecko check predates these singleton edits and is not relabeled as an exact successor check. No browser/WPT repair count or exploitation claim follows from this result.
