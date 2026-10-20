# Natural flex baseline donor candidate

Native/WPT gates pass; independent review and formal companion remain pending.
This is a separate ordinary-item donor-selection repair. It does not incorporate
the pending collapsed-item allocator or edge-fallback repairs into its standalone
patch.

## Behavior and source change

For row-oriented containers lacking a shared baseline, the selected start/end
line is searched for an item with a natural baseline. First/last search order is
order-modified document order, independent of row reversal. Struts and orthogonal
items are ineligible. The direct GetNaturalBaselineBOffset API preserves absence;
the synthesized ascent cache is not treated as evidence of natural availability.
First/last offsets are converted into the container's corresponding block-edge
offset. Existing shared baselines, column behavior and edge synthesis fallback
remain unchanged.

This implements the natural-donor stage in [Flexbox container baselines](https://drafts.csswg.org/css-flexbox-1/#flex-baselines).
The direct provider and native coordinate operations have explicit validity and
range assumptions. Existing actual-child-position treatment is retained; the
separate relative-position/normal-flow provider question is under investigation.
No complete baseline, fragmentation, provider or compiler proof is claimed.

## Paired browser evidence

The unchanged 48-case WPT has 16 baseline failures and 32 passes; the candidate
passes all 48 with 32 identical status/message pairs. Unique natural donors,
two natural donors with CSS order changes, row reversal, first/last baselines,
inline/flex parents and all-synthetic fallback are covered. Ordinary 160x80px
geometry and remove/restore controls are unconditional. No large-value or optional
numeric admission is used. Earlier discovery reproduces the unique-donor issue
in installed release Firefox as well as the shared development build.

The first build tested the unformatted signature. A second successful build
changed only signature whitespace. Clang-format then corrected two indentation
spaces; exact whitespace-only transfer is recorded. The 28-file regression run
uses the second binary and final formatted source snapshot. All 23 reftests,
261 subtests and five harnesses pass. Final native lint and WPT lint pass.
Both builds report zero compiler warnings and retain the existing Mach export-tier
monitor KeyError alongside success; logs and command receipts remain intact.

## Packaging

The exact two insertions are recorded in SOURCE-CHANGE.json. The standalone
patch contains only nsFlexContainerFrame.cpp and the WPT, and independently
applies/reverses on both retained Git bases. The complete shared source has other
pending project repairs; no isolated upstream build is claimed. HEAD, the index
and native working files were preserved during packaging. No signed commit is
created or counted by this checkpoint.
