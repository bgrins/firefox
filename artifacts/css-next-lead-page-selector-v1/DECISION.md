# Next independent bug: page-selector list name filtering

Resume the existing page-selector-name candidate. It has a clear specification oracle, a two-Rust-file repair boundary, and historical paired print evidence. It does not require the provider readiness or contextual easing work. This is unfinished work recovered from the inventory, not a new discovery or an accepted fix.

## Current source and precise defect

Captured HEAD is `0197d1c8e8fd678680d78b212f6a2c0ae9d82d51`. `ExtraStyleData::add_page` indexes a whole rule under each selector name. `PageRuleMap::match_and_append_rules` visits the nameless bucket and the actual named bucket separately. But `match_and_add_rules` passes only pseudo-class flags to `PageRule::match_specificity`, whose maximum includes selectors for every name in that rule. Indexing by a name does not prove that the selector contributing applicability or specificity has that name.

Two decisive examples, with `body { page: alpha }`:

- `@page alpha:first, beta { margin-top: 96px }` must not affect the second alpha page. The current rule can match through bare beta after entering the alpha bucket.
- `@page alpha, beta:first { margin-top: 96px }` followed by `@page alpha { margin-top: 0 }` must give the first alpha page zero top margin. The current maximum can improperly use beta:first specificity.

The historical repair passes the bucket name into `PageRule::match_specificity` and filters selectors by that name before testing pseudo-classes and taking the maximum. The nameless pass still handles nameless selectors on named pages. Empty lists remain universal. Duplicate bucket entries are unchanged; deduplication is not necessary to fix this defect. `TRANSPORT.json` records successful private application of the exact historical native patch to both captured current files. No live source was edited.

## Current normative trace: REACHED

The official CSS Paged Media draft fetched 2026-10-28 is dated 21 October 2026. [Section 4.1](https://drafts.csswg.org/css-page-3/#at-page-rule) makes a nonempty rule applicable through a matching selector. [Section 4.2](https://drafts.csswg.org/css-page-3/#page-selectors) requires every component of that selector to match; its name must match the named page. [Section 4.4](https://drafts.csswg.org/css-page-3/#cascading-and-page-context) uses ordinary cascading with page-specific specificity tuples. [Selectors specificity](https://drafts.csswg.org/selectors-4/#specificity-rules) chooses the greatest specificity among matching list members. Thus neither cross-name applicability nor cross-name specificity is permitted. No property-registration policy or computed-value cycle assumption is needed.

## Evidence and deduplication

Historical four-phase receipts independently read in this audit report 10 FAIL + 8 PASS before the repair, 18 PASS after, and six existing regressions PASS in each phase. Their recorded input-preservation flags are true. This is historical evidence, not a fresh browser run or a new acceptance decision. The prior root report also records pixel nonvacuity and a successful build; this audit did not re-execute those checks.

All 24 current test bodies match their historical candidate input hashes. `CURRENT-COMMITS.json` reports 138 committed accepted fixes; its accepted/new, pending, and unaccepted-candidate queues contain no page-selector entry. The historical native report explicitly has no commit and the formal target remains a draft. Preserve this provenance; do not credit the old ten failures as new bugs.

## Execute next

Run a fresh current-binary print baseline of the 18 target/control pages and six existing print regressions listed exactly in `ROSTER.json`, under the current owned-profile/epoch-preservation workflow. Use genuine WPT `--test-types=print-reftest --headless --processes=1 --reftest-screenshot=always`, an absent output directory, raw logging, and retained screenshots. Do not rerun the historical scripts in place: their output paths already exist and their process/preservation checks predate the current lifecycle helpers. Reuse their exact tests and resource captures, adapting only execution ownership/binding.

After baseline, apply only the two-source patch under root control, rebuild, and repeat the same print roster with pixel nonvacuity. The six historical landable HTML bodies are applicability-print, applicability-ref, specificity-print, zero-margin-ref, control-unnamed-mixed-print, and controls-ref, all prefixed `testing/web-platform/tests/css/css-page/page-selector-list-name-`. The broader split/reversed/layer/name controls remain useful paired validation. A standalone native+WPT commit should follow fresh comparison and actual lint; no need to wait for a complete CSS formalization.

A small useful later theorem is equivalence between an exhaustive matching-selector maximum and the union of named/nameless bucket maxima, assuming complete indexing and the existing page specificity ordering. It would support the filter boundary; it would not prove pagination, print pixels, native bucket completeness, or the full cascade.

## Limits

No browser, build, lint, native apply, index, ledger, or epoch mutation was performed. No new formal theorem was claimed. Upstream Searchfox page_rule.rs matches the captured HEAD byte-for-byte; stylist is the exact committed local capture because that file has accepted local changes. The historical patch transports, but current native compilation and browser behavior still require the proposed experiment.
