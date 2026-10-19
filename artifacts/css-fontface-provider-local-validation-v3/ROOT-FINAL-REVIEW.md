# Final FontFace test bytes

Both final runs use the actual successful v2 build, with only authenticated WPT metadata/whitespace changes and removal of the obsolete style/family-swap FAIL expectation. The pre-build snapshot remains the original observed v2 snapshot. No new pre-build observation was invented.

The final matrix exits 0 with 68 PASS and three OK endings. The final regression run exits 0 with 19 PASS subtests and four PASS, one expected FAIL and three OK endings. Every regression tuple matches the v2 candidate except the repaired style/family-swap test's obsolete expectation. Its earlier unexpected PASS and the unchanged descriptor-override failure remain recorded.

Lint now has zero errors and two ESLint ignored-file warnings. Separate descriptor-retirement tests on the same binary pass all eight cases and both wrappers; no delete occurs before those observations. Their no-support comparison remains pending.

This is shared-tree macOS validation. The standalone provider patch needs the earlier worker-family rebuild support. An isolated upstream checkout/build is being used to establish that dependency and validate the support-containing patch. No independently landable native commit is accepted by this record; other-platform builds and the documented lifetime/local-font limits remain open.
