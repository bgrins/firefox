# Typed attr in fallback: bounded source investigation

Status: **UNEXECUTED browser hypothesis**, not an accepted browser bug or formal proof. No Git, browser, compiler, Mach or native/WPT-tree edits were performed. Only this artifact directory changed. The prior sealed namespace review is unchanged.

## Minimal witness and independent oracle

```html
<div x="13px" style="width:attr(missing type(<length>),attr(x type(<length>),5px))"></div>
```

The expected computed width is **13px**. The primary attribute is absent, so CSS Values 5 attr substitution's failure step substitutes its fallback. That fallback names existing x; its literal 13px matches <length>. The inner fallback 5px is not reached. No namespaces, custom properties, fonts or nontrivial layout are needed for this expectation.

Source prediction for both the frozen original and namespace-only candidate is **5px**: x was not loaded into the typed-attribute map. That is a prediction until root runs the proposed browser probe. Single typed attr(x) should work, and a separate height:attr(x type(<length>)) declaration should accidentally make the same width work by preloading x. This control discriminates missing preparation from parser/type support.

## Primary spec trace

Authoritative primary: https://drafts.csswg.org/css-values-5/#attr-substitution, with attr argument semantics at #attr-notation and #typedef-attr-name. The full HTML snapshot is authenticated from the preceding review, acquired 2026-10-19T15:28:26.897754Z; original retrieval URL/status/hash are retained. This turn's web tool also opened the current primary section. A direct shell HTTP refetch failed DNS; its failure is preserved and not represented as a fresh successful capture.

The algorithm first looks up the specified attribute. Missing attributes, unknown namespace prefixes and values failing the specified syntax take the failure branch. That branch substitutes the fallback's arbitrary substitution functions. Successful primaries return before the fallback is substituted. Typed attr values also substitute arbitrary functions in their contents before parsing. The normative oracle therefore treats declaration-local fallback, custom-property fallback and a fallback inside an attribute's text consistently. Computed absolute length equality is exact; the fixture does not rely on text metrics.

Unused fallback references must not introduce cycles. Existing attr-cycle.html tests this directly. The current CSSWG resolution associated with issue 11500 and bug 2051901 is retained in the issue audit; the proposed repair must preserve the existing lazy graph-edge rule rather than restore unconditional fallback edges.

## Complete relevant local source paths

Complete original and namespace-candidate versions of custom_properties.rs and cascade.rs are pinned under source/. They were authenticated from the sealed independent review, not refreshed from a moving working tree.

| Stage | Exact native function | Relevant behavior |
| --- | --- | --- |
| Parse | parse_declaration_value_block | Each fallback gets a separate References collection; only flags bubble to its enclosing reference list |
| Declaration collection | iter_declarations | Custom properties go through cascade_custom_property; ordinary declarations are noted and passed to maybe_note_non_custom_dependency as needed |
| Preparation | maybe_note_non_custom_dependency → update_attributes_map | Iterates only top-level refs.refs; skips non-typed references; never descends fallback.references |
| Root admission | cascade_custom_property, substitute_all final loops | Custom-property roots with references and explicitly seen typed attrs are traversed; arbitrary ordinary declaration values are not graph roots |
| Prioritary admission | maybe_note_non_custom_dependency, traverse(NonCustom) | Registered property dependencies can reach font/line-height/color-scheme nodes and their recorded declarations; being font-size alone does not imply traversal |
| Graph | visit_value_references | Can load a missing attr on demand and traverse the selected fallback when it considers the primary invalid |
| Substitution | substitute_reference | Typed ordinary attr reads the DOM, then requires a precomputed map entry; missing entry selects fallback even when DOM contents are valid |
| Final cascade | apply_custom_and_prioritary_properties followed by apply_non_prioritary_properties | Direct width cannot repair omitted graph preparation at final substitution time |

### A. Preparation gap

The parser intentionally separates fallback reference trees. update_attributes_map does not walk those trees. The ATTR flag alone only causes entry into the top-level loop; a var()/env() outer reference is skipped, and a missing/unknown typed attr outer reference cannot cause its fallback value to be traversed as an attribute-value root. Final typed lookup still requires a map entry.

This explains the direct missing/unknown primary, nested fallback, var fallback and env fallback cases. Missing known namespace and unknown prefix are included to show this is independent of qualified-key collision. No test has two distinct existing namespaces with the same local attribute name.

Custom-property --result roots should exercise the lazy graph and succeed for a missing primary: visit_value_references follows the now-used fallback and populates x. An attribute whose literal contents contain the missing-primary expression is another admitted graph root and should succeed. These are disconfirming controls, not assumptions silently replacing execution.

A plain font-size declaration with only attr references causes an early return after update_attributes_map; applying it as a prioritary property later does not itself walk the fallback graph. A separate registered length --preload-trigger:1em creates a font dependency; including var(--absent,...) in the font-size fallback ensures the non-custom declaration was recorded for traversal. That explicitly admitted graph control should compute both font-size and --preload-trigger to 13px. The WPT asserts both outputs, so merely parsing @property without registered dependency behavior cannot pass unnoticed.

### B. Fallback eligibility gap reached through a custom-property root

`--result:attr(bad type(<length>),attr(x type(<length>),5px)); width:var(--result)`, with bad="not-a-length" and x="13px", is a separate discriminator.

