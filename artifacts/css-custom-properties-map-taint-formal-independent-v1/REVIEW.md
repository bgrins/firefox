# Independent taint shortcut proof review

## Verdict

**Accept this conditional mathematical component within its documented scope.** No blocking proof, source-correspondence or replay issue was found. This is not acceptance of complete native cascade/URL correctness. The two-site native proposal was independently reviewed in the separate taint source package; root owns its build/browser gates.

The immutable producer has 29 inputs, four proof modules, 31 exact axiom reports and 27 complete source bindings. Fresh relocated execution passed all reports and four compiled semantic mutants. Five independent integrity challenges failed before output creation. Source authentication was repeated after replay. No native compilation, Firefox build, browser or Git operation was performed by this review.

## Mathematical substance

`Value P` retains an arbitrary payload and separate outer attribute-taint bit; absence is a distinct Option case. `mapUpdate` models the unique-owner replacement before the shared-owner shortcut. `pipeline` separately models an earlier declaration skip before resolving and updating. The reference history unconditionally replaces with the resolver result and never calls either comparator. Thus the central proof is not a definition equating optimized output with its desired result.

`metadata_same_sound` derives equality of taint and payload from the compared predicate. `PayloadSound` needs only comparator true implies equality of the selected abstract payload: reflexivity, symmetry, transitivity and completeness are unused. Nonreflexive comparisons such as a native floating NaN can refuse a shortcut without violating this theorem. However, this does not establish a quotient for all native values. Ignored URL data and other metadata remain open; abstract P cannot silently be the entire native struct. The same comparator used at the two modeled stages also needs an appropriate native projection at each admitted stage.

`map_correct` then derives replacement equivalence for all optional states and ownership flags. `gate_correct` additionally uses both reference-free eligibility and provider correspondence. The pipeline and finite-history induction compose these results without assuming equality of the shortcut outcomes. Every-prefix observation follows from that state equality. Unique replacement, absent versus present empty-like values, taint addition/removal and no-reference domain failure are represented separately.

The concrete masking witnesses are meaningful: fixing only the map can leave the earlier gate skipping, while fixing only the gate can still reach the old shared-map skip. A unique map cannot repair a prior gate skip. These support one two-site metadata-preserving repair, not an arbitrary decomposition into independently observable fixes.

## Native source boundary

Read the complete four modules, driver, checker, exact patch, final scope/mapping, and 27 source bindings with their retained complete files. The map reuses existing `can_deduplicate_values`; the cascade compares the existing **outer** wrapper taint with incoming `is_attr_tainted()` and then compares CSS text. `Substitution::into_value` can carry taint outside an inner resolved token value, so comparing that inner token's taint would be insufficient. The incoming predicate combines the ATTR flag and explicit-taint bit, matching the model's separate fields.

The source `Value::PartialEq` intentionally omits URL data and taint; `VariableValue::PartialEq` compares CSS text. The proof adds taint to a selected semantic projection rather than changing global equality. The native unique/shared/COW machinery is abstracted at one selected value; actual Arc lifetime, map chains, count, iterator and routing are not proved here. Committed fix 74 is live count; fix 75 is nearest-owner iteration. Neither prior component is imported or silently treated as discharged by this proof.

Most importantly, native `value_may_affect_style` executes before `has_references` is computed. It has no reference-free guard. Its eligibility depends on declaration kind, existing `as_universal()` and earlier guards, whereas `Incoming.eligible` is supplied. The final SCOPE explicitly requires correct labels relative to each evolving native state and a contextual resolver represented by the fixed model function. The no-reference universal constructor motivates one source subdomain; no theorem derives that every native gate enters it. The unresolved-reference witness demonstrates a mathematical counterexample if the domain premise is removed, not a reproduced additional browser defect.

## URL observation boundary

`Observation` uses the native inclusive endpoint predicate, including its endpoint behavior; it does not reinterpret the source comment's exclusive end. Valid query containment derives overlap with a whole tainted substitution region. State equality preserves both scalar and range observations for an arbitrary shared payload parser. This does not derive actual serialization, selected-substitution taint propagation, byte-range placement, parser advancement, resource resolution or mixed-range semantics. Those explicit assumptions prevent the simple scalar observer from becoming a false full URL theorem.

The retained spec source supports preserving origin taint when equal text is copied and removing it when replaced by an independent literal. That normative requirement alone does not validate native offset production or URL-data quotienting. No security severity or network-exfiltration conclusion follows from this component.

## Replay and discrimination

The manifest-only copy was authenticated using external FREEZE/MANIFEST/checker hashes before execution. Replay used `python3 -I -S` and the exact Lean 4.35.0-rc4 executable plus 5,092 pinned library files from TOOLCHAIN. All 31 reports contain only the allowed standard axioms (`propext`, `Quot.sound`, `Classical.choice`). No producer local axioms or proof placeholders were admitted.

All four mutated Model definitions compiled before their seven-observation driver ran. Payload-only map and gate mutations fail both taint-direction observations; dropping explicit taint fails the taint-addition observation; retaining old value on unique ownership fails the typed unique update. Compiler failure is not counted as mutation discrimination. Exact outputs and command logs are retained in receipts/replay.

Independent guards reject modified source, extra input, missing input, symlinked input and an output path containing `..` that resolves inside the copied capsule. The latter addresses the previously documented lexical-path caveat in a different older component: this producer resolves output before containment checks. All rejected invocations left output absent. These tests do not prove checker/parser/compiler security.

## Practical conclusion

The companion proves the mathematical reason both metadata-aware shortcuts preserve a selected taint-bearing value under explicit comparator/provider/eligibility admissions. Those admissions remain substantive open work for whole-native refinement. The component is suitable to accompany the narrowly reviewed fix, with separate native runtime evidence; it does not close arbitrary CSS declaration histories, attributes/SCC effects, registration changes, heap safety or URL parsing.
