# Computed-size progress for the variable typed-attribute case

Safe dynamic Appearance/Family preparation is necessary but does not finish the first case: its selected attribute primary still waits for registered `--len:1em`, while the generated chain waits for Appearance. The native diagnostic establishes this no-action size-readiness state, not actual computed property values. This is a concrete next-boundary proposal, without a patch, new model or executed test.

## Supported operation and actual reads

Prepare the selected FontSize declaration before traversing the full generated scheduling list. Initially recognize a retained `FontSize::Length(LengthPercentage::Length(l))` only when `l.to_px_if_absolute()` succeeds. This covers absolute units, not particular test constants. A dynamic declaration can qualify only after its exact selected-reference continuation yields the owned AST; retain rollback reads and do not substitute twice. The semantic FontSize SCC must close normally before issuing readiness.

Actual conversion initializes keyword_info to None for this branch. Later Family/XLang keyword-size recomputation returns immediately for None. This supports a narrower read set, but does not waive effects:

1. Finish selected Zoom and XTextScale, including their references and eligibility. Keep XLang, MathDepth and minimum-size ratio explicit. Replace XTextScale's Family ordering requirement only under this retained operation's certificate, not globally.
2. Apply final XTextScale and run inherited-font unzoom **before** fresh size publication. Deferred unzoom could transform the newly computed size again.
3. Use real property conversion, effective zoom, applicable text zoom, quantization and size hooks. Do not hand-calculate pixels or transplant registered-value conversion context.
4. Expose final computed size only to the appropriate unit consumer. Resume `len`, its exact attr primary, Appearance and Family through owned selected consumption. Metrics still need final font/family/weight/orientation inputs.

`Gecko_nsStyleFont_ComputeMinSize` reads the zero-size condition, XTextScale's policy, language-dependent document preferences and minimum-size ratio. Preserve those inputs and its zero-size early return. `constrain_font_size_if_needed` modifies used `mFont.size`; em reads computed size. This distinction does not authorize skipping the hook or claiming metrics ready.

## Facet, node and ordinary completion remain distinct

The current shared `NonCustom(FontSize)` node uses `ClosedValue::Prioritary`, and Complete means ordinary ensure succeeded. Do not silently weaken that contract. Introduce an explicit computed-size certificate and demand-tagged unit-read reply, while retaining semantic-SCC closure separately. Only a caller requesting that facet may consume it. Generic `visited`, ordinary ensure, stronger demands and custom/attr reference walks must not see generic Ready from a partially fulfilled node.

Keep the certificate in the outer shared ledger, bound to exact selected operation, context and input generations. Later ordinary finalization closes remaining ordering obligations without applying size or unzoom twice. `publish_closed`, frame replies and reset/retirement need explicit handling: retain unresolved continuations, or retire a closed session only after transferring its certificate and proving no caller retains its indices. Do not weaken reset assertions to lose pending work. Test that the computed-size caller can proceed while ordinary/stronger callers remain Pending, and that marking the whole node Complete is rejected.

The staged preparation currently requires full generated prerequisites before selecting an AST, and its publication gate checks them again. Both gates must consume the same retained-operation certificate. Changing one gate or the terminal assertion is insufficient. The ownership successor's shared ledger/Prepare identity supplies handoff points, but enabling Appearance/Family alone does not solve size progress. Begin this bounded size selection before creating a waiting Appearance action, rather than replacing an already-owned action.

## Eligibility before final Appearance

Accept only a reached selection prefix whose decisions are independent of the unresolved flag. If a higher candidate was skipped because APPEARANCE_BASE is absent, keep Pending. Also reject unresolved eligibility reads in substitution or rollback decisions. Stop the prefix at the first retained non-revert winner; lower declarations cannot displace it. The application/tweak read set must be independent too.

The diagnostic does not contain this prefix, so it does not prove the actual first case qualifies. Inspect it rather than assuming eventual Appearance none. A later flag change cannot invalidate an already-consumed value: either recorded decisions/read sets prove independence, or early publication was impermissible. Blanket completion reset is not proof. Existing stability/publication models state related premises abstractly; they do not prove this native certificate.

## Counterexamples and validation boundary

- A higher Appearance-base-only declaration becoming eligible defeats a winner-only classifier. Require an extracted rejection test for that prefix.
- Deferred unzoom can corrupt the fresh size. Exercise effective zoom and text-zoom disabling with inherited and fresh fields.
- Keyword, percentage/em inheritance, smaller/larger, system/math, no declaration, Initial/Inherit/Unset and invalid/default operations lack the absolute branch's None-keyword guarantee. Keep the full path until separately classified. Include zero/minimum-size and default/inherited controls; unsupported is Pending, not ready.
- A `1ch` consumer can see the wrong font despite correct size. Preserve stronger metric/alias demands; do not make scheduling links CSS cycle edges.
- Retain all 21 callbacks in fresh paired validation, especially raw `var(--len)` in the typed attribute. Passing literal/missing controls alone is not the fix. No new test result is claimed here.

## Spec boundary

Current [Values 4](https://drafts.csswg.org/css-values-4/#font-relative-lengths) bases em on computed font-size and distinguishes metric units. [PVAPI](https://drafts.css-houdini.org/css-properties-values-api/#dependency-cycles) supplies the registered em→FontSize dependency; literal font-size supplies no reverse custom-reference edge. [Values 5](https://drafts.csswg.org/css-values-5/#attr-substitution) resolves attribute substitutions and requested type before deciding fallback. These support the existing oracle, not Gecko's scheduling or this proposed certificate. A successfully substituted length reaches Appearance grammar invalidation; Appearance rejecting it does not by itself select attr fallback.

Exact source excerpts and primary references accompany this note. No native source, application, runtime, index or canonical state changed. True metric feedback policy remains open; this is not a completed repair.
