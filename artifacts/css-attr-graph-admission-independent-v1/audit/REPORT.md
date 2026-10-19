# Graph/source admission audit after typed eligibility

## Status

Two concrete source obstructions remain. The proposed probe has thirteen cases: four predicted discrepancies and nine controls. It has not been run in a browser. This is a source audit and test proposal, not a new native fix, a Tarjan proof or closure of C1–C13.

The complete candidate is copied from the authenticated, sealed `css-attr-typed-eligibility-repair-v1` package. That package's manifest and seal are retained. A fresh Searchfox cascade snapshot is discovery evidence only: it differs from the locally changed candidate and does not establish correspondence to root's build. Fresh primary specification snapshots and fetch metadata are retained in `spec/`.

## Finding 1: ready values can erase required non-custom dependencies

### Source chain

1. `parse_declaration_value_block` recognizes relative length units and records their `ReferenceFlags`. The initial attribute value `1em` therefore has a font-unit flag.
2. `traverse` treats attributes as unregistered. `find_non_custom_references` returns no implicit dependency for them. With no var/attr references, the attribute follows the early completion path through `substitute_references_if_needed_and_apply`.
3. That function's attribute branch reconstructs the successful result using `VariableValue::new`. This constructor sets `references: References::default()`, even though the resulting CSS can still contain relative units. The attribute's computed universal wrapper is ready, but its unit flags have disappeared.
4. Back in `visit_value_references`, the registered consumer looks up this ready attribute and ORs the now-empty flags into its accumulated flags. The new occurrence-specific parse succeeds for `1em`; it returns a specified length and does not compute its relative unit.
5. The registered consumer consequently lacks the edge that would ensure `font-size` before calling its registered `compute_value`. `apply_custom_and_prioritary_properties` ensures any still-unvisited prioritary properties only after this traversal.

Minimal acyclic witness:

```css
@property --length { syntax: "<length>"; inherits: false; initial-value: 11px; }
/* Parent font-size: 23px. Attribute a on the target: "1em". */
.target { font-size: 17px; --length: attr(a type(<length>)); width: var(--length); }
```

Expected width is 17px. The source predicts a premature computation against the inherited 23px font. This does not require deciding whether unused fallback syntax contributes cycle edges. The paired direct `--length: 1em` control has its original unit flag and should ensure 17px first.

A second witness closes the font back edge using `font-size: var(--length)`. The source predicts a missed cycle: `--length` and width become 23px rather than the registered initial 11px, while font-size is 23px in both cases. Reading the custom property and width prevents that equal font value from hiding the difference.

The same loss occurs through a substituted universal custom property: `--unit: 1em; --raw: var(--unit); --length: var(--raw)`. `Substitution::into_value` rebuilds a universal value with `VariableValue::new`, losing the unit flags before the typed consumer observes it. A literal `--raw: 1em` takes the trivial existing-value path and retains its flags. These are distinct routes to the same metadata-loss obstruction.

### Admission consequence

“Ready and reference-free” establishes absence of remaining substitution functions, not absence of relative-unit computation dependencies. A native admission theorem needs a summary of the successful token sequence's non-custom dependencies, or a justified equivalent observation through the graph/evaluator. Merely preserving old source flags also cannot establish exactness, because those flags include unused fallback syntax (see Finding 3). No repair is proposed here.

## Finding 2: attr-only non-custom declarations can hide a graph edge

`maybe_note_non_custom_dependency` preloads attributes, then returns when the declaration's lexical flags omit VAR. Thus `font-size: attr(a type(<length>), 5px)` is not recorded in `references_from_non_custom_properties`, even when the runtime attribute is `var(--length)`.

With registered `--length: 1em`, traversal does create `--length → font-size`. But the font node has no retained declaration to visit, so the reverse path through the attribute is absent. It applies font-size while the typed attribute cache still contains unresolved var tokens. The final type parse rejects those tokens and uses 5px; the registered length can then compute to 5px. The source predicts font-size, width and `--length` all become 5px instead of the cyclic result 23px/11px/11px.

