# Single-argument linear() lead

The current CSS Easing2 editor draft grammar permits one comma-separated argument. Its output algorithm explicitly handles a single control point. The local contextual-easing candidate retains the parser restriction requiring two authored stops. A root browser probe on System Firefox158 rejected all three single-argument forms in OBSERVATION.json, while a two-argument constant control animated at opacity0.5 at all four sampled times. This is a browser observation, not a clean local-branch comparison or accepted new fix.

Primary specification: https://drafts.csswg.org/css-easing-2/#linear-easing-function and https://drafts.csswg.org/css-easing-2/#linear-easing-function-output (read2026-10-29). Relevant implementation: TimingFunction::parse_linear in the authenticated css-contextual-easing-activation-prototype-v2/native.patch; the same minimum is retained by that candidate.

Before implementation, trace the CSSWG change/resolution, check the contemporary upstream WPT grammar expectations, and deduplicate Bugzilla and prior project work. The current spec also changes serialization details; that is a separate issue, and the historical broader easing suite has twelve existing linear serialization failures. Do not change the prepared315-case experiment or reinterpret its controls based on this lead. No proof or native acceptance credit.

The probe used an owned about:blank tab, created one temporary div, sampled paused Element.animate effects, canceled them, removed the div, and closed the tab. CSS.supports and animate each rejected linear(0.5), linear(0.5 50%) and linear(0.5 0% 100%). The exact two-argument control was linear(0.5, 0.5). Errors were caught and recorded as TypeError.

Contemporary upstream WPT checked: https://raw.githubusercontent.com/web-platform-tests/wpt/master/css/css-easing/linear-timing-functions-syntax.html explicitly expects linear(0), linear(0 0% 100%) and linear(0% 100% 0) to be invalid. This is a spec/WPT disagreement, so browser rejection alone does not establish a new implementation bug. Keep this lead unaccepted pending specification history.

## Deduplication result

The lead is already bug1917125, assigned to dshin and NEW/S3 in the live moz connector response. CSSWG issue10580 resolved on2024-09-04 to allow a single stop and records spec commits9573034 and aaad9c7. Bug1917125 comment4 has an existing WIP attachment9423269. BUG-1917125.md retains the connector response. The mismatch is established as a known feature gap, not a new discovery, and no competing patch was prepared.

https://bugzilla.mozilla.org/show_bug.cgi?id=1917125
https://github.com/w3c/csswg-drafts/issues/10580
