# Bounded dynamic FontSize admission

The smallest proposed extension admits `font-size:var(--size)` when a locally selected, unregistered `--size` supplies one immutable absolute length. This is a source design against sealed f0d21a, not an implemented repair or browser result. The separate four-case probe remains unchanged and unobserved by this report.

## Existing route

`maybe_note_non_custom_dependency` records FontSize references. `TraversalFrame::PriorityReferences` walks them before FontUnits closes its semantic SCC and enters Publish. A plain unregistered `--size:20px` can finish through `start_frame`'s no-dependency return without allocating a custom node. Thus requiring a custom node index would incorrectly exclude this case; conversely `Complete` alone also covers a missing value and cannot certify an absolute length.

At Publish, `size_input_prefix_is_stable` rejects an eligible WithVariables declaration. Even without that rejection, `prepare_computed_size` calls `resume_font_selection` with no resolved reference, so it returns References. The caller then discards `size_preparation` and resumes the full ordinary path. Neither obstacle is solved by accepting a map lookup as ready.

## Proposed narrow change

1. Preserve the existing static checker for XTextScale, Zoom, XLang, MathDepth and minimum-font-size ratio. For FontSize alone, retain a selection continuation and an evaluated-prefix witness. Continue rejecting every encountered APPEARANCE_BASE declaration, including a currently skipped higher declaration. Preserve static rollback operations and priorities exactly.
2. At a reached dynamic declaration, initially accept only an exact single `var(--name)` without fallback, whose local unregistered leaf is an absolute length token with no functions or references. Capture provenance during custom declaration collection, before those declarations are discarded: the selected local leaf identity and whether **any** declaration of that name is APPEARANCE_BASE-gated. Reject gated names, inherited-only leaves and CSS-wide/rollback custom declarations for this initial narrow route. This conservative per-name inventory is a stability check, not a new dependency edge. Existing `Declarations` stores only longhands, so the proof cannot be reconstructed from that list at Publish.
3. Join the leaf with the completed reference traversal and exact current substitution-map value. A missing entry, SemanticOpen, ComputationPending or merely scheduled child is not sufficient. Bind the raw declaration Arc, FontSize consumer context, semantic session, flags, initial rollback/seen state and leaf identity. Keep this identity until facet retirement; a later mutation invalidates the preparation before publication. For the admitted plain local leaf, establish that no substitution or cycle operation writes it after its no-dependency terminal result. Do not generalize that argument to registered or alias values without their finality evidence.
4. Resume the existing `resume_font_selection` once with that exact resolved Arc. Retain its owned parsed operation and bookkeeping. Accept only its terminal absolute FontSize AST. An invalid substitution, Initial/Inherit/Unset, dynamic revert/revert-layer/revert-rule, percentage, em/ch/lh, calc or another unsupported operation must not create a facet. Dynamic rollback must not silently advance into lower declarations under a certificate that checked only the old prefix.
5. Make the executable prefix validator consume the retained result for that exact reached declaration, rather than running substitution again. Its terminal absolute result ends the checked prefix; a lower gated declaration remains unreachable and need not invalidate this FontSize prefix. Recheck the continuation's state and leaf provenance before applying existing XTextScale and FontSize hooks once. Keep the current demand-tagged ComputedSize reply: no whole FontSize/XTextScale completion, changed semantic edge, bypassed zoom/minimum-size input, or reset while partial.

The proposed API replaces the boolean preparation outcome with Ready, References (FontSize/raw Arc plus its bound consumer/session), Unsupported, or Invalidated. It reuses `ComputedSizePreparation.size` for the cursor, waiting Arc and retained operations. The frame must keep that state on References; the existing generic metric action allowlist does not admit FontSize and must not be extended by pretending the full generated dependencies are complete. The initial literal leaf can be authorized from the already completed PriorityReferences walk without launching a new child computation.

The unsupported result must retain or explicitly transfer its prepared operation to the ordinary path. Presently clearing `size_preparation` was safe only because admitted preparation was static. After evaluating a dynamic value, discarding and reevaluating it could repeat parsing/cache/random/attribute effects in a broader implementation. The initially restricted literal route avoids those volatile inputs, but retaining the operation is still the correct ownership boundary. No unsupported branch may be marked ready merely to avoid the current top-level Pending assertion.

## Distinguishing checks required before native use

| Input or mutation | Required evidence |
| --- | --- |
| Local `--size:20px`, then 30px; exact var FontSize | Resolve once, retain absolute AST, existing typed-attr probe reaches expected size/appearance. |
| Missing name, unresolved node, stale Arc or changed consumer context | No facet publication; map presence or old Complete must not authorize it. |
| Higher APPEARANCE_BASE FontSize currently skipped | Reject before evaluating the dynamic winner. |
| Lower gated FontSize below terminal dynamic absolute winner | Accept the FontSize prefix; do not scan unreachable declarations as dependencies. |
| Static revert-layer prefix followed by dynamic absolute winner | Preserve evaluated rollback trace and final winner exactly. |
| Dynamic var fallback producing revert-layer, unset or invalid syntax | Reject this narrow facet; never silently choose a lower absolute declaration. Broader support must check the newly reached prefix. |
| `--size:1em` unregistered, or registered length depending on FontSize | Reject literal admission; preserve existing semantic-cycle traversal, with no invented value oracle here. |
| Alias/attr/env/random or inherited-only source | Unsupported initially; no claim that their finality follows from a literal leaf. |
| APPEARANCE_BASE custom declaration for --size | Reject even if the current map contains 20px; no unseen selection-stability assumption. |
| Repeated polling and full ordinary completion | One substitution, one size/text-scale effect; generic and metric consumers remain Pending until their actual prerequisites finish. |

The sealed Prefix theorem currently handles static evaluation and explicitly rejects eligible dynamic declarations. It does not prove this proposal. A focused extension would replace a reached dynamic entry by its retained, identity-bound terminal operation, prove that the executable witness rejects every unstable reached decision, then reuse the existing visited/rollback/read-trace equivalence. Separate obligations remain for native declaration collection, leaf finality, consumer identity, substitution effects and the existing size readset. No new Lean or native code was added here.
