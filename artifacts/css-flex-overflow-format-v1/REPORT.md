# Final candidate formatting and WPT lint

The actual native source path passes clang-format with no byte changes. The unchanged candidate WPT passes the WPT-specific linter with warnings enabled: zero errors and warnings. Temporary source/test installation is restored; HEAD/index are unchanged. Because formatting changes no native or test bytes, the earlier candidate runtime evidence applies to the same inputs.

Retained unsuccessful preparation attempts are not gates: the old mach clang-format entry is removed; formatting via a stdin copy reordered the primary include because the tool did not retain the source basename, and that copy was never transferred into native source. The actual-path run is authoritative. General mach lint reports an expected ESLint ignore-pattern warning for the WPT tree; the separate explicit wpt linter validates the test instead. No warning was suppressed in the retained WPT-specific run.

No new build is claimed for this formatting-only check. The original browser build stays intact while source is temporarily installed for lint, then restored. Final native acceptance depends on the separately authenticated source/formal review.
