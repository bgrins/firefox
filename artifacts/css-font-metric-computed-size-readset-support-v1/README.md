# Computed-size facet implementation support

This package supplies exact readset evidence and twelve proposed test inputs for the c6c0cf39 successor. It contains no implementation, executed new tests, native matched-rule trace, or repair claim. It supplements the sealed computed-size design; the full variable-length typed-attribute case remains the required end state.

## Fixture prefix evidence

The frozen iframe uses a button and a single author `#target` rule with literal `font-size: 20px` / `30px`, plus `--len: 1em`. The first case gives Appearance a typed attribute containing `var(--len)` and sets Family to serif. There is no author font-size rollback or variable in this rule.

The locally captured UA button rule supplies normal `font: -moz-button`. Its `@appearance-base` block supplies normal `font: inherit`; neither excerpt makes font important. These lower-origin declarations cannot displace a reached normal author absolute-size winner. This is a bounded source relationship, not proof of the actual entire native prefix: the diagnostic did not log matching rules, priorities, user sheets or all eligibility flags. The certificate must inspect the actual retained prefix. A higher skipped APPEARANCE_BASE declaration rejects certification; a lower unvisited one does not by itself do so. Revert chains retain all reached decisions.

## Actual conversion and effects

Use `NoCalcLength::to_px_if_absolute()` only to classify the retained operation, then use the normal FontSize conversion/application. `FontSize::to_computed_value_against` initializes keyword metadata to None for an absolute length, applies applicable zoom through the actual length/context APIs and quantizes the result. `Context::maybe_zoom_text` reads final XTS and device text zoom. Registered-value conversion context must not replace property conversion context.

The generated dependency comment explicitly explains XTS→Family: Family can recompute keyword sizes, and inherited unscaling normally follows it. A bounded absolute-size route can instead finish selected XTS and inherited unzoom before fresh FontSize, then rely on fresh keyword None to make later Family/XLang keyword recomputation return. This requires final selected/default XTS, not merely a temporarily matching enum. An absent declaration does not manufacture a seen bit or hook; deferred whole-property finalization must not replay unzoom.

Early XLang can update initial family and inherited keyword size. Early minimum-size ratio can clamp inherited used size. The exact Gecko `set_font_size` overwrites mScriptUnconstrainedSize, mSize, mFont.size and keyword metadata, so those pre-size numeric writes do not survive fresh absolute publication. Preserve the hooks and run FontSize's actual final minimum-size hook. Its language/preferences/ratio and zero-size behavior remain required; em's computed-size read is distinct from the used font-size clamp. The Math hook exits for non-Math keyword metadata; later family prioritization changes font selection, which is still required by metric consumers.

## Completion and lifetime boundary

The facet must not certify generic NonCustom(FontSize), ordinary ensure, XTS completion or metric readiness. A typed unit reply may consume it while the retained ordinary publication remains pending. The exact selected operation, eligibility/read generations, parent/device zoom and already-run effects belong to the certificate. Later flag changes currently clear completion; they do not prove that an already-consumed value stayed valid. Either the recorded prefix/readset is stable across the flag change, or early consumption was unsound. Session reset currently rejects nonretirable nodes and owned work: preserve that obligation and transfer no dangling Tarjan indices.

`TEST-INPUTS.json` contains proposed positive/negative inputs, including prefix eligibility, rollback, zoom ordering, zero/minimum sizes, defaults, stronger consumers and reset. These are not test results. No whole-scheduler proof or genuine-cycle policy is supplied.

## Authentication and discovery

`SOURCE.json` preserves sixteen exact local excerpts and `REFERENCES.json` pins twelve inputs. Searchfox discovery used indexed revision 28b7a7bffb5f82828143d9ad63839ad263b598be; local bodies are authoritative for this branch, not assumed identical to that index. Relevant discovery receipts: 27c48d/89cb29 (UA rules), 45fc74/952067 (zoom), 9dfe57/a71a48 (XTS), 473a85 (setter). Exact local reads: 16f5d1/3923e3/5a91a4/460f7b/9defca. The sealed design supplies the earlier minimum-size native consumer captures. Only this new artifact directory was written.
