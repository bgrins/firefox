# Attribute provenance around successful animation arithmetic

## Scope and result

The repair's wrapper preserves the union of its two input attribute-provenance bits whenever the supplied payload operation succeeds. Fifteen kernel-checked results cover payload and first-operand URL-data preservation, failure equivalence, either-input and clean-input propagation, optional guaranteed-invalid/mismatched inputs, failed discrete selection, fixture observers, finite successful expression trees, and concrete repaired/omitted-provenance witnesses.

`finite_success_provenance` concerns a finite expression tree with one pure supplied binary operation. Successful evaluation preserves the disjunction of all leaf provenance bits. It is not a theorem about native effect histories, scheduling, arithmetic interpolation, or CSS parsing. Arbitrary payload and URL-data types need no equality assumption. The numeric sum witness is a generic inhabited arithmetic example, not a CSS .25/.75 sample.

## Source-bound replay

The original/candidate `value.rs` and unchanged `animated.rs` are retained in full. `BINDINGS.json` records exact complete extracted bodies for `Value<Component>::animate`, `Procedure`, `Procedure::weights`, and `Animate for Option<T>`. Replay regenerates and checks all four bodies for each variant before compiling. Candidate source SHA485c097931bcb385bc0ada6679c3429f6f300ffae5f03c75268458feb3316fa0 is root's final native candidate.

Each compiled variant emits45 ordered rows:12 successful arithmetic wrappers,24 failing provider wrappers,9 optional-invalid/mismatch cases. Procedures are interior interpolation .25, addition, and accumulation count2; all four provenance pairs and rejection from either input are included. An independent fixed row oracle checks payload, first URL-data identity, taint, error status, ordering and complete roster. The compiled original first-operand-only implementation is the semantic omission mutant: it disagrees exactly on clean-first/tainted-second successful rows1,16,31. All33 failure/optional controls and nine other successes remain unchanged. This is one compiled native mutant plus successful Lean witness theorems, not a mutated Lean proof rejection.

The native facade uses synthetic `Payload` and `ValueInner` types, u32 URL data, a small exact-number arithmetic provider, and a locally declared `Animate` trait. These make the selected real wrapper bodies executable; they do not compile actual Gecko value representations or generated enum derives. The source-body equality and finite native agreement are evidence for a conditional bridge, not a compiler correctness proof.

## Explicit admissions

- Payload success/failure and its arithmetic are supplied. The source wrapper forwards the procedure unchanged; the model abstracts it into `op`. No real-number/IEEE, clamp, interpolation-domain, count/extrapolation, or generated-provider theorem is claimed.
- The wrapper is reached for matching property names and supported payload variants. The outer name check, generated variants, complete effect stack, base lookup, map publication, FFI/lifetimes and scheduler are outside this component. The optional wrapper's selected native body is included, but this does not prove every caller establishes its inputs.
- `bundleObserver` and `directObserver` are admitted fixture-level observation contracts: valid clean data URL, nonnegative in-range numeric slice, correct registration/substitution, whole-custom-property taint, and computed-style observation. The model does not prove CSS URL validity, token substitution, shorthand parsing or IACVT computation. The separate browser fixture calibrates these premises.
- Failure/discrete selection is modelled as selecting the supplied original operand; the source proposal separately reviews the real segment fallback. No theorem equates the entire segment function with this small sample wrapper.
- URL data intentionally stays from the first input. No URL-data quotient correctness or global declaration equality change is claimed.
- OR conservatively retains zero-weight operand provenance. The oracle leaves the opposite clean boundary diagnostic; positive-weight interior and positive-count/add behavior supply the required repair evidence.
- Rust compiler, standard runtime/linker and Python host are trusted tooling; the compiler executable is pinned. Lean executable and installed `.olean`, `.olean.private` and `.dylib` library bytes are pinned as in prior components. This is not a verified compiler/runtime claim.

## Spec and browser connection

The independently written oracle and proposal are predecessor evidence, not imported model theorems. [Registered custom-property animation](https://drafts.css-houdini.org/css-properties-values-api-1/#animation-behavior-of-custom-properties), [numeric combination](https://drafts.csswg.org/css-values-4/#numbers), and [attribute security](https://drafts.csswg.org/css-values-5/#attr-security) provide the interpretation. The predecessor's `#animation-behavior` hyperlink was invalid in the retained draft; the actual anchor is used here and root corrects the landing test via a separately pinned help-link-only transfer. Source assertions, not invalid-anchor resolution, supplied the interpretation.

Root's paired browser run reported focused22PASS2FAIL→24PASS, and three additional diagnostic improvements;253 candidate subtests passed, with248 outcomes unchanged. Exact raw execution, build and two-file standalone packaging remain in `css-animation-interpolation-taint-final-root-v1`, outside this proof's executable closure. Neither those browser results nor hypothetical full CSS correctness follow merely from the15 theorem count.

## Replay and integrity

Authenticate external FREEZE/MANIFEST/checker pins, then run `python3 -I check.py --out ABSENT_EXTERNAL_DIRECTORY`. Before executing any owned helper, the checker authenticates the complete regular-file/directory closure, rejects symlinks/extra entries/duplicate JSON keys/path escapes, checks source/tool pins, and requires fresh output outside the capsule. Lean runs from fresh output with its search-path overrides removed. Native helper runs isolated with `-I`; no local module imports occur. Output retains exact source bindings, compiler logs, raw rows, oracle rows, axiom inventory and result.

The checker uses exact whole-output equality, so extra rows/fields/garbage, nonbinary values and missing rows fail. Three explicit row-corruption controls supplement the semantic mutant. Independent review still owns adversarial interpretation and replay; integrity checks cannot establish the admitted semantic interfaces.

Development included two Lean tactic corrections (case equality and leaf substitution) and an initial Rust invocation using the default old edition; final replay explicitly selects Rust2021. No incomplete proof or failed compilation is accepted as success.
