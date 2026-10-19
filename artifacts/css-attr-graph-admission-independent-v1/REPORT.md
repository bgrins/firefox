# Attribute graph admission: independent oracle and repair review

## Verdict

The thirteen-case audit has a sound oracle for its four predicted failures. Root's retained baseline actually reports those four failures and nine passes. The failed subtest messages distinguish three relative-unit metadata-loss cases from one attr-only non-custom collection case; this is not merely a comparison to predictions.

Approve the **narrow collection repair for candidate testing**: remove the three-line lexical-VAR early return after attribute preparation in `Cascade::maybe_note_non_custom_dependency`. Keep the outer VAR-or-ATTR filter, existing attribute preparation, property-to-node mapping, originating property/shorthand context and traversal unchanged. Root's ten-case WPT is correctly scoped to this repair and does not require fixing relative-unit metadata loss. No native build or candidate browser acceptance is claimed by this reviewer.

Exact root two-file patch: `00393f6fca5f814524a28f2e8b659c8c5b3cd85236cf3c4146291919e1519441`. Exact WPT: `ad03d87fe03f1575c35f2f354672a6a26fd86ff4119a286e43ed3ca2fa92b079`. Complete original cascade: `62b107265cb3a6a43a50d8972150fbc210916e908393b48d939d3cf1e29199ad`; candidate: `9fc12829fede773010371d954854df8c9d28e877c50d5709d30c5db5b03a6be0`. Root copies equal the independently constructed three-line-deletion snapshots. The patch also adds exactly the retained WPT, with no other changed path.

## Normative trace

Current [Properties and Values API computed-value rules](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values) require a registered length to compute its units; universal custom values retain substituted tokens. [Its dependency-cycle rules](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles) add current-element font-size dependencies for em and font-size plus line-height dependencies for lh. A cycle involving font-size makes that declaration behave as unset. Registered non-inherited properties then use their registered initial value.

