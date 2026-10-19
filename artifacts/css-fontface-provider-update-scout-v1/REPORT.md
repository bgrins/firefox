# Loaded FontFace descriptor/provider scout

19 October 2026. Static source hypothesis; **browser probe unexecuted**. No native/WPT edit, Gecko build, browser execution, Git operation, or Lean proof. Scope is one concrete provider update failure, with a second invalidation observation kept separate. This is a precise candidate within broad known bug 1072149, not established novelty.

## Recommended first gate

Serve `probes/loaded-size-adjust.html` together with `Ahem.ttf`, await `window.ready`, inspect `window.results`. Require both independent fresh-face calibrations to succeed before interpreting any mutation row. The file records nine rows and no WPT dependency.

The most discriminating case is:

```js
const face = new FontFace(uniqueFamily, fontBytes, {sizeAdjust: "100%"});
await face.loaded;
face.sizeAdjust = "50%";
document.fonts.add(face);
```

First rendering of `XXXX` at20px should have advance40px, like a fresh50% face. Source predicts80px. This sequence mutates **after binary font loading but before set addition and first rendering**. It avoids any old text run or cached font group, and addition explicitly requests set rebuilding. A failure therefore cannot be explained solely by missing layout invalidation of previously rendered content.

## Independent oracle and resource admission

