# Generated priority readiness: bounded repair design

This is source investigation against the frozen a6f4 candidate, not an executable repair, a native result, or a promotion recommendation. The current portable pair is uninstrumented and independently owned by root. This package neither reads its live outputs nor changes any source. The separate literal-attribute cache isolation proposal does not resolve the active-property problem discussed here.

## Concrete distinction

The admitted generated dependency table mixes value dependencies with ordering constraints. It documents XTextScale → FontFamily as ordering keyword-size recomputation before text un-scaling. FontFamily → Appearance exists for Appearance-base eligibility. Meanwhile the candidate's selected traversal already asks for Appearance when a reached eligible declaration needs that flag. Ordinary `ensure_prioritary_property` does not inspect that graph ownership: it sets ensured, recurses through the generated list, and applies an ordinary declaration. `apply_prepared_priority` uses that route before applying its retained declaration chain.

The discovery captures make the actual reads more precise. `FontSize::to_computed_value_against` computes an absolute length and then calls `maybe_zoom_text`, which reads the current XTextScale. A keyword instead reads current family and language through `FontSizeKeyword::to_length`. An em consumer uses the computed font size; ex/ch consumers query font metrics and used size. Thus literal pixels do not justify skipping text-scale, and computed-size readiness does not establish metric readiness. These upstream bodies were read at Searchfox revision 86136a; their equivalence to the local native branch has not been authenticated here.

## Minimal operational direction

The first boundary should be one selected-declaration consumption path for graph and ordinary callers. Its result must distinguish **ready** from **not ready**, without treating the latter as missing attr, invalid-at-computed-value-time, or a semantic CSS cycle. Only actually reached declarations prepare their attributes; raw values with references require the selected reference traversal, not a cache-presence shortcut. A graph-active property cannot be applied by the ordinary fallback route. Neither ensured nor seen may advertise successful final computation before that computation completes.

That guard alone is insufficient: a generated dependent cannot continue using builder defaults after it receives not-ready. For the observed source-shaped font route, the smallest concrete dependency redesign worth evaluating is:

1. Resolve XTextScale's actual selected declaration and its actual var/attr/eligibility reads. Do not require FontFamily merely because of the current generated ordering entry.
2. When XTextScale is final, apply it and run inherited-font unzoom immediately, **before** calculating a fresh FontSize. Do not queue unzoom until after the fresh size is published.
3. Resolve the other actual FontSize inputs, including Zoom and applicable math/default operations. Determine whether the selected/default font-size operation can later be changed by family or language. If it can, close those actual reads before exposing FontSize to custom-unit conversion; otherwise the FontSize computation can finish without publishing Appearance through the conservative family chain.
4. Resume the suspended attr/Appearance selection using that final size. Only its final selected declaration publishes Appearance/eligibility. Family and remaining priorities then complete through the same selected consumption path, not an ordinary bypass.

This is a design of the required successful route, not a complete scheduler algorithm. If a prerequisite is itself graph-active or has unresolved selected references, the caller must remain pending without publishing. A rule for completing or invalidating every such scheduling wait is still missing. The existing semantic SCC graph should retain actual custom/attr/selected-eligibility dependencies; inserting every generated scheduling link would reintroduce false cycles.

The corresponding proposed edit sites are `Context::apply_prepared_priority`, the call sites of ordinary `ensure_prioritary_property` while the graph is live, and the documented XTextScale → FontFamily scheduling entry. They require a readiness result and retained continuation, not an early-return-as-success. No patch removing that entry in isolation is supplied: it would let keyword/default FontSize consumers observe a value later changed by FontFamily.

## Why eager text-scale is different from deferred fixup

