# Refresh both SVG length conversion bases

**Proposal only.** The ordinary working-build diagnostic reproduced four persistent conversion errors: scalar/list50%→px stored100 instead of200 after a200→400 viewport resize; scalar/list100px→percentage stored50 instead of25. Later layout resolved these as100 instead of200 and200 instead of100 respectively. All six rows calibrated and repeated stably, with both getter controls passing. The referenced runtime and independent result review retain that evidence. This proposal has not been compiled, browser-tested or accepted.

## Standalone change

`standalone.patch` contains only `DOMSVGLength.cpp`, its private helper declaration in `DOMSVGLength.h`, and one WPT. The exact originals are from HEAD90 and do not depend on the separate SVG matrix repair or any prior CSSOM precision fix. `native.patch` contains the two native paths alone. Artifact-only patch replay produces exact candidate bytes and reverses to exact originals; it does not establish C++ compilation or browser efficacy.

`ConvertToSpecifiedUnits` still rejects read-only objects before invalid units. For differing source/target units it now requests `FlushIfNeeded(aUnit)` before acquiring any owner/item reference used for conversion. The helper selects Layout if either unit is percentage, otherwise Style if either is font-relative. GetValue/SetValue keep the existing default source-only behavior. Absolute-to-absolute and detached conversions perform no new document flush. The original arithmetic, finite checks, mutation notification and storage code is unchanged.

The source unit comparison uses `ToSVGLength()` by value. Its temporary ends before the flush; no `SVGLength&` or scalar animated-length pointer is saved across reflow. The helper's existing strong owner locals protect their own calls. After returning, conversion queries the current `mOwner` again and only then obtains `InternalItem()`. If flushing detaches a list item, the existing detached path is selected using the value copied by `RemovingFromList`; there is no assumption that the old internal list storage survives. General script/reflow lifetime safety is not formally proved here.

Same-unit conversion deliberately avoids the added flush. There is no new early return: the existing scalar distinction between already-set and unset base values, including its notification/initialization behavior, is preserved. Read-only/error precedence, detached absolute conversion, list identity shortcuts and later current-value reads are covered by the proposed controls; the removal control is before conversion, not a claim to simulate arbitrary list mutation during reflow.

## WPT scope and interpretation

The nine names in EXPECTED-TESTS match execution order. Four independent tests exercise source-percentage and destination-percentage freshness for scalar rect.x and list text.x. Each warms a visible200×100 viewport, changes only the host class to400px and calls conversion synchronously before any fresh `.value` or geometry read. Stored first/repeat factors are copied before forcing layout. A separate pre-flushed reference calibrates each expected factor, and the later resolved value checks persistence. Two getter tests, two error/identity tests, and one detached-list absolute test protect adjacent behavior. No animation, hidden content, viewBox, transform, unusual numeric range or font dependency is needed for the regression.

The private helper also correctly selects Style when the target is font-relative, matching its existing source-unit policy. That branch has source justification but no newly reproduced font-size defect is claimed. Existing conversion tests from the audit provide additional format/unit/font/percentage controls for a future paired run.

This correction retains document Layout flushing; it does **not** establish hidden-subtree provider readiness. Skipped-content unit conversion may require its own forced-layout policy, just as the existing `.value` getter may. It is outside this ordinary visible-size repair. No native viewport-factor trace was collected, so the exact cached-factor explanation remains source-supported correspondence to the observed outputs.

## Existing formal correspondence, no new proofs

The sealed14-theorem `SvgLengthConversion` model is reused unchanged:

| Native concern | Existing result | Remaining premise |
| --- | --- | --- |
| Need both bases current | `two_factor_agreement`, `ready_preserves` | Document flush must actually supply coherent current source and target factors for the admitted provider. |
| Preserve current user-space meaning | `sound`, `conversion_iff`, `unique` | Positive/nonzero target factor and native multiply/divide correspondence. |
| Same-unit shortcut | `identity`, `stale_identity_preserves` | Applies to list/already-set scalar representation, not scalar unset-state notifications. |
| Two observed error directions | `stale_source_witness`, `stale_target_witness` | Browser outputs match exact rational witnesses; native branch/factor sampling is not instrumented. |
| No all-future-context promise | `future_context_not_preserved` | The invariant concerns the context at conversion time. |

The native operations remain float-based. The rational model does not prove IEEE rounding/overflow, serialization, animation, ownership, reentrancy, notifier ordering or provider acquisition. It proves why source-only freshness cannot establish the required current-context invariant; it does not by itself certify this patch. No theorem count or canonical CSS coverage credit is added.

## Validation and next gate

Changed C++ hunks were formatted with the existing Mozilla clang-format binary. The PATH clang-format wrapper was unusable outside a Chromium checkout; no tool installation was needed. Exact artifact-only apply/reverse and Node parse-only validation passed, with owned temporary directories removed. No full C++ compile, WPT lint, browser execution, native working source change, parent index operation, or runtime epoch binding occurred. Next gate is an independently reviewed normalized-HEAD comparison with the four main cases and existing SVG length controls, preserving the current restored/installed working tree.
