# Independent URL native-state review, v1

## Verdict

**BLOCKED: do not accept v1's complete native trace validation claim.** The mathematical component is substantive, and its fresh relocated replay passes. Five malformed traces are nevertheless accepted by the frozen native comparator. This is an evidence-validation defect; this review identifies no new Firefox defect or false Lean theorem.

The author is preparing v2. This review and its v1 counterexamples must remain immutable. Root owns final acceptance.

## Authentication and fresh replay

Before executing or importing producer code, independently authenticated externally supplied FREEZE `ab963101784ea7d7fd077ac96a63b2d1075bf586eda752fc13a803859567261b`, MANIFEST `f6a64601cd26d168e98c8dd17bccd75f93e12d916a1eb506788b8a01742191d5`, and checker `84c490eeb94a8aacf3d592492c27797d2bf1333b00e752ca2b3c6d5f12a80bf4`. Checked all 428 inputs, duplicate JSON keys, confined canonical paths, symlinks, and closed file/directory rosters; retained an exact relocated source copy in `package/`.

Fresh `python3 -I -S -B package/check.py --run --output /private/tmp/url-state-independent-replay-v1` completed with exit 0. Evidence retains commands, hashes, logs, raw traces and receipts, excluding generated binaries/olean files. Results: 51 modules, 388 axiom reports, including 17 new modules and 107 new reports; 44 source function and five field bindings; three native modes agree on 59 cases, 230 helper transitions, 56 slices, 46 bulk events and 112 Lean entry/exit observations. Uninstrumented token/final-field comparison passes. These counts describe the actual retained run, not an independently enforced completeness invariant of v1's trace comparator.

## Blocking finding: open trace grammar and missing control continuity

`native/check_states.py` groups events by case and checks individual helper transitions against independently computed source-prefix fields. It does not require an ordered complete helper/slice/bulk control trace. Unknown event tags fall through; extra fields are ignored by slices. Totals are reported, not required. Entry/exit comparison and cross-mode raw equality do not exclude systematic recording omissions.

`challenge_v1_trace.py` starts from the fresh valid debug trace and independently applies five corruptions. Each returns exit 0 from the sealed comparator:

| Corruption | What v1 accepts |
| --- | --- |
| Missing helper | First `step` removed |
| Unknown event | Appended `0\|unrecognized\|ignored` |
| Duplicate helper | First `step` repeated |
| Extra helper field | Appended `\|ignored` to first step |
| Reordered helpers | First two steps of the same case swapped |

Exact altered traces, commands, hashes, accepted totals and output are retained under `evidence/trace-challenges/`. They are counterexamples to validator completeness, not to the good run's reported arithmetic. V2 needs exact event grammar, expected per-case source-derived control coverage and order/continuity. Requiring only aggregate totals is insufficient: swapping steps preserves every count.

## Substantive model and source review

| Obligation | Assessment |
| --- | --- |
| Actual mutable fields | Positive in the modeled domain. Position, wrapped line start and packed line are independently mutated; observers are related by inductive proofs rather than assigned as desired outputs. |
| Helpers, hex and escape | Positive conditional composition. Intro/continuation masks and six-hex escape consumption are bound to retained source. Escape-cut/no-split lemmas handle CRLF composition. |
| Owned and borrowed loops | Positive. State-handoff joins follow branches and helper operations. Owned decoded-buffer allocation is not mistaken for original source identity. |
| Raw source and endpoint | Positive conditional composition. Start position is captured from original full source; terminal recursion derives EOF or a genuine ASCII close boundary. Numeric bounds alone are not used as a substitute for that marker. |
| Leading scan and bulk | Positive. Stats are accumulated separately, bulk assignment is modeled after scanning, and quoted return rolls back without applying those assignments. |
| UTF8 public entry | Positive within structural encoding premises. Final `body_valid` derives body alignment from whole-input validity after whitespace; internal `TailValid` is not silently assumed for an arbitrary native entry. |
| Caller seam | Correctly limited. Modeled Function denotes the URL helper's error/delegation seam. Actual caller subsequently sets parenthesis block state and observes the function. Finite final packed-bit checks include this effect. |
| Native instrumentation | Useful, bounded evidence. Inverse transformation recovers original tokenizer bytes; wrappers call retained helpers and record actual fields/slices. Separate uninstrumented output comparison passes. Complete event validation remains blocked as above. |
| Independent oracle | Source-prefix scalar arithmetic is independent of native final fields. NativeDriver derives the name seam and initial state from input. Lean trace application is not itself a full native compiler or public parser-history proof. |

The final terminal theorem and full-source invariant materially strengthen the predecessor raw-payload admission. The source mapping is not a universal theorem about compiled Rust. The independent native scalar oracle checks selected executions, while Lean proves universally quantified model relations.

## Mutation cause audit

Fresh native mutations all compile and fail intended semantics, despite the runner's overly broad acceptance of `AssertionError`:

| Mutation | Actual discriminating failure |
| --- | --- |
| Astral line-start sign | Case 15, `url(é𝄞)`: final line start 5 instead of 3. |
| Continuation sign | Same case: 4294967291 instead of 3 modulo 2^32. |
| Bulk last-newline | Case 58: final line start 10 instead of 11. |
| Capture after close | Case 22, `url(a b)tail`: captures `a b)` at offset 8 instead of `a b` at 7. End equals exit but is not EOF, triggering the intended endpoint assertion. |

The bulk mutation's survival on the old 58 cases is retained and freshly reproduced. The added unquoted leading CRLF/CR/FF case actually executes bulk assignment; the older quoted case correctly delegated before assignment. This is honest failed-discrimination evidence.

All four Lean mutated definitions plus semantic witnesses compile successfully. Unchanged theorems then fail at the intended relation: astral field relation and concrete false `decide` propositions; bad-close capture invariant reducing to False; bulk field relation; quoted rollback equality. No rejection relies on syntax errors or missing identifiers. See `evidence/MUTANT-CAUSES.json`, witness sources and rejection logs.

## Explicit boundaries

Intentional line-start underflow/wrap is modeled, including initial astral wrap. Packed-line shift/count and addition headroom are separate assumptions. Nat positions do not prove usize headroom, allocation feasibility or memory safety. Actual canonical Rust UTF8 codec/character-boundary behavior, unsafe slicing, compiler correctness and heap behavior remain external. Structural UTF8 validity is not silently upgraded to complete canonical codec equivalence. Reference columns require the documented modulus bound for exact rather than modular equality.

No whole-tokenizer, CSS parser, public cache/reset-history, URL resolution, or browser correctness conclusion follows. URL helper annotation nonmutation is source inspection plus finite absent-Option observations, not arbitrary annotation-state execution coverage. Previously accepted helper versions and their premises remain pinned. There were no live source, WPT, Git, build or browser changes during this review.

## Reproduce this review

Run `python3 -I -S -B check.py` to authenticate the closed retained review and check its receipts. Run with `--challenges /private/tmp/new-output-directory` to regenerate all five negative witnesses against the immutable copied producer. A successful review checker means the negative finding is retained and reproducible; it does not accept v1.
