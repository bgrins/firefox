# Timeline feedback diagnostic

Four modes distinguish opposing resolved offsets from the transient loss of an
animated value when a query-selected named timeline changes. This fixture checks
baseline, animation identity, and scroll offsets, and records bounded
observations. It deliberately has no guessed final-state assertion.

`check2` is the final fixture validation: WPT lint, manifest generation,
JavaScript syntax, and the inert four-callback roster pass. `check1` predates the
explicit running-state and nonzero-rate baseline assertions and is historical.
The runtime and restoration receipts are in
`../css-style-query-feedback-runtime-20261110-v1`.
