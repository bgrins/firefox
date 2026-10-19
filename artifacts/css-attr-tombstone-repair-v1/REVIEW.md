# Preserve invalid attribute entries during lazy loading

## Verdict and scope

The proposed helper and single guard change correctly distinguish a never-loaded qualified attribute from a deliberately invalidated qualified attribute. Ready for independent review and root's native application/build/runtime gates. This is an artifact-only proposal; it is not an accepted full substitution proof or a native build result.

The original diagnostic browser run against namespace candidate-v3 confirms exactly the four predicted failures, with seven passing tests including calibration and harness OK. The separate final ten-test WPT is not yet executed in this package. Root must baseline it before applying the patch, then run the identical file against the candidate.

## Source binding and minimality

`BASE.json` authenticates the complete namespace candidate-v3 custom_properties.rs, properties/cascade.rs and Gecko glue snapshots against the root's candidate input pins. The namespace-aware public insert_attr API and all other source bytes are preserved. `native.patch` adds only crate-local contains_attr and replaces the lazy-load condition in visit_value_references. It changes no representation, external ABI, order-index allocation, graph edge, fallback traversal or evaluator body. No existing namespace, cascade rollback, or experimental source delta is included in the patch.

The helper asks whether the namespace bucket contains the particular local-name entry. A bucket for another name does not suppress loading. A same-name entry in another namespace does not suppress loading. Present None counts as present; get_attr continues to flatten it to invalid. Searchfox confirms OwnMap uses contains_key. Searchfox's indexed getter has the older unqualified signature; local candidate-v3 snapshots are authoritative for this patch.

The patch is generated against candidate-v3. Artifact-only forward/reverse application is checked exactly against those snapshots. HEAD application is a distinct root gate because the cascade snapshot contains other local experiments; this agent performed no Git/index operation. The two small hunks need no experimental behavior to distinguish entry occupancy, but clean applicability to the signed namespace stack is not asserted without root's check.

## Caller and write audit

Discovery outputs are retained in evidence/. The indexed Servo-wide get_attr matches include unrelated DOM/selector methods; they are not calls to ComputedSubstitutionFunctions. All relevant candidate-v3 calls are:

| Function / operation | Treatment |
| --- | --- |
| visit_value_references lazy fetch | Only changed caller: contains_attr distinguishes absent from present-invalid before a provider/parse attempt. |
| visit_value_references resolved-primary classification | get_attr remains unchanged, so invalid entries use fallback. |
| traverse attribute shortcut | get_attr remains unchanged, so a tombstone returns None before consulting an old numeric index. |
| substitute_internal typed attribute lookup | get_attr remains unchanged; invalid remains failure rather than a parsed raw token stream. Container-query bypass remains unchanged. |
| update_attributes_map preload | Same namespace/name Seen dedup and success-only insert, before graph resolution; not changed to occupancy checking. |
| visit_value_references lazy insertion | Still happens only following provider/parse success and now only for an absent entry. |
| substitute_references_if_needed_and_apply success | Still stores computed attribute text under its qualified key. |
| substitute_references_if_needed_and_apply failure | Still writes a present None through remove_attr. |
| Context::handle_loop | Still writes a present None for cyclic attributes. |
| Gecko glue substitution helper | Still preloads through public insert_attr in its own substitution map; it does not call this lazy guard. No new visibility requirement. |

Public attributes storage and other constructor/evaluator consumers retain their existing behavior. This patch does not turn contains_attr into a value-validity predicate at any other caller.

## State transition argument

| Entry before lazy visit | Previous behavior | Proposed behavior |
| --- | --- | --- |
| Namespace bucket missing | Attempt fetch/parse | Same |
| Bucket present, local name missing | Attempt fetch/parse | Same |
| Local entry present with None | Attempt fetch/parse and possibly replace semantic invalidation | Preserve None; skip fetch |
| Local entry present with Some(value) | Preserve entry | Same |

Unknown namespace is rejected before the guard and retains used-fallback traversal. Known null namespace remains a normal namespace key. Missing DOM values and initial parse failures never insert an entry, so repeated attempts remain possible. This fix does not cache those failures as tombstones. Failed substitution and cycle handling deliberately insert None, so repeated visits preserve those decisions. A skipped reload also avoids redundant attribute-provider observations; the original load that established the entry already recorded the attribute dependency. Full observer/evaluator equivalence is not inferred merely from that local observation.

For the shortest witness, --out has index 0 and x has completed at index 1. Originally a second reference reloads raw x, traverse returns the retained index 1, and visit_link takes its larger-index branch, setting min(0, 1) = 0. It does not traverse x again. Typed final substitution then accepts raw attr()/var() tokens under type(*). The corrected guard preserves None, so traverse returns before the index lookup and both sibling attr invocations use their own fallbacks. The earlier frozen trace's mistaken finished-marker branch is preserved with its explicit correction in evidence/source-trace-correction.md.

The qualified index/reload proof package already proves corrected_loader_preserves_any_present_entry and corrected_loader_retries_absence, plus finished-terminal preservation for the corrected load transition. This patch implements that transition by the nested map membership check. Those universal model results remain conditional on Hash/Eq/map correspondence and on completed resolution storing terminal values. They do not prove the whole native Tarjan traversal, provider stability, arbitrary substitution completion, bounds, cache invalidation or all observers. Completion invariants apply at completed-visit checkpoints, not while var_info.var has just been taken before apply. Namespace identity and source ownership obligations remain as previously stated.

## Browser evidence and WPT

Retained baseline-v1-receipt.json reports unchanged inputs, suite end once, 4 FAIL / 7 PASS / harness OK. Its two source pins match BASE.json. Failures are:

- repeat-cycle: expected 13px 37px, received attr(x type(*)) twice.
- repeat-invalid: expected 13px 37px, received var(--missing) twice.
- repeat-two-node-cycle: expected 13px 37px, received attr(y type(*)) twice.
- same-cycle-value-different-names: expected 13px 37px, received attr(x type(*)) twice.

The new attr-repeated-invalid-value.html retains these four witnesses and six controls: single cycle, constrained length type, single missing variable, valid literal, distinct cyclic attributes, and separate declarations. It removes diagnostic readbacks/support/calibration and directly asserts computed custom-property values and margins. It uses per-test cleanup and no nonstandard helper resources. Its cases are null-namespace examples, so the semantic issue is independently testable from namespace collisions; the patch is expressed against the namespace fix's API and follows it in the current stack. Final WPT baseline/candidate results remain a root gate.

## Spec and remaining gates

The retained primary CSS Values 5 snapshot and SPEC-TRACE establish substitution before attr type parsing, cyclic guarded-context invalidity, and per-invocation outer fallback. The source is fetched 2026-10-19 and its anchors are checked. The type(*) parser cannot legitimize unresolved substitution functions. The known container-style-query chained-attr limitation (source TODO bug 2028861) is unchanged and not this claim.

Remaining gates: independent source review; clean signed-stack apply/reverse; native formatting/build; final ten-test original/candidate pair; relevant existing attr regressions and mutation/invalidation coverage as root deems necessary. No performance-neutrality or full CSS-substitution closure claim is made.