The graph's `primary_valid` logic considers a resolved universal token value with no references valid. It does not apply this attr reference's requested syntax. The primary's value can therefore be considered valid while the eventual substitute_reference rejects it as a length. The fallback attr x was never traversed/prepared. Source prediction: 5px rather than 13px even though the custom-property graph root was admitted.

A recursive non-custom preload-only patch would not fix this custom-property route. It requires actual used-fallback eligibility to agree with substitution, or a carefully reviewed broader preparation strategy plus correct cycle edges. This is separate from the other agent's finished-SCC/tombstone-reload investigation; no duplicate repeated-reference witness is added here.

## Probe and controls

`attr-fallback-preload.html` is a self-contained WPT candidate containing 19 cases and no extra resource besides standard testharness scripts. It belongs under css/css-values when root chooses to run it. CASES.json records normative expected values and separately labels static predictions; the HTML includes only normative assertions. All cases remain UNEXECUTED in this artifact.

The probe uses unique stylesheet ID selectors so qualified names resolve in stylesheet namespace context. It reads back all literal attributes, verifies all asserted properties parsed, fixes parent font size and containing width, and compares the complete computed output vector. It has no optional-support exits. Controls include direct typed attr, same-expression cache warming, numeric-unit inner attr, graph-root admissions, used and unused custom-property cycles, and an unused registered-property cycle through font-size.

The simplest witness is the second case. The last case distinguishes B from A. Keep these separate in triage: a shared result does not prove a shared repair. The rest of the fixed cases are boundary controls; do not broaden the matrix until an actual discrepancy demands it.

## Bounded prior-art and WPT review

Fetched via moz Bugzilla provider in this turn:

- Bug 2009001 (resolved): added recursive typed attr resolution. Comment 2 explicitly discusses pre-parsing references before prioritary substitution and the differences from fallbacks. Related architecture; no exact duplicate conclusion.
- Bug 2021110 (new): namespaced chained references. The minimal null-namespace witness does not need that missing namespace context.
- Bug 2014060 (resolved): namespaced attr syntax/lookup. Not the minimal witness's issue.
- Bug 2021155 (resolved, inspected through linked issue history): property graph redesign. It notes cycle/substitution separation as remaining complexity. No regression range is claimed.
- Bug 2051901 (resolved invalid): rollout discussion for unused-fallback cycle semantics. Confirms the intended lazy branch constraint; not evidence that our preload witness runs.
- Bug 2026785 (resolved): propagation of invalidity through registered/unregistered properties; related but different scenario.
- Bug 2051770 (resolved): Servo compilation after graph changes, rejected as unrelated.
- Search hit bug 2067875 contains “attr() fallback substitutes locally”; inspection shows CSS mixin function-local binding tests, rejected as the same defect.
- Search hits bug 2006626 (invalid type grammar fallback) and 2034337 (pseudo-element style sharing) are related wording, not evidence of a duplicate. Their titles/summary were inspected via primary Bugzilla search results; full comments were not exhaustively reviewed.

Web searches were bounded to Bugzilla attr/fallback and Stylo; one unrelated-heavy query did not establish novelty. Direct Bugzilla REST search failed DNS. No exhaustive issue search or novelty claim.

Searchfox CLI discovery identified update_attributes_map and existing attr tests; a later full parser request failed DNS. The web Searchfox view indexed revision e2c1c288 dated 2026-10-09 shows nested fallback References too, so that parser shape is not inferred solely from our local experimental cascade. This is a bounded upstream check, not a complete upstream byte comparison or regression identification.

Inspected existing WPT: attr-all-types.html mostly tests direct attr and chains *inside attribute values*; attr-cycle.html covers many selected/unused fallback cycles mainly through custom-property roots; attr-namespace-non-existing.html uses a literal fallback. Their complete local files and available metadata are copied. No execution is inferred from absent metadata. None of these files is claimed to exhaust the fallback-preparation surface.

## Suggested native repair scope

First reproduce A and B independently. For A, a small candidate is a worklist over nested References in update_attributes_map, descending fallbacks of every substitution kind before skipping non-typed primaries. It must preserve qualified seen keys from the namespace repair and populate independently parsed attr values without adding unconditional graph edges to the caller. A SmallVec/reference worklist avoids introducing native recursive call depth. Do not flatten parser reference structure: that would regress unused-fallback cycle selection.

Eager preparation is not the same as eagerly following graph dependencies. Its costs include additional DOM reads, parsed values and attribute-tracker invalidation dependencies even for unused fallbacks. The gate must keep unused cyclic attr, custom and registered-property controls passing. It also cannot claim to repair B, because custom-property values do not call this non-custom preload routine.

For B, factor or reuse the actual attr substitution eligibility decision when deciding fallback edges: missing/unknown/invalid type/unresolved-cycle states differ. Token text existing in the map is insufficient. A syntax check must use the same parser options, type/unit/raw distinctions, namespace and computational-dependency admission as final substitution. Do not manufacture a generic “has map value” validity flag or resolve properties out of dependency order. A lazy shared resolver/preparation API could be cleaner but is larger than the first preload change and needs separate review.

No native candidate is authored here. Both suggested changes need normal root-owned browser/source pairing and regression gates. Full Tarjan correctness, cache tombstone semantics, DOM mutation scheduling, style sharing, parser/OOM and container-query paths remain outside this bounded scout.
