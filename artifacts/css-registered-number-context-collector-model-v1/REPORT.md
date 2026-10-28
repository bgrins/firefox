# Registered-number context-summary model

The completed Lean replay verifies the sealed collector's context-summary algebra over arbitrary finite ASTs. It audits 25 generalized declarations and checks 12 closed examples. Seven deliberately incorrect collectors are each rejected by a kernel-backed false-proposition check. This is a research model with manual native correspondence, not a proof of the Rust implementation or new canonical CSS coverage.

## Result

`Flags` contains independent current-font, current-line-height, root-font and root-line-height bits. `merge` returns the bitwise union only when both operands are supported; unknown on either side absorbs the result. `summary` recursively combines the actual operation families: unary, binary, ternary and arbitrary finite variadic operands. A missing log base is unary; a present base is binary. Unsupported native nodes/leaves produce unknown.

A separately defined eager event trace concatenates operand events and records modeled context reads or unsupported markers. `summary_correspondence` relates the recursive Option/bitset calculation to summarizing that trace. `summary_unknown_iff` proves that unknown occurs exactly when the trace contains an unsupported marker. `supported_read_exact` proves that each successful summary bit is present exactly when the corresponding read appears in the trace. Consequently `supported_absence_no_read` and `supported_empty_no_reads` exclude corresponding modeled reads for every finite AST, not just the examples. There is no absence guarantee for `None`.

The algebra also proves associativity, identity, commutativity and idempotence of demand union, unknown absorption, inverse preservation, retention of both binary operands and all three ternary operands. The variadic laws quantify over any member of any finite operand list: an unsupported child forces unknown, and every modeled child read is retained when the whole summary succeeds. Empty lists are modeled as the union identity; actual CSS parsing can enforce narrower arities.

## Native mapping

`MAPPING.json` accounts for all 27 captured `CalcNode` variants and all nine specified `Leaf` variants, with exact enum/visitor inventory checks. The model groups only nodes with the same eager visitation shape. Operator metadata and numeric magnitudes are omitted because they do not change the captured visitor's recursive calls. It does not omit operands of min/max, clamp, round, progress or optional log bases.

The supported length table mirrors the collector: em/ex/ch/cap/ic require current font; lh additionally requires current line height; root counterparts use the root bits. Absolute length, number, angle, time and resolution leaves add no represented read. Viewport/container/internal-width and percentage/color/tree-count/random-key leaves remain unsupported. Random/anchor/anchor-size nodes reject their entire subtree; one unsupported event records that boundary without claiming to describe their own evaluation.

The examined computation path eagerly maps surviving specified leaves before resolving the numeric tree. The model starts at that retained AST, after the real parser's simplification/admission. It does not restore operands already simplified away. This is why inverse length operands and every surviving min/clamp operand contribute even when the eventual arithmetic could cancel or choose another value.

No concrete mismatch between the sealed native collector's branch/operand inventory and this model was found. Matching inventories and manual inspection are weaker than a checked refinement relation.

## Negative controls

The seven mutant collectors respectively replace unknown with empty, erase inverse operands, erase a binary right operand, erase a ternary third operand, erase a variadic tail, erase root demands, or erase line-height demands. Their witnesses include dimension-cancelling ratio shapes and supported math families. Each purported agreement with the real summary is rejected by `decide +kernel`; a compiler/import/type error is not accepted as a successful negative test. Five additional diagnostic-gate controls reject wrong exits, extra errors, stuck reduction and unrelated diagnostics.

These mutants establish nonvacuity of the stated boundaries. They do not constitute mutation testing of compiled Rust. Some closed structural examples are intentionally broader than CSS-admitted expressions; no example's numeric value is used as a CSS oracle.

## Scope and relation to prior work

The preceding admission model covers selected substitution, exact-number admission and a small current-font expression grammar. This artifact addresses its structural collector obligation with more native operation shapes and four demand bits. It neither imports nor extends that model's parser assumptions into a Rust correctness theorem. The two artifacts are linked by source pins and a manual boundary description.

A modeled read means a font/line-height graph requirement represented by these four bits. It does not mean every real context read or side effect: absolute lengths can use zoom, font metrics can use writing mode, and normal computation must preserve invalidation/effect tracking. Root-to-current-node mapping at the document root remains the existing native scheduler's job; it is not proved here.

There is no tokenizer, descriptor grammar, typechecker, arithmetic evaluator, floating-point model, DOM, attribute/provider readiness, SCC algorithm, taint system, effect transaction or publication scheduler here. No theorem determines numeric self-font cycle invalidation/defaulting. Canonical Lean coverage and accepted-bug credit are both zero.

## Reproduction

Run with a fresh absolute output directory:

```
python3 -I -S -B artifacts/css-registered-number-context-collector-model-v1/replay.py --output /private/tmp/registered-number-context-replay
```

The replay authenticates the existing Lean executable, Init import, sources and referenced artifacts. It compiles with one thread in a uniquely owned temporary directory and removes all temporary compiled outputs. `replay-complete/CHECK.json` is authoritative: 25 audited declarations use only foundational `propext` and `Quot.sound`; no user axioms, `sorryAx`, admitted proof or `native_decide` is permitted. All 12 closed examples and seven negatives use kernel-backed decide. This pins the executable and Init, not every transitive toolchain file or an independently rebuilt compiler.

Only this new artifact was written. The canonical CSS Lean repository, live native sources, shared build/browser outputs and Git index/HEAD were not modified. Root's concurrent native experiment remains separate evidence.
