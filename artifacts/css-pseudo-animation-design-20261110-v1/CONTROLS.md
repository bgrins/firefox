# Bounded controls for a candidate

These are proposed tests, not executed results. Extend the existing underlying-value fixture where practical; avoid a Cartesian product.

| Group | Minimal control | Failure distinguished |
| --- | --- | --- |
| Existing admission | Existing target WPT; preserve unrelated placeholder expectation | Identity/retarget semantics versus unsupported pseudo |
| Existing base controls | All nine existing cases, both generated and missing pairs | Implicit base, changed base, important precedence, cancel, transform toggle |
| CSSOM cache | Retain one CSSStyleDeclaration, read before animation; add animation; seek twice without DOM mutation; cancel; add again | Cached raw style before admission, stale animation sample, stale result after removal |
| Fresh property membership | Same retained declaration; setKeyframes from margin-left to opacity; retarget to another origin | Reuse of cached effect properties or origin identity |
| Composition | Two paused effects on one absent pseudo: lower replace and higher add with an implicit endpoint; change underlying value | Fresh base map versus previous composed value; composite order |
| Cascade levels | Retarget a retained transition to the pseudo if supported by existing API, combine with an ordinary animation of the same property; important rule control | Incorrect transition filtering or skip-mask union; do not fabricate a CSS transition on a nonexistent pseudo |
| Current context | One inherited font-size change with an em endpoint, one registered provider/consumer endpoint case, one attr-dependent endpoint update | Fresh base alone may not imply correct endpoint dependencies |
| Normal traversal isolation | Read missing transform pseudo, generate it, read/render, remove it, read, regenerate; also run identical sequence with CSSOM reads omitted | Transform hints, stale compositor state or pseudo cache publication induced by query |
| Query identity | Before and after with different bases/effects; a supported marker case; ordinary element control | Accidental pseudo retargeting, missing property restrictions |
| API exclusions | Disconnected origin, default-only internal caller if unit-testable, non-dynamic/printing integration control | Broadening CSSOM reach or animation execution into excluded modes |
| Pending state | Paused deterministic case plus one pending/unresolved-timeline case recording pending/current time before and after read | Query triggering readiness/ticking or using a rendering-only timing shortcut |

Do not require all property families to start a copied prototype. For an accepted native fix, at least resolve or explicitly scope the provider/timing gates in REPORT.md, and run the transform sequence in a debug browser. A useful invariant check records EffectSet masks, animation generation, progress bookkeeping and overflow-sync fields around the isolated helper *after the preexisting CSSOM flush*; whole-getComputedStyle invariance would be false because its ordinary flush can legitimately update renderer state.

No new broad performance suite is required initially. Confirm repeated retained-object reads are bounded and do not schedule extra restyles. This does not establish a general performance guarantee.
