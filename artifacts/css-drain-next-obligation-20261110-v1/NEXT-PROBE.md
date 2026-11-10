# Next actionable step

Keep #160 held. No further native drain experiment is justified by the inspected lifetime callsites alone. The missing architecture/refinement premises are:

1. An exhaustive cause classification for productive normal admissions, including finite initial work and any same-target lifecycle budget; the existing descending-phase theorem already handles its stated transition graph.
2. A lifetime boundary argument distinguishing strict-descendant data clearing inside traversal from DOM/frame/pseudo replacement in the outer restyle process. The number of producer functions is not a generation bound.
3. Native correspondence for coalescing and retirement over full target/pseudo/cascade/lifetime identity, including absent generated elements and replaced EffectSets. A removed queue key does not imply installed style.
4. A finite administrative-processing contract for queue selection, task execution and style installation. Pending eligibility and failed posting need explicit treatment.

A producer-local handoff alone already fails 27 of the acceptance callbacks. A hard cap silently weakens first-read behavior. Choosing a dependency-specific scheduler versus maintaining the combined global drain is now an architecture decision; neither choice is established merely by another finite passing fixture.

For useful independent browser work, start with the existing `web-animations/interfaces/KeyframeEffect/target.html` WPT, particularly these already checked-in callbacks:

- Change target from null to an existing pseudoElement setting target first.
- Change target from null to a non-existing pseudoElement setting target first.

They create a null-target keyframe effect for margin-left 0px→100px, set current time to 50% and assign the element and ::before target. The control creates generated content; the other leaves content absent. The existing WPT expects the pseudo's computed margin-left to change from 10px to 50px in both. Current metadata attributes the absent-pseudo failure to bug 1615083. Do not invent a new expected result or count a new bug before checking the current runtime and tracker.

If the pair still fails, investigate lazy pseudo style resolution, animation-rule inclusion and EffectSet::PropertiesForAnimationsLevel freshness. Root's fresh bug 1615083 review identifies comments 2–5 and the old animation-rule patch linked in comment 8 as relevant prior work. A nonexistent pseudo should not be forced through generated-element restyling; the posting early return is not independently evidence of a defect.

Record the logical target/pseudo, effect timeline progress, inclusion of animation rules in the lazy resolved style, current property sets used for composition, and resulting computed value. First authenticate the tracker patch and source path. Do not infer a repair from a failed generated-element lookup.

This optional surface is separate from #160 convergence. The immediate proof implementation is in NEXT-PROOF.md. No fixture was created or executed here; root owns the existing-WPT run and fresh tracker snapshot.
