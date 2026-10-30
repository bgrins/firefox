The three original callbacks stop at parsing. Bug 2037743, retrieved from Bugzilla during this run, tracks the deliberately unsupported computed-value-time expressions in easing functions; it is UNCONFIRMED and unassigned. Its description identifies these as carve-outs from bug 2035572. These three failures therefore reproduce a known feature gap and do not independently establish an animation-refresh bug.

Source: https://bugzilla.mozilla.org/show_bug.cgi?id=2037743

The existing contextual-easing candidate implements this missing admission/conversion behavior. Further original/candidate observations must distinguish enabling that feature from defects exposed in the candidate's invalidation or ownership behavior.
