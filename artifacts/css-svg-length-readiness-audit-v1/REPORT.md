# SVG length conversion readiness audit

**One source-backed, unexecuted ordinary-size lead:** `SVGLength.convertToSpecifiedUnits()` appears able to commit a conversion using an old SVG viewport after a synchronous visible host resize. The ordinary `.value` getter is the useful differential control. This is distinct from the pending hidden GetCTM/GetScreenCTM proposal: no skipped content or matrix API is involved.

## Exact source chain

All 14 source files in SOURCE-PINS match explicit commit `90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e` and the working tree when read. SOURCE.txt retains selected exact spans and file hashes. Searchfox supplied new symbol/path discovery; local old-HEAD reads established the actual source role. No source writes occurred.

| Operation | Relevant source behavior |
| --- | --- |
| `DOMSVGLength::GetValue` | Calls `FlushIfNeeded` before resolving its scalar/list length. Percentages request document Layout; font-relative units request Style. |
| `DOMSVGLength::ConvertToSpecifiedUnits` | Validates read-only/unit errors, then calls scalar `SVGAnimatedLength::ConvertToSpecifiedUnits` or list `SVGLength::GetValueInSpecifiedUnit`; no `FlushIfNeeded` call. |
| Scalar conversion | Resolves old and target pixels-per-unit before constructing the change notifier; then stores the converted factor/unit. No Layout flush in this calculation. |
| List conversion | Constructs `SVGElementMetrics`, resolves old and target unit factors, then creates its change notifier and stores the converted length. No Layout flush in the conversion. |
| Percentage factor | `SVGLength::GetPixelsPerUnit` selects `GetAxisLength()/100`; `SVGElementMetrics::GetAxisLength` calls its viewport's `GetLength`. |
| Context | `EnsureCtx` → `SVGElement::GetCtx` → nearest viewport ancestor; these traverse element ancestry, not layout. Both rect.x and text.x have X directionality. |
| Outer viewport, no viewBox | `SVGViewportElement::GetLength` reads `mViewportSize`; `SVGOuterSVGFrame::Reflow` updates it through `SetViewportSize` after computing the new content viewport. |

The wrapper is obtained and warmed before the host mutation, avoiding any claim about getter construction causing a flush. The percentage-to-px route needs the **source** unit's current viewport; px-to-percentage needs the **destination** unit's current viewport. Merely inserting today's source-unit-only `FlushIfNeeded()` would not cover the second case. This is a repair constraint, not an implementation proposal.

## Falsifiable diagnostic

`probe.html` is an unexecuted standalone six-row diagnostic: scalar rect.x and list text.x, each with `.value`, 50%→px, and 100px→percentage. Each fresh target is visibly laid out in a 200×100 host, whose SVG fills it and has no viewBox. The warm value is 100. A synchronous class change makes the host 400×100, immediately followed by the selected operation; there is no await, computed-style read, geometry query or `.value` read between mutation and conversion. First/repeated stored-factor reads are copied before a forced geometry query. Each row subsequently records the resolved value, a separately constructed pre-flushed 400px reference conversion, and a restored 200px calibration.

Expected first observations are 200, 200 and 25 respectively. The source hypothesis predicts conversion observations 100 and 50, while `.value` controls return 200. Conversion can persist the wrong representation even after layout is later updated; the after-query record distinguishes that from a transient stale getter. These predictions are not recorded browser outcomes. Any warmed/calibrated case returning the correct conversion immediately falsifies this proposed witness for that path; unexpected geometry, unit types or reference results make it inconclusive.

The fixture emits complete JSON to a visible pre, `window.results`, and `/result` when served over HTTP. No runner or installation is supplied, and no browser/lint execution is claimed. Parent can reuse the controlled browser capture only after independently validating the payload/ownership and source epoch.

## Negative findings and boundaries

- Absolute-unit conversion has no viewport dependence; no stale-viewport lead there.
- `valueInSpecifiedUnits`, `unitType`, and serialized attributes are representation observers. They need not change just because the containing viewport changes.
- ViewBox-backed user coordinates legitimately remain fixed under CSS resizing; confusing those with CSS pixels would create a false positive. Inner SVG dimensions also take a different provider branch. Neither is the proposed witness.
- The visible `.value` path already requests Layout for percentages. Hidden layout forcing remains an adjacent question but would share the existing matrix provider concern, so it is deferred here rather than duplicated.
- Font-relative conversion can involve style resolution inside the font-metric provider. This audit does not infer a font-size bug merely from the missing outer flush.

The three existing tests pinned in TEST-PINS cover font change, non-px source units and percentage directionality. They use viewBox-fixed bases and/or explicit pre-conversion value/layout reads; the font-change file mainly mutates the font after converting. They do not establish this synchronous CSS-viewport-resize history. Metadata presence/absence is retained only as source context, not a fresh test result.

The readiness obligation is concrete: before committing a relative-unit conversion, obtain current bases required by **both** units. Existing abstract ProviderObservation success/readiness machinery does not prove this native mutating API's provider acquisition or preservation of represented user-space value. No additional theorem, accepted bug, repair, release novelty or security claim is added.
