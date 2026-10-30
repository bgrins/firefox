This isolated Lean companion models the literal-zero policy question and the six-case observer already proposed from source/spec research. It does not discover a new bug, resolve CSSWG issue 7472, or report browser outcomes. The original browser run was live during preparation and its output was not read.

Two policies are explicit: mathematicalLiteral makes unsigned, plus-signed and minus-signed literal zero positive; preserveLiteralSign retains a minus-signed literal as negative zero. The former matches the current Values 4 wording cited by the probe; the latter captures the compatibility alternative discussed in the existing CSSWG issue. Choosing the former in a theorem is not a resolution of that issue.

The model has seven semantic classes: NaN, positive/negative infinity, positive/negative one and positive/negative zero. Explicit finite tables define sign(), reciprocal and multiplication by negative one. Generated negative zero is an expression evaluated from negative-one multiplication, never routed through literal normalization. Number and pixel-length labels deliberately share the same supplied class semantics; `quantity_erasure_explicit` states this modeling choice rather than proving native dimensional parsing.

The observer follows the fixture's `calc((2 + sign(1 / sign(value))) / 4)` composition. Exact outputs are represented as integer quarter-units: 3 means 0.75, 1 means 0.25, and 0 means zero. `biasedQuarters` explicitly includes top-level NaN-to-zero and opacity clamping as model operations. It does not implement a generic floating-point evaluator or prove these host steps. Positive zero, negative zero and NaN have pairwise distinct outputs. The finite reciprocal table agrees with the reused SpecialValueObserver companion on all five of its classes; this is model-to-model agreement, not native refinement.

| Existing fixture callback | Mathematical literal policy | Sign-preserving literal policy |
| --- | --- | --- |
| positive number zero | 0.75 | 0.75 |
| literal negative number zero | 0.75 | 0.25 |
| generated negative number zero | 0.25 | 0.25 |
| positive length zero | 0.75 | 0.75 |
| literal negative length zero | 0.75 | 0.25 |
| generated negative length zero | 0.25 | 0.25 |

Six-case results and the fact that only negative literals distinguish the policies are kernel checked. Both policies preserve arithmetic-generated negative zero; globally normalizing computed zero changes its observation. Four expected-false Lean files reject global computed-zero normalization, equating positive/negative observer outputs, equating NaN/negative-zero outputs, and equating both complete policy result vectors.

Actual successful run2: launch acb794, session 57396, terminal 34f41d/0. It checks 16 theorem declarations and rejects all four false claims with the intended decide-is-false diagnostic. Axiom output uses only propext or no axioms; no sorryAx, custom axiom or native_decide reduction is accepted. Toolchain version, exact commands, source hashes and all logs are retained. The first run (63612/de740e/1) failed because two finite proofs left a Quantity variable unsplit; its source and diagnostics are retained. Splitting that explicit finite parameter fixes the proof scripts without changing the model definitions.

Replay with `python3 -I -S -B replay.py <fresh-output-name>`. The pinned Lean 4.35.0-rc4 executable and existing observer source are reused; compilation runs only in an owned temporary directory. Both runs removed their scratch directories and retained no olean, target, Lake build or dependency cache. No canonical library, native source, Git/index, application, browser, signing or coverage record was changed. Canonical coverage increment is zero. The proof does not cover tokenization, parsing, dimensional type checking, CSSOM/computed-style transport, compiler correctness, floating accuracy, all CSS expressions, or browser refinement.

Primary interpretation and prior-art links remain in the pinned probe/browser DEDUP notes: [Values 4 signed zero](https://drafts.csswg.org/css-values-4/#calc-ieee), [CSSWG 7472](https://github.com/w3c/csswg-drafts/issues/7472), and [the primary compatibility comment](https://lists.w3.org/Archives/Public/public-css-archive/2022Jul/0195.html). Source/spec investigation and the existing WPT conflict preceded this model; no new discovery or accepted fix credit follows.
