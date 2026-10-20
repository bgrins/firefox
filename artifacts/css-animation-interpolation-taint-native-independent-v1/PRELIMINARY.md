# Interpolation taint repair: preliminary independent source review

Not sealed or accepted; final producer patch and source pins pending. No native or browser execution by this reviewer.

The proposed change is only successful Value<Component>::animate output attr_tainted = self.attr_tainted || other.attr_tainted. Existing payload result, error, URL-data clone, allocation/representation and global PartialEq remain unchanged.

## Complete inspected transition paths

- CustomAnimatedValue checks name equality; Option handles Some/Some by delegation, None/None as None, and mismatches as error. The changed Value body is not reached for the two latter cases.
- ValueInner derive rejects different variants; Universal is animation(error). String and CustomIdent components are animation(error). The inspected derive emits Err before constructing a result for those annotations.
- ComponentList verifies multiplier then delegates to by_computed_value list behavior. Any error propagates through `?` before the new metadata expression; successful list outputs receive the union of wrapper provenance.
- compose_animation_segment selects explicit/underlying endpoints, handles Add or Accumulate via composite_endpoint, and optional iteration accumulation via accumulate_endpoint. On failed interpolation it clones one selected endpoint; OR in the failed Value call cannot affect that branch.
- Procedure::weights is (1-p,p), (1,1), or (count,1). The interior numeric contract and positive accumulation/addition retain both contributions. Zero-weight interpolation and count=0 accumulation remain conservative-taint policy boundaries; the narrow oracle does not prove unique correct taint there. Procedures for other components can have specialized semantics, so a universal all-value metadata algebra is not established.
- URL-data selection remains from self. The fix does not establish URL-data equivalence or replace provider/keyframe/scheduling admission.

## Standalone scope prediction

The test's fresh target, explicit initial/inherit endpoints, differing 12/8 numbers, and whole-bundle observer avoid raw attr keyframe conversion and metadata-only replacement/base invalidation. Exact patch applicability/upstream source comparison is still required. No claim that all earlier code is unnecessary merely from this construction.

No concrete source correctness blocker found for the intended successful arithmetic combination path. Await final patch, test, original/final source hashes and root runtime before bounded final review.
