# Declaration fallback repair browser pair

The baseline has 24 failing and 65 passing subtests; the candidate passes all89. All48 new checks pass, all41 existing subtests are unchanged, and all5 test harnesses finish OK. Comparison uses94 unique(action,test,subtest) keys; exactly24 change from FAIL to PASS and70 remain unchanged.

The five files cover the new font-family fallback cases, existing var-with-blocks semantics, invalid nested rules, custom-property/rule ambiguity, and nesting-limit recovery. Source/config/test/metadata/binary hashes are checked before and after each browser run. The only changed fixed input is properties/mod.rs. Candidate Rust library and binaries builds both succeed; logs confirm recompilation of style. No unexpected outcomes remain. Runtime evidence uses the current shared macOS worktree; there is no isolated upstream browser build.

WPT lint reports zero errors/warnings. Rustfmt with the correct2024 edition leaves the changed hunk stable. Its whole-file check also reports existing substitution_property_id wrapping in both baseline and candidate; FORMATTING-CHECK.json verifies that the raw and formatted change deltas are identical. The unrelated formatting is preserved. The first2021-edition attempt rejected existing let-chain syntax and is retained.

The repair rewinds before whole-value curly validation. It adds a consumed-prefix rescan on fallback/error paths; normal successful parses return before it. Browser performance is not measured. Full tokenizer, generated property-parser and arbitrary substitution evaluation proofs are outside this pair.
