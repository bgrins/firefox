# Collapse traversal proof plan

This is a proposed companion scope, not an executed proof or acceptance gate.
The candidate and required boundary probes remain under independent review.

## Separate classification from aggregation

Model signed adjoining margins by their maximum nonnegative component and
minimum nonpositive component. The observable collapsed value is their sum;
store the pair rather than discarding information after every addition.

A block contributes its start margin before the traversal considers whether
it can collapse through. Its first in-flow child's start margin can join that
set even when the block itself has positive preferred height. A following
sibling is visited only after the preceding child's end margin is eligible.
Do not implement the new positive-size guard as an early return that suppresses
valid parent/first-child collapse.

Keep two outputs: collected start-margin summary, and collapse-through eligibility.
Represent resolved block size as unknown or a finite nonnegative value, and
minimum block size and both border/padding sides as explicit inputs. Existing
eligibility and hidden-by-parent classification remain separate booleans.
The new rejection refines existing eligibility only for nonhidden frames.

## Mathematical obligations

- Signed margin join is associative, commutative and idempotent.
- A non-monotone min/max percentage expression can be zero at both endpoints
  and positive at an interior basis; endpoint inference requires extra premises.
- For a nonhidden frame, positive resolved separation excludes collapse-through.
- An old nonempty result stays nonempty; zero/unknown resolved values preserve
  existing eligibility; the explicit hidden-parent exception is preserved.
- Traversal includes the next sibling's start only after the preceding subtree
  reports collapse-through. Show the concrete 10/20/80 counterexample and its
  corrected start-margin membership, not just the final arithmetic result.
- Keep clearance/empty-line/formatting-root tags distinct. A zero-valued
  clearance is not the absence of clearance.

## Source bridge

Prefer compiling the complete exact ComputeCollapsedBStartMargin definition,
with original and candidate versions, rather than a hand-copied guard. A finite
adapter can provide frame/line trees, ReflowInput values, style flags, wrappers,
normal/overflow lines and next-in-flow chains. Capture aggregate margins,
empty results, retry flags and dirtied-line effects. Authenticate exact helper
and caller branches and permit only the reviewed guard insertion in whole-file
preservation checks.

A modeled IsSelfEmpty boolean or size provider is an explicit premise, not a
proof of the global frame implementation. Retain the endpoint counterexample
as the bridge to the accepted browser witness. Resolved min/max/box-sizing and
fragment-consumption correctness belong to provider/boundary tests unless an
actual source-bound provider proof is separately built.

Finite fixtures should include the nested accepted witness, genuine-zero bases,
nonempty/empty inline lines, BFC barriers, absent output pointer, explicit hidden
parent, positive preferred/minimum/padding values, unconstrained sentinel,
clearance early exit, and small finite overflow/continuation chains. Control
mutations must detect moving the guard too early, ignoring min size/end padding,
counting the unknown sentinel as positive, admitting a later sibling after a
nonempty child, changing the hidden exception and losing signed margin extrema.

Universal claims should initially cover the pure finite-tree contract with
supplied providers. Native finite tests are additional evidence, not a compiled
C++ proof. Avoid whole-browser, arbitrary fragmentation or global emptiness
claims. A final companion requires source review, fresh replay, negative
controls and independent review before preceding the native/WPT commit.

## Independent review correction: output initialization across fragments

The native function sets aBlockIsEmpty after the first block's normal lines.
A later overflow/next-in-flow nonempty exit only assigns false if that output
has not already been set. Therefore a later nonempty line can stop traversal
while an earlier true result remains. This can reflect first-fragment semantics;
no new defect is established by the observation.

The exact native capsule must model setBlockIsEmpty and the initialized output
explicitly. Do not equate a true return slot with structural emptiness of every
visited fragment. The sibling-membership contract refers to the child's actual
reported result. Restrict the initial abstract all-subtree soundness theorem to
ordinary normal-line finite trees, with overflow/continuation state treated as
separate finite compatibility coverage until its semantics are established.
The candidate's final positive-size rejection remains separately testable in
all output-initialization states.
