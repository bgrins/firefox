# Client dimension precision probe

Unrun standalone diagnostic for the earlier float-conversion loss in `clientWidth`/`clientHeight`. It is a distinct conversion policy within the integer-geometry precision family, not an accepted fix or additional counted bug. No native/browser/build/index action occurred. The current offset+scroll comparison is untouched.

The eight ordered cases are x/y × content size 16/16777200 × end padding 0/17. The page copies first/repeat, reset-padding and restored-padding observations from the same empty target. It reads client dimensions before scroll dimensions, then records zero client-origin controls, exact DOMRect/client rectangles, computed styles, parent identity and host geometry. “First” means the first collection sequence after mutation, not independently the first flushing query for every getter. Reset has one observation; first/repeat and first/restored stability are separately checked.

The validator is adapted from sealed `css-cssom-scroll-client-proposal-v1`, with only the size and padding constants changed. Exact style, target rectangle, one-box rectangle, host geometry, viewport, scroll position and parent/empty-target checks remain mandatory. Offset widths/heights and the client/scroll values under investigation never certify their own expected geometry. Uncalibrated phases have no observer pass/fail verdict. Require all eight rows and 32 phases calibrated, eight repeat-stable and eight restored-stable before interpreting results. Preserve failures instead of relaxing tolerances or inferred sizes.

`probe.html` needs no WPT environment. It renders JSON and exposes `window.clientPrecisionProbeResult`; under HTTP(S) it also posts the same payload to `/result`. A future root-owned runner can use the existing reviewed local capture helper. `validate.py` exposes `validate(payload)`; no browser runner is included here.

## Source conclusion

Searchfox discovery of `Element::GetClientAreaRect` was checked against explicit HEAD `90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e`; SOURCE-PINS.json binds five complete source bodies, and SOURCE.txt retains only the relevant excerpts. The transient live native source was not read.

All four `Element.h` client getters currently call `CSSPixel::FromAppUnits(GetClientAreaRect().field).Rounded()`. `FromAppUnits` converts the signed32 coordinate to binary32 and divides by 60; `CoordTyped::Rounded` applies floor(value + 0.5) using a double literal. The proposed witness loses precision before that final floor: exact 1006633020 app units becomes binary32 1006633024, whose binary32 quotient is 16777218. The intended integral dimension is 16777217. This differs from the 8388609 offset/scroll witness, where the final float half-add caused the error and client controls stayed correct.

For the empty, overflow-visible block target, source inspection selects the padding-rectangle path of `GetClientAreaRect`, with its existing frame-position subtraction and `EffectiveZoom().Unzoom`. Scroll-container and root viewport paths are different existing branches. This is a source applicability argument; no native branch was traced for this new fixture.

The constituent declarations are separately exact: 16777200×60 = 1006632000 and 17×60 = 1020. Their sum 1006633020 and the target endpoint including the 40px host position, 1006635420, both remain below named nscoord_MAX 1073741823, as well as signed32_MAX. The dimension is therefore below the earlier known DOM rectangle range-cap threshold. No obvious native cap obstruction appears on this chosen path. This arithmetic does not prove which native values will be produced: computed-style serialization, layout sizing and DOM observation must still pass the unchanged strict runtime calibration.

## Possible conversion boundary

An exact integer implementation of the existing ideal client policy is:

```cpp
const int64_t bias = aCoord >= 0 ? 30 : -29;
return int32_t((int64_t(aCoord) + bias) / 60);
```

C++ truncation then equals mathematical floor((aCoord + 30)/60), including negative half ties toward positive infinity: -30au maps to 0, whereas the offset/scroll helper maps it to -1. The numerator lies within [-2147483677,2147483677], and the quotient within [-35791394,35791394] for every signed32 input. Promotion precedes bias addition, so INT32_MIN is handled without narrow negation. The independent reviewer is preparing the corresponding compact Lean proof; this artifact adds no duplicate model.

The helper must receive the raw `nscoord`, before `FromAppUnits`; changing only `Rounded()` after float conversion cannot recover the lost integer. Because these four getters are inline in `Element.h`, a helper local to `Element.cpp` requires moving their definitions into that file and keeping declarations (including their existing script-running annotations) in the header. Each implementation would still call `GetClientAreaRect` exactly once and convert its same field. No change to padding, scrollport/root sizing, position subtraction, existing branch-specific unzoom, or the generic gfx floor helper is needed. An alternative shared CSS utility affects a larger caller set and is unnecessary for this bounded proposal.

This preserves the ideal client tie policy and corrects float-induced deviations; it does not promise every historical large output remains identical. Moving inline getters out of line introduces a code-generation/performance consideration to review separately. The four-getter arithmetic scope is source-supported, but this probe tests only large width/height inputs. Its clientLeft/clientTop values are zero controls, not evidence of large reachable origin defects. Earlier sizing/unzoom errors would remain outside the conversion repair.

The official CSSOM View draft read for the preceding audit (8 October 2026 draft, read 23 October) defines the non-root block client dimensions from the unscaled padding edge, excluding scrollbars. This fixture has neither borders nor scrollbars. Its exact integral-size oracle does not select a fractional rounding interpretation; the proposed tie behavior deliberately preserves the existing client implementation's ideal policy. [CSSOM View, section 6](https://drafts.csswg.org/cssom-view/)

## Predictions and static checks

With old converters, six first client rows should match and the two large-plus-17 rows should report 16777218 instead of 16777217; their reset values should be exact. Old scroll metrics share the earlier float loss and are predicted to have the same two mismatches. If the separate offset+scroll repair is applied, scroll should match all eight while client remains six. `PREDICTED-OLD-SUMMARY.json` and `PREDICTED-OFFSET-SCROLL-FIX-SUMMARY.json` are synthetic validator inputs, never browser evidence.

`python3 artifacts/css-cssom-client-precision-proposal-v1/check.py` checks JavaScript syntax and synthetic validator controls, including bad geometry, parent, reset style, roster and boolean metric. `arithmetic.py` retains source-shaped binary32 predictions and a small exact-integer boundary check; it is not native execution or an IEEE proof. No compiler products or target directories are created.
