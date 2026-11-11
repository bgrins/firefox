# Independent feature and sensitivity preparation review

No remaining source blocker was identified for root's isolated experiment. This is approval of the preparation and acceptance checks, not a claim that Cargo resolved, the native variants compiled, or the mutations were detected. I did not execute Cargo, rustc, a native binary or a browser, and did not modify the author's inputs or Firefox sources.

## Evidence replayed

The frozen source-only checker passed in `replay/`: 18 copied input pins, 19 crates reconstructed from 437 Git objects with vendor checksums, 180 correctly typed actual model rows, 18 schema refusals and four synthetic metadata refusals. Nine schema controls distinguish values that Python equality conflates. This materialization used a temporary source tree and removed it; it did not create a build target.

`independent.py` additionally verified all 19 dependency records exactly equal their entries in the pinned Firefox root lock. Eight separate malformed-row controls reject string codepoints, null observations, tuple rows, true error flags, a changed input, an extra row field and a null classification flag. Running the new strict comparator wrapper on the previous immutable native logs gives exactly the previous comparison result plus its explicit type-validation flag. These remain record/schema controls; they do not stand in for compiling the native mutations.

`FINAL-SOURCES.json` authenticates the final 33 inputs, with SOURCE-ONLY SHA `7d5e92d34c15c940548e54ab7a17b33429467ff38515bf3b30562b7be5ae34d4`. The source replay used the preceding allowlist. Its only subsequent Python change is two incremental receipt writes in `run.py`; removing those exact statements reproduces the previously reviewed runner hash. Every other Python source is unchanged, and every final allowlist hash was rechecked.

## Source assessment

`strict_model.py` validates actual JSON rows before delegating to the preserved comparator. Exact bool/int/list/string checks close the observed malformed-input gap, including float codepoints that compare equal to integer codepoints. The existing lexical oracle and actual 180 Lean output rows remain unchanged. The new experiment borrows those authenticated rows; it does not rerun Lean.

The workspace uses the pinned Firefox Git-source replacement into its own vendor directory, an isolated Cargo home and target directory, and offline resolution. The seed lock contains exact root-lock records but is explicitly not a prevalidated resolved lock. Actual Cargo metadata must establish source/version/path constraints and precisely the cssparser default dispatch feature set before builds. The resulting lock is retained and frozen for all builds. The source checker exercises synthetic metadata only; real resolution remains an execution gate. All materialized source bytes are checked around every variant, with explicit tokenizer and checksum-manifest amendments.

Each mutation changes actual tokenizer behavior before the inherited trace hook: sign reporting, exponent integer classification, or exponent lookahead at EOF. These are not edits to printed expected answers. Both plain and instrumented variants must finish the entire corpus and agree on public observations. The unchanged comparator must then fail first at the specified cold witness, with exact changed lexical columns. A compile failure, crash, malformed trace or unrelated comparison failure cannot satisfy that gate. The source anchors and initial corpus ordering support the proposed witnesses; only execution can establish that they compile and are detected.

The baseline separately compares its lexical/public results with the previous feature-disabled run. Float bits and numeric Debug strings are excluded from this cross-configuration comparison, as documented; their agreement still matters within each new instrumentation/reset pair. Float differences across configurations are recorded without declaring mathematical correctness.

## Corrected finding

The initial runner retained binary/source hashes only after all variants finished, although its temporary directory was removed on exceptions. A later failure could therefore lose the hashes of earlier successful binaries. The final runner persists BINARIES immediately after each hash assignment, before process invocation, and persists each accepted MUTANTS entry. The exact two-statement amendment was independently checked. Command stdout/stderr receipts are already written after each process. No native execution was needed to assess this control-flow correction.

## Remaining gates and limits

Root must execute and inspect the actual offline lock/metadata/feature tree, eight successful builds and complete driver runs, baseline 196-case/284-comparison acceptance, and all three exact mutation failures. Source preparation does not establish those results. A failure is a review point, not permission to weaken expected witnesses or reuse synthetic results.

The experiment covers default cssparser dispatch features, not Firefox's complete feature union, allocator, optimization/LTO or browser path. Rust/Cargo binaries are pinned; the host SDK, linker and other inherited environment are not fully pinned. Sixteen off-domain legacy cases still lack the normalized-ASCII model correspondence. Numeric core remainder differs from token remainder and units. No native refinement theorem, floating-point correctness, complete parser-state proof, new specification derivation or new bug count follows from this preparation.
