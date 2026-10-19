# Font-face selection: round 17 static audit

Date: 2026-10-18. **Static candidates and proof targets only.** No browser,
native capsule, build or formal proof was run. No production/WPT/Git changes.

## Ranked next steps

| Rank | Target | Disposition | First gate |
| --- | --- | --- | --- |
| 1 | Combined numeric match score violates descriptor priority at fractional gaps | Concrete source candidate; width/style and style/weight manifestations of one scoring strategy | Calibrated downloadable static faces with distinct size-adjust values |
| 2 | Oblique search uses 14 degrees instead of 11 | Separate source candidate with explicit CSSWG resolution | Positive/negative 12-degree requests and italic fallback |
| 3 | Face-set update and eligibility refinement | Useful formal contract; existing mutation WPT already fails | Reproduce and localize known failure before extending scope |

Ranks 1 and 2 use supported font-face syntax and ordinary finite values. They
are unrelated to the earlier from-font zero-size/axis candidates, Unicode
casing, whitespace, relative-unit caching, or sizing findings. The prior
round11 font-metrics, round5 text, round6 sizing reports and current bug index
were read and retained. Font selection is the scope; shaping, glyph metrics,
optical sizing and rasterization are not proved or broadly audited here.

## Normative selection boundary

Within a selected family, matching filters width first, then style, then
weight. A range acts as its supported individual values; faces survive a stage
only if their ranges contain the selected value. Equal surviving descriptors
can form a composite face subject to unicode-range and ordering. This is
lexicographic filtering, not a tradeoff between different properties.
[CSS Fonts 4 matching](https://drafts.csswg.org/css-fonts-4/#font-matching-algorithm).

For oblique requests at or beyond positive 11 degrees, search larger angles
first; below positive 11, search smaller positive angles first. Negative
requests mirror that direction. Italic fallback starts positive-oblique search
at 11 degrees. Unspecified `oblique` denotes 14 degrees; these are different
constants. [Style matching](https://drafts.csswg.org/css-fonts-4/#font-style-matching),
[font-style](https://drafts.csswg.org/css-fonts-4/#font-style-prop).

Current primary specification HTML/text is retained. Style fallback prose has
other complexities and recent changes; the ranked witnesses avoid fallback
between an oblique request and an italic face. Unsupported fractional italic
syntax and synthesis-only draft features are not used as alleged bugs.

## 1. A scalar score can reverse width/style/weight priority

### Exact native boundary

`WeightStyleWidthDistance` in `gfxFontEntry.cpp` computes:

`widthDistance * 1e8 + styleDistance * 1e4 + weightDistance`.

`gfxFontFamily::FindAllFontsForStyle` minimizes this value. The shared platform
font list independently uses the same expression in `WSSDistance` before
`Family::FindAllFacesForStyle`. Constants live in `gfxFontUtils.h` and the
three distance functions in `gfxFontUtils.cpp`.

The multipliers look sufficient for integer differences, but the supported
values are finer. `computed/font.rs` stores oblique angles as signed 8.8 fixed
point (gap 1/256 degree) and width as unsigned 10.6 fixed point (gap 1/64
percentage point). `FontStyleRange::compute` and `FontWidthRange::compute`
retain these representable endpoints. `FontFaceImpl::GetAttributesFromRule`
passes them into native ranges; `gfxUserFontEntry` stores them without rounding
to integers. `StyleFontStyle::ObliqueAngle` returns the fixed-point float value.

The smallest style contribution is therefore 39.0625, less than a possible
weight penalty. The smallest width contribution is 1,562,500, less than a
possible style penalty. The source assertions bounding each distance do not
establish the minimum nonzero gap needed for scalar priority preservation.

### Independent witnesses

All faces use one downloaded static Ahem resource. Face A has size-adjust
100%; face B has 50%. At 20px, four X glyphs give calibrated widths 80px and
40px. Explicit font-synthesis none prevents artificial weight/style changes;
calibrations under the same request still gate that premise.

| Request | Face A (required winner) | Face B | A score | B score |
| --- | --- | --- | ---: | ---: |
| width100%, oblique20deg, weight400 | width100%, oblique20deg, weight1000 | width100%, oblique20.00390625deg, weight400 | 1200 | 39.0625 |
| width100%, normal, weight400 | width100%, italic, weight400 | width99.984375%, normal, weight400 | 7,000,000 | 1,562,500 |

In the first case A is the exact style match, so weight must not eliminate it.
In the second A is the exact width match, so style must not eliminate it. The
scorer instead favors B. These exact binary fractions avoid relying on values
below the implementation's precision. Range variants use A style19..20 and
weight900..1000 versus B style20.00390625..30 and weight400..500, and A
width100..110 versus B width90..99.984375. The same respective reversals result.

`static_witnesses.py` recomputes these authored rational calculations against
pinned constants. It is not an execution or translation validation of C++.
Changing scalar factors alone deserves care: larger products can lose lower
fields through floating-point precision, and other fallback callers store
scores as floats. Lexicographic comparisons or a proved bounded encoding would
be preferable design candidates; no production diff is proposed in this audit.

### Reachability and controls

`gfxUserFontFamily::AddFontEntry` explicitly asserts that user families are not
simple families. Its inherited constructor initializes that flag false, and
only platform-family callers invoke `CheckForSimpleFamily`. Thus two downloaded
faces reach the full scorer, not the four-slot system-font shortcut.

The provider route is descriptor parsing/computation →
`FontFaceImpl::GetAttributesFromRule` → user-entry ranges →
`gfxUserFontSet::AddUserFontEntry` → family lookup →
`gfxFontGroup::AddFamilyToFontList` → `FindAllFontsForStyle` → selected entries →
`GetFontAt`. User families shadow system families of the same name. `GetFontAt`
checks load state/unicode eligibility and obtains the platform font entry;
the probe loads every face and uses identical complete glyph coverage to keep
that later gate from changing the intended comparison.

Controls include a coarse 1-degree style gap, coarse 1-percentage-point width
gap, equal-style weight selection, equal-width style selection, both declaration
orders, and isolated per-face size calibrations. Interval cases check the same
selection mechanism without requiring an actual variable-font axis. A later
variable-font test must additionally verify axis application; descriptor-range
selection alone does not prove interpolation or clamping.

## 2. Default oblique angle is reused as the search threshold

`StyleDistance` assigns `kDefaultAngle` from
`FontSlantStyle::DEFAULT_OBLIQUE_DEGREES`, which is 14. It uses that value both
for the positive/negative search branch and for italic-to-oblique fallback.
These are the stages whose normative search threshold is 11.

Small independent examples with equal width/weight:

| Request | Required face A | Other face B | Native prediction |
| --- | --- | --- | --- |
| oblique12deg | oblique14deg | oblique10deg | B (distances 102 vs 2) |
| oblique-12deg | oblique-14deg | oblique-10deg | B (102 vs 2) |
| oblique12deg | oblique13..14deg | oblique8..10deg | B (101 vs 2) |
| italic, ordinary synthesis policy | oblique12deg | oblique20deg | B (102 vs 7) |

Use the same independent 80px/40px face calibration. For the italic row,
`font-synthesis:none` still permits normal italic-to-oblique matching; it is
not the special oblique-only value. Positive requests 10 and 14 supply controls
on either side of both thresholds. The first three cases avoid italic fallback
entirely and are the clearest initial gates.

[CSSWG issue 2295](https://github.com/w3c/csswg-drafts/issues/2295) resolved the
default angle to 14. The separate
[issue 2539](https://github.com/w3c/csswg-drafts/issues/2539) resolved the search
threshold to 11 and records applying that edit to italic fallback too. Both
issue bodies and comments are retained. Thus this is not an inferred change
based only on an unresolved note in the current prose. Browser reproduction
and independent defect review remain required; no release impact or novelty
claim follows from this source comparison.

## 3. Selection and update contracts

### Directional range filtering and priority

Model a face as a family identity, three supported intervals/style categories,
eligibility, and declaration index. Define a reference selector by successive
set filtering and independently ordered directional searches. Prove each
surviving face contains the selected value at each stage; lower stages cannot
revive a discarded face; the survivor set is independent of iteration order;
and final declaration order only resolves the specified remaining ties.

Lean can prove finite-list filtering and interval lemmas over rational values,
then over the bounded fixed-point representation. Prove width reversal at100,
weight transitions400/500, oblique transitions0/±11, inclusive endpoints,
overlapping ranges and sign changes. A native companion should compile exact
complete distance and selection helpers with source-bound range types and
compare a generated corpus to the independently defined selector. Mutants:
weighted tradeoff, swapped priority, wrong11/14threshold, exclusive endpoints,
wrong directional order, and using a range's first endpoint instead of its
best point. This would be a bounded provider contract, not full CSS-fonts or
font-file refinement.

### Update and eligibility boundary

`FontFaceImpl` setters call `DescriptorUpdated`; that recreates/updates the
user entry and marks every associated font set dirty. `FontFaceSetImpl` handles
family removal when renaming, then `UpdateAttributes` replaces ranges and
forgets the old user-font cache entry. `gfxFontGroup::UpdateUserFonts` uses
rebuild generation to invalidate resolved faces, and ordinary generation to
refresh load state. These are existing invalidation mechanisms, so the simple
hypothesis that setters never invalidate matching is rejected.

FontFace attributes feed matching and setters update their parsed descriptor
values. [CSS Font Loading](https://drafts.csswg.org/css-font-loading-3/#fontface-interface).

A useful future theorem states that selection after a finite descriptor/set
mutation sequence equals selection in a fresh set with the same final logical
faces, assuming generation propagation and provider updates are correct.
Preserve distinction among unloaded, loading, failed, excluded-by-unicode and
loaded states; account for family shadowing and declaration ties. Sources
inspected here do not prove complete failure reselection or multi-set/worker
lifecycle behavior.

There is already an expected failure in
`fontface-descriptor-updates-2.html` for style swapping followed by family
renaming. [Bug 2019181](https://bugzilla.mozilla.org/show_bug.cgi?id=2019181)
records the imported test and its prior result. Localize that existing failing
substep before claiming a new mutation defect. The test is retained but was
not run. A generation-only model would be insufficient if the platform face
still carried stale descriptor attributes.

## Coverage and rejected-lead ledger

| Inspected boundary | Result |
| --- | --- |
| Width scalar/range direction around100 and membership | Branches match the inspected directional rule; combination score is rank1 |
| Weight scalar/range direction below400,400..500,above500 | No new branch mismatch found; retain endpoint/range proof target |
| Oblique sign,0,range containment,search direction | Rank2 threshold; no blanket claim of all style fallback conformance |
| Descriptor parsing and native fixed-point storage | Ranked fractions and ranges supported; finite precision explicit |
| Shared/unshared scalar score | Same rank1 issue; downloadable witness uses unshared user family |
| Simple system families | Different fast path and existing weight-search WPT; not used for ranked witness |
| User-family precedence over installed same-name family | Explicit early return supplies correct shadowing boundary; no mismatch found |
| Composite ties, reverse face iteration,unicode map | Relevant source inspected; no new claim; full fallback/grapheme coverage excluded |
| Dynamic style/weight/width/family updates | Dirty/generation paths present; existing mutation failure, no new bug claim |
| Oblique-only last-resort matching | Existing expected failure tracked as bug2033377; excluded from new candidates |
| Variable ital axis and synthetic oblique/italic mapping | Existing failure/history; not generalized from abstract style categories |
| Actual variation-axis application, shaping,metrics,hinting | Outside this bounded survey |

## WPT and history coverage

Eleven selected WPTs and present metadata are listed in
`WPT-METADATA-v1.json`. Seven have metadata; four do not. All are **not run**.
The three matching range reftests have Mac failure/disable conditions and
Windows conditional expectations. `at-font-face-font-matching.html` covers
coarse priority, weight directions and many style/width ranges, but not the
ranked fine fractional gaps or12-degree boundary. Metadata absence is not a
fresh pass result. The parsing test's known failing mixed-unit calc case is
not used here.

`oblique-last-resort-weight-selection.html` is already expected FAIL and tracked
by [bug 2033377](https://bugzilla.mozilla.org/show_bug.cgi?id=2033377); its
oblique-only policy is distinct from both ranked witnesses. `ital-variable.html`
also expects FAIL. [Bug 1945642](https://bugzilla.mozilla.org/show_bug.cgi?id=1945642)
records the deliberate recent oblique/italic fallback change and priority-test
backouts; do not undo that behavior casually.
[Bug 1436061](https://bugzilla.mozilla.org/show_bug.cgi?id=1436061) supplies prior
range-descriptor implementation history.

Retained bounded Bugzilla summary searches contain18 matching,86 font-stretch,
and41 oblique results. This is not exhaustive and does not establish novelty.
The initial dynamic-test Searchfox query timed out; the concrete existing test
was subsequently located through primary bug history. All failed requests are
retained. No Git history operation or fabricated Searchfox permalink was used.

## Proposed probe and integrity

`probe.html` is **unexecuted**. Serve the checkout root, open its repository
relative URL, await `window.ready`, and read `window.probeResult`. It has28rows:
8candidate cases and6controls, each in both declaration orders. Each row has
its own two isolated font calibrations and a fresh element comparison. It
records every FontFace descriptor/status, parsed rule, support result and
computed request. A root-owned run must require all112faces loaded, all
calibrations80/40, valid descriptors, synthesis none, and fresh agreement before
interpreting selection. The probe is not yet a WPT or a descriptor-mutation test.

`ORIGINS-v1.json` retains54complete local source/test/history snapshots, including
the exact Ahem bytes. References/resources are retained where listed; this is
not a standalone copy of the whole WPT harness. Source bytes, not HEAD, define
the reviewed version because the workspace contains other authorized patches.

`python3 artifacts/css-breadth-audit-round17-v1/font-matching/verify.py` checks
the frozen SHA256 manifest and authored arithmetic receipt. `--live` additionally
checks production/test inputs against the current tree; historical artifact
reports/indexes remain pinned snapshots. Neither command executes native code
or a browser. Future runtime evidence must live separately so this static
survey remains unchanged.
