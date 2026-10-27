# Native origin correction review

GO for a guarded local comparison of the reviewed patch against the six-case v1 and stronger twelve-case v2 WPTs. No blocker found for these representable cases. This is not native acceptance or a claim that either fixture has passed.

The patch retains the existing margin/content/padding box selection, half calculation and line-edge offset, then returns that scalar or its complement using the already line-inversion-adjusted `group`. Using `group`, rather than the original `aGroup`, is necessary here.

Let E be the frame block size and r the retained line-edge offset. The four raw helper returns become:

| Writing mode | Requested First | Requested Last | Both logical query results |
| --- | --- | --- | --- |
| Non-inverted | r | E − r | r |
| Inverted | E − r | r | E − r |

`GetLogicalBaseline` complements only a requested Last result. Thus the final block-start-relative baseline is independent of source preference, while retaining the physical line-edge anchoring. For E=100 and margins 10/30, r is 60 in vertical-rl and 40 in vertical-lr; both modes now yield the physical block-start midpoint 60 for both requested sources. For reversed margins both yield 40, and symmetric margins yield 50. This satisfies the independently derived v2 physical-center oracle, unlike preserving the original First result in both writing modes.

The source review follows `PlaceFrame` to `VerticalAlignFrames`, shared baseline translation in `VerticalAlignLine`, then `SetRect`/`LogicalRect::GetPhysicalRect`. Vertical-lr maps logical BStart directly to physical x. No blanket line-over inversion rescues an incorrectly anchored First value. Source hashes and the full path assessment are retained in the preceding audit and v2 oracle report.

Rounding is performed once, by the unchanged C++ division/remainder expression. The patch complements that rounded point rather than rounding again from the opposite edge. Negative odd totals retain the old away-from-zero half behavior; no new claim is made that the specification mandates that negative-extent policy. The same branch includes central, mathematical and middle baseline synthesis, but current proposed WPTs exercise default central alignment only.

Machine-range limitation remains explicit: all algebra assumes the existing extent/margin additions, negation, half sum and the new `E − offset` are defined nscoord operations. The new inverted-First subtraction was not present in that helper path before. This review neither proves its global range nor treats the unbounded arithmetic model as a native overflow proof. Small finite fixtures are suitable for the next experiment; extreme margins, odd app-unit rounding and other synthesis box types remain separate preservation/range obligations before broader acceptance. No saturating projection or new overflow workaround is recommended by this review.

Reviewed artifact bytes only. No native install, build, browser, test installation, index or commit action.
