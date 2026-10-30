# Numeric oracle and scheduling boundary

Reviewed current primary sources on 2026-10-29:

- [CSS Values 4, font-relative lengths](https://drafts.csswg.org/css-values-4/#font-relative-lengths): `em` uses the element's computed font size; `rem` uses the root basis. The child inherits the middle font. Neither duration is itself a font-affecting property.
- [CSS Animations 2, animations](https://drafts.csswg.org/css-animations-2/#animations): changes to animation properties update associated CSS animation state, subject to per-member script overrides. This probe never overrides either CSS duration through updateTiming.
- [CSS Animations 2, pending style changes](https://drafts.csswg.org/css-animations-2/#requirements-on-pending-style-changes): animation-interface queries must reflect pending computed-value changes. This is also why membership and timing queries are postponed until the initial child-only measurements finish.
- [Web Animations 1, iteration progress](https://drafts.csswg.org/web-animations-1/#calculating-the-iteration-progress): with the chosen finite durations, no delay, one iteration, normal direction and linear easing, active progress is 750ms divided by duration. Linear endpoint interpolation gives the table in README.

The finite dependency graph gives a unique numeric result; it is not the earlier self-dependent recurrence. The exact number of implementation traversal passes or refresh callbacks needed is not established by these citations. The first sample has no required convergence result, and the bounded passive-frame assertions are observations to interpret with acquisition, ordinary and literal controls. A failure after three sampled frames alone does not establish infinite starvation or the native path responsible. A pass does not establish all Pending producers are serviced.
