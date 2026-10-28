# Registered-value normalization source review

Verdict: one concrete correction required in the reviewed seven-file draft before experimental execution; no additional concrete blocker found in the bounded six-file review. This is not compilation, runtime validation, normative closure, or native verification.

## Finding: preserve zero effective-zoom behavior

The captured `ContainerSizeQueryResult::resolve_size` divides by `zoom.value()` whenever the registered-value scope is active. `Zoom::unzoom` explicitly preserves its input for zero effective zoom, and `Zoom::compute_effective` multiplies float zoom values. The new raw division therefore loses an existing defensive behavior and can produce infinity or NaN when that product is zero. Retain the zero/ONE guard while doing the division in f64; casting the whole size through f32 would change the intended ordinary arithmetic. The reviewed draft is preserved in `container-rule-reviewed.rs`; a subsequent correction must be checked separately.

## Six-file review

The Context Cell scope saves its prior value and restores it through Drop, including nested calls and unwinding; all constructors initialize it. The outer registered `Value` conversion retains the derive-equivalent generic trait bounds and fieldwise conversion, URL data, attribute taint, and reverse conversion. It does not rewrite builder zoom or font state.

Absolute length conversion bypasses zoom only inside this scope. Font-relative conversion first retains existing dependency and metric work, then uses existing Zoom::unzoom. Current and inherited font bases are represented in current effective zoom; inherited font resolution applies effective_zoom_for_inheritance. Root-relative caches likewise acquire current zoom on the existing paths. This supports the chosen placement but is not an exhaustive proof of platform font metrics or float behavior.

Viewport conversion removes zoom before the existing app-unit truncation, preserving the existing truncation convention. All six numeric style-range operand conversions are now scoped. Custom CSSOM length and length-percentage resolution skips ordinary unzoom. That skip requires every registered producer to supply canonical values, so producer completeness remains an acceptance prerequisite.

The inspected custom-animation paths clone computed custom values or invoke registered specified-value conversion; they do not establish a new regression through the ordinary CSSPixelLength::ToAnimatedValue unzoom. CSS-wide values continue copying stored initial/inherited computed values. No change to URL/taint or from_computed handling was identified in this review.

## Seventh-file review

The three container result constructors pair each available physical axis with the queried container style's effective zoom. Merge preserves the first available tuple per axis, so different ancestor sources retain their individual zooms. Logical and min/max getters normalize each selected axis before comparison; viewport fallback remains a raw viewport size. Searchfox identifier searches found only the implementation and updated specified-length caller uses for the four getters.

Outside the registered scope, Au-to-f64 conversion is moved into the getters without adding an intermediate f32 conversion. For finite app-unit sizes, min/max of converted values preserves the old ordering. The existing target-writing-mode selection and lookup scheduling were not redesigned. The separately observed logical cqi/cqb scheduling issue is therefore not fixed here.

A guarded experimental build is useful after the zero guard is corrected. The source-container zoom interpretation is still an experimental contract supported by the parent's observations; this review does not claim full container-unit semantics, resolution of ordinary bug1894104, or complete producer coverage.

## Evidence and limits

`INPUT-PINS.json` binds the exact proposal source bodies available during this read. The v2 package was under preparation; its source snapshot is the reviewed object, not a claim that a final package was sealed. `SEARCHFOX.json` and the captured upstream body bind the Zoom API evidence. Searchfox showed Copy and public value(); the zero guard is in the captured body. Getter searches completed as 53be4b/0 (width/inline), d2d0fb/0 (height), and 8c36e9/0 (block). Candidate diff read:91be13/0; constructor/merge read:b3b4ac/0; upstream read:321dcf/0; saved source:15186a/0. The initial network-limited source attempt failed DNS and was not used as evidence.

No native edits, browser run, build, Git/index/epoch mutation, or new accepted-fix/coverage credit occurred. The source review does not prove float inverses, matrices, all producer paths, font platform behavior, or parser correspondence. Peer producer/math review is separately sealed in css-registered-zoom-normalization-boundary-review-v1 (FILES SHA f2c0bb722f58785749b3d075afe07f89b3bed18690960a66bac12d2953a3ab98).
