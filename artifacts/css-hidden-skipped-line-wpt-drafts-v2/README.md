# Skipped block-line WPT draft v2

Formatting-only successor to sealed css-hidden-skipped-line-wpt-drafts-v1. The18 case descriptors now occupy three readable JavaScript lines each. Exact descriptor values, ordering, names and rectangle arrays are unchanged. Every byte before and after the descriptor array is unchanged, including styles, construction, query ordering, assertions and cleanup.

The source remains an unrun artifact-only draft for potential installation under `css/css-contain/content-visibility/hidden-skipped-block-line-queries.html`. It contains6percentage-block,4inline-sibling,4table-first-rescue and4float/OOF boundary cases. Each retains visible-peer and explicit full-rectangle calibration, outer-only flush, first/repeat query, restore and show. The four rescue cases intentionally query the table first; later-inline cases use independent fixtures. The complete scope and geometry reasoning remain in v1/README.md.

Static checks authenticate every v1 payload, compare all18 parsed objects and array-external bytes exactly, preserve CASES/EXPECTED-ROSTER verbatim, and run Node syntax-only validation. No browser, WPT lint, live file installation, native build or Git operation occurred. Visible calibration and actual candidate discrimination still await a browser run. No expectation has been weakened and no candidate pass is assumed.
