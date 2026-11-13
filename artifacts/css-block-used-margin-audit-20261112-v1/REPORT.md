# Block used-margin audit

The negative-space branch of ReflowInput::CalculateBlockSideMargins adjusts
its reflow-state margin but returns before refreshing UsedMarginProperty.
getComputedStyle and margin-box geometry consequently observe the earlier
margin for auto and percentage values. This is a remaining case of the old
bug 381328/bug 1298008 family, found by source/spec inspection while auditing
exact reflow interfaces. It is not a Lean-discovered bug or a security finding.

The first headless browser probe records 24 observations: both directions,
two widths in a 100px container, and six margin forms. Fitting auto margins
resolve correctly; an overflowing 200px child reports zero auto end margin
instead of the -100px required by the block-width equation. Percentage and
calc values also expose the missed cache refresh. Plain lengths use a separate
existing reporting path.

The first quad probe successfully ran 24 subtests but the API was unavailable,
so every quad is null. It provides no geometry coverage. Its wrapper failed
process-group inspection after the WPT command exited zero. RECOVERY.json
records a separate fresh absence check, validated observations, and removal
of the byte-pinned temporary WPT. The original failure receipts remain.

The quads-enabled successor explicitly sets layout.css.getBoxQuads.enabled
in the temporary test profile and calls the current DOMQuad.getBounds API.
All 24 observations complete with a present quad, unchanged browser binaries,
and confirmed cleanup. For the overflowing both-auto case the margin-box
width is 200px rather than 100px; fitting auto cases report 100px. These are
observations, not passing normative assertions. The unavailable-API attempt
must not be counted as a successful geometry test.

SPEC-TRACE.md records the current CSSOM/CSS2 rule chain, scenario and historical
evidence. The raw section queries retain their source hashes. Source inspection
of current Chromium supports the auto-end calculation but no Chromium runtime
or broad cross-engine agreement is claimed.

The separate repair capsule, ../css-block-used-margin-repair-20261112-v1,
contains the focused native/WPT patch and actual baseline/rebuilt-browser
checks. This audit leaves literal-length compatibility outside that repair.
All temporary probe WPT files are removed. The initial sandbox launch failed
before browser execution and is retained in sandbox-attempt.
