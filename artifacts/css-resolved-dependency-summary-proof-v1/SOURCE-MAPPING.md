# Source-to-model map

All paths below refer to complete files retained under `source/inputs/sources/`. Their bytes are authenticated against the sealed design manifest. The source predates the separate attr-only non-custom collection repair and any proposed resolved-summary scanner; the model has no compiled native admission claim.

| Model construct | Actual source path | Admission or difference |
| --- | --- | --- |
| Successful emitted token stream | `custom_properties.rs`: `substitute_internal` → `do_substitute_chunk` | Source returns a CSS string, token-boundary metadata and taint. Fully resolved token output is a premise, not inferred merely from `Ok` |
| Literal piece | `do_substitute_chunk` source slices before/after a reference, and its no-reference borrowed slice | Slice boundaries must denote component-value boundaries; lexical correspondence remains open |
| Selected replacement piece | `substitute_one_reference` primary branches and final fallback `do_substitute_chunk` call | Primary validity and provider values are external inputs to this component |
| Failure | `?` propagation from `substitute_one_reference` / `push`, or absent fallback | Modeled by outer `none`; no claim about which native parser/provider paths fail |
| Empty emitted piece | `VariableValue::push` returns immediately for empty CSS | Model `emit` does the same for an empty token list; equivalence of CSS-byte emptiness and this token representation is part of adaptation |
| Optional separator | `VariableValue::push` tests last-token `needs_separator_when_before(css_first_token_type)` and appends `/**/` | The boundary predicate is arbitrary in the theorem; source metadata and token preservation need separate proof |
| First piece | `first_token_type.set_if_nothing`; empty destination does not need separation | Model emits an initial nonempty piece directly; exact token metadata is not modeled |
| Whole-reference fast return | `do_substitute_chunk` returns the selected `Substitution` without assembly when it covers the whole slice | Equivalent selected output under adapter assumptions; taint-range handling is outside the theorem |
| Attribute persistence sink | Attribute branch of `substitute_references_if_needed_and_apply`: `VariableValue::new(substitution.css.into_owned(), url_data, first_token_type, last_token_type)` | Proposed scanner must summarize this successful output; current retained source discards dependency flags |
| Universal custom-property persistence sink | Universal branch of `Substitution::into_value`, same `VariableValue::new` arguments | Same proposed adapter; typed branch computes a typed value and is not changed by the design |
| Typed attr intermediate | `substitute_one_reference` parses a specified registered value then calls `to_variable_value` | Specified relative units can survive. A cached universal result reaches a persistence sink later |
| Typed serializer | `properties_and_values/value.rs`: generic `Value::to_variable_value` clones universal data or serializes typed components via general constructor | Proposed narrow repair leaves this general constructor unchanged; no proof of list token-boundary metadata |
| Unit classes | `ReferenceFlags::from_unit` | `.font` includes em/ex/cap/ch/ic, `.line` produces font+line, root variants preserve their two root dependency classes; aliases/escaping/case decoding belongs to native tokenization |
| Incomplete scan | Root's planned scanner identifies remaining substitution functions or bad tokens | Modeled explicitly by `Token.unresolved`; no exact flags claimed for that branch |

## Source counterexample to unconditional resolved admission

`Flags` in Lean is a function from four semantic dependency classes to Booleans, not the native `u8` layout. In the retained source specifically, `from_unit(LH)` returns FONT_UNITS | LH_UNITS and `from_unit(RLH)` returns ROOT_FONT_UNITS | ROOT_LH_UNITS. A different implementation could represent line dependencies alone and derive the font edge during traversal. Correspondence would then require a semantic mapping through that traversal; the model does not require identical raw bits or establish that broader mapping. Root/non-root normalization and the implicit line-height-to-font-size edge remain native admission obligations.

`CssEnvironment::get` parses arbitrary link-parameter CSS through `VariableValue::parse`. The env substitution branch directly wraps it in `Substitution::from_value`. Remaining var/attr functions can therefore survive a successful native return. This source comments on bug 2028998. No modeled theorem converts those outputs to complete zero flags.

## Information the model does not erase

The independent accumulator ignores unused fallback tokens, but the actual graph still uses pre-substitution `References.flags`, which include syntactic fallback flags. That graph summary is not identified with this selected-output summary. Similarly, the scanner changes neither CSS bytes nor URL/token/taint metadata by design; this model has not established a universal observer or taint preservation theorem for a native implementation.

The conditional tokenizer bridge compares token sequences modulo inert separators, not their already-computed dependency masks. A proof that only assumes equal masks would miss token fusion. Separate token streams corresponding to `1` and `em` have no dimension; the incorrectly fused stream `1em` has a font dimension. Native comment separators are intended to prevent that fusion, but the complete lexical theorem is open.
