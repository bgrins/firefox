# Root review

Root independently authenticated fourteen pinned Git sources, twenty-seven
excerpts and four primary specification snapshots, and reran current fixture
syntax, registration, WPT lint and manifest checks. The misleading function
name in REPORT.md was corrected to get_animated_properties; source excerpts and
all measured fixture bytes are unchanged.

Browser results are independently retained in the separate
css-animation-taint-calibration-runtime-20261110-v1 capsule. They confirm both
direct timeline failures and the first inherited animation-name failure in local
and installed Nightly, while the ordinary-variable control passes. The inherited
callback's later assertions were not reached.

CSSWG issue13933 discusses acquisition and inheritance policy; the current-text
expectations do not settle those prospective changes. The conditional stale
registry deduction remains unmeasured. No new repair or security finding is
accepted by this review.
