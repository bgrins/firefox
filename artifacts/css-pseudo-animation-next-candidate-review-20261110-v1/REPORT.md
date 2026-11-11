# Owned keyframe-input extraction review

No blocking source-level finding in the frozen two-file prerequisite refactor.
It is suitable for a separate build and ordinary-path preservation experiment.
This is not acceptance of a missing-pseudo CSSOM fix, and it does not waive that
work's debug, range-timing, cascade-freshness, or lazy-resolution gates.

Reviewed `css-pseudo-animation-next-candidate-20261110-v1/snapshot.patch`, SHA256
`b37e4885614c5b2acb7fa4320ca734fd2c7fa1062e12f5b55c6e60be71d25166`,
against source revision `7382007a82b49e83e5399a31f47b598e0f260fe5`.
`CHECK.json` authenticates all twelve copied sources against their Git objects,
both candidate file hashes, and exact forward/reverse patch application in an
isolated review-owned tree. All other bytes of `KeyframeEffect.cpp` and its
header are unchanged outside the extraction/insertion. No native build or
browser execution was performed by this review.

## Ownership and capture order

`PropertyInputSnapshot` owns its specified/computed array storage, captured
composite, and `OwningAnimationTarget`. The latter holds a strong element
reference and the complete pseudo request. Keyframe copies retain their
reference-counted Servo declaration blocks; they do not deep-copy those blocks
or prove arbitrary semantic immutability. This is accurately stated in the new
header comment. No raw style or timeline pointer is retained in the snapshot.

`CapturePropertyInputs` first checks for a target, clones the specified array,
then calls the existing virtual `GetComputedKeyframes` exactly once. Only after
that call does it copy the target and effect composite. This preserves the
old ordering of the relevant reads across virtual dispatch. The generated
array and the generator's Boolean are both retained: false still selects the
specified clone, even if a future generator happened to write its output
before returning false.

The new strong target reference extends lifetime through property conversion.
This is a deliberate ownership improvement, not a claim that all reference
counts or destruction instants are byte-for-byte unchanged. The existing
base/CSS overrides do not mutate target/composite during generation. No claim
is made about arbitrary hypothetical future overrides with different side
effects. An independently retained snapshot is also not a guarantee that its
target's later style, layout, timeline, or rule state remains current.

## Ordinary behavior preserved by the source transformation

The ordinary `BuildProperties` entry still asserts a style, initializes the
attribute-reference output to false, and returns before cloning or virtual
generation for a missing target. It captures inputs and delegates conversion.
The helper independently initializes the output, returns empty for a missing
captured target, and passes the same selected array, target element, pseudo
request, style, effect composite, timeline, and attribute-output reference to
`KeyframeUtils::GetAnimationPropertiesFromKeyframes`.

The original debug comparison against the specified array remains after
conversion, as does moving that clone back to `mKeyframes`. Empty computed
property results do not skip either operation. The helper does not publish
`mProperties`, `mReferencesAttributes`, base-value caches, animation generation,
or effect-set bookkeeping. Existing callers continue to handle those steps;
their implementation bytes are unchanged. The exact local attribute-reference
parameter was checked, rather than relying on older indexed Searchfox code
which lacks it.

`GetKeyframes` is unchanged, including its CSS style flush, computed-offset
update, virtual completion call, serialization and implicit-base handling.
`CSSAnimationKeyframeEffect::GetComputedKeyframes` and the CSS setters are also
unchanged. Thus the JS-set-keyframe generation opt-out, CSS default easing and
default composite distinct from effect options, stable range-keyframe order,
unresolved-range treatment, missing endpoint/property generation and null
declaration-block markers continue through the same implementation.

The copied arrays use existing `Keyframe` and `PropertyValuePair` copy/move
operations. Existing includes already supply their types and
`OwningAnimationTarget`. There is no new WebIDL surface or cycle-collected
object member; the snapshot is an owned C++ value. Its intended consumer must
still obey the existing main-thread and supplied-context requirements.

## Important narrowing of the proposed milestone

This patch captures the completed output of CSS generation. It does **not**
extract independently reusable CSS generation parameters or make the generator
operate on an externally supplied specified-keyframe snapshot. Captured
generated frames preserve the offsets/defaults already used at capture time.
They cannot be assumed correct after later named-range offset refresh or a
changed CSS generation context.

That narrowing is acceptable for this prerequisite but must remain explicit.
The next missing seam is owned-input range refresh followed by generation using
the appropriate CSS defaults and opt-out state, without silently consulting a
mutated live effect. `BuildPropertiesFromInputs` also receives style and timeline
from its caller; it does not select or prove their freshness. Target/pseudo
style resolution, base styles, selected cascade-level membership, composition
ordering, lazy CSSOM recursion, and dispatch/pending timing remain outside this
refactor.

The source extraction does not repair bug 1615083 by itself. In particular,
the prior investigation's distinction between CSSOM-only nonexistent pseudo
resolution and generated-element restyling remains relevant; this patch adds
no animation posting or resolution rule. The established missing-pseudo debug
gate is retained unchanged.

## Remaining acceptance gates

A real native build must validate C++ declarations, aggregate/move construction
and linkage. Focused runtime comparison should preserve ordinary CSS-generated
and JS-set `getKeyframes`, missing endpoints, CSS-vs-effect easing/composite,
attribute dependency behavior, null target, and existing range-offset controls.
This report neither ran those tests nor certifies them from source inspection.
It also makes no formal refinement or numerical-equivalence claim.

The author may finish harness/report preparation after this source review;
those execution inputs require their own review before a browser transaction.
The candidate source and patch hashes above are the reviewed boundary.

Only this review directory was written. No live native source, browser,
canonical library, Git index, or commit was changed. Temporary patch directories
were removed.
