# Percentage keyframe grouping candidate for bug 1778402

Prepared against `f3949d2992abdc02536b9a61e51dc7d603ce0868`, using copied source only. `ordering.patch` changes two native files, strengthens one existing WPT case, adds one case to that same page, and removes only the expected-FAIL stanza for bug 1778402. No live source, browser, build, index, or Git history was changed. This is not runtime acceptance or a new bug count.

## Contract and change

The preceding [spec triage](../css-css-animation-keyframe-failure-triage-20261110-v1/REPORT.md) establishes the current [CSS Animations 2 grouping rule](https://drafts.csswg.org/css-animations-2/#keyframe-processing): matching selector/easing/composition groups retain their earliest source position, then percentage offsets are stably sorted. Declaration precedence within each group still favors later declarations. Bug 1778402 describes the existing failure, although its historical argument used older specification wording.

Current `Servo_StyleSet_GetKeyframesForName` traverses percentage rules in reverse to retain later declaration values. `Gecko_GetOrCreateKeyframeForPercentageOffset` currently leaves reused groups where their latest occurrence created them. The final array reverse therefore orders groups by their latest occurrences. The fixture's source groups `A, B, C, B` become `A, C, B`, while the current contract requires `A, B, C`.

The candidate rotates the matching whole `Keyframe` to the array tail before returning it to the Rust caller. During reverse traversal, each earlier occurrence therefore updates the group's eventual position. The final reverse yields earliest-occurrence group order. New groups and matches already at the tail use an empty rotation. The shared matcher and named-range helper remain byte-for-byte unchanged.

`std::rotate` uses a raw pointer range ending at `Elements() + Length()`; `nsTArray::end()` is a different iterator type and is deliberately not mixed with raw pointers. `<algorithm>` is explicitly included. The header documents percentage relocation and the named-range exception.

## Caller, ownership, and order audit

Searchfox global text search and the pinned branch search identify one actual caller: the percentage loop in `Servo_StyleSet_GetKeyframesForName`. Other indexed occurrences are the declaration, definition, and generated FFI declarations. Receipts are `searchfox-callers.txt` and `pinned-callers.txt`.

| Boundary | Source fact | Consequence |
|---|---|---|
| Construction | The Rust entry point asserts an initially empty output array. The complete percentage loop runs before reversing that array and before appending any named-range frames. | Rotation never sees mixed percentage/named-range storage in this caller. |
| Offset sorting | `KeyframesAnimation::from_keyframes` sorts percentage steps by offset; the caller visits them backwards. | The current offset forms the array's final block. |
| Matching | `FindMatchingKeyframe` searches backwards and stops at the first different percentage offset. It compares the existing offset/easing/composition tuple. | A reused match and every group after it have the same percentage offset. Rotation preserves descending offset order and the existing entry assertion. |
| Empty/new array | `GetOrCreateKeyframe` either finds an existing element or appends one before returning. | `keyframe`, `keyframe + 1`, and the one-past-array endpoint form a valid nonempty-source rotation range, including the no-op tail case. |
| Matching borrow | The matcher's loop reference and iterator have ended when `GetOrCreateKeyframe` returns. Its temporary pair's numeric index is not retained by the percentage helper. | Relocating elements does not invalidate a still-used matcher reference or index. |
| Rust borrow | The FFI call happens before the caller forms the current `&mut Keyframe`. The previous iteration's reference is used only to append declarations during that iteration. No pointer to a percentage frame is saved across calls. | Return `LastElement()` after rotation; returning the old pointer would be incorrect. |
| Function arguments | Timing function is the caller's separate local value, composition is passed by value, and the offset is scalar. | Rotation does not move storage borrowed by those arguments. |
| Keyframe ownership | `Keyframe` has default move construction/assignment and owns its property array. Property pairs retain their declaration blocks through `RefPtr`. | Moving a whole frame preserves its offset, easing, composition, computed-offset bits, and property payload together. No style callback, effect publication, or JS invocation is introduced. |
| Range grouping | Named-range frames use a separate temporary array and index set after the percentage phase. The shared helper and range helper are unchanged. | No saved named-range group index is invalidated by this change. This candidate does not claim to repair analogous range-order questions. |

The invariant is one frame per matching tuple. Moving that unique frame changes future search order but cannot select a different matching frame. The payload association remains unchanged: physicalization, per-offset property admission, reverse declaration iteration, important/non-animatable filtering, and later-wins behavior all still occur in the unchanged Rust loop. In particular, this change does not broaden or redefine the current handling of the same property appearing in different easing/composition groups. It repairs group position, not every aspect of CSS keyframe assembly.

The intended final array order changes, so callers of `getKeyframes()` observe a change. No arbitrary outside borrower may retain element addresses across this helper; the audited existing caller meets that requirement. This is a source audit of the current synchronous construction path, not a general lifetime theorem for future callers.

## Cost

Let `g` be the number of groups at the current offset. A reused non-tail match rotates at most `g` frames, adding O(g) element moves; a new or tail group incurs no element movement. The existing reverse linear search already scans the same intervening groups, so the asymptotic worst case remains quadratic for adversarial repeated tuples. This is not a performance-equivalence claim: moving owning frame objects adds a potentially meaningful constant cost when groups are large/numerous. The rotation does not allocate a second array or duplicate declaration payloads. A runtime timing benchmark has not been performed. If real profiles identify this assembly path as sensitive, an explicit source-position index plus final sort could be evaluated separately; it would be a larger design with different allocation costs.

## Tests and delivery shape

The canonical WPT page is `css/css-animations/KeyframeEffect-getKeyframes.tentative.html`:

- Its existing bug-1778402 case distinguishes `A, B, C, B` earliest versus latest group ordering. The later `B` block now additionally overrides `margin-top` from 8px to 10px; its existing expected frame now requires 10px. Passing requires both earliest group placement and later declaration precedence.
- One new case uses authored offsets in `100%, 50%, 0%, 50%, 50%` order. At 50%, easing groups are `linear, ease-in, linear`. The last linear declaration uses `margin-inline-start` to override the earlier `margin-left` under explicit horizontal-tb/ltr context. Expected frames must be offset-sorted, place linear before ease-in, and retain the later 30px physical value.
- Existing cases on the page already cover same-easing merging, distinct easing, distinct composition, equivalent easing, overlapping selectors, empty/non-animatable frames, implicit endpoints, and property serialization. Those callbacks must remain unchanged.
- The two custom-property expected failures remain exactly as they were. Their independent stale-expectation issue is not part of this patch.

The standalone delivery patch has exactly four paths: `GeckoBindings.cpp`, its declaration header, the existing WPT, and that WPT's metadata. No proof/tooling/docs belong in the eventual bugfix commit. All such material remains in this preceding research capsule.

## Gates

`check.py --check-git` authenticates the copied source, exact before/after roles, forward/reverse patch replay in a temporary directory, unchanged shared/range helpers and Rust source, and precise metadata scope. It does not compile C++, execute WPT, or prove that `std::rotate` uses the expected move implementation. Range formatting used the actual Gecko filenames and repository style; commands/hashes are in `FORMAT.json`.

The [targeted runtime plan](TEST-PLAN.md) is outstanding. Require a real optimized build, intended two callback improvements on the modified WPT, unchanged remaining callbacks/messages, unchanged named-range controls, and complete source/app restoration. Compilation, WPT lint, browser runtime, and performance timing have not been run by this agent. This isolated array-order change introduces no new effect/lifetime admission path and does not inherit the separate missing-pseudo CSSOM repair gate; that final CSSOM repair still needs its own debug coverage. An optimized experiment cannot establish general debug/assertion coverage.

Parent-owned Lean work is separate: `css-keyframe-group-order-lean-20261110-v1` targets the abstract order transformation. This capsule does not duplicate or claim those proofs, nor does an abstract order theorem discharge the native ownership/declaration/runtime gates above.
