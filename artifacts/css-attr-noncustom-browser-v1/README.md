# Attribute-only non-custom dependency collection

The runtime attribute value can contain `var()` even when the declaration only
contains `attr()`. The inner lexical-VAR early return in
`Cascade::maybe_note_non_custom_dependency` prevented those declarations from
being retained for graph traversal. The repair deletes that return, preserving
attribute preparation, the outer VAR-or-ATTR filter, property mapping and
occurrence-specific fallback traversal.

The standalone patch contains one three-line Rust deletion and a ten-case WPT.
The WPT covers font-size, line-height, a used attribute fallback, an unused
fallback and literal/missing/no-back-edge controls. Registered relative units
are literal so this repair does not depend on fixing resolved unit metadata.

The original ten-case test has three failures and seven passes. The candidate
passes all ten. All 183 earlier checks pass in both runs. The separate graph
probe improves from four failures to three: its omitted-edge case passes,
while both lost-summary cycle cases and its acyclic ordering case still fail.
Across the complete run, four statuses improve and 213 are unchanged. Each
run has 206 checks plus eleven harness statuses. Both harness commands exit 1
because the retained diagnostic page intentionally exposes unresolved bugs.

`accept_pair.py` checks raw results, exact named changes, counts and input
hashes. Only cascade.rs and the two binary hashes change between the runs;
all pinned inputs remain stable during each run. The native build completed
with exit 0 despite nonfatal build-monitor export KeyErrors. The warning-enabled
lint command reports zero errors and one ignored-WPT ESLint warning, exiting 1.
The first lint invocation used the optional warning argument incorrectly; its
CLI failure is retained separately. Independent JavaScript syntax checking is
part of the review gate.

This discovery came from manual source admission analysis following the typed
fallback model. It is not an automatically found Lean counterexample or a new
proof of the native SCC implementation. Full parser/provider/graph correspondence,
resolved dependency summaries and unused-relative-fallback semantics remain open.
Browser runs used the shared experimental tree. The isolated commit patch applies
to committed HEAD and excludes those unrelated changes; no clean-base build is
claimed. Research, review and browser evidence precede the native/WPT commit.
