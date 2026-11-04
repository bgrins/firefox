# Typed empty ArcSlice storage

Two isolated candidates preserve valid generic Rust empty slices: one against committed a6/current servo_arc6fb, and one against the final true-DST/FFI module007793e8. Each retains the shared u64 singleton for compatible element alignment and otherwise constructs a fresh correctly laid-out empty ThinArc. The fallback calls the underlying constructor directly, avoiding recursive ArcSlice::from_iter(empty). Allocators accept zero-sized elements only when the requested length is zero; nonempty ZST tails remain rejected. Empty over-aligned ZST callers are supported without arbitrary panic narrowing or a permanent allocation per call.

Frozen production bodies remain under current/candidate and dst/candidate, with SOURCE-ROLES.json and two-path native.patch files. The same ArcSlice7e4181d7 is used in both; current libb5948172 and DSTmodulec45eed58 implement only the empty-ZST allowance. The related inaccurate singleton comments are corrected. This does not repair the other current-library whole-header/allocator/provenance issues.

## Independent delivery and regression test

Each variant's delivery.patch includes three paths: those two Rust changes, the additive in-tree ArcSlice test module, and a constructor-local C++ singleton guard. DELIVERY-ROLES.json binds exact final bodies. The unmodified runtime-tested production ArcSlice prefix plus tests/module.rs equals tests/arc_slice.rs. One test covers u64/unit/aligned-sized/aligned-ZST via Default and empty iterator, checks empty/aligned view, clones, drops the original, reads and drops the clone. No replacement implementation or test-only allowance is used.

The C++ static_assert is inside default construction only. It rejects element alignment beyond u64 before reinterpreting the untyped singleton; it does not reject correctly allocated over-aligned owners, copy/span access or their destruction. Existing pointer representation/export ABI is unchanged. It deliberately does not add a generic over-aligned C++ default factory.

Four zero-fuzz forward/reverse operations reconstruct both three-path deliveries exactly (b508d8/exit0). Temporary delivery trees are removed. The exact additive module is compiled and executed separately as described below.

## Actual C++ evidence

057ca2/session31460/268c52/exit0 checks current and DST generated headers with the candidate constructor guard and pinned configured Gecko flags. Each positive instantiates all ten canonical concrete C++ tails, including SimpleShadow from nsStyleStruct's text-shadow member, against the complete header. Assertions cover destination alignment, full referent size/extent and outer data/header/length placement relative to the singleton layout. Default construction succeeds. A nondefault High owner can still be copied, viewed and dropped. Each negative instantiates only High default and fails at the intended constructor-local assertion. All1,537 parent dependency hashes remain unchanged. This is aarch64 configured-source evidence, not a universal platform/layout proof or regenerated native application.

## Accepted Rust runtime evidence

The separately sealed validation capsule a9548aaf accepts ad4dae/session2645/b4fe04/exit0: current/DST, debug assertions on/off, Tree/Stacked Borrows, strict leak checking. Each of eight configurations executes eight empty constructor/read/clone/drop cases and two caught nonempty-ZST refusals with exact element-drop counts (64+16 executions). Actual variant type_name, one-/two-word HeaderSlice reference widths and refusal panic locations distinguish the dependencies. Independent review158c39 authenticates the exact source copies/check inputs/eight logs.

The initial shared-target attempt ddf897 was withdrawn after root found putative DST logs matching current; it is retained in the validation capsule. Only the corrected separate-target run is accepted. These are unoptimized dev-profile assertion configurations, not optimized release/browser execution. Logging is not enabled in this matrix. The original failing witness remains sealed separately.

The layout reuse invariant is in css-arcslice-empty-layout-review-v1: field addresses, complete referent extent, correct empty-tail alignment/provenance and static lifetime matter together. Merely aligning an undersized singleton does not suffice. The nonempty/true-DST broader safety work, full rebuilt application, cross-language runtime transfer and shared-UA serialization remain separate. No reachable over-aligned browser type or WPT oracle is asserted.

## Exact additive test evidence

The sealed css-arcslice-empty-layout-unit-check-v1 capsule (321f52b7) runs the unchanged delivered module through a public-API import adapter against both real candidate dependencies. Actual 9e5a08/session16695/2ccfb8/exit0 reports the named regression test and an independent variant guard passing for both current and DST. Separate targets and one-/two-word reference fingerprints distinguish their execution. Original-current control f53134/session87532/9d4377 has collection exit0 but actual Miri test exit101: the same named test fails the original debug alignment assertion, while the identity guard passes. This is an intended assertion failure, not another UB run. Read-only auth e104c6 verifies all21 capsule payloads, exact module identity, tested inputs, logs/receipts and scratch absence.

This compiles the exact proposed in-tree module, not every dependency cfg(test) module. The adapter uses the real style_traits::arc_slice::ArcSlice with no duplicated implementation. Its run uses Tree Borrows and strict leak checks; the separate matrix supplies Stacked Borrows and debug-configuration coverage. No full Firefox rebuild, cross-platform C++ ABI acceptance or browser reachability follows.
