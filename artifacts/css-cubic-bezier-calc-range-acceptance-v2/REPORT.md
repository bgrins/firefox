Pending cubic landing successor

The four-path patch preserves exact reviewed Rust and new 36-case WPT bodies, removing only the two calculated cubic-bezier expected-FAIL blocks. Other subtest and platform-specific harness expectations remain unchanged.

The active comparison intentionally uses original metadata. It establishes raw behavioral comparison, not validation of revised expectations. A post-install metadata-sensitive capture remains required. Candidate outcomes, repair count and acceptance remain unset.

The separate fix 133 correction removes its two jump-none blocks. Both patches passed individual scratch apply/reverse. Their context overlaps in valid.ini, so an explicit after-steps-metadata-gecko-wpt.patch is supplied and passed exact composed apply/reverse with fix 133. Use that route after folding fix 133 metadata. Native and HTML bytes are identical on both routes. Both routes and expected metadata hashes are recorded in METADATA-ROUTES.json; no live changes occurred.

The steps(calc(-10), start) stale expectation is associated with the prior integer repair and remains out of scope. Three contextual failure controls are retained.
