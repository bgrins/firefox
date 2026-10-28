Status: **unfinished frozen research draft**. Independent fixture review, final static recheck, WPT lint and browser validation remain pending. No executable runner is included. This archive is not execution clearance.

# Provider error and initial-context controls

Two new artifact-only WPT drafts: 32 provider-error assertions and four initial-color calibrations. No browser callbacks, native candidate, lint or build have run. Static syntax and test-name enumeration passed f3b09d/0. Each callback collects all three mutation snapshots before asserting, so a first failure retains later observations.

The original mixed16, lh-only16 and supplement32 pages are preserved byte-for-byte under preserved/ and pinned in PRESERVED-FIXTURES.json. The new cases complement rather than replace them. Existing declarations/query-order cross-products remain in those originals; new controls pair declaration and first-query order to keep the expansion bounded.

The error page distinguishes missing var/env/typed-attr, inherited/root defaults, CSS-wide trailing junk, selected self/mutual cycles, inner fallback attempts and an unused self fallback. Distinct initials expose partial cycle invalidation. Selected cycle providers contain no relative units. The unrelated length uses fixed line-height 40/60/40.

The color page uses @property initial light-dark(red,blue), direct and no-declaration calibrations, and light/dark/light mutation. It is not evidence that CSS.registerProperty accepts that initial. Calibration failure and unsupported context types must remain visible; neither may be reclassified as a provider repair. See SPEC-TRACE.md for current-ED assumptions and limits.

The release observer is a separate sealed artifact and uses only the two exact historical16-case fixtures. These drafts do not change that experiment. No accepted bug count, security conclusion, native-refinement proof or canonical formal coverage is added.
