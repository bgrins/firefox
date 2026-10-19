# Variable font axes and feature precedence: round 23

Static audit, 18 October 2026. No browser, native capsule, Gecko build, Git operation, or completed formal proof was run. The probe was syntax checked only. Source findings below are hypotheses and proof targets, not accepted bugs or claims about release impact.

## Recommended order

| Rank | Target | Evidence and first gate |
| --- | --- | --- |
| 1 | FreeType converts an unbounded axis number before clamping | Concrete numeric domain mismatch; extract the complete provider and run a float-cast-overflow sanitizer, then compare rendered endpoints on Linux/Android |
| 2 | An `opsz` face descriptor prevents automatic optical sizing | Concrete ordering mismatch against current Fonts 4; compare descriptor+auto with an otherwise identical auto face |
| 3 | Automatic optical size omits `font-size-adjust` | Known unresolved family, explicitly acknowledged in CSSWG 6190 and tracked by bug 1704039; add a calibrated rendering test |
| 4 | Ordered feature-map composition and mutation equivalence | Useful assurance contract; existing implementation handles the ordinary precedence seams, with backend and cache premises requiring explicit boundaries |

The round 17 font-matching and round 11 font-metrics reports were read and retained. This survey does not repeat the accepted matching score/11-degree repairs, zero-size inheritance, or metric-axis findings. It starts after a concrete face has been selected. Face selection, arbitrary font-file validation, shaping correctness and rasterization remain separate problems.

## 1. Clamp before narrowing to FreeType coordinates

`gfxFT2FontBase::SetupVarCoords` iterates the font's axes, initializes each coordinate to its default, then finds its tag in the resolved variation list. On a match it does:

```cpp
FT_Fixed val = v.value * 0x10000;
val = std::min(val, aMMVar->axis[i].maximum);
val = std::max(val, aMMVar->axis[i].minimum);
```

