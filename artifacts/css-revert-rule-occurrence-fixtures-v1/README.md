# Repeated-source occurrence fixtures

Prepared for separate review and execution. No browser, native build or WPT run was performed. This package changes neither live source nor the active WPT tree. It is a private fixture artifact, not a complete runner. Mount `inputs/css/css-cascade` under that path in a private WPT root with standard `/resources/testharness.js` and `/resources/testharnessreport.js`, retaining the CSS `.headers` files. Root owns execution and binary/source provenance.

`revert-rule-shared-occurrences.html` registers six promise tests: three source families in each of LTR and RTL. Each compares an intended shared-source document against an independently parsed control, through four mutation phases. The `layout.css.revert-rule.enabled` preference must be true. The fixtures assert support rather than silently skip unsupported syntax. Implicit-scope failures also need to be separated from rollback failures.

| Family | Intended repeated-source path | Control |
| --- | --- | --- |
| `selector-list` | `.target, #target` shares one style-rule block; `.target.other` sorts between the matching selectors | Two separate `.target` and `#target` rules with identical declarations |
| `cache-clone` | Load one external URL, await `load`, insert a different effective competitor, then load the exact same URL again | Two distinct URLs with differently commented, otherwise identical CSS bodies |
| `implicit-scope` | Same sequential load, but `@scope { ... }` owners have outer and inner parents; the competitor's owner is in the middle | Distinct external URLs at the same owner locations |

Each fixture creates a fresh iframe per side. Cacheable response headers encourage the completed-sheet reuse path. Distinct control URLs and text avoid the completed-sheet/inline-text cache sharing under audit. Neither side reads `cssRules` or mutates stylesheet rules. The only post-setup mutations are a receiver's `data-value` attribute; fixed rules supply or remove `--occurrence-value`. The repeated blocks use `var(--occurrence-value, revert-rule)`, so the test does not mistakenly assign a CSS-wide keyword directly to a custom property. In the scoped case owners are appended to their nested parents: their final document order is inner, middle, outer, while their load order is outer then inner. The competitor lies between them and proximity determines their cascade order.

Both copies contain ordinary `margin-left:17px` and `margin-right:19px`, plus an important logical `margin-inline-start` trigger. The competitor sets physical margins to 31px/37px. A missing variable invokes Rule rollback; defined values are 29px then 43px. Removing the attribute returns to rollback. This reaches both importance partitions, exercises physical/logical identity, and checks that a subsequent receiver mutation changes the result. It does not test `attr()` taint or attribute-substitution dependency recording.

## Expected values

| Phase | LTR: left, right | RTL: left, right |
| --- | --- | --- |
| Initial rollback | 31px, 19px | 17px, 37px |
| Small value | 29px, 19px | 17px, 29px |
| Large value | 43px, 19px | 17px, 43px |
| Return to rollback | 31px, 19px | 17px, 37px |

For the affected physical margin, Rule removes its rule's ordinary fallback as well as its important declaration; every independent copy reaches the same Rule trigger. The competitor then wins. A defined variable instead supplies the important value. The opposite margin retains the highest-precedence repeated rule. This follows the [Rule rollback definition](https://drafts.csswg.org/css-cascade-5/#revert-rule-keyword) and [cascade order](https://drafts.csswg.org/css-cascade-5/#cascade-sort).

Repeated links must behave as independent stylesheet occurrences. An implicit scope uses its stylesheet owner's parent, and closer scopes take precedence after specificity. Thus the nested owner arrangement places the middle competitor between the two copies in proximity order. See [stylesheet import processing](https://drafts.csswg.org/css-cascade-6/#import-processing), [scope roots](https://drafts.csswg.org/css-cascade-6/#scoping-root), and [scope proximity](https://drafts.csswg.org/css-cascade-6/#scope-proximity). The read-only webspec-index database failed to open for updates; these provisions were checked through the official CSSWG pages instead. The expected table is reasoned, not browser-validated.

Every phase asserts shared/control equality and both absolute results. Failure can therefore expose an ordinary rollback regression even when both sides fail identically. A relational pass alone is insufficient. `EXPECTED.json` lists the exact six callbacks. At most 12 frames are created over the run, two live per callback; each callback performs eight computed-style reads. Each frame/sheet load has an eight-second timeout; the page requests WPT's long timeout. Page timers do not bound a synchronously stalled browser. No timings or performance thresholds are collected.

## What constitutes sharing evidence

A successful test does not prove the same-URL sheets shared a block. Nor does cache/network success or identical text. The separate source audit identifies the native sharing producer; a bounded trace is needed to show these fixtures take it in the tested build. The optional diagnostic described in `diagnostic/README.md` records the original rule-tree roster at first Rule, before the owner index deduplicates sources. It must not be used for performance measurements.

With `dom.window.dump.enabled=true`, the test emits `CSS_OCCURRENCE_PHASE_V1` begin/end markers around setup and each synchronous read, identifying family, direction, phase where applicable, and side. These assist trace correlation; asynchronous style work outside the markers remains possible. Interpret only complete records from the same process and retained cascade lifetime. A positive source-sharing witness requires repeated equal block pointers **at equal raw priority in one roster**, separated by the expected competitor; the normal/important pair of a single occurrence is not evidence of two occurrences.

Static preparation checks parse JavaScript without running callbacks, verify six callback registrations, compare control/resource declarations and verify the diagnostic patch against copied sources. These checks do not validate CSS parsing, cascade results, cache sharing or Rust types. No new bug is claimed.
