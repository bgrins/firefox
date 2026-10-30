# Overridden line-height probe

This separate four-case WPT probe covers the LineHeight branch's additional FontSize dependency. It is not part of the frozen 77-case baseline/candidate experiment. No browser result or new bug is claimed yet.

The overridden case registers a non-inherited length with initial zero, specifies `--actual: 1lh`, and places a variable-dependent line-height declaration below an important literal winner. The winner changes from 20px to 30px. No-loser and absolute-length controls distinguish ordinary unit computation from a spurious cycle; an active-cycle control removes the winner. Each case uses an isolated registration and samples the initial flush plus three subsequent frames in both phases.

The proposed oracle follows [PVAPI relative-unit cycles](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles), [the lh unit](https://drafts.csswg.org/css-values-4/#lh), and cascade selection. Current primary text was read on 2026-10-30: registered lengths containing lh add line-height and font-size dependencies. The actual losing declaration must not participate in the winning value. The active-cycle control expects the registered initial value and inherited line-height after invalidation; that endpoint still needs runtime verification. This probe does not use the unresolved unused-unit-fallback timing premise.

Run against both published and candidate native sources after the existing coherent comparison. Keep the probe as research until both results and the oracle have been reviewed. The existing Firefox frontend skill was read; style flushes here are intentional measurements in a bounded regression test.
