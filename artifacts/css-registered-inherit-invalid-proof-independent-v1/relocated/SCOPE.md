# Scoped explicit-inherit admission

This component models only the selected `CSSWideKeyword::Inherit` route through `Cascade::value_may_affect_style` and `Cascade::cascade_custom_property`, after priority/revert/seen filters admit that declaration. It is not a whole-cascade or tokenizer proof.

The input store has inherited and reset maps, optional values, an incoming INHERITS_RESET_STYLE bit and arbitrary other flags. None represents the selected-map getter's guaranteed-invalid absence, not a concrete C++/Rust allocation layout. Values remain abstract and may carry arbitrary representation/URL/taint data.

Admitted native representation premises: the selected entry is seeded from the actual parent for inherited properties on nonroot elements and from the computed registration initial for roots/reset properties; root parent maps are empty; selected registration/name/stylist and root status are coherent; native getters/clones/map mutation implement the abstract Option store; ordinary control completes normally. Source inspection supports these premises but the component does not prove cache freshness, scheduling, heap/compiler, full custom-map reuse, unrelated seen-state or caller filter semantics.

Required results: corrected selected value equals independent root-initial/nonroot-parent expectation; unrelated names and bucket preserved; arbitrary other flags and existing true reset-inheritance bit preserved; characterize the exact reset-inheritance bit including the root/no-initial branch; show the original nonroot absent-parent counterexample and independent necessity of each changed site; show root-skip overcorrection and dropped flag mutation rejection. Source bindings include complete native functions and exact original/proposed patch. No numerical/token payload equivalence is assumed.

Producer WPT proposal v2 had a cleanup callback returning removeProperty's string; root detected this after proposal freeze and is correcting final runtime files separately. Its syntax-only check was not a successful browser gate. This proof does not use incomplete candidate browser outcomes as evidence.
