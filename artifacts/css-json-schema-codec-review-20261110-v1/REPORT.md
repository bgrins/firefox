# Independent JSON-value codec acceptance review

Verdict: **accept the bounded JSON-value schema/codec artifact**. No source or harness blocker remains. The reviewed 34-file source manifest has SHA-256 `60b2dc0fa39434863a626991ca02d81327498c63b3f883dc6d51321041e70e08`; `REVIEWED.json` pins those exact inputs. This acceptance does not claim a verified JSON text parser, mechanical CSS-spec derivation or native Firefox behavior.

## Proof strength

The new relations quantify over actual `Lean.Json` values. `ExprSchema` and `StmtSchema` are independent inductive grammars whose constructors fix tags, arities, literal meanings, child order, variable indices and scan budgets. They are not aliases for successful decoder return. `Reader` produces a constructor-data tree with a schema witness; the separate completeness proofs establish an iff between decoding and that grammar. This adds a real guarantee against accidental over-rejection beyond certificate soundness.

The encoder emits actual JSON objects for arbitrary typed expressions/statements. Its universal roundtrip uses the same reader and existing typed checker. The accepted-result theorem exposes both the raw Json schema derivation and exact normalized typed erasure. The stronger alias-free iff relates any accepted Json value to precisely the returned typed tree's erasure. These results preserve operation and operand identity, not only result types.

The relation handles all four exact two-node map shapes and field arrangements, with arbitrary cached sizes. It therefore does not assume raw Json maps are already sorted, balanced or constructed by `mkObj`. Duplicate raw keys, extra tree nodes, wrong primitive fields and wrong arities are excluded. The canonical encoder chooses the valid args/op layout. The result does not require every accepted value's original raw representation to equal its re-encoding.

Natural-number interpretation shares the standard `Json.getNat?` primitive. Scalar admission additionally proves valid Unicode scalar bounds. This remains a primitive/text-representation boundary rather than an independent decimal lexer proof.

## Aliases, types and execution linkage

The generic alias relation specifies first-match lookup, including the matched name and declared scope head. It cannot silently choose a later matching alias. The typed checker still validates that head and all variables/binders. Raw schema acceptance is deliberately weaker than typed acceptance: a syntactically represented add with a Boolean operand can have a grammar witness and still be refused by the typed checker.

`Document` reads each of its four fixed definitions through the new reader with an empty alias environment and checks the declared singleton context/result. Program decoding uses the same reader with those definitions. Singleton definition validation and top-level version/fields/metadata handling belong to the concrete document adapter, not the generic alias theorem. The preserved old `foldJson` remains imported but the new document/runner definitions do not call it.

The standalone Runner imports Document and executes the parsed/checker-produced value. RoundtripRunner serializes that value to canonical JSON, reparses and rechecks it before execution; ReferenceRunner compares the decoded tree with the proved fixture before executing the decoded tree. No reference result replaces the decoded program. The fixed fixture equality and execution relation compose with the old escape semantics, under the same caller/preprocessing assumptions.

## Independent evidence

The final independent source-only replay rebuilt the 21-module core closure in temporary storage and audited **124 declarations: all 108 core/dependency theorems plus 16 independent boundary proofs**. CHECK.json verifies the core theorem roster exactly equals the author's full audit minus its 35 boundary cases. Only `propext`, `Quot.sound` and `Classical.choice` occur. Temporary source/object trees were removed.

The independent proofs cover all four raw layouts with unusual size metadata, duplicate-only and three-node duplicate-key trees, extra fields, wrong arity, Unicode scalar bounds, first-match aliases, valid/mismatched heads, absent aliases, and raw-schema acceptance paired with typed rejection. These tests are authored separately in Boundary.lean.

The independent actual-file runner produced all 13 expected escape rows. A different valid JSON program produced its own literal result for another 13 rows, leaving each input unchanged; this checks that execution is not replaced by the reference fixture. Five malformed actual files were refused: an extra AST field, surrogate literal, wrong arity, alias cycle and missing alias scope. Three provenance mutations were also rerun independently and rejected at their intended authentication boundaries.

`replay3/REPORT.json` is the final independent replay receipt. Earlier replay1 stopped because the review scanner truncated dotted theorem names; replay2 passed but omitted six same-line annotated theorems from its inventory. The scanner was corrected and the entire core rebuilt/audited again. The earlier 118 count is superseded by 124; no codec failure was inferred from either review-wrapper issue.

All 28 predecessor allowlisted files were authenticated against commit `2f8edd8effa87071d0576d488cb6cfa2fc65721c`. The current 15 preserved files match that independent authentication. All 34 final inputs, the expected-output fixture and every author command-log hash were checked. The recorded compiler binary hash identifies the used Lean installation; this is not a hermetic proof of the toolchain itself.

## Harness and controls

The frozen author harness was reviewed. Its 143 audits include the 108 core theorems and 35 authored kernel cases. Its three actual-file runners, parser observations and malformed-file refusals check the intended interfaces. The six compiling semantic mutants are appropriately separated from proof-carrying implementation edits that would fail to compile.

For each mutant, the positive witness passes, changed implementation compiles, an unchanged proof fails, and the concrete witness ends in the exact false-proposition diagnostic. Authenticated receipts show wrong subtraction opcode (9 instead of 5), reversed subtraction operands (0 instead of 5), changed scan budget (two characters instead of one), omitted unit/layout acceptance, and incorrect document alias selection. No arbitrary compilation failure is counted as a successful semantic witness. These six full mutant runs were inspected and hash-checked here, not independently rerun by this child; root owns the separate full frozen-harness replay.

## Remaining boundaries

The parser's last-wins duplicate **text** keys are distinct from rejected duplicate **raw-tree** keys. Text parsing, compression, quotation/elaboration, file acquisition and numeric spellings are not universally proved. The observed fixture text roundtrip is finite evidence. Outer document orchestration and alias weakening are not universally proved either.

The wire schema is the research IR protocol, not a CSS grammar. Existing CSS clause excerpts and manually chosen AST links remain provenance and reviewed interpretation, not mechanical derivation from English. This work increases confidence in transporting that model through JSON; it does not add CSS feature coverage, establish latest-draft coverage, fix a browser bug, or prove native memory safety/performance.

No native source, WPT, canonical library, browser, build tree, Git index or history was changed by this review. Only this review capsule was written.
