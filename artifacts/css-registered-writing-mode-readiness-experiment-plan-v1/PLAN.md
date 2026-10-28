# Readiness outcome discriminator and next repair experiment

The saved zoom7-only source binding exactly matches writing-mode v3's original custom_properties.rs/cascade.rs bodies. Thus the early LH→ensureWM→recursive raw-provider substitution path already exists on the current source role. This is a source prediction, not an executed reproduction; no fixed number of failing tests is predicted.

| Readiness family (four cases each) | Expected source behavior |
|---|---|
| Literal writing-mode | Existing FONT/LH scheduling applies literal vertical before the mixed length computes |
| Literal registered keyword | Dependency-free provider is computed early; WM receives vertical |
| Used keyword fallback | Even premature recursive substitution yields vertical; no registered default is needed |
| Invalid registered provider | At risk if mixed length traverses first; safe if the provider is admitted first |

The specific risk signature is provider CSSOM vertical-rl but WM horizontal-tb and registered/consuming widths360/380/360 rather than220/240/220 across LH40/60/40. The provider correctly defaulted, but too late to repair WM. ProviderV/WMV with horizontal-axis length instead points to stale context during length computation. Providerbogus or an unexpected initial value challenges admission/defaulting itself. Inspect all saved snapshots before assigning a cause.

The old16 logical-axis fixtures use100vi-only values and lack FONT/LH scheduling in the original source. This readiness fixture intentionally uses1lh+100vi, which already invokes existing scheduling. Its failure therefore need not be caused by the absent new WM flag. In v3 the actual WM graph edge is processed after FONT and LH, so the same early publication remains possible. BaselineFAIL/candidateFAIL with identical snapshots is a held baseline limitation, not a v3 regression. BaselinePASS/candidateFAIL or changed unresolved snapshots is a candidate blocker. Only paired identical-input evidence can decide.

For the imminent32-case run, keep the16 readiness cases separate from the16 container-source controls and change neither fixture. If allfour risk cases pass, retain the source limitation: declaration/query order does not force native hash-map traversal. Only then consider a small fixed set of independent property-name pairs in a separate fixture to sample order, without claiming coverage of all schedules. If the risk signature fails, a minimal reduction removes100vi while retaining1lh: WM still should bevertical and the length40/60/40. This separates provider readiness from logical-axis scheduling without introducing a reciprocal dependency. Do not prepare that extension until actual outcomes justify it.

## Existing-ordering repair route

For a value that already has an actual WM contextual edge, visit that dependency before FONT/LH. In the acyclic witness, this allows WM's selected provider to be admitted/defaulted before the broad LH implementation prerequisite applies WM. It preserves graph edges rather than adding a synthetic LH→WM edge. This is the smallest v3-specific ordering experiment, not a complete solution:1lh-only values have no actual WM edge, and unconditional insertion recreates the fixed-LH false SCC. Reordering output requires updating the bitflags order probe/model expectations and replaying all mixed/fixed-LH controls; do not change source before paired evidence.

The full publication boundary needs actual provider readiness. `ensure_prioritary_property` sets its ensured bit before application; `apply_one_prioritary_property` also commits through seen.longhands and `did_apply_prioritary_property`, which updates builder.writing_mode. Merely moving the ensured-bit insertion or retrying later does not undo those side effects. If selected providers are still unadmitted, return an explicit incomplete/demand result before either publication path; resolve actual selected providers and retry. Do not feed raw recursive tokens into a registered consumer, turn incomplete into invalid, or replace readiness with synthetic SCC edges. Genuine vi/if()/style() cycles remain held observations.

Use the existing36 v3 controls plus the unchanged16 readiness controls in the later paired experiment. A zoom7 versus zoom7+v3 pair can isolate local behavior, but clean original0 versus v3's two native files is still required to establish standalone runtime validation. No accepted-bug or canonical coverage increment follows from this plan.

## Axis oracle

The pinned Values4 detailed vi definition uses “the box’s inline axis” at https://drafts.csswg.org/css-values-4/#vi; vb analogously uses the box's block axis. The summary table still contains root-axis wording. That inconsistent summary is not used to override the detailed definition. The fixture's independent literal vertical-rl calc control and fixed320x180 iframe test the actual assumption; a failing calibration must be investigated before attributing a registered-provider result.

Evidence: exact source-role join4c9360/0; prioritary publication path298f9e/0; pinned detailed vi/vb textba2761/0. No browser, native, staged file, Git/index, nested repository, or runtime epoch was changed. Only this short new artifact was written.
