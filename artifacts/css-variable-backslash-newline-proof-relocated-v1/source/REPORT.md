# Backslash/newline preservation component

Producer checkpoint for independent review. This component addresses fix86's terminal backslash/newline preservation; it does not prove general CSS serialization or arbitrary native parser translation.

## Mathematical result

53 named declarations are audited:39 general/helper theorems and14 kernel-reduced finite witnesses. The predecessor Span module is imported and pinned but its theorems are not counted again.

Tokens retain the full native serialization class plus an independent DelimBackslash bit and raw bytes. The reference partitions the complete terminal whitespace suffix from the right and protects it only when the preceding token is DelimBackslash. It never reads the native accumulator or its trailing length. Under explicit whitespace coalescing, the integrated scanner's trim extent equals the reference removed suffix; stored bytes and first/last outer metadata then match the retained list. Exact raw lengths preserve CRLF and mixed whitespace, and ordinary token payloads may end in escaped whitespace.

The standalone accumulator is proved to make the same protection decision under the named backslash-followed-by-newline condition. Its final bit is not the integrated scanner's final previous-token bit. The standalone constructors retain their preexisting ASCII trim behavior, including repair85's escaped-space defect, so whole-output equality is deliberately neither assumed nor proved.

Boundary theorems cover initial readiness after one maximal whitespace token, conditional EOF completion, bounded retained reference slices and the adjacent backslash/whitespace case. Kernel witnesses expose absent coalescing, a tokenizer-inadmissible terminal Backslash, class-only conflation, stale metadata, comment/block reset, the original newline loss and the standalone escaped-space difference.

## Native/source connection

24 exact complete-body bindings retain the six constructor/scanner source versions, unchanged tokenizer/serializer mechanisms and complete byte dispatch. These are inspected concrete source bindings, not a general Rust parser or translation proof. The compiled source review independently authenticated here is css-variable-backslash-newline-review-v1; selected complete constructor/scanner hashes are cross-checked against its extraction receipts.

A fresh full cssparser projection reads56 balanced, non-provider cases. It records exact outer token bytes, native serialization class and DelimBackslash identity. The checker validates nonempty raw spans, their complete source partition, CSS whitespace payloads, coalescing, backslash/newline adjacency and initial readiness. The generated Lean inputs must equal that fresh projection.

The model's integrated, standalone and pre-fix stored bytes match224 comparisons against the accepted source review's four constructor traces. Those constructor traces are retained historical execution evidence; this capsule freshly compiles the tokenizer projection, not all four complete constructor variants. Native constructor metadata is source-bound and covered by conditional model theorems, not directly compared by those raw-byte traces.

## Admissions and limits

Source tokenization/UTF-8/raw-span translation remains a provider contract beyond the finite calibrated inputs. WellFormed records a necessary internal consistency condition: a set lexical bit has class Other and raw byte 0x5c. Exact correspondence of that bit to native Token::Delim is a separate projection admission, calibrated by the fresh native harness; WellFormed alone does not prove the converse. Serialization Kind alone is insufficient. EOFReady and native reference bounds remain explicit admissions. Source recursion creates a local flag per scan and discards child/fallback summaries at the inspected call sites; no whole recursive scanner theorem is claimed. Inner block contents are represented by their outer opener span and never flattened into the outer token sequence.

The stronger complete component has coalescing, follower, positive-span and initial-readiness premises. Helper lemmas intentionally use only the premises they need. None implies used-dependency correctness, full substitution/provider behavior, separator-table adequacy, arbitrary retokenization or browser scheduling correctness.

## Replay

Authenticate FILES.json and FREEZE.json externally, then run `python3 -I -S check.py --output /absolute/new/external/directory`. Entry guards precede all non-builtin imports. The controller checks an exact recursive lstat roster before dispatch and again afterward. The replay compiles the Lean closure, audits all53 names, rebuilds the token projection, checks224 native trace comparisons and rejects three semantic Lean source mutations. Source/toolchain/compiler/runtime/OS trust boundaries remain explicit in the retained inputs.
