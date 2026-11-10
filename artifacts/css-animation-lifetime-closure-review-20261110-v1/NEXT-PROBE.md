# Proposed next bounded discriminator

## Primary case: initial scroll provider, existing outside target

Use the successful paused-SMIL reveal entry with a fresh iframe. Keep `layout.css.display-animations.enabled=false`; explicitly record `layout.css.scroll-driven-animations.enabled=true`, which is true by default in the pinned source. `animation-timeline`, scroll/view timeline definitions and `timeline-scope` share that pref in `longhands.toml`.

Prepare a visible common ancestor with `timeline-scope: --t`. Give that ancestor itself, or a visible sibling of the hidden branch, one existing CSS animation of font-size driven by `animation-timeline: --t`. Use nonconstant font endpoints and establish an in-effect sample on a visible fallback scroller defining `--t`. Record baseline computed timing, effect properties and timeline identity before hiding/reveal measurement. Do not use an idle or paused-unresolved animation as the eligibility baseline.

Later in tree order, place a second `--t` scroll provider inside the previously unstyled SMIL-hidden subtree. Give it ordinary dimensions/overflow and content; do not put `timeline-scope: --t` on the new provider or its hidden branch, because that would exclude it from the outer scope's candidate search. Initial styling creates the provider when SMIL reveals it. The pinned TimelineManager searches valid same-name providers in reverse tree order, so the new provider should replace the earlier fallback in the outside target's lookup.

Using the common ancestor as the animated target directly tests a backward tree-rank edge. A sibling target is a simpler alternative. Keep the target visible and use a property such as font-size to avoid a compositor-only/throttled effect. A newly created provider can have unresolved current time before frames exist; that is an intended measurement boundary, not an assumed final pixel oracle.

Require native attribution within one primary StyleDocument call:

1. Newly visible provider: `AnimationOnly`, absent old primary style, initial `MatchAndCascade`, task including ScrollTimelines (32).
2. Provider task executes; affected names include `--t`; outside target is in the matching name map.
3. Capture old/new timeline identities and class, the equality/deferral decision, and the target's DOM relationship to the provider. A different concrete timeline must reach `SetTimelineNoUpdate`; a deferred unresolved result does not pass this gate.
4. Capture `HasComputedTimingChanged`, nonempty properties, request type and cascade level. Require an actual eligible Animations request on the outside target, not merely `UpdateNamedTimelineAnimations` entry.
5. Join the new request to hint/admission/installation during a later drain iteration before the primary getter returns. Attribute any descendant normal work and initial data creation separately. Record subsequent stable timing/pixels without using a later getter to repair the first observation.

## Small controls

- **Scope-only global visit:** newly admitted element declares an unrelated `timeline-scope: --scopeProbe`, without a new `--t` provider. Expect TimelineScopes (128) and global map visitation; do not expect a changed outside timeline/request when lookup is unchanged. This separates broad enumeration from actual injection.
- **Missing-name/removal:** make lookup lose its last matching provider in a separate callback. Record the deferred set insertion and later phase separately; do not count it as same-drain injection.
- **Ordinary reveal:** same provider/target setup revealed by a class mutation. Compare initial task phase while retaining the outside-target causal join.
- **View variant, after the scroll gate:** replace the new scroll provider with `view-timeline-name: --t`; require ViewTimelines (64), a distinct concrete ViewTimeline and the same timing/request gates. The fallback and later-tree selection remain explicit.

Adding scope/scroll/view declarations to one hidden element can exercise all bits, but obscures which update caused the request. Keep these callbacks separate initially.

This proposal targets one new non-descendant edge. It does not predict a hang, repeated lifetime recreation, new bug, or universal termination result.
