# Physical-center successor

Artifact-only WPT proposal; no browser, build, native, index, or installed-test changes. The frozen six-case v1 fixture and its runner are unchanged. This successor has twelve independent source/reference assertions: two writing modes × three margin pairs × two requested sources. Each test creates all three empty inline-blocks in one line. The third has the same 100px block size, symmetric 20px/20px margins and explicit first source.

The oracle uses physical geometry: `center = rect.left + (rect.width + marginRight - marginLeft) / 2`. It compares each asymmetric box's center to the symmetric reference's center. This is independent of the helper's first/last origin representation, logical side names and line-inversion choice. The CSS Inline atomic-baseline synthesis rule places each central baseline at this midpoint, so all three must coincide. Separate named assertions keep one source's failure from hiding the other's result. Sizes, applied styles, empty content, same-line positions and repeated rectangle stability are calibrated before comparing centers. All dimensions are small integer CSS pixels; this probe does not test odd app-unit rounding or negative margin-box extents.

## Consumer inversion audit

Pinned HEAD is `90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e`; source hashes are inherited from the v1 audit. Searchfox discovery used `IsLineInverted`, `mWritingMode =`, and `LogicalRect::GetPhysicalRect`; actual bodies were checked at pinned HEAD.

1. `nsLineLayout::PlaceFrame` takes explicit first/last logical baselines in the matching writing mode.
2. The baseline branch of `nsLineLayout::VerticalAlignFrames` assigns `mBounds.BStart(lineWM) = baselineBCoord - mAscent`. Line-inversion swaps text-top/text-bottom and certain explicit shift policies, but does not change this baseline branch.
3. `nsLineLayout::VerticalAlignLine` adds a common baseline coordinate to each baseline-aligned sibling and calls `SetRect` with the same line writing mode. There is no per-source correction.
4. `nsIFrame::SetRect` delegates to `LogicalRect::GetPhysicalRect`. In vertical-lr its physical x is BStart; in vertical-rl it is container width minus BEnd. No extra line-over/under inversion occurs here.

Thus, for this specific path, preserving an incorrect inverted First result and merely complementing Last would make both groups agree at an incorrect physical location. The stronger oracle rejects that workaround. This does not establish that every baseline API caller follows the same convention, or resolve every existing alphabetic inverted-margin behavior.

For E=100, margins 10/30, the physical block-start midpoint is 60. Current vertical-rl logical results are First=60, Last=40; current vertical-lr results are First=40, Last=60. Predicted v2 outcomes: asymmetric vertical-rl First passes and Last fails; asymmetric vertical-lr First fails and Last passes; symmetric controls all pass (8PASS/4FAIL total). These remain predictions until browser execution. Equal total margin extent and identical content sizes make the symmetric reference a direct center anchor without requiring a font baseline measurement.

Author arithmetic discussion also identifies that the legacy half expression rounds negative odd totals away from zero, not universally upward. Any repair should distinguish preserving that oriented rounding policy from proving physical midpoint behavior. No native expression is accepted by this artifact.
