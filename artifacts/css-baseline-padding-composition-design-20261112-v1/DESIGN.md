# Exact padding composition: proposed connected unit

The next useful unit changes padding and border-padding authority, its frame cache, and the readers that rebuild reflow inputs together. Changing only the addition or widening a return value after `LogicalMargin` arithmetic does not preserve the computed result. This is a source-only design, with no new implementation or compiler evidence.

## Storage and operation strategy

Use a physical four-side integer record for authoritative computed padding and border-padding, with explicit writing-mode permutation views. Signed128 storage matches the containing-block candidate's exact sizes; the local current-input composition needs much less headroom. A physical record also lets `UsedPaddingProperty` retain the same exact side values without a narrow logical-to-physical intermediate. No implicit conversion to `nsMargin` or `LogicalMargin`, and no projected legacy getter, should exist.

Do not give this record unrestricted signed128 `+`, `-`, `Size`, or negation operators and then assume they are total. Storage, copying, side permutation, equality and skipping a side are total. Current acquired side composition is total by the bounds below. Arbitrary future wide setters require a new producer contract or a retained expression representation; the current sixteen-field theorem does not establish their arithmetic.

At each existing signed32 boundary, promote each side before any addition, subtraction or magnitude calculation. In particular:

1. Initialize all four padding sides from the selected theme, SVG zero, explicit override or style/percentage provider. Do not first add sides in `LogicalMargin` or `nsMargin`.
2. Read each baseline property once, choose its side using the original sign, promote its value, then form its magnitude and add it to that side. Preserve the existing flags, property presence and block-axis dirty-bit behavior. The source's state-bit branch also runs for a positive magnitude originating from an end-side property; do not silently implement the narrower comment instead.
3. Promote each acquired border side, then form border plus adjusted padding componentwise. Do not promote the result of the old `border + padding` expression.
4. Preserve the scrollbar zero-size reset of both records, then perform exact old/new padding comparison and cache replacement/removal with unchanged `needPaddingProp` and sticky `HasPaddingChange` behavior.
5. Reconstruct border from the two exact records before any observer conversion. On this producer path, `(border + padding) - padding = border`; independently installed records need their own bounds. Preserve independent setter semantics until every caller is migrated, rather than pretending every arbitrary pair is a coherent border/padding snapshot.

Proposed API shape: exact physical/logical padding and border-padding getters; full-record exact setters; one explicit raw-`LogicalMargin` acquisition overload that promotes individual components; a virtual exact used-padding getter and exact logical conversion; exact used-border-plus-padding composition; one authoritative exact padding property. Retire the old getters at the transition so unconverted callers remain visible compiler errors. This is a coordinated partial migration, not a claim that the whole tree would already compile.

## Derived headroom and its domain

The accepted theorem applies when the *acquired* original padding and border sides are signed32 and one baseline magnitude in `[0, 2147483647]` is added per axis. It gives:

| Expression | Mathematical interval |
| --- | --- |
| adjusted padding side | `[-2147483648, 4294967294]` |
| border plus adjusted padding side | `[-4294967296, 6442450941]` |
| axis sum of both border-padding sides, one contribution | `[-8589934592, 10737418235]` |

These fit signed64 and therefore signed128. Do not claim all theme/style conversion arithmetic is safe merely because its final type is `nscoord`: `LayoutDevicePixel::ToAppUnits` and style resolution are prior acquisition obligations. Explicit signed32 overrides may be negative; the nonnegative CSS padding branch does not cover them.

There is no general all-signed128 content-plus-side operation: `INT128_MAX + 1` is a counterexample. Root available-minus-padding and final content-plus-border sizing still need their own producer bounds or expression-preserving consumers. Likewise, reconstructing border from two independently arbitrary signed128 setters can require `INT128_MAX - INT128_MIN`. Those are integration blockers, not reasons to assert, clamp or drop layout.

## Reset, feedback and the limit of the single-contribution argument

`InitOffsets` replaces the full padding record before its two guarded property applications. `ComputePadding` also assigns every side in every branch. Block and inline applications each occur at most once, with `IsGridMeasuringReflow` and `ShrinkWrap` retaining their independent suppression. Orthogonal grid property mapping is a permutation, not a second contribution to one axis.

This proves one *new* contribution per axis per invocation; it does not prove an override contains no earlier baseline adjustment. The indexed non-root reflow-root path in `PresShell::DoReflow` passes `GetLogicalUsedPadding` back to `ReflowInput::Init` as an override. Once that value is exact and possibly wider than signed32, the previous raw-input bound no longer applies. Whether a baseline-bearing frame reaches this path, and whether flags suppress the repeated adjustment, requires a caller argument. No reachable double-adjustment bug is asserted here.

The smallest honest implementation should preserve the acquired-vs-already-adjusted distinction in its design and trace this feedback before choosing a bound for migrated overrides. Possible resolution is an explicit initialization mode for an already resolved record, but changing whether baseline is reapplied is a semantic change requiring reachability and compatibility review. It must not be silently folded into a width change. Arbitrary repeated `p := p + d` would escape any fixed per-invocation bound.

## Cache and reader semantics that must survive

`nsIFrame::GetUsedPadding` has first-reflow/SVG zero handling, theme acquisition *before* property lookup, cached-property lookup, then style fallback. Preserve that precedence initially; the theorem does not establish that the themed getter equals baseline-adjusted `InitOffsets` padding. Make that consistency question explicit rather than secretly switching the cache to win.

Migrate virtual dispatch: border-collapsed `nsTableFrame`, table rows and row groups return zero padding. Ordinary tables delegate. Preserve separate used-border overrides, skip-side application by consumers, and frame lifecycle. Existing UsedPaddingProperty comments mention style-change caching, but the indexed direct property inventory alone is not a proof of every generic property/lifetime mutation.

The raw signed baseline properties can remain signed32 in this unit. The grid measuring-reflow cache key reads that raw value and can remain unchanged. Widening the baseline producer later requires revisiting both that cache key and the mathematical target.

## Connected implementation order and completion criteria

First implement the exact records and the `InitOffsets`/`ComputePadding`/computed getter-setter/cache unit. Include frame virtual accessors, table overrides, `GetUsedBorderAndPadding`, and RestyleManager's two containing-block/parent reconstruction chains in the same copied-source patch. Restyle must copy exact cached padding and composed border-padding without a narrow roundtrip. This does not by itself settle its computed-size and position arithmetic.

Then migrate a real observation path, preferably CSSOM padding values, using the existing reviewed terminal app-unit conversion policy, preserving safe-origin compatibility. CSSOM's terminal numeric conversion is distinct from feeding padding into geometry. Keep GetBoxQuads/BCR acquisition, ResizeObserver, overflow, painting, sticky, float shape and layout reflow consumers required; no observer-only completion claim.

Before claiming a compiling closure, resolve the PresShell override feedback and migrate all retired getter callers. Existing exact size/position components may be reused where they genuinely accept these values. A caller that still requires `nsRect`, `nsMargin` or narrow `LogicalSize` is an unresolved sink, not permission to cast.

Meaningful future validation: maximum positive/last-baseline magnitudes; minimum input clamped/removed; both independent flags and both axes; repeated initialization replacing rather than accumulating base state; negative overrides; scrollbar reset; theme and SVG branches; all writing-mode permutations; cache absence/presence/style transition; table virtual zeros; restyle roundtrip; the PresShell feedback scenario if reachable; exact border cancellation and axis totals beyond signed32. Compile mutations should move promotion after addition, omit reset, double-apply one axis and narrow the cache. No such tests or native execution were run for this design.
