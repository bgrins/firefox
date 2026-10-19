# Duplicate declaration publication: browser baseline

At `005739ed34b336b8dc23492a492a0754d0b03265`, the local Firefox build reproduces six failing subtests in the archived diagnostic WPT: setting a previously absent `link-parameters` property to a `param()` value containing `var()`, `env()`, or `attr()` leaves `style.length` at 2 instead of 1. Removing the property then leaves length 1 instead of 0. Nineteen controls pass and the harness completes successfully. The expected-failure run exits 1.

The existing WPT directory metadata explicitly enables `layout.css.link-parameters.enabled`. This establishes a defect with that feature enabled; it does not establish release-default exposure. The baseline contains earlier local fixes and is not an isolated upstream build.

`baseline-raw.jsonl` retains the original test events. The before/after snapshots bind recorded source, test, configuration, and browser binary hashes. `ROOT-CHECK.json` records an independent re-read of the raw outcomes and a recheck of every recorded live pin. These pins are not a claim that every build input was captured.

The source lead is the successful ordinary parse followed by deferred substitution parsing in `parse_non_custom_property_declaration_value_into`. The ordinary scratch declaration is retained before `WithVariables` is published. `prepare_for_update` can consequently plan two appends for the same initially absent property. The archived source and runtime observations support investigating a clear at the fallback boundary. Native repair, paired validation, formal model, and independent review remain pending.

The failing length assertions run before later assertions in their subtests. This run therefore does not independently establish indexed names, serialized text, or getter results after those failures. No formal-verifier discovery claim is made: source inspection suggested the case, and the browser reproduced it.

The diagnostic HTML is archived under `source/`; the live WPT remains uncommitted for inclusion with the eventual standalone fix. `run-browser.py` expects that live test and the recorded local build. This commit contains discovery evidence only.
