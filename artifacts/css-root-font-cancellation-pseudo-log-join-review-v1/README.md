# Pseudo-node to animation-host log join

Source-only review of sealed instrumentation 4cee0e2fc3334a17d34453c0b4957716ae0ea7b197a36b255883d817fb309ab3. That package is unchanged. Searchfox discovery babb51/fc3408/94b460/df9be8/76f375 was checked against exact e86 Git objects in SOURCE.json (reads b92f0b/945bf1). No live native source, browser, build, or index operation occurred.

## Exact mapping

SequentialTask::update_animations stores the supplied element in SendElement; execute passes that same element to update_animations. GeckoElement::update_animations borrows that element's current primary computed style and calls Gecko_UpdateAnimations(self.0, before_change_values, computed_values_opt, tasks.bits()). No pseudo-host normalization happens on this Rust path.

Gecko_UpdateAnimations first checks composed-document membership and a dynamic pres context. It then calls AnimationUtils::GetElementPseudoPair(aElement). For a generated-content ::before container, the result is GetParent()->AsElement() plus PseudoStyleRequest::Before(). Ordinary elements return themselves plus NotPseudo(). With non-null computed style and the EffectProperties task bit, the function calls EffectCompositor::UpdateEffectProperties(aComputedData, element, pseudoRequest).

Consequently a Rust animation-task address can identify the generated-content node P while the C++ delivery node identifies host H and pseudo Before. Casting H to nsINode fixes C++ base-class address representation only; it does not make H equal P. The queued element's style is also read at sequential execution, not retained as the new style at queue creation (only before-change style is retained).

The existing child-decision event can show some parent/child relations, but is conditional on an ancestor-font hint and does not label pseudo type. It does not generally establish this normalization join. A missing address-equal delivery for P must not be interpreted as missing task delivery. An ordinary existing-child witness and the root-owned ::before witness remain separate.

## Small proposed addition, not applied

PROPOSED-LOG.txt contains one diagnostic statement immediately after the existing structured binding from GetElementPseudoPair in Gecko_UpdateAnimations. It records only the already available input element, normalized host, pseudo type, task mask, and computed-style argument. Node casts give a direct join to Rust opaque nsINode addresses. No second normalization call, getter, style flush, metric read, or task is added. This would be an extra GeckoBindings.cpp instrumentation source in a separately reviewed successor; no compiler check or patch application is claimed here.

Join within one unambiguous lifetime: Rust animation-task(P) -> normalization(input_node=P,target_node=H,pseudo=Before,tasks,style=S) -> C++ delivery(node=H,pseudo=Before,style=S) -> effect update on that target. The normalization event demonstrates the FFI call passed the early document/context guards, not that the EffectProperties branch necessarily ran. A null style returns before that branch; task bits must be checked. The existing delivery event establishes actual branch entry. Other callers can also invoke EffectCompositor; do not attribute every host/pseudo delivery to this path merely by its address.

This is not a unique invocation identifier: repeated identical tasks, pointer reuse and mixed-thread stderr can remain ambiguous. Preserve episode/process boundaries, target/pseudo distinctions and the existing requirement to reproduce the calibrated failure under logging. The proposed event is on the existing main-thread FFI path; it does not establish global order with worker logs. No broad tracing or identifier framework is proposed.
