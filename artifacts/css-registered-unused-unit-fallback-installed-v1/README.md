# Disabled installed-browser observation

This is a small adapter of the executed overridden-dependency observer (active596af9bf). It serves the exact sealed359e873d three-case unused-unit fixture and shared harness, appending only a completion report script. It uses the existing localhost HTTP transport rather than adding WebDriver machinery. No browser is launched during preparation.

The report copies `window.unusedUnitFallbackObservations` after testharness completion: all three named WPT statuses/messages and harness status, both phases, four custom-value samples per phase, target font, primary input, parent font, and declared expectations. It adds no style getter or assertion. Registration, parent and input calibration checks are recomputed independently by the receiver. Literal control success is separate from defined-fallback and genuine-cycle expectations; the policy verdict remains null. Ordinary failures remain complete observations when capture and cleanup succeed. Missing setup records remain null/incomplete, not fabricated values.

Only validate changes substantively in run.py. Main changes only temporary-prefix and result-label strings; all server/profile/process/cleanup/app-admission functions are unchanged. The executed Firefox158/portable Chrome156 saved pins are reused. Root execution reauthenticates actual installations. The existing nonce/run binding, raw HTTP request retention, exclusive REPORT, watchdog, scoped Firefox relaunch admission, joined HTTP shutdown and owned profile/group cleanup remain intact. No CSS preferences, user.js or native app are introduced. The watchdog can end a hung acquisition without a report; there is no promise of partial streaming before testharness completion.

Root must wait until the native candidate has restored, preserve disabled POLICY/FILES, then activate and reseal. Execute serially, verifying Firefox terminal/cleanup before Chrome:

```
python3 -I -S -B artifacts/css-registered-unused-unit-fallback-installed-v1/run.py --browser firefox --run
python3 -I -S -B artifacts/css-registered-unused-unit-fallback-installed-v1/run.py --browser chrome --run
```

Outputs are css-registered-unused-unit-fallback-{firefox,chrome}-runtime-1. Omitting --run authenticates saved resources only. RESULT separates transport/cleanup, observation completeness, calibration, literal control, callback statuses and harness status; suite_pass requires complete three-case capture, three PASS and harness OK. It never claims native acceptance.

Saved check5f7727/0 runs the exact reporter in a DOM-free VM, independently validates its payload, tests eight bridge scenarios,16 schema negatives and three duplicate/foreign transport negatives, and verifies exact lifecycle AST equality outside validate/main. Its owned scratch is removed. No server, live app read, process census, browser, native build, Git or control operation was performed. This is ready only for root-owned activation and actual observation, not a runtime result.
