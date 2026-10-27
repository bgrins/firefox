# Production-domain refinement for central synthesis

The source audit closes useful domains but does not establish a universal bound for every callable frame. No reachable new-overflow witness was found. No legacy-raw fallback or coordinate clamp is recommended. Five Lean declarations compile; all source pins refer to committed HEAD, not the transient experiment tree.

## Stronger range results

For the old total `T=E+s+e`, half `h=trunc(T/2)+T%2`, and raw `r=h-s`, the new complement is `E-r`.

`nonnegative_extent_lower_margin` proves it lies in [-2147483647,2147483646] if E is nonnegative, T is at most INT32_MAX, the old raw result is at most INT32_MAX, and the **opposite** addition e is at least -1073741823. There is no upper bound on e or on E beyond the existing native-operation premises. Large positive auto margins therefore do not defeat this argument.

`negative_insets` proves a separate int32 bound when E is a nonnegative int32 and both additions lie in [-INT32_MAX,0]. It does not require the inner box to fit inside the border box. This is the relevant algebraic domain for negated nonnegative border/padding contributions. A source correspondence still requires those used contributions themselves to be nonnegative representable values before negation; a prior overflow is not silently covered. Border-box synthesis has zero additions and satisfies this domain immediately for nonnegative E.

The proofs do not establish frame-size nonnegativity across arbitrary prior corruption or overflow. `SetRect` is an assignment, not a range-enforcing boundary. For an already-defined layout of nonnegative dimensions, no additional nscoord_MAX frame-size premise is needed.

## Cached margin producers

The default and percentage length conversions clamp to ±nscoord_MAX. `SizeComputationInput::ComputeMargin` uses those conversions, and its font-inflation adjustment only adds a positive amount to the inline-start side. The relevant later writers are:

| Writer | Lower-bound evidence when its own arithmetic is defined |
|---|---|
| `CalculateBlockSideMargins` | The branch publishing the UsedMarginProperty adds nonnegative available space. Its negative-overconstraint branch returns before updating that property. |
| Flex main/cross auto-margin resolution | Main-axis resolution is disabled when free space is nonpositive; cross-axis resolution returns in that case. Assigned shares are nonnegative, replacing zero auto margins. |
| Absolute-position fallback style commit | Copies style-derived fixed lengths, which retain the conversion bound. |
| `ResolveAutoMarginsAfterLayout` | **Exception:** a single auto margin can be assigned negative remaining space below -nscoord_MAX. Both-auto block margins split it; inline both-auto negative space can go wholly to the end side. |

Thus positive cached auto margins are not the unresolved obstacle. The exceptional producer is an absolutely positioned frame with a large negative auto margin. Reflow initialization resets the property before later adjustment; an old negative property is not assumed to survive arbitrary style/reflow changes.

## Which calls actually synthesize centrally

Direct margin-box helpers are reached through fallback implementations on the base frame, block frame, and fieldset. The scroll-container fallback uses its own margin-edge arithmetic and explicitly does not synthesize a central midpoint. Content-box calls are the inline button/input fallback and table-row fallback over cells. Border-box calls include flex-item fallback, grid fallback, and empty flex/grid/table handling in `GetFirstLinePosition`. Padding-box synthesis has no production caller in the discovered inventory.

`nsLineLayout::PlaceFrame` explicitly queries first/last on an in-flow frame on the line. A different block direction bypasses this helper. Regular in-flow atomic-inline margins satisfy the producer lower-bound argument above. Block descendant baseline searches traverse line/principal content; an absolute-positioned box is not itself a normal line participant or flex/grid baseline item. This eliminates the straightforward absolute-position experiment, but not every indirect query.

In particular, **absolute-positioned frames cannot simply be declared unreachable**. `StyleAdjuster::adjust_for_text_combine_upright` changes combined text to horizontal writing mode. A vertical parent's combined text can request its parent's logical baseline through `nsTextFrame::GetNaturalBaselineBOffset`'s orthogonal branch. Decoration overflow/painting requests the parent writing mode. A parent with layout containment rejects its natural baseline, allowing margin fallback. This is a concrete source route worth retaining; its live frame/margin timing and exact extreme dimensions have not been traced in a browser.

For an ordinary absolute-positioned block, that parent query selects the block's default **Last** group. It therefore does not yet supply a newly undefined full-query execution:

| Original request | Noninverted | Inverted |
|---|---|---|
| First | Helper/query unchanged | **New complement; remaining margin-domain concern** |
| Last | New helper complement equals the old logical-query subtraction | Helper/query unchanged |

For noninverted Last, `noninverted_last_defined` proves that if the old raw and old full query were int32-representable, both candidate subtractions are representable and the final result equals the old raw value. This is a no-new-overflow statement, not preservation of the old wrong baseline point. An old *helper-only* counterexample can still expose an already-overflowing old logical query.

The remaining concrete boundary is therefore an inverted **First** margin synthesis on an exceptional negative cached-margin provider, or another path violating the nonnegative-size/inset premises. The text-parent route above uses Last on an ordinary block. Default-First non-block containers and their text/wrapper structure have not been exhaustively proved to exclude the exceptional state. Do not promote the arbitrary int32 witness or the absolute-position source hypothesis to a reproduced regression.

## No general projection policy found

`Baseline.h` promises an offset from the requested border-box edge; `GetLogicalBaseline` promises the corresponding block-start coordinate. Neither grants a generic saturation or fallback rule. The scroll-frame clamps in `GetNaturalBaselineBOffset` and `GetFirst/LastLinePosition` are specifically to the scroll border box, justified there by scroll baseline semantics and bug 1791069. They do not authorize clamping central margin-box baselines, which can legitimately lie outside the border box.

If the remaining exceptional state can reach an inverted First query, the exact result can exceed int32 and the current return type cannot fulfill its exact origin contract. The justified exact-export direction is a wider result retained through the logical conversion and downstream consumer, with an explicit representability result at any remaining narrow boundary. The additive wide-baseline preparation supplies a possible interface, but currently lifts narrow synthesis and does not itself solve this obligation. A broad migration is not proposed as part of the tiny patch, nor is a silent projection or legacy-origin fallback substituted for it.

The paired small-coordinate experiment can proceed independently. Before a universal range claim, finish the exceptional caller analysis or obtain a targeted native trace. The report intentionally leaves that obligation open; no native, browser, index, compiler-of-Gecko, or standalone-library changes were made.
