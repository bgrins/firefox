# Independent default-feature native execution review

The completed bounded gate passes independent evidence audit and comparator replay. This establishes actual default-feature compilation, lexical agreement on the retained corpus, and detection of the three specified compiled native mutations. It does not establish native refinement, full Gecko configuration parity or floating-point correctness.

`audit.py` and `AUDIT.json` authenticate all 25 command stdout/stderr hashes and classify their exits. Twenty-two commands exit zero. Exactly the three mutant comparator commands exit one; each terminates with its specified Native/JSON lexical mismatch and no substituted compile/crash failure. Replaying the strict comparator into this review directory reproduces all four outcomes. No native program, compiler, Cargo command or browser was executed by this review.

| Variant | First required result | Changed lexical fields |
| --- | --- | --- |
| Baseline | 196 cases, 180 admitted model rows, 284 comparisons pass | None |
| Lost reported sign | `legacy-2-single`, cold: `-0` | hasSign |
| Lost exponent type | `legacy-8-single`, cold: `1e0` | isInteger |
| Excess exponent lookahead | `legacy-8-single`, cold: `1e0` | consumed, rest, exponentDigits, isInteger |

Each variant has 644 complete public records in each plain/instrumented run and 316 numeric traces in the instrumented run. Plain traces are empty. The review checks equality over every public record before inspecting the first modeled mismatch. It also independently traverses all cases/phases to validate numeric trace counts and source slices, every cache/reparse equality and every suffix replay, including records after the mutant comparator's intentional early failure. Thus the intended rejection does not hide an unexamined later instrumentation/reset inconsistency in these retained logs.

All eight build logs contain actual cssparser and driver compilation and successful optimized-profile completion, taking 2.90–6.68 seconds. Each command and binary receipt uses its own fixed-label target directory, and execution uses the binary from that same directory. All eight recorded binary hashes differ, including each plain/instrumented pair. This addresses v2's reused plain executable rather than accepting a zero-trace run.

The final 2a1c3512 source manifest remains unchanged. I independently reconstructed all eight tokenizer variants from the pinned source, exact mutation definitions and inherited instrumentation and matched their recorded source hashes. Toolchain binaries still match their pins. Actual offline and frozen metadata both satisfy the source/version/vendor-path constraints, yield identical features, and match FEATURES.json. The resolved lock remains `eb88094dff2b216e2a4a59c35880a787d696c36f800281a4a66cfd1a8f3b2eeb`, matching the earlier independent resolution replay. The enabled cssparser features are exactly default, fast_match_byte and fast_match_color; feature-tree output is retained.

The temporary workspace and all eight recorded target/executable paths are absent. Binary and rewritten checksum-manifest hashes are authenticated pre-cleanup runner receipts; removed executable bytes cannot now be independently rehashed. The inspected runner writes binary/source receipts immediately before execution and checks all 437 materialized vendor files before and after every variant. Prior source-preparation review independently authenticated those pinned objects. This review does not misrepresent retained hash receipts as a fresh binary read after cleanup.

The new baseline's historical lexical/public comparison is unchanged, and the independently recomputed cross-configuration float-bit difference list is empty. That observed equality is not an independent floating-point oracle. Within every new pair and reset history, numeric bits and Debug strings are compared exactly. The 16 legacy off-domain cases retain native consistency checks, not ASCII-model correspondence. The 180 Lean rows are authenticated prior execution output, not regenerated here.

`EVIDENCE.json` binds every retained execution file. Full command logs remain unfiltered. Earlier failed lock generation and target reuse remain separate historical attempts, not successful controls. This completed experiment adds no new bug count and does not close full-token semantics, arbitrary parser histories, host SDK/linker reproducibility, browser feature union, or formal Rust implementation correspondence.
