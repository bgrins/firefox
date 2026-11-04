# HeaderSlice mutable access finding

The matcher verification work exposed a safe-API soundness defect in the pinned
`servo_arc` implementation. `HeaderSlice<H, T>` is sized: its inline fields include
the length, while its elements occupy a trailing allocation. Safe mutable access
through `Arc::get_mut` permits moving the whole header independently of that tail.

The local reproducer creates uniquely owned one-element and eight-element
`Arc<HeaderSlice<u64, u64>>` values, then calls:

```rust
std::mem::swap(
    Arc::get_mut(&mut short).unwrap(),
    Arc::get_mut(&mut long).unwrap(),
);
```

The lengths move, but the allocations do not. `short.slice()` then constructs an
out-of-bounds reference. Dropping `short` separately attempts to drop an element
outside its allocation. The caller uses no unsafe code.

## Evidence

The isolated package is
`artifacts/stylo-bloom-tools/creusot-gate/matcher-dyn-capability-candidate/backend-v1/actual-context-v1/header-swap-defect-v1`.
Its standalone reproducer uses a byte-identical copy of the production crate.
The checked toolchain is `nightly-2026-09-17` on `aarch64-apple-darwin`.

Miri with Tree Borrows passes construction/slicing before the swap and a separate
metadata-only swap control. Slice creation and drop then fail with allocation
bounds diagnostics. Leak checking is disabled so controls can forget their
owners; alias checking remains enabled. Default Stacked Borrows reports an
earlier constructor provenance failure, retained separately. No uncontrolled
native execution of the failing operations was performed.

The package README and recorded commands reproduce all four Tree Borrows cases.
The reproducer refuses the failing modes outside Miri. All 39 evidence pins were
independently checked and rechecked by the primary agent.

| Record | SHA-256 |
| --- | --- |
| `header-swap-defect-v1/DEFECT-EVIDENCE-v1.json` | `da6ba49959f696f07d67633b496c99075c20f11ee87d69330a29fe4875d9cfc0` |

## Scope and next step

This is a library API defect. A bounded Firefox call-site search did not establish
a browser- or CSS-reachable path. There is no production fix or browser regression
test for this finding yet; the two existing CSS fixes remain separate.

This was found while checking the ownership assumptions needed by the formal
model, then confirmed with Miri. It was not a Lean-generated counterexample.
In particular, a structural header value cannot unconditionally identify its
trailing allocation. The matcher proof needs an allocation/borrow relationship
whose lifetime and mutation rules are justified by the implementation.

A fix needs to prevent moving or replacing the whole header through every safe
mutable or move-out API, or make the trailing slice genuinely unsized. Narrow
header and element mutation must remain available. Adding a pinning marker alone
does not prevent moves through an ordinary mutable reference. The API and layout
design need review before a production change.
