# Independent review: zoom and line-height-relative units

## Verdict and priority

| Family | Independent verdict | Existing-work boundary | Recommendation |
| --- | --- | --- | --- |
| Implicit inherited absolute line-height consumed by `lh` | **Repair warranted**, six reproduced parameter cases | Known zoom inheritance area, explicit eager-line-height source TODO, bug 1887627 and its resolved implementation dependencies; not six new bugs | Separate scheduler/normalization fix and WPT; larger formal bridge |
| `rlh` on a zoomed root | **Repair warranted**, two reproduced zoom states | Extends the round-2 lead and the root-provider repair in bug 1942329; no exact zoom-specific duplicate identified | Address first: smaller source-selection/units boundary, separate native/WPT commit |

These are two source-supported defects observed in the project's local build, **not release-browser reproductions**. No native patch, WPT execution, browser run or proof implementation was performed by this review. Parent owns final patch approval and exact original/candidate gates.

## Independent raw-data review

The independently written `checker.py` authenticates receipt SHA256 `593dbbc8bc26cacf707aeaadd5f8afba2c32008c324c1609b0d161bfbd46e888`, served probe bytes and driver identity. All **42 before/after pins** are equal; all **12 absent-metadata observations** are stable. Native/test snapshots match the historical runtime identities. No current binary is compared to a historical executable hash.

The checker ignores embedded expected values while deriving its own expectations from fixture inputs, then compares those embedded values as a consistency check. It rederives all 49 rows: **8 discrepant rows, 41 controls, 26 discrepant numeric fields**. Six rows have both width/padding and their geometric consequences wrong; two have root `rlh` padding wrong. Source stage formulas independently explain every actual value. These calculations are handwritten rational diagnoses, not native execution or formal verification.

The recorded browser is Firefox **160.0a1**, macOS, build ID **20261018145149**, headless with DPR preference 1. The standards-mode iframe reports support for zoom/lh/rlh. It creates fresh inherited fixtures across three parent zooms, three local zooms and five inheritance policies, then changes one root through zoom `1 → 2 → 0.5 → 1`.

| Case | Required unscaled length | Recorded unscaled length |
| --- | ---: | ---: |
| Implicit inherited 20px line-height, local zoom 0.5 | `1lh = 20px` | `40px` |
| Implicit inherited 20px line-height, local zoom 2 | `1lh = 20px` | `10px` |
| Explicit inherit/unset/20px or numeric line-height controls | `1lh = 20px` | `20px` |
| Root 20px line-height, zoom 2 | `1rlh = 20px` | `40px` |
| Root 20px line-height, zoom 0.5 | `1rlh = 20px` | `10px` |
| Root `1lh`, descendant `1rlh`, root zoom 1 controls | `20px` | `20px` |

Final computed line-height remains `20px` throughout. For inherited fixtures the box has both width and left padding of 1lh, so its intended unscaled border-box width is 40px; the physical width is that value times effective zoom. Exact powers of two and integral app-unit lengths avoid a fractional rounding explanation. No text content, downloadable font, normal line-height, transform, border, replaced element or form-control minimum supplies these numeric oracles.

## Current normative basis

Fresh primary snapshots and URLs are in `evidence/RETRIEVAL.json`.

