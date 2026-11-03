# Selective descendant handoff: comparison candidate

This is a separate, uninstrumented source-only alternative to the sealed route-only proposal. It explicitly composes the pending validated font-unit membership/admission repair with the same traversal-local atomic handoff. It is not natively compiled, browser-tested, accepted, installed, or publication-ready. The route-only diagnostic proceeds separately.

## Exact source composition

Base: immutable e86b64866cdc5e2260ba9be08c45756fd96e21bb. `native.patch` is the cumulative four-file change from that base. `parent/` contains the exact `css-keyframe-font-unit-dependency-fix-v1` candidate (data.rs 17aaffd1 and traversal.rs 402165f9), with unchanged e86 Gecko traversal/glue. `PARENT-DELTA.patch` adds the handoff to that pending font repair. `COMPOSITION-HANDOFF-DELTA.patch` changes only the post-join glue block after applying the sealed font patch and then the sealed route-only patch. SOURCE-ROLES records full base/parent/candidate hashes for each file; REFERENCES pins both immutable parents. No logging or root-self identity fix is included.

The new post-join block iterates the actual traversal root's existing `traversal_children()`. For each element child with existing computed styles it inserts `RESTYLE_IF_AFFECTED_BY_WM_OR_ANCESTOR_FONT`. If at least one such child was seeded, it marks the root's normal dirty-descendant bit. All writes occur after `driver::traverse_dom` returns and its workers/thread-local tasks have completed. It does not alter root.hint or root style, walk/write ancestor flags in parallel, add a flush or metric read, query animation membership at the handoff, or remove the existing animation-only guard.

## Why the pending font repair is required

On e86 alone, a conditional ancestor-font hint can miss keyframe-only dependency because normal recascade inspects ordinary computed-style flags. The composed font patch additionally supplies `has_animations` to the normal conditional recascade predicate, and evaluates that membership only for a normal traversal carrying the ancestor-font hint. This is the exact previously validated repair, not newly invented dependency tracking. Omitting it is not an equivalent selective candidate.

The normal dirty bit admits the root but does not independently force its own cascade. Normal `note_children` examines the seeded children. Each nonempty hint makes that child traversable, even when fixed font values and no animations mean no style recomputation at that child. The ordinary hint propagation still forwards ancestor-font work to its children. Thus unanimated/fixed-font intermediates are visited and forward the work; animated descendants or ordinary font-dependent styles recascade. Existing `process_animations` schedules EFFECT_PROPERTIES for animation members during normal recascade.

| Boundary | Source behavior and limitation |
| --- | --- |
| Root-self | No new hint or style change on the traversal root. The dirty bit admits child processing only. Existing independent root hints may still request root work. |
| Publisher below traversal root | All styled immediate children are seeded, so an intervening unanimated branch is not missed merely because its old dirty route was absent. This is conservative subtree visitation, without unconditional subtree style recomputation. |
| Fixed/unanimated intermediate | Nonempty ancestor-font hint admits traversal and propagates even when restyle_kind is None. The composed font admission controls whether an eventual animated consumer recascades. |
| Generated pseudo / anonymous nodes | Uses the same traversal_children/as_element interface as normal note_children, not DOM children or pseudo-host guessing. The existing descendant route and Gecko target/pseudo normalization remain unchanged. Actual child and root ::before results must be validated separately. |
| No styled immediate child | No new normal dirty bit is set. No missing style data is allocated and no style getter is called. Existing dirty flags/work remain untouched. Initial/unstyled descendants are left to their existing lifecycle; this proposal claims only retained work for styled descendants. |
| display:none | Existing recalc_style_at clears descendant data when styling a node to display:none; the handoff then finds no styled child to seed. A styled display:none child can receive a hint, but normal traversal retains its existing subtree pruning. No discarded descendant data is recreated. |
| Ancestors above traversal root | Not modified. Servo_TraverseSubtree already invokes the following normal pass for this same explicit root. Normal note_children/post-traversal bookkeeping remain responsible for its processed descendants. An incorrect traversal root or out-of-subtree dependency is not repaired here. |
| Parallelism | No ancestor writes while workers run. Child hint writes and root dirty write occur sequentially after the join; all child-data borrows end before root dirty mutation. |
| FinalAnimationTraversal | Existing final cleanup does not remove the normal dirty bit or ancestor-font hints. Fresh font hints suppressed by finish_restyle's final-pass/first-style early return still cannot set the shared atomic: that separate limitation is unchanged. Final-only initial-style callers are not claimed covered. |

## Comparison with the route-only diagnostic

Both candidates visit the affected traversal subtree conservatively after an animation-only font signal and exclude forced root-self recascade. The route-only version needs no font-unit membership repair but forces every styled descendant to recascade, including independent fixed-font branches, on each qualifying animation font change. This version still visits those branches and invokes the existing conditional membership check, but can avoid their matching/cascading when they have neither relevant computed-style dependencies nor animations. It adds an immediate-child iteration after the join and the explicit dependency on the pending two-file repair. These are source-level cost observations, not performance measurements or proof of semantic equivalence.

## Validation and next decision

Actual focused source check **9eface / exit 0** verifies all four exact e86/parent/candidate hashes, forward/reverse zero-fuzz patches for base and font parent, reconstruction in the explicit font → route → selective-block order and reversal to base, Rustfmt parsing, six reference pins, and scratch removal. It is not a Gecko typecheck or scheduler test. No browser, native build, live source, Git/index, or canonical mutations were performed.

Reuse the exact unchanged eight-case WPT/resources in the sealed route-only package (its INPUTS and FILES are pinned); keep full unchanged34 and all controls. After the route-only diagnostic is measured, compare this explicit composed source against its own authenticated baseline and require the same first/settled results. Depth controls through fixed-font intermediates and a publisher below the traversal root, generated-content routing, no-work/no-child cases, and initial/final lifecycle behavior remain required before choosing a landing form. Preserve the independent root-self matrix; any root-identity repair composition must be separately named. No new runner or fixture is introduced here.
