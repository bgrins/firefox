# Computed-name canonical integration proposal

Prepared, not applied. Ten paths: two new Lean modules plus aggregate imports, audit/example wiring, case expectations, coverage registry and three documentation files. No canonical/shared .lake/index/native/ledger files were written; no compiler or canonical checker was run for this proposal.

`GuardedNames.lean` and `GuardedNamesExamples.lean` transfer the sealed standalone Names/Examples with namespace/import renaming only for definitions and proofs. Examples adds fifteen Boolean checks: twelve established positive propositions and three exact false propositions. TRANSFER maps all twenty-five named statements once. The standalone model passed author replay and root replay 83562 (exit 0, terminal 44b7ed); integration success is not inferred from those runs.

The checker changes only by appending fifteen EXECUTABLE_CASES. Old audits, runtime cases, proof sources and coverage entries stay intact. All new named theorems, including helper lemmas and named examples, have direct audits; no duplicate audit names. The existing snapshot/draft fallback witness is not copied or changed.

| Registration | Existing checked | Delta | Intended after full check |
|---|---:|---:|---:|
| Audits | 11805 | 25 | 11830 |
| Executable cases | 12409 | 15 | 12424 |
| Source hashes | 2151 | 2 | 2153 |
| Expected-false rows | 167 | 3 | 170 |

These are registration counts, not new proof discoveries or a numeric CSS coverage increment. Twelve examples and thirteen bridge/implementation statements are transferred from the existing research proof.

The proposed registry entry preserves the parser boundary: NameAdapter exactness relates a supplied function to a supplied acceptance predicate. Raw CSS parsing correspondence is not proved by that interface. Examples admit one already-classified name token; no raw parsing, escaping, spread, registration, taint, native cache, animation-provider or animated-cycle correspondence is claimed. Current primary-draft full-body hashes are attributed to root's validated snapshots. Old specification/feature entries remain unchanged as parsed JSON; their claims are not silently broadened.

Reviewer clarification: the standalone file named early-fallback refutes `run valid = 20px`. Its actual fallback is the cyclic `ref --x`, not literal 20px, so this is a decisive wrong-result negative, not an executed eager-fallback mutant. The canonical case is accurately named `reject wrong valid-target value`. The sequencing theorem still proves that successful lookup avoids evaluating fallback. The other false rows refute lost caller marks and enclosing-cycle rescue. No negative claim or proof body was changed.

Static validation completed (exit 0, tool 936993): exact proof transfer, complete twenty-five-name audit set, old audit/case prefixes, checker AST equality except appended cases, old coverage preservation, exact ten-path scratch apply/reverse, scratch removed. This is not a Lean integration run. V1 remains immutable. V2 keeps all Lean proof/case/registration bodies identical and changes only coverage JSON insertion formatting and two shortened documentation summaries.

## Root application and checking (not executed)

1. Authenticate FILES and referenced source/replay capsules. Run the inert check below. Before mutation compare every live canonical path with PLAN changes.before, including absence for the two new modules. Refuse mismatches. Preserve root/nested indexes, unrelated working files and previous verification logs/report in the root application receipt.
2. Once the build guard owner releases canonical source guards, from artifacts/css-spec-lean run `git --no-optional-locks -c core.fsmonitor=false apply --check /ABSOLUTE/PROPOSAL/library.patch`, then apply that exact patch without --index/--cached. Verify all ten postimages and unrelated preservation maps.
3. Run the established full checker, for example `LEAN_NUM_THREADS=1 python3 -I -S -B check.py --lake /Users/bgrins/code/firefox/artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lake`. Redirect complete output to a fresh root-owned artifact log. Verify actual audit/case/source/false counts, complete old prefixes, namespace integration and preservation. Predicted counts are not execution evidence.
4. Record actual terminal and preservation receipts. On failure retain evidence; do not silently weaken a gate or reset unrelated work. No staging/signing or ledger mutation belongs to this proposal.

Inert command: `python3 -I -S -B artifacts/css-variables-computed-name-library-proposal-v2/check.py --output ABSENT_ABSOLUTE_DIRECTORY`.

External dependencies are the referenced standalone/root replay capsules and, for full checking, the current canonical dependency tree and pinned Lean installation. This package contains modified-file snapshots, not a self-contained library replacement. Actual application/check fields remain null.

V2 correction: COVERAGE-INSERTIONS records exactly two insertions into the original coverage.json text. Existing Unicode spelling, whitespace and all other text are retained, including Editor’s, en dashes, ≤ and arrows. The static check reconstructs the candidate from that original text and those insertions, in addition to the existing parsed-prefix checks. README and coverage-map use short summaries linking the full assumptions in ARTIFACT; the latter candidate body is unchanged from v1. V2-DELTA.patch exposes these three candidate-file differences. Seven other candidate files are byte-identical to v1.
