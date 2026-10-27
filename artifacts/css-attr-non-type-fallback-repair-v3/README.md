# Used non-type attribute fallback repair, version 3

This proposal contains only two Rust-file changes and the unchanged 34-case WPT. Relative to v2, the new non_type_primary_is_valid method matches ParsedNamespace::Known/Unknown directly instead of calling the branch-only namespace() helper. No other behavior, fallback gate, parser operation, attribute tracking, taint handling, or WPT oracle changes. The direct match and complete shared parse_attr_number primitive are byte-identical to the sealed upstream-compatible proposal.

The fix admits used fallback references from failed non-type attr() primaries into the existing dependency walk. Present raw/bare attributes, including empty strings, succeed. Numeric/unit primaries use exactly the same complete-number-token parser as substitution. Missing/unknown attributes and invalid numeric input select fallback dependencies. Existing can_chain behavior, including the separate raw-nested issue, remains unchanged.

## Scope and transport

SOURCE-PINS.json retains the original committed source baseline 87445004c1ae44d9c1e2873b91f01414cf75cbb2. Current signed HEAD 4ebfb9861c95d33290f5fb472fddd78de241d043 has byte-identical two-file preimages. Captured base-live files preserve unrelated native work; candidate-live changes only the proposed hunks. The fixed fix-head.patch applies to both captured original roles, yields their exact respective postimages, reverses to original bytes, and reapplies. The candidate inventory is exactly two Rust paths plus one WPT. The patch is not applied to the live tree or index.

Run python3 -I -S -B artifacts/css-attr-non-type-fallback-repair-v3/verify_transport.py to reproduce the ten scratch transport checks. No Git repository or object database is created by this transport check.

## Independent review and upstream export

The main branch fix is an incremental two-Rust-file plus WPT commit. Its new classifier has no namespace() helper dependency. The parse_typed_value context in the patch is only an insertion anchor, never a call from the new fix. The full new parse_attr_number function contains every numeric operation needed by both new classification and existing substitution.

The branch parent already contains numeric correction 499c0c6b72ac4bc0a6396bffa3fa0d71665409ce. Therefore the incremental substitution hunk removes that corrected inline code, while pristine captured upstream still has the earlier numeric prefix/whole-string implementation. This is a patch-base and overlapping behavior distinction, not a reason to import the animation prototype or namespace cache repair. Do not claim this literal branch patch applies unchanged to pristine upstream.

The exact standalone upstream export is artifacts/css-attr-non-type-fallback-upstream-v1/upstream-self-contained.patch, pinned in REFERENCES.json. It adapts insertion/substitution context to upstream ff3b300c151f45f09f300284659f24f5d95b0f25 and supplies the same complete shared numeric primitive, direct ParsedNamespace classifier, fallback graph change, and unchanged 34-case WPT. Its overlap with 499c0c6 is explicit; this is not a second numeric bug discovery, and the earlier independent numeric bugfix is not squashed or erased. Both the self-contained export and numeric-prerequisite-plus-adapted repair yielded identical upstream postimages in the prior audit. No unrelated namespace-cache patch is bundled.

## Validation limits

All ten scratch apply/check/reverse operations passed. Rustfmt parsed all four copied postimages with edition 2024; the added primitive and classifier match its output. An initial edition-2021 invocation correctly rejected existing let-chain syntax; rerunning with the repository language edition passed. JavaScript syntax passed, and WPT bytes remain SHA-256 6f966f427d1a6884c0a666e173333d62a26b19ee779dcd70f74b4617d2dbd5a3. Existing regression tests and provenance remain pinned in REGRESSION-ROSTER.json and REFERENCES.json.

These are transport and syntax checks, not type checking or browser execution. No v3 native build, browser run, WPT result, accepted-fix claim, or upstream-runtime validation is recorded here. Root must bind v3 to a corrected comparison capsule before its original/candidate run. Testing the branch does not by itself validate the standalone upstream export. Only the native delta and WPT belong in the eventual fix commit; this artifact is separate research material.