[Font Loading3](https://drafts.csswg.org/css-font-loading-3/#fontface-interface) exposes a settable `sizeAdjust` attribute. [Fonts5 size-adjust](https://drafts.csswg.org/css-fonts-5/#size-adjust-desc) scales glyph advances and other font metrics without changing computed font size. No carveout makes this descriptor immutable after load. Existing WPT `fontface-descriptor-updates.html` explicitly expects updated descriptors to take effect; the sizeAdjust WPT only tests constructor values.

The current Font Loading draft's explanatory attribute lists omit sizeAdjust even though its IDL and linked WPT include it; this editorial omission is recorded rather than hidden. The oracle combines the supported setter/descriptor identity with Fonts5's multiplier semantics. Any native repair acceptance should independently confirm this interpretation.

`inspect_font.py` independently decodes the pinned Ahem head/hhea/hmtx/cmap tables: unitsPerEm1000, actual X advance1000, hence four X glyphs at20px advance80px at100% and40px at50%. Browser controls independently require those exact widths from fresh separate buffer-backed faces. No local font lookup, variable font, generic fallback metric, ligature or glyph ink-bound oracle is used. Explicit synthesis none, optical sizing none, adjustment property none, zero spacing and fixed line height keep other providers out of the width oracle. Awaiting `loaded`, retaining status/serialized descriptor/computed font family, and fresh geometry are all required admission evidence; table values alone do not prove browser selection.

## Source causal chain

1. `FontFaceImpl::SetSizeAdjust` parses and invokes `DescriptorUpdated`. `GetAttributesFromRule` reads the actual descriptor percentage into `gfxUserFontAttributes`.
2. `DescriptorUpdated` calls `FontFaceSetImpl::FindOrCreateUserFontEntryFromFontFace`. Its existing-entry branch calls `UpdateUserFontEntry` and returns the same wrapper. `SetUserFontEntry` immediately returns when identity is unchanged.
3. `gfxUserFontEntry::UpdateAttributes` assigns wrapper `mSizeAdjust`, metric overrides, feature/variation arrays and other matching fields. It neither replaces nor updates `mPlatformFontEntry`, and does not reset loaded state.
4. Complete `LoadPlatformFont` copies these fields into a newly created platform entry and retains that entry. The local-font branch of `DoLoadNextSrc` does likewise. Those are loading paths; `Load` returns once load state differs from NOT_LOADED. The probe uses buffers and awaits completion, so no pending load can later copy the new value.
5. `FontFaceSetImpl::Add` sets `mNonRuleFacesDirty=true`. `FontFaceSetDocumentImpl::UpdateRules` detaches/reinserts entries; `InsertNonRuleFontFace` retains an existing wrapper and does not reload its platform entry. Rebuilding therefore does not repair the stale provider.
6. `gfxFontGroup::GetFontAt` replaces the wrapper with `ufe->GetPlatformFontEntry()` before calling `FindOrMakeFont`. `gfxFont::GetAdjustedSize` multiplies the requested size by that **platform** entry's `mSizeAdjust`, and caches the result. Thus even a brand new glyph/font instance still reads100%.

`gfxFontGroup::UpdateUserFonts` does implement generation-based list/cache clearing. That positive guard is insufficient to establish descriptor freshness when the selected platform provider remains unchanged. `gfxFontEntry::FindOrMakeFont` also caches by entry/style/range, so merely marking layout dirty would be an incomplete repair.

A further observation: `UpdateAttributes` calls `UserFontCache::ForgetFont(this)` with the wrapper, while cached load results are platform entries and `ForgetFont` compares pointers. That call does not itself refresh this retained provider. Do not count it as a separately demonstrated browser defect or security issue.

## Controls and falsification

Nine rows:

1. Fresh100% face, expected80.
2. Fresh50% face, expected40.
3. Loaded100%→50% before first add/render, expected40 (primary isolation case).
4. Active initial100% face, expected80.
5. Existing element after50% mutation, expected40.
6. New element using the same mutated face, expected40.
7. Delete/re-add mutated face, expected40 (explicit rebuild control).
8. Same face after document.fonts.ready and two animation frames, expected40.
9. Restore100%, expected80.

If row3 passes while rows5–6 fail, reassess the platform-update claim and prioritize invalidation. If only row5 fails, old text-run reuse is implicated. If all mutated rows pass, the traced source missed a provider-refresh path and the hypothesis is rejected. Calibration failure makes the experiment inconclusive. Restoration alone cannot establish successful updates because stale100% also produces80.

## Separate invalidation lead, not another ranked bug

For active non-rule faces, `DescriptorUpdated` calls `MarkUserFontSetDirty`; the document implementation requests a style flush and document dirty bit. `UpdateRules` gates `IncrementGenerationLocked(true)` on its `modified` variable, initialized from `mNonRuleFacesDirty` and rule changes. Descriptor mutation shown here does not directly set that non-rule membership dirty bit. This may explain existing active matching failures, but the complete document dispatch-to-reflow chain has not been audited here. It is **not** needed for the primary before-add witness, where Add does set that bit, and it is not classified as a second confirmed defect.

## Known issues and WPT

- [Bug1072149](https://bugzilla.mozilla.org/show_bug.cgi?id=1072149), open, broadly requests effective FontFace descriptor modification. The new contribution is a source-localized loaded-provider boundary and a discriminating sizeAdjust fixture, not a new bug-family claim.
- [Bug2019181](https://bugzilla.mozilla.org/show_bug.cgi?id=2019181) imported `fontface-descriptor-updates-2.html`; its CI summary records one style/family matching failure. That test checks pre-add descriptor getters and style/family selection, not post-load sizeAdjust rendering.
- `fontface-descriptor-updates.html` mutates family/weight/unicode before waiting for load. `fontface-size-adjust-descriptor.html` and `fontface-override-descriptors.html` set constructor descriptors. These do not disconfirm the post-load provider hypothesis.
- Bounded public summary searches for size-adjust dynamic and FontFace sizeAdjust returned no matching bugs. That does not establish novelty beyond1072149 or exhaustive absence of duplicates.
- Seven WPT/reference files and metadata presence are archived. All were NOT RUN; missing metadata is not pass evidence. Other harness/directory metadata is not exhaustively evaluated.

## Small formal target and repair boundary

Rank1: descriptor/provider observational equivalence. Independently represent font data identity, mutable logical descriptors, immutable/shared platform entries, per-instance metric caches, and face/set membership. After a successful mutation, first use must observe the new descriptor; untouched faces sharing the original data must retain their values. Preserve loaded promise/status semantics and resource ownership. A correct implementation may allocate a new provider or use a descriptor-specific instance; blindly mutating a shared platform entry could corrupt another face.

Rank2: invalidation sufficiency. Prove changed descriptor state either changes every relevant cache key or invalidates cached selection/metrics before observation. Generation increments alone are not the property: the end-to-end provider association is required. Native admissions include parser results, main/worker dispatch, shared cache ownership, font cloning/reconstruction, actual metrics and layout scheduling. No C++ memory safety or complete font-loading theorem is claimed.

## Coverage/replay

Prior round17 font matching and round23 variation reports were read; both explicitly left loaded platform-entry update open. Inspected setter→wrapper update→retained platform load/use, set addition/rebuild, exact size adjustment consumer and font instance cache lookup. Full files are retained; that is not whole-file audit coverage. Uninspected: worker concurrent mutations, cross-document ownership, CSS-connected rules, in-flight network races, variable-feature backend mutation, error/retry/display timers, and complete document style/reflow dispatch. Those are not inferred correct from this scout.

`remote/` records current primary HTML and public issue retrieval URL/time/headers/hash. `evidence/searchfox.json` records bounded source discovery; source bytes define this working-tree audit. `check.py` authenticates all listed inputs before importing the font-table parser. Local and relocated checks validate the static font oracle and source hash integrity only. The probe remains unexecuted. No large proof corpus is added.
