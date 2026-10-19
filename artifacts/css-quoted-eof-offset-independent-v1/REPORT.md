# H1 quoted-EOF endpoint independent review

Verdict: **accept the native repair and its standalone WPT**, with the precise proof boundary below. Reviewed 2026-10-19. No blocking defect found. This review makes no acceptance claim for the separate even-backslash or escaped-final-quote repairs.

## Native change

The formatted source is exactly the producer candidate with one assignment wrapped differently. The root patch changes only `custom_properties.rs` and adds `quoted-eof-fallback-endpoints.html`. The independent checker applies its exact context hunks to the pinned original and reconstructs both final files. Root additionally records apply/reverse checks against both the working HEAD and upstream; those repository checks are retained evidence, not independently rerun Git operations.

`VariableValue::parse` used to remove one terminal ASCII backslash after recording reference ends. Its CSS bytes became one byte shorter, but enclosing reference ends retained the old length. The patch records that deletion during parsing, threads the state through every recursive declaration/fallback call, subtracts it at reference finalization, and uses the same state for final serialization. The intended deletion and recovered CSS bytes remain unchanged.

I read the complete changed parser functions, their recursive calls, the actual cssparser string tokenizer and nested-block control flow, the declaration caller, `do_substitute_chunk`, `substitute_internal`, and `substitute_one_reference`. Admission reasoning:

- An unterminated quoted token admitted as `QuotedString` consumes physical EOF. An unescaped newline instead gives `BadString`, which the declaration parser rejects. Once the recovery quote is recorded, there can be no later sibling token on a successful parse. Unwinding only appends missing closing delimiters and finalizes enclosing references.
- An earlier missing comment/URL/block closer also requires EOF. It cannot be followed by a second successfully parsed terminal quoted token. Therefore the bool assignment cannot erase an earlier relevant deletion on an admitted successful parse.
- In the no-fallback validation branch, scanning is followed by reset; `parse_nested_block` uses `parse_entirely`. Unexpected remaining tokens invalidate the parse rather than publishing speculative reference state.
- Earlier siblings finalize before the deletion flag is set, so their endpoints stay unchanged. Enclosing references finalize afterward and lose exactly one byte. Starts and fallback starts precede the terminal backslash and remain unchanged UTF-8 boundaries. The removed character and recovered delimiters are ASCII; no UTF-8 continuation byte is removed.
- The actual declaration entry calls `skip_whitespace` before capturing its state. The harness mirrors it. Arbitrary calls violating this premise, allocation failure, machine-size overflow, and universal parser/caller correctness are outside this companion.

The shared flag is local to a single parse, and errors discard that result. The patch adds no repeated scan of the already accumulated reference tree.

## Formal scope and mutation evidence

The ten Lean theorems prove natural-number boundary relocation after deleting one byte: earlier endpoints stay fixed, enclosing endpoints shift by one, nested/fallback bounds follow from their stated ordering premises, arbitrary finite lists of enclosing/sibling endpoints preserve the relation, and the old outer endpoint exceeds stored length. The geometric deletion map is independently defined from the native-shaped endpoint expression. This is useful conditional arithmetic, **not a formal proof that every parser execution establishes the premises**, nor a proof of CSS substitution/provider correctness or Rust compilation.

Fresh compilation succeeded for all ten. Printed axioms are confined to `propext`, `Quot.sound`, and `Classical.choice`; the concrete witness is axiom-free. There is no admitted axiom or `sorry` in the accepted source. The producer's Lean mutation is a rejected proof compilation, not a successful Lean counterexample program. The positive old-overrun theorem and concrete witness provide successful kernel evidence. The native omission mutant really compiles and executes: it exactly reproduces original rows and panics.

Fresh producer replay: 40 cases, original 18 OK/22 PANIC, candidate 40 OK, omission mutant identical to original. Original/candidate stored bytes agree throughout; existing successful rows agree completely. Actual cssparser and complete parser/chunk bodies are compiled from authenticated inputs. `substitute_one_reference` has its signature and fallback tail retained, but its var/env/attr providers are an explicit facade. Atom/storage/context/namespace/typed-attr facades and handwritten function-kind dispatch are external boundaries. Namespace/typed-attr behavior is not established by these native rows. Reading/hash retention of a full provider body is not the same as compiling it.

