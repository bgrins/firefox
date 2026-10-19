# Independent review: selected-output dependency composition

## Verdict

Accept the sealed package as a **conditional mathematical composition component**. I found no false theorem or hidden assumption that invalidates its stated scope. Do not describe it as a proof of the proposed Rust scanner, native substitution execution, or CSS dependency-cycle handling.

I authenticated the communicated FREEZE hash and all 23 inputs before executing the replay. Fresh compilation passed all three modules and 25 declaration audits with only `propext` and `Quot.sound`. All four supplied mutants failed on semantic proof goals, not syntax or missing imports. Full fresh logs are retained in `replay-v1/`.

The forthcoming native repair was not sealed when this review was performed. No production files, WPT files, Git state, browser, or Firefox build were changed. Artifact-local Lean compilation is the only compiled execution in this review.

## Independence and substance

`execute` selects replacement outcomes and assembles token lists through `emit`. `accumulate` independently pattern-matches pieces and folds summaries without calling `execute`, `select`, or `emit`. Their structural independence is sufficient for the stated composition result: a branch-selection or assembly bug in one side can disagree with the other. The supplied primary/fallback and unused-fallback mutants demonstrate that disagreement.

Both computations intentionally share `scan`, `tokenScan`, `unitFlags`, and the supplied primary/fallback outcomes. The reference is consequently an independent **composition** calculation, not an independent CSS lexer, unit classifier, provider, or fallback-eligibility oracle. Its theorem remains true if both sides use the same incorrect dimension classifier. This boundary is acknowledged in the producer's documentation and must stay visible.

To make that limit concrete, `primitive-control.py` changes `.line` from font+line to line alone, recompiles TokenSummary, SelectedOutput and Audit, and observes all original proofs still passing. The altered definition contradicts the retained native `from_unit(LH)` bit combination but preserves the algebraic laws being proved. `primitive-control-v1/` records this expected pass. This is a coverage diagnostic, not a failed claim in the original component.

The principal induction is universal over arbitrary finite pieces, arbitrary initial output, and any separator predicate. It is not a list of the browser examples. Supporting associativity and identity lemmas are appropriate machinery; 25 audits should not be reported as 25 separately verified native obligations.

## Hypotheses and outcomes

| Claim | What is actually established | What must not be inferred |
| --- | --- | --- |
| `selected_output_summary` | Scan of modeled successful assembly equals the independently accumulated selected-piece summary | Native provider/typed-parse eligibility is correct |
| Unused fallback independence | Changing an unused fallback cannot affect modeled emitted tokens or their summary when the primary is supplied as successful | Original graph dependency collection may ignore syntactic fallback references |
| Separator preservation | Inserting the semantic inert separator does not change a token summary | Actual CSS-byte concatenation preserves tokenization |
| Failure propagation | A modeled replacement with neither successful primary nor fallback makes execution fail | Every native push limit, allocation or parser failure is represented at its exact program point |
| `tokenizer_bridge` | Actual token equality modulo inert separators transfers the composition result | The source's serialization metadata satisfies that lexical equality |

Native `VariableValue::push` can fail on size limits. This model does not make literal emission independently fallible. The source mapping's generic outer `none` explanation must not be read as full native failure refinement. The successful-output bridge avoids that overclaim.

The nested option type is correct and useful: substitution failure, successful output with incomplete scan, and successful output with exact flags remain distinct. Incompleteness is absorbing across the scan; later execution failure still remains an outer failure. An unresolved token in an unused fallback is not visited. The concrete witnesses exercise all of these distinctions.

## Compatibility with the proposed scanner

The planned Rust helper returns `None` for a remaining recognized `var`, `env`, or `attr` function and for bad string/URL tokens. Mapping these cases to the model's `.unresolved` token is a valid coarse abstraction for summary completeness.

The planned two native sinks preserve their old empty reference metadata on that `None`. That behavior is **not** an exact-zero result in this model. Native exact-summary correspondence must therefore be restricted to `Some(flags)`. The producer explicitly records this restriction, including env link payloads that survive an otherwise successful outer substitution. There is no theorem equating native compatibility fallback with `scan []`, and none should be added.

For fully substituted valid input, the suffix-tokenizer design from the earlier scanner review is compatible with this mathematical interface. This proof does not establish its strict byte progress, lexical restart equivalence, UTF-8 boundary safety, arbitrary-depth behavior, or runtime complexity. Recursive Lean list definitions also do not prove native stack bounds.

The `tokenizer_bridge` premise is stronger than merely assuming equal masks: it requires matching semantic token sequences after separator removal. It therefore exposes token fusion as an admission obligation. However, `tokenize` remains an arbitrary supplied function; the proof does not construct it from cssparser. Inert token identities must be assigned consistently, and generated comment separators must receive a compatible abstraction. Removing semantic separators is not permission to remove `/**/` bytes before real tokenization.

## Semantic flags and source mapping

The current definitions agree with the retained native unit classifier:

| Semantic unit | Model dependencies | Retained native groups |
| --- | --- | --- |
| absolute | none | unrecognized/absolute unit returns empty |
| font | font | em, ex, cap, ch, ic |
| line | font and line | lh returns FONT_UNITS and LH_UNITS |
| rootFont | rootFont | rem, rex, rch, rcap, ric |
| rootLine | rootFont and rootLine | rlh returns ROOT_FONT_UNITS and ROOT_LH_UNITS |

Case folding, escapes, and classification of Dimension versus Ident/string/URL are not established in Lean. The native scanner should reuse `ReferenceFlags::from_unit` on the decoded Dimension unit to avoid introducing a second unverified classifier. If a later native implementation uses a different raw representation, require an explicit semantic mapping through its consumers; the producer's hypothetical discussion of that possibility is not such a proof.

`COLOR_SCHEME`, current-element/root normalization, and the final property-edge mapping are outside the four-class model. Nothing here proves graph SCC traversal, graph admission, registration parsing, algebraic cancellation, or native observer/taint preservation.

The retained historical source identifies both intended sinks and the typed serializer path accurately. It predates the later collection repair and the new scanner. Its hash cannot authenticate a new native candidate. The snapshots are enough to establish design provenance, not to close a source-to-binary claim.

## Native review gates

Before accepting the implementation companion, independently check:

1. The two exact persistence sites call the new helper; the general constructor and typed computed-value path retain their old behavior.
2. The helper uses the actual decoded token classifier, handles all units above, consumes positive byte lengths, and never silently truncates deep valid input.
3. Any incomplete scan discards all partial flags and preserves the documented compatibility behavior without being labeled exact zero.
4. CSS bytes, URL data, first/last serialization types, empty reference list and caller taint assignments remain unchanged.
5. Native source execution covers lexical examples, generated specified attr values and selected fallback cases; a shared-token-list theorem does not replace those source checks.

There is no blocker to retaining this component with those open admissions. Native review should be a separate append-only handoff once the producer freezes the actual repair.

## Reproduction

Authenticate this review's MANIFEST/FREEZE against the communicated hashes, then run:

```sh
python3 artifacts/css-resolved-summary-proof-independent-v1/check.py \
  --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --output /tmp/resolved-summary-independent-fresh
```

The output directory must not exist. The checker authenticates every retained file before launching the producer replay and the independent primitive control. Lean's standard prelude/toolchain remains trusted; the executable hash is checked, but this package does not vendor and independently validate the whole compiler or standard library.
