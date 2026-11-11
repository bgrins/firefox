# Independent v3 terminal review

The optimized candidate compiled, and all 130 WPT assertion/harness records exactly preserve the baseline statuses, messages and expected classifications. The direct query fixture completed all 208 assertions in all 13 tasks: 199 PASS and nine FAIL, comprising five setup and four dependent result failures in the finite-scroll and named-range tasks. The harness correctly ended FAIL and the wrapper stopped. The 100 recascade assertions never ran; no transient recascade runtime acceptance is established.

Independent raw parsers checked lifecycle, inventory, order and exact saved-record correspondence. No extra callbacks or missing assertions were found. The two failed tasks have invalid setup for their expected samples; the other eleven tasks pass. This does not turn the failed experiment into an overall acceptance.

## Restoration and build provenance

REVIEW.json authenticates the frozen b81b1a21 manifest, actual build/source/config and sampled binary receipts. All four installed lint commands and the real binaries build exited zero. The WPT and query commands exited one, consistently with retained expected WPT failures and the nine direct failures. Full raw build diagnostics are retained in the source capsule; BUILD-LOG-SUMMARY.json distinguishes warnings and nonfatal monitor tracebacks from compiler errors.

The independent live scan verified all 9,378 app entries, 42,811 installed Mochitest entries, six extras, 14 source roles, tracked test/config files, original HEAD/index, and all 527 unrelated untracked path identities. Temporary fixtures, backups and lock are absent. All nine owned command groups are absent from the independent process snapshot. Root was explicitly notified that the live hold is released. This review performed no live mutation or browser execution.

## Fixture geometry

The query fixture is byte-identical to the accepted earlier query-v4 fixture. It specifies a 100px square scroller with overflow:scroll on both axes. The raw geometry assertion measures a 215px block scroll range instead of 200px. A 15px horizontal scrollbar reducing client height to 85px explains the entire mismatch: finite samples are 100/215 and 200/215; the view cover interval becomes [15,200], yielding narrow progress ((100-15)/185-.25)/.5 and expanded progress (50-15)/185. These match all measured setup values. The raw trace does not independently log clientHeight or establish which platform preference changed, so that environmental attribution remains an inference.

The minimal portable correction is overflow-x:hidden with overflow-y:scroll, retaining block scrolling while removing the unnecessary horizontal scrollbar. Keep all 208 assertions, timing values, geometry expectations and native bytes unchanged. Prepare that correction only in a fresh v4 capsule and preserve this failed v3 evidence. No native regression, new browser bug, public CSSOM repair or debug acceptance is claimed.