The frozen `unzoom_fonts_if_needed` invokes `unzoom_fonts` on the current font struct. The discovery implementation changes all of mSize, mScriptUnconstrainedSize and mFont.size. Deferring it until after computing FontSize with the new text-scale would unzoom newly computed values. Eager unzoom avoids that particular double adjustment. Later keyword recomputation already reads the new text-scale through `maybe_zoom_text`; it does not simply copy the old computed size. KeywordInfo carries factor and offset, and its conversion applies text zoom to keyword length and offset. These bodies provide a plausible reorder route, not proof that all font bookkeeping commutes.

## Counterexample to classifying FontSize alone

The frozen custom-property provider groups em, ex, ch, cap and ic into the same FONT_UNITS flag, and maps FontUnits to FontSize. This loses the distinction needed by the proposed narrower scheduling route. Consider a registered length `--len: 1ch`, a final literal `font-size: 20px`, and a separately selected `font-family: monospace` that has not yet been applied. Removing XTextScale → FontFamily and declaring the absolute FontSize ready could allow the custom value to compute using the old family. `query_font_metrics(CurrentStyle)` passes the current complete font and used size to the device. A later final monospace family cannot repair the already-computed custom length. Different glyph metrics are an explicit premise; this is a source-supported counterexample to the shortcut, not a reproduced browser result.

Consequently, the smallest defensible continuation of this design has a further concrete edit: preserve **computed-size demand versus metric demand** from the custom-value unit inventory through the resolver. This must preserve existing fallback/cycle policy rather than silently resolve the separate unused-unit question. Keep the existing semantic FontSize graph identity initially; a readiness facet must not itself invent a new CSS cycle edge. A computed-size-ready result is sufficient for em, but not ex/ch/cap/ic. A metric request must additionally close actual selected font and writing-mode reads before conversion. Unknown or mixed demands require the stronger readiness. This likely needs a separate readiness bit/facet rather than treating the existing ensured bit as both contracts.

That is a concrete proposed source boundary, not a finished implementation: propagating demands through aliases, defaults and attr, handling later stronger demand, and resolving scheduling waits against active graph nodes remain to be defined. No one-line dependency deletion, FontSize-AST classifier alone, or literal-cache setup is an implementation-ready full repair.

## Specific unresolved implementation obligations

Family-read classification cannot be a literal-only whitelist or `kw != None` test applied after premature computation. The selected operation includes rollback exhaustion/no declaration, Initial, Inherit, Unset and invalid substitution. The retained/inherited initial font may carry keyword provenance. Inherit/Unset also have an effective-zoom-dependent non-skip path in the existing application helper; that path must be classified without assuming every inheritance operation is a no-op. In the discovered conversion, em, percentage, smaller and larger compose parent keyword information; calc and system branches have different behavior; math uses inherited metrics and own MathDepth/text-scale, and its later hooks need separate treatment. These cases must be classified before declaring the value final.

XTextScale itself can contain selected references or require an eligibility flag. Removing its Family ordering does not make its inputs final. Zoom, min-size and math hooks also have mutations or dependencies; retaining an ordinary ensure for those paths cannot silently bypass the same ownership rule. Used-font metrics require more than the computed em size. A blanket generated-edge SCC, a cached-ready-var restriction, or final flag clearing cannot substitute for these obligations.

The proposed route must also preserve the selected chain's skipped-prefix decisions, evaluated rollback reads, owned substitution/tweak result, forced-color adjustment and final default publication. The sealed Publication model states these premises abstractly; it supplies no native continuation or dependency classifier.

## Concrete validation boundary

Before any repair is accepted, use the existing portable four and Mozilla five controls, plus selected XTextScale references/eligibility, zoom-disabled inherited and fresh size cases, keyword/default/inherited font sizes, metric versus em consumers, and genuine custom cycles. Record the candidate's complete observations, including changes inside an already failing callback. No new tests or browser execution are supplied here, and the current pair is not changed.

Seven exact local source excerpts and seven upstream discovery captures are pinned by `SOURCES.json`. The source inspection distinguishes a plausible small font-ordering change from a complete coherent-consumption repair. The latter remains unimplemented; this package does not authorize native publication.
