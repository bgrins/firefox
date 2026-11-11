# Named-range group-order extension for bug 1778402

Prepared a copied three-file extension to local fix #172. It preserves group
indices through property deduplication, then emits named-range groups by their
earliest source occurrence. This is the same group-order issue, not an additional
counted bug. No live source, browser, WPT installation, build, or Git mutation was
performed by this agent.

The base is `883d620fdbd6b66d4df871d660ee9612d1c20985`, which already contains the
percentage repair. `range-order.patch` changes only `servo/ports/geckolib/glue.rs`,
the expected ordering in `merge-timeline-offset-keyframes.html`, and the new
`named-range-group-earliest-order.html` test. The final standalone bugfix should
include both percentage and range repairs through parent-owned history
restructuring; research/proof material remains outside that commit.

## Evidence and contract

The [source review](../css-named-range-group-order-review-20261110-v1/REPORT.md)
establishes **REACHED** for equal resolved named offsets under current
[CSS Animations 2 processing](https://drafts.csswg.org/css-animations-2/#keyframe-processing).
Groups retain their earliest occurrence; declarations within a group retain
later-wins precedence. Equal-offset stable sorting cannot repair an earlier
grouping mistake.

Root subsequently ran the exact original two-callback proposal on the current
#172 optimized browser. The unique-group control passed. The repeated group
passed finite offset `0.5` and later declaration `30px` assertions, then failed:
expected `linear, ease-in, ease-out`, observed `linear, ease-out, ease-in`.
The harness ended OK; the root transaction reports restoration verified and no
error. `BASELINE-EVIDENCE.json` pins the raw callbacks and result receipt. This
agent read those receipts; it did not execute the browser or independently repeat
root's complete app-restoration audit. The expanded three-callback candidate has
not yet run in a browser.

## Construction and ownership

The named-range vector is enumerated **before** reversing it. Thus each stored
position is the original expanded `KeyframesStep` index, not reverse visitation
order and not a CSS source line number. The unchanged helper chooses one stable
frame slot for each offset/easing/composition tuple.

| Operation | Frame slots | Position metadata | Saved deduplication indices |
| --- | --- | --- | --- |
| Initially | Empty | Empty | Empty |
| Create a group | Append one frame; helper returns post-append length as sentinel | Append this step's position | No index added |
| Reuse a group | Existing slot stays in place | Replace that slot's position with the earlier step position | Insert the same existing numeric slot |
| Deduplicate | Existing helper consumes the index set; no slot reorder | Unchanged | Fully consumed |
| Emit | Drain whole frames, pair with positions, sort by position, append owned frames | Consumed with the paired vector | No remaining consumer |

For an old length `n`, creation returns sentinel `n + 1`, which equals the new
array length and cannot be an old slot. Reuse returns an index below `n`; array
length remains `n`, and metadata length is also `n`. Exactly one metadata entry
is appended for each frame creation, so lengths stay aligned. A debug assertion
checks that alignment before zipping; the source invariant, rather than the
assertion alone, prevents release-build zip truncation.

Reverse enumeration strictly decreases source positions. Each stored value is
therefore replaced by an earlier occurrence of its own group. A newly processed
position is distinct from all values still stored for other groups. Final earliest
positions are unique, so `sort_unstable_by_key` cannot arbitrarily permute ties.
The helper's matching relation and stable slot identity are native premises;
the Lean model does not execute that FFI call.

The original declaration collection remains unchanged: physicalization, reverse
declaration iteration, animatability/importance filtering, and first-seen property
deduplication after reverse traversal retain the same payload winners. Percentage
construction and its final reverse are unchanged. The C++ range helper and its
signature are unchanged. No post-resolution sorting, endpoint generation,
composition, or timeline behavior is modified.

No frame is reordered until the deduplication index set has been consumed. The loop's
temporary mutable frame reference is not retained across that phase boundary.
`drain`, owned `Vec` elements, sorting and `extend` move the entire `Keyframe`,
including offset, easing, composite, computed-offset fields and its owning property
array. No property/declaration payload is cloned, and no extra unsafe operation,
style callback, effect publication or script call is introduced. Moving these
values is already required by the existing ThinVec construction/drain path.

The alternative of moving each reused range group immediately is intentionally
excluded: it would invalidate previously saved numeric indices even if the current
match returned its new index. The `A, B, C, B, A` case specifically guards against
that shortcut.

## Cost

For `g` distinct range groups, the change adds a metadata `Vec<usize>` and a
temporary owned `(Keyframe, usize)` vector. Both are O(g); while collecting the
pairs, the original ThinVec buffer and metadata storage can coexist with the new
buffer. No deep property-payload copy occurs. Final sorting is O(g log g), and
metadata updates during traversal are O(1). Existing group lookup can still be
quadratic in the number of authored occurrences/groups; this does not remove that
cost. Zero groups allocate no vector elements. The simpler ownership and stable
index reasoning come at a real extra allocation/movement cost, not performance
equivalence. No timing or allocation benchmark was run.

## Test changes

The existing merge WPT's first callback authored `entry 0%, entry 100%, contain 0%,
entry 100%`. Its `entry 100%` and `contain 0%` groups resolve to the same `1/3` offset. The corrected
expectation moves merged `entry 100%` before `contain 0%`, retaining every value,
offset and other field. This follows the current earliest-group contract. The
second callback's distinct easing creates a distinct group, so its expectation
is unchanged. The prior percentage-only comparison remains valid: it deliberately
preserved this old range expectation while changing only the percentage path.

The new WPT contains three callbacks at `cover 50%`:

- `A, B, C`: unique-group control.
- `A, B, C, B`: ordering plus B's later property winner.
- `A, B, C, B, A`: two duplicated groups; both later winners must survive.

All check source validity and finite equal computed offsets, then B's later
`margin-left` winner before the group-order assertion. The third case also checks
A's later opacity winner. This can expose stale saved-index deduplication even
when an attempted rotation appears to repair order.

Root should run these **final test bytes** against baseline and candidate. The
corrected existing expectation is predicted to fail on baseline along with both
repeated-group callbacks; only the original two-callback probe is already
browser-observed. Preserve the existing percentage and range controls. Require
native optimized compilation, genuine WPT lint and exact comparison/restoration
before integrating the extension. No broader missing-pseudo/debug gate is waived.

## Verification and proof limits

`verification-final/report.json` passes:

- Exact Git-source authentication and forward/reverse three-path patch replay.
- Rustfmt check with the repository's `servo/rustfmt.toml`.
- Inert JavaScript syntax checks of both candidate WPT pages.
- Fourteen Lean axiom audits; only standard `propext`, `Quot.sound` and
  `Classical.choice` are allowed.
- Two rejected false claims: uniqueness without freshness, and zip cardinality
  without length alignment. These are proof-boundary controls, not native mutants.
- 3,280 finite sequences over three groups, checking position uniqueness/alignment,
  earliest group order and later winners for two property IDs.

`Slots.lean` proves conditional create/reuse length preservation, valid slot
access/sentinel distinctions, descending-position freshness and uniqueness,
earlier-position minimum, and aligned zip cardinality. The separate root-owned
[source-position model](../css-keyframe-source-position-lean-20261110-v1/PositionLaws.lean)
proves pointwise reverse-update metadata equals the first source occurrence,
including its `zipIdx` instantiation. That corresponds to enumeration before
reverse traversal here. It is distinct from the native group-slot representation.

Neither proof executes Rust/C++ or proves ThinVec/Vec ownership, sorting,
allocation behavior, CSS parsing/equality, or declaration payload semantics.
The slot invariant is manually connected to the audited helper contract and
reverse enumerator; the finite model is not a universal refinement proof.
No compiled outputs are retained. Native compilation, candidate browser execution,
and genuine WPT lint are parent-owned outstanding gates.

Reproduce the source-only checks with:

```sh
python3 -B check.py --lean /path/to/pinned/lean --out /new/receipt/directory
```

`prepare.py` regenerates the copied inputs from the frozen review sources. It must
not be run against live native files; it writes only this capsule's copies.