[CSS Values typed attr substitution](https://drafts.csswg.org/css-values-5/#attr-substitution) substitutes attribute contents before checking their requested syntax. Its [substitution contexts](https://drafts.csswg.org/css-values-5/#substitution-context) invalidate all participants when a repeated active context closes a cycle; an interior fallback does not rescue the already-cyclic participant. Used fallback evaluation and unused fallback omission follow the replacement algorithm. These are active dependencies, not every lexical reference in every fallback.

Consequently, with parent font-size 23px, registered non-inherited `--edge-length` initial 11px, `--edge-length:1em` and `font-size:attr(a type(<length>),5px)` where a is `var(--edge-length)`, the cycle invalidates the custom value and font-size declaration. Expected custom/width are 11px and font-size is inherited 23px. The 5px attr fallback cannot make that cyclic font declaration valid. For the corresponding `1lh`/line-height cycle, the explicit parent line-height 31px is inherited while the custom value resets to 11px. This does not rely on font metrics or platform default font sizes.

The acyclic metadata witness (`font-size:17px`, attribute `1em`, registered typed consumer) must compute to 17px. Its observed 23px is an ordering failure independent of cycle invalidation. The universal chain preserves relative tokens until the typed consumer computes them; substituting through another universal property is not permission to discard their dependency summary.

Primary full HTML snapshots and retrieval metadata are preserved from the authenticated audit; current web-tool reads independently checked the relevant clauses on 2026-10-19. No assertion is made about novelty or all CSS substitution features.

## Two separate native obstructions

**Metadata loss:** `parse_declaration_value_block` records relative-unit flags. `VariableValue::new` constructs empty references. Ready attribute reconstruction and `Substitution::into_value` for a universal property use that constructor, so the resulting CSS can contain `1em` while its flags are empty. `traverse` treats attributes as unregistered; they do not compute away the relative unit. A typed consumer's `visit_value_references` observes the ready value but cannot recover the erased flag. It can compute before font-size is ensured, or omit the implicit back edge. The direct literal-universal path retains its original value and therefore discriminates this loss.

**Collection omission:** the non-custom declaration collector already detects ATTR and preloads its references, enabling `may_have_custom_property_cycles`. It then returns solely because the outer declaration has no lexical VAR. Runtime attribute values may contain var(), so that early return does not establish absence of a custom dependency. `traverse(NonCustom)` subsequently has no originating declaration to visit. The three-line removal lets the existing visitor inspect the attribute with the correct property/shorthand context and qualified identity. `visit_link`/SCC invalidation and prioritary application need no change for these witnesses.

The repair records a declaration for later branch-sensitive traversal; it does **not** add graph edges for every prepared attribute or unused fallback. The property match still restricts registration to FontSize, LineHeight and ColorScheme. Other attr-bearing declarations retain their existing preload-only behavior. VAR-only declarations and declarations without either flag follow unchanged paths. Qualified keys and invalid-value tombstones are not changed.

## Ten-case WPT review

The exact root WPT contains:

| Cases | Independent expected behavior |
|---|---|
| Attr-only em/font-size and lh/line-height cycles | Initial registered 11px; corresponding inherited 23px or 31px property |
| Same two cycles with lexical zero-valued var() | Identical result; syntactic VAR presence must not alter semantics |
| Missing primary, used attribute fallback | Same active font-size cycle |
| Successful 13px primary, unused cyclic attribute fallback | No font cycle; font-size and registered value 13px |
| Literal attribute 13px | No reverse custom edge; registered 1em computes to 13px |
| Missing attribute with literal 5px fallback | Font-size and registered 1em compute to 5px |
| Literal registered 13px, chained attribute in font-size or line-height | No relative-unit back edge; both active values 13px |

All relative-unit declarations under test are direct registered literals. Attribute values are either absolute lengths or references to that registered property; the test avoids the separate erased-relative-unit path. The unused fallback contains a reference, not a relative-unit literal summary, so this case does not decide the unused-relative-fallback interpretation discussed below. The explicit parent lengths make exact computed px serialization appropriate. The same registration is intentional across independent elements; each fixture is removed, and no optional-precondition pass masks missing support.

Root's recorded ten-case baseline reports 3 FAIL / 7 PASS, while the broader thirteen-case diagnostic reports 4 FAIL / 9 PASS. The copied candidate gate records all ten scoped cases passing, all 183 prior checks passing, and the broader diagnostic at 10 PASS / 3 unchanged FAIL. Across the exact 217 paired rows there are four improvements and 213 unchanged outcomes. The broader diagnostic remains available: its three metadata failures are not waived or attributed to this collection repair. Root owns build/browser execution; this reviewer authenticates and reparses the retained evidence only.

Root-unit tests are not needed to establish the changed collector condition. A later rem/rlh test should use an isolated document root and calibrate the root's initial font/line-height, rather than assume the parent of an ordinary element supplies the root dependency. This review does not expand the runtime corpus.

## Metadata repair recommendation, separate from this patch

Preserve a summary of the **successful substituted token sequence** when storing ready universal/attribute values. Two reconstruction paths need the same invariant; repairing only the attribute path leaves universal chaining broken. Reusing a shared tokenizer to derive non-custom dependency flags from the output tokens is a plausible narrow approach. Do not blindly OR all old flags, since original summaries include unused fallback tokens. Do not compute relative units at the universal/attribute cache stage; their consuming property's context determines computation.

A correct implementation must handle escaped units, nested calc/functions, comments and strings without treating string contents as dimensions; preserve token boundary serialization, attr taint and URL/context provenance; and distinguish an already-computed typed value from a ready universal token stream. Occurrence-generated units and any other constructors of universal values need an explicit call-site inventory. This is a design recommendation, not an implemented or verified patch.

The unused-relative-fallback diagnostic remains **unadjudicated** as a normative defect. Substitution omits unused fallback evaluation, while the Properties API cycle paragraph speaks of a property containing relative units. Their exact timing relationship needs a settled oracle before changing all syntactic unit-summary behavior. None of the accepted four baseline failure expectations depends on that ambiguity.

## Substantive formal admission proposal

Do not call a Boolean proof that ATTR passes a filter a full graph-admission proof. A useful next companion should establish:

1. **Source declaration retention:** for each applicable winning non-custom declaration, collection retains its full unparsed value, originating longhand/shorthand context and every relevant non-custom node mapping. The pre-existing filtering/cascade/visited-style callers must supply the declared premises; attr-only declarations may not disappear before traversal.
2. **Selected dependency correspondence:** an independent guarded replacement evaluator and native-shaped visitor agree on the ordered active property/qualified-attribute reads, including missing/invalid primary, type eligibility, used versus unused fallback, and attr-valued var chains. Preparation alone must not imply an edge. The existing `can_chain` and parser/provider boundaries must be modeled or stated; collection does not prove the whole visitor complete.
3. **Unit-summary preservation:** ready universal/attribute storage has no unresolved substitution calls while retaining exactly the non-custom dependencies of its admitted output tokens. Show both reconstruction paths, inherited/universal values and typed computation separately. The current implementation violates this obligation, so it cannot be assumed for convenience.
4. **Cycle/publication composition:** connect retained declarations and selected reads to SCC invalidation and prioritary execution order: no typed length computes before required properties or before removal of a containing cycle. Either prove the actual graph algorithm/reset semantics or clearly identify those as premises; do not claim Tarjan correctness from an abstract graph example.
5. **Independent discriminating witnesses:** deletion of attr-only collection, erasure of output-unit flags, unconditional traversal of unused fallback references, and failure to invalidate a participating non-custom property must each alter an independent expected result. Finite browser matrices support source admission but do not replace these universal obligations.

This review supplies the source/oracle boundaries for that scope. It contains no new Lean proof, parser verification, universal CSS graph theorem, or claim that previous full cascade milestones are closed.

## Replay and inspected limits

The checker authenticates every source/spec/test/receipt before reading local executable review inputs. It verifies the exact three-line delta, equality with root native snapshots, exact patch-added WPT, immutable spec anchors, and recorded raw baseline outcomes. It does not compile Rust, run Firefox, or modify the production tree. The indexed Searchfox snapshot differs from local work and remains discovery-only evidence.

Inspected complete collector, preload, visit_value_references, visit_link/traverse, non-custom flag mapping, prioritary scheduling and the two universal reconstruction paths; relevant replacement/cycle/computed-value clauses; exact thirteen- and ten-case tests and root baseline logs. Not proved: whole parser/typed-value semantics, attribute observer effects/invalidation, allocator behavior, dynamic graph/SCC correctness, all shorthand and arbitrary substitution functions, or the candidate browser result. Absence of test metadata is not evidence of execution.
