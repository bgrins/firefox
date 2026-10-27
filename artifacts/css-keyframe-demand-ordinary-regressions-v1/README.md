# Ordinary substitution regression roster

Four existing testharness files cover the ordinary no-pending route while the pending-provider prototype is integrated. All four local bodies exactly match the current upstream bodies fetched through Searchfox. No fixtures, metadata or native sources were changed, and no tests were run. ROSTER.json lists exact paths, types and limitations; SOURCE-PINS.json includes present bodies and absent header/metadata roles.

| Test | Relevant coverage |
|---|---|
| `css/css-variables/variable-cycles.html` | Self/mutual/overlapping cycles, valid outside consumers and unused fallback cycles. |
| `css/css-variables/variable-css-wide-keywords.html` | Registered/unregistered initial, inherited and unset values; fallback defaulting and layer reversal. |
| `css/css-values/attr-cycle.html` | Typed attribute/property cycles, attribute-only cycles, raw-string distinction, fallback selection and font-relative dependencies. |
| `css/css-values/attr-all-types.html` | Typed parse success/failure, defaulting, raw strings, unit forms, registered values, nested attr()/var() substitution and relative units. |

These are ordinary testharness pages, not reftests or crashtests. Their direct external resources are `/resources/testharness.js` and `/resources/testharnessreport.js`; none requests custom fonts, images or auxiliary test pages. The resources and inherited/per-file metadata are captured. This is a fixture resource roster, not a replacement for the root runner's server/profile/configuration preservation evidence.

## Prefs and expected metadata

Use normal WPT inherited metadata rather than adding experimental prefs. Root metadata enables tree-counting/supports-at-rule and platform harness settings; CSS metadata supplies its existing shape/style-query/custom-media/progress/typed-arithmetic prefs. The variables directory additionally enables `layout.css.properties-and-values.enabled`; the values directory enables `layout.css.random.enabled`. Exact lists are in captured `__dir__.ini` files. None of these four pages supplies an additional per-test pref.

`variable-css-wide-keywords.html.ini` expects FAIL for three named revert-layer fallback subtests: unregistered, non-inheriting registered and inheriting registered. Keep those established expectations. `variable-cycles.html.ini` allows PASS/FAIL for the unused-fallback case only on Android non-debug. `attr-cycle.html.ini` similarly permits Android non-debug intermittents for two auto-numbered subtests. No file metadata exists for attr-all-types. No desktop exceptions occur in the cycle metadata. This describes metadata, not observed statuses. Counts and actual results must come from the subsequent raw run; do not prescribe all-PASS.

## Oracle and coverage review

The var-cycle page already expects unused fallback cycles to be valid and cites CSSWG issue 11500. Its `#cycles` help anchor is stale in the current Variables draft, but that does not make its unused-fallback expectation obsolete. The taken cycles retain literal fallbacks and remain invalid as required by the current context-guard rules.

One attr-cycle row appears stale against the 27 October 2026 Values 5 draft: the section labeled “Multiple attributes cycling simultaneously in bare attr() form” expects `abc`. The exact setup and manual trace are in ORACLE-CAVEAT.md. Keep this caveat separate from the no-pending compatibility comparison: passing the old oracle alone would not establish current-draft conformance, and a changed outcome needs adjudication rather than automatic labeling as a regression. No observed browser discrepancy or new bug is claimed here.

Two narrower coverage limitations: the CSS-wide page's row labeled unregistered `revert` fallback actually uses `unset`; attr-all-types includes dimension iterations whose selected ordinary property cannot meaningfully accept the supplied value (including frequency with no property mapping). Its whole-page pass must not be described as exhaustive coverage of every named CSS type. The direct typed-number/length/string, nested substitutions and fallback assertions still make it useful for this scoped regression run.

Run these exact four files after the root build/host gate. Preserve ordinary statuses and messages under the actual platform metadata, retain raw lifecycle, and investigate unexpected changes. These tests do not admit pending animation winners or exercise the new demand callback directly; they supplement the native real-resolver tests.