[CSS Values 4 font-relative lengths](https://drafts.csswg.org/css-values-4/#font-relative-lengths) bases lh on the element's line-height and rlh on the root's. Its special font-size/line-height self-reference rules are not invoked by the width/padding witnesses. The root and descendant controls use the same explicitly absolute root line-height.

[CSS Viewport zoom and CSSOM](https://drafts.csswg.org/css-viewport/#zoom-property) composes ancestor and local zoom into effective zoom, scales layout lengths, exposes non-auto/non-percentage computed-style lengths unscaled, and exposes client rectangles scaled. Thus a 20px inherited absolute line-height supplies a 20px unscaled lh unit at the child; local zoom changes physical scale, not that relation. At the root, 1rlh and 1lh agree for ordinary width/padding consumers. Offset width is an unscaled geometric observation; the fixture needs no rounding tolerance at its selected values.

[CSSWG issue 9397](https://github.com/w3c/csswg-drafts/issues/9397) resolved consistent zoom treatment of inherited absolute lengths. [Issue 14402](https://github.com/w3c/csswg-drafts/issues/14402) remains open in the fetched issue metadata, but both retained comments agree to remove an obsolete computed-value explanatory note. The current draft has removed it and describes the used-value effect. This review **does not claim Gecko must store its internal values at a particular CSS specification stage**. The violated unscaled unit/geometry relationships are independent of that implementation choice.

## H1: implicit inherited `lh` observes a value before normalization

Complete source snapshots, not indexed line numbers, identify this chain:

1. StyleBuilder starts with inherited font data. `effective_zoom_for_inheritance` represents the local inheritance adjustment; ordinary positive author zoom composes with the inherited effective zoom.
2. `apply_custom_and_prioritary_properties` and `ensure_prioritary_property` resolve priority dependencies. `data.py` includes line-height as a priority property, dependent on font inputs whose closure includes zoom. The `LineHeight` predefined type is already included in `is_zoom_dependent`; this witness is **not a missing property-inventory entry**.
3. Applying Zoom calls `did_apply_prioritary_property`, recomputes effective zoom and eagerly normalizes inherited font-size. Its source TODO explicitly identifies line-height as another eager dependency.
4. `apply_one_prioritary_property` returns immediately when a priority property has no declaration. The inherited line-height therefore remains in the parent's scaled coordinate system when there is no child declaration.
5. The ordinary width/padding declarations compute through `reference_font_size_and_length`'s Lh branch. `StyleBuilder::calc_line_height(CurrentStyle)` selects the current font struct. `Device::calc_line_height` passes it through `Gecko_CalcLineHeight` with no element and inflation 1, then through `ReflowInput::CalcLineHeight`/`ComputeLineHeight`. The absolute branch returns the stored length in app units; it does not repair an earlier cascade-stage normalization omission.
6. The Lh branch also records a line-height dependency for non-inherited property caching. That records the value it actually read; it does not recascade the width automatically after a later line-height write.
7. Only after ordinary declarations does `apply_non_prioritary_properties` call `recompute_zoom_dependent_inherited_lengths`. That sweep synthesizes inherit for unseen inherited zoom-dependent properties. The final line-height is corrected, but already computed width/padding remain wrong.
8. Explicit inherit/unset follows the generated `cascade_property` inheritance branch earlier: it reconstructs the parent's computed value and recomputes under the inheritance zoom, restoring the builder's effective zoom afterward. Numeric line-height is a different passing control: its provider multiplies by the eagerly normalized font size.

For parent zoom P, local zoom Z and unscaled line-height L, the inherited absolute storage initially contains LP. A correct consumer reads LPZ; the observed implicit consumer reads LP and CSSOM exposes `LP/(PZ) = L/Z`. Later correcting line-height does not alter the consumer's stored result. The six raw failures follow this formula for every parent zoom in the fixture; all explicit/numeric controls instead follow L.

This is a source-level causal trace supported by exact observations. The run did not instrument Rust/C++ stages, so the trace is not a claim that every individual callback was directly logged.

## H2: root `rlh` converts a scaled direct value twice

The same complete `reference_font_size_and_length` function distinguishes three Rlh providers:

- Root: `StyleBuilder::calc_line_height` using the selected current/inherited base. This returns a length already expressed in the consuming builder's scaled coordinates. Its InheritedStyle branch explicitly applies the local inheritance zoom; the ordinary witness uses CurrentStyle.
- Non-root media query: default-style font provider.
- Other non-root elements: `Device::root_line_height`, a cache stored in zoom-independent CSS pixels.

After selecting any of these providers, the current Rlh arm unconditionally zooms the result. The root direct provider consequently receives an extra multiplication. `matching.rs` explains why the cached descendant path needs its multiplication: after computing the root line-height, publication explicitly unzooms it before calling `set_root_line_height`. The getter/setter preserve an f32 bit pattern, and the getter tracks usage.

For root zoom Z and unscaled line-height L, the direct provider gives LZ, the extra multiplication gives LZ², and CSSOM returns LZ. Root Lh uses LZ directly and exposes L; descendant Rlh reads cached L, scales once by descendant effective zoom E and exposes L. Every recorded root state matches these distinct paths. The successful descendant/control values argue against a stale-cache explanation for this witness.

`nsComputedDOMStyle::SetValueToPixels` and Rust `CSSPixelLength::to_resolved_value` perform the relevant unzoom at exposure. `Device::calc_line_height` uses app-unit conversion; Gecko's length provider preserves the stored absolute value. Form-control minimums cannot intervene because this call passes no element. Root cache freshness and its dependency predicate are distinct from the direct-provider double conversion; the round-2 normal-line-height invalidation lead remains separate and unproven here.

## Known issues, prior work and test coverage

- [Bug 1887627](https://bugzilla.mozilla.org/show_bug.cgi?id=1887627) is NEW and tracks consistent inherited-length handling. Comments 10–12 discuss remaining inventory generation after earlier WPT repairs. H1 is a concrete remaining **ordering** witness in that known area; novelty of an independently filed exact lh-consumer case is not established.
- [Bug 1968431](https://bugzilla.mozilla.org/show_bug.cgi?id=1968431) introduced the implicit recascade infrastructure. [Bug 1968552](https://bugzilla.mozilla.org/show_bug.cgi?id=1968552) repaired explicit inheritance. [Bug 1911195](https://bugzilla.mozilla.org/show_bug.cgi?id=1911195) repaired broad zoom property tests. Their retained comments explain the existing sweep and passing explicit controls; those fixes must not be claimed again.
- [Bug 1942329](https://bugzilla.mozilla.org/show_bug.cgi?id=1942329) is FIXED. Comments 2–8 describe replacing the default-style root rlh provider with the actual builder and landing `b4774563617f`. It fixed the unzoomed root witness. H2 is a zoom-specific extension adjacent to that change, not the original root-unit discovery.
- Bounded Core summary queries for “zoom line-height” and “zoom rlh” returned 5 and 0 results respectively. Several hits concern page/text-only zoom, which is different. This is not an exhaustive novelty search of issue comments or every component.
- Read the prior relative-units round-2 report and current bugfix ledger. Root rlh zoom was explicitly noted there. The accepted **bounded conditional** registered-numeric dependency proof concerns dependency capabilities and assumes scheduler readiness; its native patch remains pending per the retained review. It does not establish readiness of an absent ordinary line-height declaration. The current cascade file contains that ongoing project work and must be treated as shared-tree context, not pristine upstream source.

Retained WPTs explain the gaps: `rlh-on-root-lengths.html` asserts root padding without zoom; `line-height-computed.html` has explicit line-height and descendant root-unit consumers; `font-relative-units.html` compares local/root units on descendants; `length-implicit-and-explicit-inheritance.html` checks final property values, not early lh reads. The broader retained selection has 14 tests and two metadata files. Twelve absent metadata files do not establish fresh passing results. No existing WPT was run by this reviewer.

## Separate minimal repair/WPT proposals

### H2 first

Keep the direct root Rlh value in its existing scaled units; apply consumer effective zoom only to providers that return unscaled lengths. A minimal candidate is a root/non-root conditional around the existing final multiplication, preserving the non-root media-query and cache behavior. Prefer expressing the distinction close to provider selection. Do not remove zoom from all rlh paths or change the cache to scaled storage.

Add a standalone testharness WPT under `css/css-values` or `css/css-viewport/zoom`: standards iframe root with explicit 20px line-height, left padding 1rlh, right padding 1lh, descendant width 1rlh. Cover fresh root zoom .5/1/2, then 1→2→.5→1 updates and descendant zoom independent of the root. Assert both actual root/descendant effective zoom and exact unscaled results; no font download needed. Preserve `rlh-on-root-lengths`, `lh-rlh-on-root-001`, line-height-computed and descendant relative-unit zoom tests. Add self-reference/font-consumer and media-query controls before accepting the general source-selection change.

### H1 separately

Ensure omitted inherited line-height is normalized **before any dependent lh read**, using the parent's stored value and the already established inheritance zoom. The missing-priority-declaration path is a promising insertion point after dependencies are ensured; another candidate is a dedicated eager inherited-line-height helper alongside the existing font-size adjustment. The precise expression should be chosen after tracing seen/ensured bits, CSS-wide defaults/revert exhaustion and custom-property priority reads. Do not move the entire inherited-property sweep ahead of dependencies or multiply a potentially already normalized value blindly.

A dedicated `inherited-line-height-lh-zoom.html` WPT can use the existing 45-case matrix with width/padding, computed line-height, physical width and offset width. Keep implicit/explicit inherit/unset/absolute/numeric policies. Add dynamic local zoom changes and fresh-final-style equivalence. Exercise a harmless calc wrapper and dependent priority/custom-property consumers separately, with clear acyclic expectations; do not assert a new cyclic font-consumer policy. Parent should review existing registered-numeric and zoom inheritance tests for shared-file regressions.

Each accepted defect should be one native+WPT commit, with proof/tooling in its own preceding commit. Neither proposal is a patch approval. Exact original/candidate WPT pairing, unchanged controls and source-isolation checks remain necessary.

## Useful formal scope, native bridge and limits

**H2 is the more tractable first contract.** Define nominal scaled/unscaled length wrappers indexed by element/root identity and zoom owner; explicit conversion relations must prevent treating a root cache value as an already scaled builder value. Model root/direct, default media and descendant cache source selection independently, current/inherited line-height bases, coefficient multiplication, root publication and CSSOM exposure. Prove for positive finite rational zooms and ordinary absolute lengths that root/local/descendant unit observations agree, including arbitrary finite root-publication/descendant-read sequences under an explicit freshness relation. Unitless numeric controls can use a separately typed font-size provider. Normal-font metrics remain external.

A complete native connection needs the **whole** `reference_font_size_and_length`, `StyleBuilder::calc_line_height`, `Device::calc_line_height`, actual `Gecko_CalcLineHeight`/`ReflowInput::CalcLineHeight`/`ComputeLineHeight`, root getter/setter/publication call site, coefficient conversion and resolved-value unzoom. Source extraction must retain unexecuted branches and name metric/style providers, rather than replacing the selector with an expected answer. Whole matching/traversal publication is large; if it remains a traced external provider, the theorem must explicitly assume publication/freshness rather than claim all cache invalidation verified. Full real layout and CSSOM flushing remain WPT obligations. Moderate cost for the typed selector/absolute provider bridge, substantially more for traversal.

**H1 is a scheduling contract with a larger bridge.** Define inherited and final line-height states separately and track read events. Prove every admitted lh consumer sees the final normalized value; implicit, inherit and unset agree after normalized input selection. Include ordered priority dependencies, ensured/seen state, absence, explicit declaration, final sweep and cache dependency capture. Universal finite sequences can show a late write cannot retroactively repair an earlier consumer; proving multiplication alone would miss the bug.

Native obligations include complete priority scheduling/absence handling, zoom bookkeeping, generated dependency and zoom-dependent sets, generated inheritance cascade, ordinary declaration traversal, final sweep, Lh dispatch and the actual line-height provider. `cascade.rs`'s custom-property traversal and generated Rust/C++ integration make this high effort. An abstract readiness theorem with supplied readiness is useful but would **not** verify this defect's implementation; obtain approval for any narrower boundary before claiming completion.

Mutants: restore the unconditional root zoom, drop cached-provider zoom, publish a scaled root cache, select default style for a root non-font consumer, delay implicit normalization past a read, normalize twice, skip explicit-inherit rescaling, drop line-height's dependency, or reuse a stale cache after an admitted root change. They must execute and produce semantic differences in native/model traces, not merely fail compilation. Invalid source roles/owner identity and malformed numeric domains need separate diagnostics.

The initial numeric contract should specify app-unit conversion and rounding domains. The recorded powers-of-two cases are exact; arbitrary rational identities do not by themselves prove f32 multiplication, saturation, underflow or app-unit rounding. Explicit exclusions unless separately implemented: zero/document reset semantics, extreme zoom products, page/text-only zoom, actual font metrics/downloads, form-control minima, arbitrary registered/custom cycles, pseudo/flat-tree inheritance, shared-style cache concurrency, media-query environment invalidation and full layout. No proof or native harness was implemented here.

## Artifact integrity and reproduction

`ORIGINS.json` pins historical whole source/test snapshots and identifies historical-only roadmap/report copies. All substantive native/test files still matched live at review capture; the archived roadmap alone had changed. The live tree includes project repairs, so these pins are not represented as HEAD/upstream release identities.

Run `python3 -I -S verify.py --expected-manifest DIGEST` to authenticate every input before importing the independent checker. `--live` additionally checks native/test origins and the retained absent-metadata set, never historical binaries or archived roadmap snapshots. Searchfox discovery and current primary sources are retained. The installed spec-index capability was unavailable in this session; direct primary retrieval follows the established fallback. Integrity checks support reproducibility, not a proof of the review's normative reasoning.