Independent challenge: 360 cases across both quotes, var/env/attr, depths 1/2/3/8/32, no prefix/leading whitespace/earlier sibling, Unicode payload, and 0/1/3/5 trailing backslashes. Expected recovered bytes and substituted output are constructed from the input grammar independently of the production endpoint expression. Candidate passes all 360 exact-output and UTF-8 slice checks; original and mutant match exactly and panic on 270. These are additional finite tests, not a universal native theorem.

## WPT and browser evidence

Independently reviewed all test construction and expectations. The 38 cases cover 28 odd-backslash endpoint cases plus ten controls. Both quote types and one/three terminal backslashes exercise direct/nested fallback, custom-property carrier, unused fallback, earlier sibling, environment fallback and attribute fallback. Controls cover closed strings, EOF without backslash, escaped newline, closed literal backslash and a non-ASCII prefix. The expected font family is a separately constructed properly terminated declaration. It does not reuse malformed EOF recovery as its oracle.

Current primary CSS Syntax draft (16 October 2026), `consume a string token`, independently retrieved during review: EOF returns the string token; a backslash immediately before EOF contributes nothing; newline escape consumes the newline. Hence an odd run contributes paired literal backslashes and drops its final unmatched backslash. Ordinary EOF closure of enclosing functions and fallback selection supplies the WPT expectation. Spec retrieval is retained in `evidence/current-css-syntax.json`; primary URL: https://drafts.csswg.org/css-syntax-3/#consume-string-token . Earlier bug 2013337 concerns missing closing parenthesis detection and is retained as context, not proof of H1 novelty or correctness.

The independent checker reads raw JSONL, rejects duplicate result keys, verifies summary/raw/log identities, and compares every other status/expected pair. Baseline endpoint file crashes before any subtest outcome; candidate has 38 PASS and harness OK. **Do not describe this as 38 independently observed baseline failures.** All 34 other outcome records are unchanged, including eight separate unfixed semantic failures and three existing expected failures. Candidate process exit 1 is therefore expected in this mixed run. Both before/after run pin sets agree; all fixed input pins except the intended native file agree between baseline/candidate, and the exact WPT SHA is bound to both.

Root build/lint evidence is retained: successful style/XUL compilation and linking, exit zero, lint exit zero. The build log also contains export-tier monitor KeyError callbacks. I did not rerun Firefox, Mach, or a browser. This is local shared-tree browser evidence with pinned relevant source/configuration, not an isolated upstream browser build.

## Authentication and replay qualification

Parent-supplied FREEZE/MANIFEST hashes authenticated the producer's 152 inputs and formatted binding's seven inputs before source execution. The reviewed capsule contains only those listed source inputs; no producer-built binary is trusted. A fresh producer replay and the additional challenge ran locally, then both passed again in a clean relocated manifest-only capsule. Independent controls reject a changed theorem, wrong external manifest pin, and a symlinked source before replay. The first safe-path launch exposed the producer’s required local `rust_reader` import; the final replay supplies only that authenticated directory and succeeds. The checker here authenticates its externally supplied manifest, rejects noncanonical/duplicate/case-colliding paths and symlinks, then rederives patch/browser relationships. Optional fresh replay copies only authenticated producer inputs to a new capsule and clears ambient Python/Lean path overrides. The authenticated capsule native directory is then the sole explicit Python module path, required by the producer’s `rust_reader` import; safe-path mode suppresses ambient script/current directories. Child tools are the pinned Rust/Lean installations; compiler/standard-library trust remains external.

The producer checker itself is not a general secure capsule loader: it imports Python standard modules before its own manifest validation and does not authenticate its manifest externally or reject arbitrary extra shadow modules. Its `tamper_rejected_before_imports` result means the altered theorem is rejected before native/proof work, **not literally before Python imports**. This independent review compensates with external pins, isolated execution and a manifest-only copied source capsule; it does not endorse that broader wording. No frozen producer files were modified.

## Recheck

Authenticate `FREEZE.json`/`MANIFEST.json` and checker using the handoff digests. Then:

```
python3 -I -S -B artifacts/css-quoted-eof-offset-independent-v1/check.py --manifest <MANIFEST_SHA>
python3 -I -S -B artifacts/css-quoted-eof-offset-independent-v1/check.py --manifest <MANIFEST_SHA> --replay-output /absolute/new/output/path
```

The second command builds only artifact-local Rust/Lean programs and runs the 40 producer plus 360 independent cases. It performs no browser/build-system/Git action. Toolchain locations and hashes remain those explicitly pinned by the producer. Large generated native binaries are excluded from the review manifest; source, raw rows, command receipts and logs are retained.