The semantically equivalent declaration `font-size: calc(var(--zero) + attr(a type(<length>), 5px)); --zero: 0px` carries a lexical VAR bit, so it is recorded. This is the discrimination control. A 13px registered value removes the relative-unit back edge and supplies a successful chained-attribute control.

The collection predicate would need to account for dependencies discovered in runtime attribute contents; syntactic absence of var() in the declaration does not prove absence of custom-property dependencies. This is separate from the new typed eligibility decision and from eager fallback preparation.

## Finding 3: unused fallback flags, not yet a normative defect verdict

The parser unconditionally bubbles every fallback's flags into its enclosing `References`. `find_non_custom_references` uses this summary before branch selection; `visit_value_references` also ORs the whole summary on entry. Therefore an unused relative-unit fallback can still contribute an implicit font edge even though its reference list is never visited.

`unused-fallback-diagnostic.html` compares successful 13px primaries with 1em and 7px fallbacks. The source predicts a cycle for the first but not the second. This page deliberately has no testharness assertion. CSS Values 5 substitutes before interpreting the resulting property value and leaves unused fallbacks unsubstituted; Properties and Values API §2.7.1 says to add edges when a registered property “contains” relative units, without specifying that timing in this paragraph. Resolving that relationship is required before treating the diagnostic difference as a normative bug. The model obstruction remains: an unconditional syntactic flag summary is not proved equal to a summary of used tokens.

## Primary specification trace

CSS Values 5's [attr substitution](https://drafts.csswg.org/css-values-5/#attr-substitution) substitutes attribute contents before parsing the requested syntax. Its [syntax parser](https://drafts.csswg.org/css-values-5/#parse-with-a-syntax) returns parsed values without converting them to computed values. Its [property replacement](https://drafts.csswg.org/css-values-5/#property-replacement) substitutes before parsing the resulting property value. Successful primaries leave fallbacks unused; failed primaries use them.

Properties and Values API [computed-value behavior](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values) requires registered lengths to convert relative units to computed lengths. [Relative-unit cycles](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles) adds current-element font dependencies for em and specifies invalidation for the demonstrated length/font cycle. Registered var() references substitute the computed value. In the acyclic witness the target font is 17px, so 1em becomes 17px. In the cycle witnesses the registered value resets to its 11px initial value and font-size behaves as unset, inheriting the calibrated 23px parent value. The probe uses an explicit non-inherited registration and a real parent to avoid initial-font ambiguity.

The used self-referencing fallback control has only a custom-property self-cycle, without a relative-unit edge to font-size. Its registered property resets to 11px; font-size then validly reads 11px. This differs from the font-cycle controls, whose font-size inherits 23px.

Verdicts: the acyclic ordering expectation is REACHED; the used relative-unit cycle expectations follow the specified implicit dependency plus active substitution chain. Actual browser discrepancies remain UNEXECUTED. The unused-relative-fallback interpretation is INCONCLUSIVE.

## Remaining source obligations

| Boundary | What the candidate establishes | What remains open |
| --- | --- | --- |
| Ready non-universal registered values | `as_universal()` exits early for already-computed typed values | Admission that their prior computation used all required dependencies |
| Ready universal / attr values | No remaining substitution functions | Preservation of unit dependencies through `VariableValue::new` is refuted as a general source invariant |
| Per-occurrence type eligibility | Shared primary parser after readiness, exact source property context | Full parser/evaluator/provider correspondence and side-effect algebra |
| Used fallback traversal | Reference lists follow the occurrence's primary decision | Initial/bubbled flag summaries are not proved branch-sensitive |
| Non-custom collection | Lexical var() declarations retain originating property and shorthand | Attr-only runtime dependency chain is omitted by the early return |
| SCC bookkeeping | Index/lowlink/stack state remains unchanged by this draft | No general correctness theorem for the dynamically revealed graph, reset order or observer effects |
| Providers | Qualified attribute lookup and tombstones are preserved | Stability and full invalidation/cache correspondence remain external |

No claim is made that the historical full cascade scope is complete. There is no fresh native build, browser result, original-versus-candidate regression claim, or novelty claim in this package. The probe is intended for root's isolated execution after the typed repair gates finish.
