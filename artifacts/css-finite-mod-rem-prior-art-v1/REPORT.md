A narrow public search and fresh moz Bugzilla read found bug2022920, the WPT sync of PR58452, resolved in March2026. Its description records a Chromium fmod-based implementation and a distinct exact-multiple/sign correction: normalize zero to the divisor sign before opposite-sign adjustment. This is useful implementation precedent and a regression-control source. It is not evidence that the large finite quotient-loss witness is already reported in Firefox, nor proof that it is new. No exhaustive novelty search was performed.

Sources inspected24October2026:
- https://bugzilla.mozilla.org/show_bug.cgi?id=2022920 (fresh moz get_bugzilla_bug response, comment0)
- https://github.com/web-platform-tests/wpt/pull/58452 (linked by the bug; direct web retrieval failed)
- https://chromium-review.googlesource.com/c/chromium/src/+/7661079 (linked implementation change; not independently retrieved)

Searches: site:bugzilla.mozilla.org CSS mod rem precision remainder33554432; site:bugzilla.mozilla.org CSS mod rounding precision float. Search results were not used as proof of absence.
