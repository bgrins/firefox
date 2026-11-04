# Current ArcSlice empty singleton alignment

The unrestricted safe `ArcSlice::<T>::default()` and `from_iter(empty)` paths admit an over-aligned `T` when debug assertions are disabled. With the exact current `servo_arc` source and unchanged a6 client crates, both empty-slice access and dropping the returned value produce Miri's invalid-reference diagnostic. The existing debug assertion rejects the same calls when enabled.

This is a library API witness, not a Firefox reachability finding. The separate caller audit `css-arcslice-empty-alignment-caller-review-v1` found no demonstrated over-aligned production caller; it did not compile every transitive platform layout. No WPT repair count or browser consequence follows from this capsule.

| Construction and action | Debug assertions on | Debug assertions off |
| --- | --- | --- |
| `ArcSlice<u64>::default()`, read and drop | Pass | Pass |
| `ArcSlice<u64>::from_iter(empty)`, read and drop | Pass | Pass |
| `ArcSlice<High>::default()`, read | Existing assertion panic | Invalid reference |
| `ArcSlice<High>::from_iter(empty)`, read | Existing assertion panic | Invalid reference |
| `ArcSlice<High>::default()`, drop only | Existing assertion panic | Invalid reference |
| `ArcSlice<High>::from_iter(empty)`, drop only | Existing assertion panic | Invalid reference |

`High` has `repr(align(64))` and a 64-byte payload. The caller contains no unsafe code. Each process first checks and prints its actual `cfg!(debug_assertions)` value. These are unoptimized dev-profile executions with the assertion switch changed, not a claim about optimized machine-code execution.

All four disabled-assertion failures occur after the driver reports successful construction. `Arc::inner` forms `&ArcInner<HeaderSlice<u64, High>>` outside the bounds of the allocation for the `u64` singleton. The read route reaches it through `Deref`; the drop-only route reaches it through `Arc::is_static`. Thus the observed failure is stronger and earlier than merely forming a misaligned zero-length slice. No destructor completes in those four cases. Debug failures stop before the transmutation and are ordinary panics, not UB observations.

`SOURCE.json` pins all 227 copied input files. The ArcSlice and remaining client bodies are the unchanged a6 sources already captured by the sealed client-integration capsule. `servo_arc/lib.rs` is the exact locally changed current source `6fb0d15828b928fa637d499a1d3f3ceaa678fd970bb32861d9d4f62bcde6167a`; this is deliberately not presented as an unmodified upstream-library witness. The driver/workspace metadata are the only added sources. The complete real selectors, style_traits, ToShmem and supporting crates are compiled, with Gecko feature selections; no ArcSlice body is extracted or replaced.

`check.py` ran twelve offline Miri processes under the retained nightly toolchain and Tree Borrows. `-Zmiri-ignore-leaks` excludes the intentionally retained static singleton from leak reporting; it does not disable the invalid-reference checks. No Stacked Borrows, serialization or C++ execution is claimed here. `CHECK.json`, `CHECK.log`, the twelve case logs and `RECEIPT.json` retain the actual 4 successes, 4 assertion panics and 4 UB diagnostics. The driver completed as `141ccc / 90308 / 972055`, exit 0. That exit indicates successful collection of the matrix, not universal validity.

Vendor packages were copied from the existing checkout into an owned temporary directory, with exact pre/post source hashes. Only the copied Cargo checksum metadata was refreshed as recorded in `VENDOR.json`, reusing the documented offline client-check setup. All source inputs and vendor files remained unchanged; the temporary target/vendor directory was removed. No live native source, index, application, toolchain installation or network operation was involved.

The result establishes a constraint on the future DST migration: retaining this unrestricted singleton cast would remain unsafe even if the tail representation is repaired. Empty handles need the correct per-type layout, not just a sufficiently aligned address. An unconditional supported-alignment restriction or a correctly laid-out empty representation is a separate API choice. This capsule makes no source change and does not claim a fix.