The retained FreeType header defines `FT_Fixed` as signed long. Both 32-bit and 64-bit destinations are exceeded by the finite binary32 representation of `1e20` multiplied by 65536. That multiplication is itself finite. C++ floating-to-integer conversion is undefined when the truncated value is outside the destination range; a later clamp cannot establish definedness retroactively. [C++ conversion rule](https://eel.is/c++draft/conv.fpint).

### Complete input route inspected

`VariationValue<Number>::parse` accepts an ordinary `Number`; `Number::parse` uses `AllowedNumericType::All`. Its inline `NoCalcNumber::get` bounds at binary32 extrema, not the font axis or fixed-point integer range. `FontSettings::to_computed_value` sorts/deduplicates tags but preserves the numeric value. The longhand's Gecko field is `mFont.fontVariationSettings`; `nsFont::AddFontVariationsToStyle` copies it to `gfxFontStyle::variationSettings`. For descriptors, `parse_for_font_face_rule` only additionally requires parse-time resolvability; `Servo_FontFaceRule_GetVariationSettings` transfers each resolved float into the native array. `FontFaceImpl::GetAttributesFromRule`, the user entry constructor, and the loaded platform entry copy preserve those settings.

`gfxFontGroup::GetFontAt` obtains the selected loaded platform entry and calls `FindOrMakeFont`; cache misses invoke its backend `CreateFontInstance`. `GetVariationsForStyle` applies high-level values, replaces them from face descriptors, then from the element's variation property. It does not clamp low-level custom-axis values. The Linux `gfxFontconfigFontEntry::CreateFontInstance` and Android `FT2FontEntry::CreateFontInstance` clone an FT face, obtain `GetMMVar()`, and call `SetupVarCoords`. A matching axis is needed: an unknown tag is ignored before any conversion. A loaded downloadable variable font avoids installed-family matching and non-CSS weight-scale exceptions. Failure to clone a face or obtain MMVar prevents reaching this operation and must be recorded by a native harness.

The contract is that supported values outside a font's interval clamp to its nearest endpoint, while unsupported tags do not affect other settings. [CSS Fonts 4 variation settings](https://drafts.csswg.org/css-fonts-4/#font-variation-settings-def). The Mac `CreateVariationDictionaryOrNull` and `CreateVariationTagDictionaryOrNull` instead clamp in double before constructing CFNumber values; this particular narrowing finding does not apply there. DirectWrite forwards floats to its resource API; its full platform clamping behavior was not proved. HarfBuzz receives the variation list separately for shaping, so a disagreement between FT coordinates and shaping coordinates is an additional observable risk, not a demonstrated effect.

### Discriminating gate

The retained WPT `variabletest_box.ttf` has a real `UPWD` axis [0,350], default0. Its A glyph moves from a lower box at0 to an upper box at350. Use ordinary-sized text and test `"UPWD" 1e20` against350, and `-1e20` against0. Do not infer glyph changes from element width: this fixture changes outlines. Controls: endpoints,175,351,-1, unknown tag+175, a huge earlier duplicate overridden by175, and property175 overriding a huge descriptor. Run property and descriptor routes, mutation175→huge→175, and fresh equivalent elements. Capture font load status, computed values, matched fixture identity and actual glyph pixels. The supplied page provides the static pairs; dynamic sequences are proposed next work.

A source-bound native test should retain the complete `SetupVarCoords` body and actual `FT_Fixed` type, capture the complete coordinate vector at `FT_Set_Var_Design_Coordinates`, and include both ABI widths. Use `-fsanitize=float-cast-overflow` explicitly; plain UBSan defaults should not be assumed to cover this conversion. Do not assert that every compiler maps overflow to the minimum: there is no defined result. This audit executes only arithmetic diagnostics, not that native gate.

### Formal contract and cost

For each valid signed 16.16 font interval L≤D≤U and finite CSS binary32 x, define a reference coordinate by clamping x to [L/65536,U/65536] before bounded quantization. Prove totality, endpoint saturation, monotonicity, in-range error <1/65536, tag noninterference, default preservation and iteration-order independence for unique resolved tags. A native refinement must additionally cover multiplication precision and endpoint rounding: simply moving a clamp around a float expression is not automatically safe at the largest signed fixed-point endpoint. Model 32/64-bit long separately and retain the font-table validity premise. Bridge cost: small for the full helper plus resolved settings, medium for parsing/backend admission. Mutants: cast-before-clamp, swapped bounds, first/last duplicate confusion, default instead of selected value, and wrong axis lookup.

## 2. Automatic optical sizing versus the face descriptor

Current Fonts 4 lists face `font-variation-settings`, then `font-optical-sizing`, then the element `font-variation-settings`, in ascending precedence. [Feature and variation precedence](https://drafts.csswg.org/css-fonts-4/#feature-variation-precedence).

`nsFont::AddFontVariationsToStyle` sets `autoOpticalSize` for `auto` unless the element property already contains `opsz`. `gfxFontEntry::GetVariationsForStyle` merges the descriptor into the list, then the property, and finally adds automatic `opsz` only if the list has no such tag. Consequently a face descriptor `opsz96` suppresses auto at48px even though no property override is present. This is a source prediction. The general statement that low-level settings override high-level properties must not obscure the specification's distinction between a face descriptor and an element property.

The clean reference uses two families backed by the same bytes, one with descriptor96 and one without; both receive size48 and `font-optical-sizing:auto`. Compare their B glyphs after calibrating explicit24 and96 as visibly distinct. This avoids imposing a particular px/pt conversion policy on a different browser. `none` retaining96 and the element property24 overriding both are controls. Change auto↔none and descriptor96↔24, comparing fresh faces and elements after each step. The existing WPT optical test covers property-vs-auto, while descriptor tests cover low-level property-vs-descriptor; the inspected tests do not combine descriptor `opsz` with `auto` in a decisive reference.

The exact policy is not wholly numeric: `auto` permits other display signals and does not mandate a universal formula. Independent normative review must adjudicate whether a UA opting into automatic `opsz` can legitimately treat an explicit descriptor as an opt-out despite the ordered algorithm. No dedicated resolution for that exception was found in the bounded search. Do not accept this as a defect solely from an abstract ordered-map model.

A useful conditional theorem treats the UA automatic choice as an independent admitted function A(face, usedSize, environment): the final `opsz` is the property value when present, otherwise A when automatic application is selected, otherwise the descriptor/default. Prove later-stage dominance and independence of an earlier descriptor when overwritten; preserve unknown axes and explicit `none`. Bridge cost small for merger/flags, medium for real axis discovery. The Mac default-value workaround deliberately perturbs values near the font default by0.01; avoid those neighborhoods in the browser gate and retain it as a separate platform premise.

## 3. `font-size-adjust` and the automatic coordinate

`autoOpticalSize` comes from `nsFont::size.ToCSSPixels()`. `GetVariationsForStyle` multiplies it by the face's descriptor `mSizeAdjust`. Actual metric normalization from the `font-size-adjust` property happens later in backend metrics initialization. On Mac, the variation CGFont is instantiated before `InitMetrics`; the latter can replace `mAdjustedSize` after measuring an aspect ratio, without updating `autoOpticalSize` or reconstructing its variation coordinates. DirectWrite and FreeType also establish variation instances separately from later metric normalization; HarfBuzz's `CreateHBFont` asks the same merger for coordinates even though its scale uses `GetAdjustedSize()`.

CSSWG6190 resolved automatic optical sizing against used size accounting for both adjustment mechanisms. Its first comment already identifies Gecko's property interaction as broken. Bug1706077 fixed the descriptor interaction; open bug1704039 records the broader resolution. This is **known prior art and a possible remaining implementation gap**, not a newly discovered issue. [CSSWG6190](https://github.com/w3c/csswg-drafts/issues/6190), [bug1706077](https://bugzilla.mozilla.org/show_bug.cgi?id=1706077), [bug1704039](https://bugzilla.mozilla.org/show_bug.cgi?id=1704039).

Use a positive-size fixture with a verified size-independent metric ratio, avoiding the prior zero-size and wrong-axis findings. The retained font has OS/2 sxHeight500/upem1000. That table value is an input premise, not browser proof of its effective metric. Calibrate 24px with `font-size-adjust:1` against48px without adjustment while holding explicit `opsz24` fixed; only proceed if glyph scale agrees. Then compare automatic optical sizing for those two cases. A descriptor `size-adjust:150%` at32px against48px supplies an existing-behavior control. Explicit property opsz must stay invariant under adjustment. A font whose metrics vary with opsz introduces a fixed-point/ordering problem; do not assume iteration or convergence without a separate contract.

The proof can initially quantify over a positive constant metric ratio r, finite adjusted size U=quantize(S·a/r), and an independent automatic policy A(U). Prove automatic policy receives U, whereas a later explicit property does not depend on U. Include device/CSS conversion, descriptor scaling and rounding as distinct operations. Bridge cost medium/high because a metric provider may itself depend on variation coordinates. Current issue13331 proposes an optical multiplication factor; it is open and is not an implemented requirement. Unit disagreements (bug2001726) and old CoreText regressions (bug1856035) are separate from this omission.

## 4. Feature-map and dynamic assurance boundary

The ordinary OpenType feature order is implemented in two stages. `nsFont::AddFontFeaturesToStyle` emits high-level kerning, numeric, East Asian and ligature features; it inserts tag0 as a sentinel before the element's low-level features. `gfxFontShaper::MergeFontFeatures` starts with face descriptor features, then caps/position and resolved alternates, then traverses that style list. Optional ligatures are disabled at the sentinel when letter spacing requires it; later low-level values can re-enable them. The empty-list path also disables ligatures. `FontTag` parsing restricts author tags to four printable ASCII characters, so tag0 is an internal delimiter rather than a legal author collision.

Computed `FontSettings` uses a stable tag sort, then swaps equal-tag entries in `dedup_by` to retain the last occurrence. Both feature and variation properties use that path. Variation interpolation consumes these canonical lists and rejects mismatched tags through the tagged value/list animation machinery. Face descriptors travel through a separate ordered-list bridge; merging replaces repeated tags in order. Do not incorrectly require descriptors to have the same computed canonical representation as properties.

HarfBuzz's `ShapeText` feeds the merged map to `AddOpenTypeFeature` and later applies script-specific kerning/vertical policy. Graphite passes the map through its feature lookup/sandbox adapter. CoreText's AAT path only consumes the merger for small-caps selection and uses separate feature flags for ligature suppression; it is not a complete execution of the same OpenType feature-map contract. Restrict a first proof to map production and the OpenType consumer, or model backend capability/translation explicitly. Caps/position synthesis and required shaping features are further boundaries. No shaping proof is claimed.

Dynamic property differences are present in `nsFont::CalcDifference`; `nsStyleFont::CalcDifference` requests reflow. `gfxFontStyle::Equals` includes feature/variation arrays, optical size and adjustment fields. `FindOrMakeFont` keys the cache by entry/style/range. Thus the simple hypothesis that these values never invalidate layout or distinguish instances is rejected. FontFace setters call `DescriptorUpdated`, update user attributes, mark sets dirty and trigger generation-based font group refresh. Loaded platform-entry settings are copied at load time, so a future mutation proof must establish propagation into that entry too; a generation-only theorem is insufficient. Existing `fontface-descriptor-updates-2.html` inspects descriptor mutation and has a known style/family failure, but does not establish all rendered-axis transitions.

Proposed theorem: folding independent ordered layers yields one value per tag equal to the last contributing layer, including the spacing layer; no tag outside a layer's domain changes. Establish sentinel erasure and sorted unique output, not just equality of list lengths. Then, under complete provider update and cache-key premises, prove any finite mutation sequence ending in a given logical state yields the same map as a fresh state. Use existing Lato ligature WPT fixtures, duplicate-tag permutations, both spacing states and explicit overrides; add rendered descriptor mutations only after provider tracing. Bridge cost small/medium for the merger, larger for font entry lifecycle. Mutants: descriptor wins last, missing delimiter, spacing wins over explicit property, unstable dedup and stale provider version.

## Coverage ledger

| Boundary | Result |
| --- | --- |
| High-level weight/width versus explicit ranges | Descriptor clamp precedes low-level overrides; auto flags bypass descriptor clamp; no new ordinary ordering mismatch |
| Default/omitted descriptor values | Existing auto/default variable WPTs retained; do not reinterpret normal matching as forced normal axis value |
| Style mapping | Ital and slnt are chosen by mutually exclusive branches; CSS/OpenType slant signs are inverted; arbitrary italic fallback remains outside this audit |
| Duplicate tags/property canonicalization | Stable last-wins path found; useful invariant, no new mismatch |
| Custom/unsupported axes | Backends enumerate available axes; unknown tags need not poison supported settings |
| Large finite values | Rank1 FreeType conversion precedes clamping |
| Descriptor/property/automatic opsz | Rank2 ordering candidate; explicit property override works in inspected source |
| Optical size and adjustment | Descriptor scaling exists; rank3 property normalization is known unresolved prior art |
| Feature/variant/spacing composition | Ordinary OpenType path matches inspected layer order; rank4 proof target |
| Dynamic values and cache identity | Property invalidation and equality fields exist; full descriptor lifecycle not proved |
| Named instances, avar2, hidden axes, AAT/Graphite translation | Separate capabilities/providers; no blanket conformance claim |
| Raster metrics, hinting, required script features, fallback | Not proved; fixture calibration and backend gates required |

## Tests, history and integrity

`WPT-METADATA.json` records23 selected tests plus15 references,38 total HTML files, and three present individual metadata files. All are NOT RUN. `at-font-face-descriptors.html` has extensive expected failures; descriptor04 has an Android14 conditional expectation tied to bug1982904; descriptor-updates2 has the known style/family expected failure. Absence of metadata is not fresh PASS evidence. Other directory/global metadata is not exhaustively evaluated here.

The optical WPTs exercise defaults, explicit property overrides and descriptor size-adjust; the four descriptor tests cover merging and fractional values. The feature resolution tests already exercise a substantial precedence matrix, so add targeted controls or extracted contracts instead of presenting their basic combinations as missing coverage. No inspected rendering test used `UPWD` at values beyond fixed-point conversion ranges.

Retained primary history includes CSSWG6190/comments,6196,13331 and an opsz/descriptor search; Bugzilla optical summary search50 records, Core variation search180, and font/clamp search5. An initial unfiltered variation search hit its150 limit and is retained as incomplete. These are bounded searches, not evidence of novelty. The known dedup repair is bug1810717; descriptor mutation test history is bug2019277; existing platform optical regressions and decimal Android coverage are separately identified. No exact rank1/rank2 duplicate was found in these results.

`probe.html` is a standalone, unexecuted22-row visual page with five downloadable faces and two deliberately unequal calibration pairs. Serve this artifact directory, await `window.ready`, inspect `window.probeResult`, and compare screenshot glyph crops. It records rectangles and computed values but does not pretend those measurements compare pixels. Font load failures are setup errors. Numeric adjustment rows require the separate ratio/scale calibration; the fixture's equal advance must not be used as proof of an optical shape change. Keep runtime evidence in a new directory after freezing this capsule.

`static_checks.py` checks source operation order, eleven binary32/fixed-range arithmetic witnesses, and four directly decoded font axes. It does not execute C++, parse CSS in a browser or prove the specification. `verify.py --checks` first authenticates every closed file before invoking that helper and compares the result to the frozen receipt. `--live PATH` optionally checks recorded implementation inputs; historical reports and tests remain snapshot evidence. The optional live check detected the parent's concurrent removal of an unused math.h include from gfxFontEntry.h; `LIVE-DIVERGENCE.json` retains that exact delta. The other35 implementation pins agreed at that check. The snapshot was preserved, and the strict live check intentionally continues to reject that changed header. Full source snapshots and origin hashes define this review even if unrelated branch edits subsequently move HEAD. The frozen capsule is relocatable; toolchain/browser reproducibility is not claimed.

Searchfox discovery was used throughout. Several redirected calls failed DNS in the sandbox and later direct calls succeeded; the retained successful outputs identify symbols without fabricated permalinks. `webspec-index` was unavailable, so current primary drafts and issue JSON were fetched directly. Applicable specmap guidance was used, with metadata interpreted as expectations rather than runtime results.
