# Registered numeric interpolation provenance

## Repair and runtime

Value<Component>::animate now unions both operands' attribute taint after the
existing payload operation succeeds. Its payload, first-operand URL data and
failure return are unchanged. The correction applies only to successful
combinations; failed/discrete selection remains in the existing caller paths.
Independent source review examined procedure weights, Option and enum/list
providers, direct FFI, endpoint composition and final segment fallback.

The initial 40-case probe has 37 passes and three failures: clean-to-tainted
whole-bundle URL observations at .25, .75 and 1. The focused landing WPT has
24 fixed-oracle cases; its fresh baseline has 22 passes and two failures at
.25 and .75. All provider, numeric, progress and direct-URL controls pass.
Both probes use new targets and explicit CSS-wide endpoints, avoiding raw
attribute keyframe conversion and metadata-only invalidation prerequisites.

The candidate build succeeds. Its matrix has 253 passing subtests and 16 OK
harnesses. The joined reference has 248 passes and five failures; those five
assertions improve and the other 248 statuses remain unchanged. The reference
joins the previous189-case candidate,40-case diagnostic and fresh24-case baseline;
it is not one fresh253-case baseline invocation. Two diagnostic boundary checks
allow either taint polarity; older attr-security entries include conditional
assertions. These limitations remain distinct from fixed-oracle WPT coverage.

Before/after source and binary hashes are stable except for the intended Rust
change and rebuilt executables. Supplemental setKeyframes test and absent new
WPT metadata checks are recorded separately. This is shared-tree runtime,
not an isolated upstream build or a release-browser/performance result. Known
build-monitor export KeyErrors remain in the successful build log.

## Test transfer and packaging

The final WPT differs from the tested version only in a rel=help fragment,
corrected to animation-behavior-of-custom-properties after checking the locked
primary source. JS, CSS and assertions are byte-identical. The original tested
fixture and exact transfer are retained. Scoped native formatting and final
lint exit zero; lint reports one warning and makes no changes.

Both branch and upstream packages contain exactly two files: one Rust line and
the 24-case WPT. Root verified complete Git apply/reverse and resulting blob
hashes against each actual base. The upstream operation is identical to the
branch's original body and needs no prior accessor, map or invalidation repair.
This establishes source applicability; upstream runtime remains untested.

## Formal gate and boundaries

Root and independent review accept the compact formal component. Fresh root
and independently relocated replays pass 15 kernel audits and 45 compiled
native observations per variant. The original wrapper disagrees only on three
successful clean-first/tainted-second combinations. Failure and optional controls
agree. The theorem proves successful metadata union and finite admitted pure
expression provenance; numeric provider correctness, fixture-to-CSS URL
semantics and native animation/scheduler histories remain explicit assumptions.
FORMAL-ACCEPTANCE.json binds the reviews and retained root replay.

The independent normative contract composes registered numeric interpolation
with provenance-through-substitution rules. Interior contributions from both
operands justify the mandatory taint assertions. Conservative zero-weight taint
retention remains an explicit policy boundary; all component arithmetic and
extrapolation are not proved. URL-data selection and global equality are outside
this repair. The separate transition-retention oracle remains INCONCLUSIVE.

Discovery was source/spec investigation followed by calibrated browser
reproduction; formalization followed. The old and repaired builds distinguish
one defect, not five separate bugs.
