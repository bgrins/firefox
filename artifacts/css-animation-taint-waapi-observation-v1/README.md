# CSS and WAAPI animation-taint observations

This standalone research page serially creates three fresh iframes: a pure WAAPI custom-property effect, a matched CSS animation, and a literal writing-mode control. The WAAPI documents contain no CSS keyframes rule. The CSS rule is inserted only after the initial observation and remains present after cancellation.

Every var-dependent writing-mode value, including CSS values before creation and after cancellation, is a policy observation. No CSS or WAAPI sink result is asserted. The unresolved WAAPI producer scope is recorded in the sealed scope note referenced below. Literal sink values, the ordinary/animated custom-property values, fixed 2000 ms timing at 750 ms, retained identities, and cancellation lifecycle are separate reference checks.

Each active and cancelled phase first samples only writing-mode, then samples it after three animation frames, before detailed style/timing and membership reads. The first active read follows effect acquisition, readiness and seeking; it is not a claim that no earlier flush occurred. Detailed fields are sequential observations, not an atomic snapshot. Cancellation behavior itself is recorded even if its lifecycle reference check fails.

`window.waapiTaintObservations` exposes the plain report. Collection completion, reference-check success, and the null policy verdict are distinct. Exceptions and partial rows are preserved. Nonfinite numeric values receive explicit JSON encodings. The page has no internal watchdog; a hung collection may never produce a terminal transported report. The separate disabled installed-browser runner provides an external watchdog.

This is not a landable WPT or a normative WAAPI oracle. Existing 106-case fixtures and native sources are unchanged. No browser execution is represented here.

Validation: Node syntax, eight arbitrary CSS/WAAPI sink cases accepted, literal positive and seven calibration negatives; independent core review 3e2654/21e97e/375c42/25f19c. Checks do not execute a DOM or browser.
