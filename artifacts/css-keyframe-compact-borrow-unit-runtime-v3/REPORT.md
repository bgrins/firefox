# Compact Arc borrow execution

Exact live servo_arc source and manifest copies compiled using the installed stable Rust toolchain and the Firefox vendored dependency configuration. An offline-generated standalone lockfile resolves a checked subset of the Gecko lockfile. The external scratch crate avoids the nested-workspace setup failure from the prior attempt.

Five unit tests pass both without optional features and with track_alloc_size. Three compile-fail doctests pass: two E0597 diagnostics reject owner lifetime escapes; two E0277 diagnostics in the third test reject the Rc payload Send/Sync requirements. Actual diagnostic bodies are retained. The wrapper also verifies complete source, index, research and binary preservation.

This establishes the exercised representation, identity, ownership, reference-count and compile-time lifetime/thread bounds. It is not Miri execution, a formal unsafe-code proof, a Gecko host build or an observable browser repair. The prior two Cargo setup failures remain recorded. Own scratch sources and build target were removed after terminal completion and an active-process check; exact source hashes, dependency lockfile and logs remain.
