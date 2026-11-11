# Named-range grouping order: bounded source investigation

**Verdict: REACHED.** The same earliest-occurrence defect remains reachable for
named-range groups at equal resolved offsets. This is a source-supported test
hypothesis and possible additional manifestation of bug 1778402 / local #172,
not a newly counted defect or a browser-confirmed result from this investigation.

The source snapshot is commit `883d620fdbd6b66d4df871d660ee9612d1c20985`.
`SOURCES.json` pins ten files, checked against both that Git revision and the live
bytes when captured. The percentage repair is already present in that snapshot;
the named-range path remains unchanged. No live source, WPT installation, browser,
build, index, or Git history was modified here.

## Normative route

Scenario: a CSS animation with unmodified keyframes, an active view timeline,
and three distinct easing groups all using `cover 50%`. Their authored occurrence
sequence is `A, B, C, B`. The repeated B overrides one of its own declarations.
All three resolved offsets are finite and equal; no endpoint is selected.

1. [Scroll Animations, named-range keyframe selectors](https://drafts.csswg.org/scroll-animations-1/#named-range-keyframes)
   extends keyframe-selector syntax to range-name/percentage pairs and attaches
   them to corresponding timeline points. The selected view timeline supplies
   `cover`; the missing-range ignore branch does not apply.
2. [CSS Animations 2, processing steps 2.2–2.3](https://drafts.csswg.org/css-animations-2/#keyframe-processing)
   groups identical selectors/easing/composition and cascades each group with
   later declarations winning. Step 4 defines specified order as
   “document order with duplicate keyframes collapsed to the earliest position.”
   It retains named-range specified order in computed order; used-order ties use
   computed order. Thus the required group sequence is `A, B, C`.
3. [Web Animations, `getKeyframes()` steps 2–3](https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-getkeyframes)
   selects computed frames for this unmodified CSS animation, then serializes
   their sequence. The endpoint-generation ambiguity is immaterial to a check
   restricted to the three authored range frames.

The three primary HTML snapshots exactly match webspec-index's SHA values.
Draft dates are 2026-08-18, 2026-09-25, and 2026-10-08 respectively. `PRIMARY.json`
records their hashes; `ANCHORS.json` validates the cited anchors. The API anchor
indexes only its IDL declaration, so `wa-interface.json` captures the containing
section's actual algorithm. The step-only graph returns no route at depths 9
and 18; this is not a negative verdict. The positive conclusion rests on the
explicit processing and serialization rules above, not graph completeness or
effects summaries.

| Alternative route or uncertainty | Why it does not decide this fixture |
| --- | --- |
| `setKeyframes()` replaces the CSS frames | The fixture never calls it. |
| A timeline lacks the selected named range | The fixture uses a view timeline and checks resolved `cover 50%` offsets. |
| Different named offsets require a post-resolution permutation | Every authored range frame in this fixture resolves to the same finite offset. |
| Initial/final frame choice or implicit composite | Range-frame filtering excludes generated percentage endpoints; all authored groups use the same unspecified composition. |
| CSS/Web Animations sorting integration note | The draft still states the relevant order explicitly; no plausible stable equal-offset sort changes this witness. |

## Exact native path

`KeyframesAnimation::from_keyframes` appends named-range steps in selector/source
order. Its percentage sort does not sort `steps_with_range_name`.

`Servo_StyleSet_GetKeyframesForName` then iterates that range vector in reverse.
`Gecko_GetOrCreateKeyframeForTimelineRangeOffset` searches the temporary range
array for an identical offset/easing/composition tuple. A match returns the
existing frame and its numeric index without relocating it; a new frame appends
and returns the array length as a distinct sentinel. The temporary array is
reversed when appended to the output.

Consequently `A, B, C, B` is encountered as `B, C, B, A`; the temporary array is
`B, C, A`, and emission is `A, C, B`. Group B still receives its later declaration
first and is deduplicated correctly. Payload precedence and group position are
different obligations.

`KeyframeEffect::MaybeUpdateKeyframeComputedOffsets` updates offsets in place;
it does not restore source order. `CSSAnimationKeyframeEffect::GetComputedKeyframes`
copies named frames and calls `StableSort(ComputedOffsetComparator())`. For equal
finite offsets its strict comparison is false in both directions, so this sort
retains `A, C, B`. `KeyframeEffect::GetKeyframes` serializes that copied sequence.
The existing percentage helper's rotation is on a separate earlier construction
phase and cannot repair the range array.

The CSSAnimation source deliberately sorts resolved range frames for endpoint
lookup and interoperation, while its comments acknowledge specification concerns
for unequal offsets. This report does not propose changing that sort or settling
every computed-versus-used-order case. Equal resolved offsets isolate the group
position defect even under the current implementation's chosen sorting behavior.

## Existing WPT expectation

The unchanged `scroll-animations/css/merge-timeline-offset-keyframes.html` already
contains a closely related witness in its first callback:

| Source occurrence | Selector | Opacity |
| --- | --- | --- |
| 1 | `entry 0%` | 0 |
| 2 | `entry 100%` | 1 |
| 3 | `contain 0%` | 0.8 |
| 4 | `entry 100%` | 0.5 |

Its expected range sequence is `entry 0%, contain 0%, entry 100%`; both latter
frames explicitly have expected computed offset `1/3`. That matches current
latest-occurrence grouping. Under the current earliest-position contract the
two latter range frames should be exchanged, preserving their values and
offsets. Its second callback uses a different easing for the final occurrence,
so those occurrences are separate groups and its source ordering is unaffected.

This is a stale-expectation assessment, not an edit to that WPT or a repudiation
of the completed percentage regression comparison. That comparison correctly
required the existing range callbacks to remain unchanged for the percentage-only
repair. A range extension must separately update the first expected sequence and
justify that change with the current contract. The copied prior bug 1778402
context establishes an existing group-order report; it is not a new live tracker
status check or evidence that someone already reported this exact range example.

## Why the percentage rotation cannot be copied blindly

`grouped_keyframes_indexes` stores numeric positions of reused frames until
`remove_duplicated_property_value_entry` runs. It selects only those positions
for property deduplication. Positions currently remain stable throughout range
construction; they are no longer needed after that pass and final emission.

Even updating the index returned for the current match does not repair previously
saved positions. `order-model.py` demonstrates this with source `A, B, C, B, A`:
after a hypothetical move-to-tail on both matches, the frame order is repaired,
but the saved set identifies only A and skips duplicated B. Returning the old
index would add a second immediate mistake. This is a counterexample to a proposed
implementation shortcut, not a current native defect caused by the percentage fix.

A narrow extension can preserve all numeric identities until deduplication has
finished, retain each group's earliest source position as separate construction
metadata, and arrange groups only afterward. Alternatively every saved index
must be remapped correctly on each move. Neither design is implemented here.
An abstract earliest-order theorem alone does not discharge this native identity
and deduplication obligation. Generated endpoint frames are created in the later
CSSAnimation copy and are not entries in this temporary index set.

## Proposed experiment and limits

`proposal/named-range-group-earliest-order.html` is a copied two-callback WPT
proposal for `scroll-animations/css/`: unique groups as a control, and repeated
group `A, B, C, B` as the discriminating case. It uses `cover 50%` throughout,
checks all resolved offsets equal `0.5`, verifies the later declaration wins,
then checks the three easing labels remain in earliest source order. The existing
scroll-animations directory metadata enables scroll animations and Typed OM.

Predicted baseline: unique control passes; repeated case fails the order
assertion after source validity and later-value checks. Prediction only: this
agent did not execute either callback. Root should first run the unchanged
current browser against this exact proposal before extending any repair.
Then test the proposed range change with corrected existing expectation,
duplicate declarations, unique groups, and the percentage controls. Retain the
same bug/report count unless independent triage justifies splitting it.

`SYNTAX.json` records a successful inert `node --check` of the inline script.
No WPT lint, manifest installation, browser run, native compilation, performance
measurement, or kernel proof was performed. `ORDER-MODEL.json` contains only
finite Python source-order/index illustrations. No visual interpolation oracle
or general unresolved-offset ordering claim is made.

Searchfox supplied discovery and exact-spec-reference receipts; reasoning uses
the pinned local sources. Installed tools reported newer versions available
(searchfox-cli 0.20.5→0.20.6, webspec-index 0.14.0→0.15.0); neither was upgraded.
The layout instructions/checklist were read using Python because this session
does not expose the requested `Read` tool.
