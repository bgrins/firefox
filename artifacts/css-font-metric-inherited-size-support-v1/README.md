# Percentage and inherited computed-size support boundary

Source-only follow-up to the f0d21abe absolute-size certificate review. The current producer does not admit these forms. No new native implementation, extracted execution, browser result or accepted fix is supplied here. Future implementation is warranted only by actual browser evidence and must retain native conversion and effects.

## What can be stable

| Input | Candidate narrow support | Necessary distinction |
| --- | --- | --- |
| Explicit percentage, including 100% | A completed, fixed parent with keyword_info.kw == None; stable selected input prefixes and final Zoom/XTS state; actual FontSize percentage conversion and hooks | Percentage scales the inherited computed size and composes parent keyword metadata. It does not behave like a literal absolute AST or independently text-zoom the resulting percentage branch. Use the native quantization, not hand multiplication. |
| Explicit inherit / unset | The same keyword-free parent and stable input prefixes; simplest first scope is inheritance zoom == 1 and unchanged parent/child text-scale policy | At unit zoom, apply_one_longhand marks FontSize seen but can skip its setter. At nonunit zoom, the generated helper takes the inherited computed value, reconstructs a specified value and converts it with the inheritance zoom. Do not replace this with the percentage path. |
| No reached FontSize declaration | A distinct certificate of effective absence after the full applicable rollback/eligibility chain, a keyword-free inherited builder value, stable inputs, unit inheritance zoom and unchanged text-scale policy | No fresh setter, seen bit or FontSize hook may be invented just to reuse the absolute certificate. A root/default-style source is not necessarily keyword-free. |

These are necessary conservative conditions for a future bounded route, not a completed sufficiency proof or implemented policy. The one computed context, parent style, device inputs and declarations must stay fixed; stronger metric/line-height consumers still require their own completed work.

## Why generic percentage/inheritance is unsafe

FontSize::to_computed_value_against composes the parent's keyword_info for a percentage. KeywordInfo::compose retains None, but otherwise multiplies keyword factor and offset. Inherited font structs and copy_font_size_from retain keyword metadata too. recompute_keyword_font_size_if_needed later recomputes non-None metadata in the child context. FontSizeKeyword::to_length reads the child's current generic family and language-specific configured base size.

Consequently a parent with medium-derived size and a child with 100%, inherit or no FontSize declaration is not generally final before the child's Family/XLang work. A concrete source-level counterexample shape is a parent with medium/serif and a child whose family later resolves to monospace, on a document whose calibrated serif and monospace keyword sizes differ. The earlier parent's number and later child keyword recomputation differ. This is a proposed discriminating scenario, not an observed browser result; do not assume default OS or preference numbers. Math-derived metadata is another reason to reject a blanket inherited rule.

The computed default FontSize::medium carries KeywordInfo::medium, and specified initial medium is a Keyword AST. Neither is equivalent to a fixed parent absolute size. An omitted declaration may inherit a keyword-derived parent, or derive from the root's default style. Conversely, an inherited completed system-font value may be keyword-free; that does not authorize early selection of a new system-font declaration. FontSize::System reads cached_system_font, and generated application first resolves that system font. Keep selected system-font declarations outside an initial percentage/inheritance extension.

## Zoom and effect obligations

FontBaseSize::InheritedStyle reads the fixed parent's FontSize and applies effective_zoom_for_inheritance. FontSize::zoom preserves keyword_info. A percentage then scales that value and quantizes it; the branch does not call maybe_zoom_text again. The child's XTS hook can separately unzoom inherited current-builder fields before FontSize selection. Therefore neither multiplying the already-mutated current builder nor treating 100% as explicit inherit is a faithful replacement for native conversion.

Explicit inherit is seen. At unit inheritance zoom the inherited-property fast path may skip a setter; at nonunit zoom helpers.mako.rs reconstructs the parent's computed value via FontSize::from_computed_value (an absolute-length AST), temporarily uses inheritance zoom, and recursively converts. Its metadata/effect behavior can differ from percentage conversion.

Omission remains unseen. apply_non_prioritary_properties later calls recompute_zoom_dependent_inherited_lengths for nonunit inheritance zoom, and generated FontSize belongs to that set. That late sweep can invoke the inherit conversion after a hypothetical early consumer. Thus keyword-free parent metadata alone is insufficient to certify omission under nonunit zoom. Either prove/account for that later native write with exact effects, or exclude it initially. This hazard does not invalidate the current f0d absolute route, which marks FontSize seen and suppresses duplicate XTS/FontSize application.

No omitted route should fabricate an XTS hook when its declaration is absent. A first conservative route can require final parent/child text-scale policies equal; supporting an actual disable transition needs exact native unzoom ordering and replay suppression. Minimum-size clamping affects used mFont.size, whereas registered em consumes computed mSize; retain actual hooks and test that distinction rather than copying the used minimum into the custom value.

## Necessary controls before widening native support

1. Fixed absolute parent at two sizes; child 50%, 100% and 150%, with custom em read first and a same-style literal em reference.
2. The same fixed parent with explicit inherit, unset and true omission as separate cases; do not implement one by rewriting another.
3. Calibrated keyword parent + different child generic family, and a language-dependent variant when configured sizes demonstrably differ. Require rejection/deferred completion or correct final value, never an early parent-number certificate.
4. Root/default medium, explicit initial/medium, system-font declaration and Math-derived parent negatives; a completed keyword-free system-font parent is a separate case.
5. Unit and nonunit own CSS zoom; specifically leave FontSize unseen for omission and compare before/after the late inherited-length sweep.
6. Text zoom enabled versus a real XTS disable transition, unchanged policy, and absent XTS declaration. Observe exactly-once effects and final numbers; do not assume OS text-zoom settings.
7. Parent zero and nonintegral percentages/sizes to exercise native normalization/quantization; minimum-font preference controls compare computed em with used metrics separately.
8. Higher ineligible Appearance-base entries, actual rollback chains and genuine absence after rollback; lower losing declarations must not become artificial dependencies.
9. Dynamic child Family/Appearance resumption and an additional later custom consumer; preserve exact semantic closure, typed demand, deferred ordinary completion and reset obligations.

All controls are proposals, not run results. The existing finite protocol/prefix models do not establish these native numeric/effect conditions. The separate full 21-case pair and unsupported-form browser diagnostics remain the runtime authorities.

## Evidence

Searchfox receipts: percentage/compose 6f743c; computed zoom/default 347c93/8f8a70; keyword readset 2537a5; inheritance helper 001970/fd830d; from_computed_value fa0ba2; generated zoom membership 4db00d; system branch 96eebc. Local exact excerpts and hashes are saved in SOURCE.json/REFERENCES.json. No live state was changed.
