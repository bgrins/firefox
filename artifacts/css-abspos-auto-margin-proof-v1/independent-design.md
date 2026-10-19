# Auto-margin repair: independent design and baseline review

Recorded 2026-10-18. Artifact-only review. **The IMCB-floor design is supported,
but candidate v1 is not acceptable: it changes automatic-inset behavior.**
The new counterexample below is a source-derived prediction, not a browser
observation. Root is arranging a regression run and revised candidate.

## Correction to the earlier review

The frozen positioning review described CSSWG issue 11478 as unresolved after
reading Position 3's retained conflict note. That description was incomplete
and is superseded here. Root retained the complete issue and all eight comments.
The August 21, 2025 resolution floors the IMCB at zero by adjusting the weaker
inset; the November 14, 2025 resolution reaffirms it after considering alignment
differences. The issue remains open with `Needs Edits` and `Closed Accepted by
CSSWG Resolution` labels. Open status does not imply unresolved policy.

Current [Position 3 resolving overconstrained insets](https://drafts.csswg.org/css-position-3/#resolving-inset-overconstraint)
contains the zero floor and selects the end inset as weaker when neither inset
is auto. The auto-margin rule then distributes signed residual space. The
literal CSS2 equation must not override that floor for negative IMCBs.
Primary records: [August resolution](https://github.com/w3c/csswg-drafts/issues/11478#issuecomment-3210792751)
and [November reaffirmation](https://github.com/w3c/csswg-drafts/issues/11478#issuecomment-3530286524).

For two definite insets, the intended formula is:

```
rawIMCB = containingSize − startInset − endInset
available = max(0, rawIMCB)
marginResidual = available − fixedMargins − borderBoxSize
```

The initial native candidate moves fixed-margin subtraction outside the floor,
which is correct for this branch. It does not justify continuing into that
branch whenever no sentinel remains in the numeric offsets.

## Required correction: automatic inset provenance

`ReflowInput::InitAbsoluteConstraints` numerically solves either automatic
inset when the relevant size is definite. `ResolveSizeDependentOffsets` can
also solve a start inset after reflow. Therefore, an offset no longer equal to
`NS_AUTOOFFSET` does not establish that its original anchor-resolved inset was
non-auto.

Concrete example in either axis:

| Input | Value |
|---|---:|
| Containing size | 100px |
| Border-box size | 20px |
| Start inset | auto |
| End inset | 0px |
| Start margin | auto |
| End margin | −50px |

The automatic margin must be zero because an inset is auto. Initialization
solves the start inset to `100 − (−50) − 20 = 130`. The numeric raw IMCB becomes
`100 − 130 = −30`.

- Original residual: `max(0, −30 − (−50)) − 20 = 0`.
- Candidate v1 residual: `max(0, −30) − (−50) − 20 = 30`.

Candidate v1 assigns a spurious 30px automatic margin. With automatic start
margin this additionally displaces the border box; with automatic end margin
the used margin changes even if the start position does not. The same arithmetic
applies when the end inset is the automatically solved one. Definite size makes
this path reachable without relying on deferred size resolution.

The old computation preserves zero here through algebraic cancellation. The
candidate must preserve that semantic result explicitly. This is a regression
introduced by the candidate, not a separately accepted pre-existing bug.
The authored checker enumerates 480 small one-auto-inset combinations and finds
192 candidate counterexamples, precisely when `fixedMargin + borderBoxSize < 0`.
These are arithmetic cases, not 192 browser bugs.

### Provenance API

Use `nsStylePosition::GetAnchorResolvedInset` on both logical sides, with the
containing block writing mode and `AnchorPosOffsetResolutionParams` constructed
from the current reflow input and actual CB size. `AnchorPosResolutionParams::From`
for `SizeComputationInput` retains its frame, anchor cache, and automatic-value
override state. `AnchorResolvedInsetHelper::FromUnresolved` resolves anchor
functions/fallbacks and then applies the automatic-to-zero override. This matters
for position-area and anchor-center.

Do not inspect raw `mOffset` alone and do not use `GetSingleAutoInsetInAxis`,
which does not detect both-auto cases. `ReflowAbsoluteFrame` already determines
the four corresponding booleans immediately after the margin call; reusing those
with correct ordering is another valid design. Either solution needs review
against anchor resolution/fallback and static-position paths.

## Unchanged branches and arithmetic limits

- Both auto margins initially zero: moving the floor preserves the residual
  exactly for every raw IMCB. Existing splitting behavior remains inline
  start-zero/end-negative versus block splitting for negative space. Integer
  division/remainder allocation is unchanged.
- Neither margin auto: both helpers leave the margin values untouched. This is
  a functional preservation argument only when the evaluated arithmetic is
  representable; unused residuals can still overflow before a helper ignores them.
- A remaining auto-offset sentinel: the zero-residual branch is unchanged.
  This alone is insufficient because numeric offset resolution erased some
  automatic-inset provenance, as shown above.
- Exactly one margin auto and both insets definite: the candidate implements
  the signed residual against the floored IMCB, for positive, zero, and negative
  fixed margins. Its final placement still depends on the current caller's
  start-inset handling and default self-alignment.

No arbitrary-int32 safety claim follows. The sums of insets and margins, raw
IMCB subtraction, floored-IMCB minus margins, final border-size subtraction, and
positioning additions must each be representable. The new and old evaluation
orders do not have identical overflow domains. A proof must state these native
premises or establish stronger upstream bounds; small WPT geometry cannot do so.
This repair does not implement all negative-IMCB self-alignment or auto-sizing
behavior. The eight pre-existing expected failures remain a separate known
coverage observation, not evidence against the accepted floor resolution.

## WPT and baseline review

The v2 WPT covers three writing modes × two directions × two axes × two automatic
margin sides × four inset pairs × three fixed margins × two initial orders:
576 testharness subtests, with three attempted states each. Border/padding are
nonzero: 14px content + 4px padding + 2px border gives a 20px border box. The
containing padding box is calibrated to 100px independently from its border
rectangle. Logical start conversion is correct for all tested modes/directions.

For definite insets, the expected start is retained start inset plus automatic
start margin (or fixed start margin). Flooring a negative IMCB adjusts the weaker
end inset, so the tested start inset remains the proper reference. The test also
checks fixed margin preservation and the CSSOM used automatic margin. The oracle
matches the Position 3 floor resolution rather than using the original faulty
native formula.

The mutation orders `F→0→F` and `0→F→0` exercise initial and changed states.
When F is zero these intentionally collapse to repeated controls. On a baseline
failure the subtest aborts at its first bad assertion, so the baseline does not
establish successful restoration for that case. A fully passing patched run
would execute all three states. Fresh-document comparison was established by
the earlier probe for its positive-IMCB cases, not for every new WPT state.

The independent checker reconstructs every one of the 576 baseline statuses and
all 240 exact assertion messages from the two formulas:

| Start/end insets | PASS | FAIL |
|---|---:|---:|
| 0/0 | 96 | 48 |
| 10/30 | 96 | 48 |
| 40/60 | 96 | 48 |
| 60/60 | 48 | 96 |

The existing selection has 70 passing testharness subtests, two passing reftests,
and eight expected negative-IMCB failures. The raw receipt records actual exit 1
and unchanged input/presence pins. Root reports session 28020 terminal exit 1.
No browser was run by this reviewer.

The current WPT does **not** include an automatic-inset case. Before acceptance,
add either/both automatic-inset controls with negative fixed margins, cover
either automatic margin side, and compare original, first-candidate, and revised
candidate behavior. The required correction should preserve existing automatic-
inset semantics, not silently bundle unrelated static-position or anchor defects.

## Frozen evidence and replay

`candidate-v1.cpp` SHA-256:
`c5a1a0d610259550fecbc7c33eba909600ff4ca9a1078ff7e848a65e81329720`.
`wpt-v2.html` SHA-256:
`1975a1c25ab71abd4d05954970fba29501cd9125fc118451b817c73bf4aaee0d`.
The complete caller/helper source and anchor API header are retained alongside
Searchfox discovery outputs. The earlier frozen positioning report is unchanged.

```sh
python3 artifacts/css-abspos-auto-margin-independent-v1/check_v1.py \
  --out /tmp/abspos-margin-review-v1.json
```

The reviewer run exited 0. Compare its result with `CHECK-v1.json`. This checker
is authored arithmetic and baseline-log reconstruction, not native execution,
Lean proof, or acceptance of a final repair. Revised-candidate and paired-runtime
review will be additive artifacts.
