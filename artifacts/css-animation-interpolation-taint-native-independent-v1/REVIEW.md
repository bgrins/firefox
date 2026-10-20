# Independent source review: registered-value interpolation taint

## Decision

**Approve the exact one-line repair at the bounded source-review level.** No concrete correctness blocker was found. Root's final paired runtime, final native/WPT packaging and corrected help-link transfer remain separate gates. This review does not accept an unobserved candidate run or establish universal CSS/native refinement.

Authenticated producer `css-animation-interpolation-taint-proposal-v1/FILES.json` SHA `dec14bde06e9c8bbcd14b9001ee6d8a6f3751a087fc0176f47bdc792803ede6b`, then all 12 listed inputs before using them. Native patch SHA `f71bde0368680e8cdfd39c9df1fc5e0ab3e302a4b76fe1eea7f46b35b7b562f8`; branch candidate SHA `485c097931bcb385bc0ada6679c3429f6f300ffae5f03c75268458feb3316fa0`; reviewed 24-case WPT SHA `c48a34cac0e4afce1bc52fb6f0614db057c0150a63e771863fe655705a6313e4`.

## Complete local operation and caller branches

`Value<Component>::animate` first calls the same payload provider with the same `Procedure`; `?` propagates its error before metadata construction. On success the patch preserves the exact payload result and first-operand URL data, replacing only the output taint with Boolean OR. It adds no allocation, representation, FFI, equality, error or null-return change.

| Path inspected | Effect of proposed change |
|---|---|
| `CustomAnimatedValue::animate` | Different names still fail; same names delegate through optional values |
| `Animate for Option<T>` | Some/Some delegates; None/None returns None; mismatched presence fails before Value construction |
| Generated `Animate` | Different discriminants and annotated error variants fail; remaining fields delegate with error propagation |
| `ValueInner` / component enum | Universal, String and CustomIdent error paths remain errors; they do not construct a union-tainted arithmetic result |
| `ComponentList` / `by_computed_value` | Multiplier and length mismatches fail; paired element failures propagate; successful lists receive wrapper provenance union |
| Direct FFI interpolate/add/accumulate | Same successful payloads and null failures; interpolability checks depend on success, which is unchanged |
| `composite_endpoint` | Add/accumulate combines underlying and explicit endpoint; missing endpoint clones underlying; failed combination retains existing fallback behavior |
| `accumulate_endpoint` | Iteration composition uses the same result/fallback selection; normal segment caller enters this only for positive iteration count |
| `compose_animation_segment` | Failed interpolation clones the existing selected endpoint; zero-length intervals select directly; neither route applies the new metadata construction after an error |

Complete indexed Procedure, list and derive implementations are retained. Exact Procedure/numeric/Option source transfer to the producer snapshot is checked separately; the whole indexed file is not presumed current. The reviewed complete local glue and value snapshots exactly match the producer's original snapshots.

## Normative scope and limits

The independent oracle composes registered numeric interpolation, weighted numeric arithmetic and [attribute-taint substitution](https://drafts.csswg.org/css-values-5/#attr-security). At .25 and .75 both endpoint contributions are nonzero; a later substitution must retain either contributing endpoint's provenance. The patch addresses the reproduced clean-first/tainted-second path. Addition and positive-count numeric accumulation likewise combine both operands.

At interpolation progress 0/1 and accumulation count 0, union conservatively retains a zero-weight operand's provenance. The reviewed text does not uniquely settle that boundary policy; no exact all-progress metadata algebra is accepted here. Other component procedures can specialize their arithmetic. Extrapolation, exceptional arithmetic, all list/component semantics, and arbitrary effect histories are not proved by this review. The patch never clears previously retained first-operand taint.

First-operand URL-data selection remains unchanged and unproved as a general quotient. Actual value construction, scoped ownership, publication, cache invalidation, scheduler delivery, numeric representation and compiler/runtime remain admissions. No transition restart or retained-endpoint-refresh conclusion follows: the separate transition-retention oracle is INCONCLUSIVE.

## Standalone and WPT review

The root-supplied upstream file SHA `a86c48b68b7cf373aa1b0039af2be1ad926bd50b57e39adf4c4b622272ba0d0c` was authenticated. Its complete Value Animate implementation is byte-identical to the branch original. Full-file differences are only the previously added public visibility/documentation for `from_computed` and the endpoint taint getter. The new operation uses neither. Four isolated artifact-only patch operations apply/reverse exactly on branch and upstream snapshots; expected entire file bytes match each time. No Git or live source was changed. This is source applicability, not an isolated-upstream browser run.

The landing test has 8 static calibrations and 16 interior samples. Each sample has a fresh target, explicit replacement endpoints, known inherited attr-derived 8 versus initial 12, and checks effect existence, exact progress, numeric payload and border-image-source. The bundle observer has a URL inside the substituted whole custom property; the direct observer keeps the URL outside the tainted numeric substitution. No resource download or support skip establishes its result.

This construction avoids raw attr/var keyframe conversion, equal-payload endpoint replacement, implicit endpoints and base-cache mutation. Static inherited and clean controls check the selected provider path. The prior metadata fixes are not source prerequisites of the one-line operation; broader histories may still need them. The test does not cover Add/Accumulate or arbitrary list operations.

**Pending documentation transfer:** the sealed WPT's `#animation-behavior` help fragment is absent from the current Properties and Values API draft. Correct fragment: `#animation-behavior-of-custom-properties`. Root will retain tested bytes and record an exact link-only correction after its pair. No semantic script/style change is requested and producer bytes remain frozen.

## Evidence and cleanup

`APPLY-REVERSE.json`, `SOURCE-TRANSFER.json`, `UPSTREAM-COMPARISON.json`, complete snapshots and `upstream-to-branch.diff` retain the checks. `PRELIMINARY.md` is historical preseal analysis, superseded by this decision. Generated apply/reverse scratch copies (56,658 bytes) were removed after receipt retention. No Firefox build/browser, native edits or Git operations were performed. No universal proof or new runtime result is claimed.
