The source mapping uses immutable candidate files authenticated by REFERENCES.json. It is an explanatory correspondence, not extracted Rust or a refinement theorem.

| Model | Native proposal | Explicit boundary |
| --- | --- | --- |
| signal | RecalcStyleOnly::needs_normal_descendant_restyle, set when animation-only recalc_style_at returns the ancestor-font child hint | Actual signal detection, worker join and relaxed atomic visibility are outside the Lean model. |
| broad / descendantHint | Broad glue traversal post-join insertion of RECASCADE_DESCENDANTS into the returned root data | entryGate projects this nonempty hint into the existing normal gate; no source-level bitset equivalence is proved. |
| selective / children / seed | Selective glue traversal_children loop, element/data/has_styles checks, and ancestor-font insertion | Child.hasStyles summarizes all three eligibility filters. The supplied list must be the correct traversal-root children, including eligible pseudo nodes. |
| selective / normalDirty | set_dirty_descendants only after at least one styled child was seeded | This is the root normal channel, distinct from animation-only dirtiness. Missing-data and unstyled children do not seed it. |
| selfHint | An independent root-self restyle request | Neither modeled operation adds this request. Existing native hints can still require self restyling; the theorem does not prohibit that. |
| normalEligible / enter | Gecko element_needs_traversal and pre_traverse | Exact Entry model is imported. Eligibility is evaluated after handoff with its flags intact; native lifetime/retirement preservation is an external premise. |
| forwardAll / route | Existing Route executable dispatch model | Correct route, per-hop forwarding and route.length dispatches before observation are stipulated. Native recascade, UPDATE_EFFECT_PROPERTIES, UpdateProperties, conversion and installation are not modeled. |

Broad native source is the standalone e86-based proposal6e00efb6. Selective8c89d437 explicitly composes the pending font-unit membership/admission repair: animated keyframe-only consumers can be eligible even without ordinary style-unit dependencies. The Lean entry proof does not establish that consumer predicate or its native implementation.

For fixed-font unanimated intermediates, the selective proposal retains nonempty ancestor-font hints and relies on normal propagation to forward them; broad recascade visits/cascades the entire styled descendant subtree. Both can admit the root without adding a self hint, but the model does not prove either native forwarding path. Pseudo/host normalization remains an independent Delivery obligation, not an equality inferred from node addresses.

No-styled-child behavior is intentionally conditional: selective supplies entry for signal AND at least one eligible child, and otherwise leaves the snapshot unchanged. This does not establish completeness for unstyled or out-of-subtree work. Fresh hints suppressed during FinalAnimationTraversal and initial styling remain outside both signal premises; a final-pass flag is not introduced in this model.
