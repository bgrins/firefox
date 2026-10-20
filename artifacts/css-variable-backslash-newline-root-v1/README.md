# Backslash delimiter and trailing newline

Status: native/WPT review accepted; separate Lean extension in progress. No native commit yet.

Trimming the newline after an actual backslash delimiter changes tokenization.
The candidate retains the complete whitespace token after that delimiter.
Final WPT: 30 passes. The corresponding baseline subset has 16 failures and
14 passes, derived from the retained original 32-case run. Two escaped-space/tab
controls were removed because they require the separate escaped-whitespace fix.
FINAL-WPT.json verifies the exact two-entry deletion and unchanged test bodies.
The earlier combined 467-check run preserves all 435 preceding outcomes.

Use PACKAGING-v2.json and its v2 patches for the final 30-case test. The original
PACKAGING.json and patches retain the superseded 32-case fixture. The HEAD v2
package base includes the leading-origin fix; the upstream package excludes all
three preceding whitespace fixes. Neither package has an isolated browser build.
The independent review compiles four extracted variants across 73 cases each.
Source extraction and bounded fixtures are not a universal translation proof.

The shared development build and final WPT pass. final-wpt-lint.log has no errors
or warnings. FORMAT-RESTORATION.json records restoration of unrelated formatter
changes. FORMAT-SIGNATURE-RESTORATION.json records the later exact reversal of
the compiled signature line wrap; no executable semantics changed.
No release-browser or security claim follows from these tests.

The formal extension distinguishes the actual backslash delimiter from other
serialization-class Other tokens and compares preservation decisions. It must
retain the maximal-whitespace premise and must not assert equality of immediate
and persistent flags or full standalone outputs.
