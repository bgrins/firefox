# Committed clip fix: local browser

The optimized browser in `objdir-full.noindex/dist/Nightly.app` includes signed
clip repair `7382007a82b49e83e5399a31f47b598e0f260fe5`. BuildID is
`20261110165601`, version `160.0a1`. It is left installed for manual testing.
The build ran from clean tracked HEAD `713bb6d320ece5371c107794b10180b91a82fef8`
with the existing mozconfig and `mach build binaries -j6`; it exited zero.
The recurring Mach progress-monitor `KeyError: 'export'` did not prevent build
completion. Source, configuration and binary hashes are in `build-result.json`.

The final headless WPT run includes the nine-case `clip-auto-composition.html`
and existing `effect-value-iteration-composite-operation.html`, using the objdir
binary, one process and `STYLO_THREADS=1`. It exited zero: 47 callbacks and two
OK harness completions, all expected. All nine new cases pass. The two retained
failures concern align-content and calc-size; the repaired clip expectation is
removed. Root compared every callback against the preceding tested candidate,
and checked that source/binary hashes and preexisting untracked paths remained
unchanged. See `WPT-RESULTS.json` and the full raw/text logs.

The broader SMIL preservation comparison and Lean guard model remain in the
preceding acceptance artifacts. They were not repeated on this final rebuild.
This is an optimized local build, not a debug/sanitizer or release-channel gate.
No temporary build target directory was created. The earlier experiment's owned
backup and the proof checkers' temporary compilation trees were removed; the
active objdir and canonical Lean build cache are retained.
