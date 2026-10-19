# Registered keyframe fix: standalone dependency audit

## Verdict

The captured two-file endpoint fix is source-independent of the unrelated dirty cascade and numeric dependency changes for the retained 16-case numeric WPT. No additional source dependency was found for its simple literal, calc, var, typed null-namespace attr, missing-attribute fallback, direct CSS-wide and invalid/missing-var cases. The same exact native diff applies with zero fuzz to both pinned revisions and reverses in a dry run.

This establishes source applicability and an audited provider-path argument. It does **not** establish an isolated standalone compile or runtime result: neither was run here. Root's candidate 16-pass result is a combined-tree observation, not an upstream-base runtime result. A formal universal equivalence of the two provider implementations is not claimed.

## Inputs and identity

- Standalone base: `976279105b2e78b8666a959eb3f25c9176cefaf8a`.
- Branch HEAD: `8071ad697b3c447b58c40d4c27df05c938193dff`.
- Seven complete source files at each revision and the current candidate were captured using read-only `git -c core.fsmonitor=false show` and ordinary file reads. `INPUTS.json` binds those 21 files. The current expanded 16-case WPT is retained separately and authenticated by the final manifest.
- No index, refs, production file or WPT was changed. Artifact-only `patch --fuzz=0` produced `application/base` and `application/head`; these are not browser build trees.
- `endpoint-native.patch` contains only the glue conversion branch and public visibility/documentation for `CustomAnimatedValue::from_computed`. `APPLICATION.json` records both applications and reverse dry runs. HEAD application equals the captured current source byte-for-byte in both files.

## Complete-body comparisons

`BODY-CHECKS.json` records exact selected complete-body identities. The entire `KeyframeCustomPropertiesBuilder` struct and impl is identical across base, HEAD and current. The original complete `Servo_GetComputedKeyframeValues` is byte-identical base versus HEAD; only the intended candidate output loop differs. Therefore the helper is already a base dependency, not a new branch-only prerequisite.

The complete `CustomAnimatedValue::from_declaration`, `Cascade::value_may_affect_style`, `apply_custom_and_prioritary_properties`, `handle_invalid_at_computed_value_time`, `normal_declaration_iter`, and `AnimationValueIterator` Iterator impl are unchanged in the compared sources. The entire `value.rs` is byte-identical base to HEAD. Existing registration-selected map lookup and CustomAnimatedValue constructor APIs are present in the base. The patch calls no newly introduced helper from the intervening fixes.

## Exact diff categories and relevance

All unified diffs are retained under `diffs/base-head` and `diffs/head-current`; names below refer to functions, not unstable line numbers.

| Difference | Path and actual effect | Relevance to retained cases |
|---|---|---|
| Uncommitted rollback/source identity | `cascade.rs`: declaration iterator supplies source block, non-custom declaration records retain it, RevertState accumulates cutoffs and rule exclusions | No revert/revert-layer/revert-rule occurs in the 16 cases. The keyframe builder's ordinary Declarations is empty. Its custom cascade passes the empty revert guards for these numeric values. These changes are not required. |
| Uncommitted numeric dependency expansion | `syntax/data_type.rs`: Number/Integer/Percentage/Angle/Time/Resolution gain LENGTH dependent classification | Every numeric operand is unitless: `0`, `14`, `30`, `42`, and `calc(40 + 2)`. Attribute and var references do not introduce font-relative units. No new LENGTH scheduling is needed for these fixtures. Dimensional arithmetic such as `calc(1em / 1px)` is outside this standalone argument. |
| Branch namespace-aware attribute maps | `custom_properties.rs` and `cascade.rs`: attr keys become (namespace, name), namespace travels through graph traversal/cache and actual substitution | Tests use one unprefixed HTML data attribute or one missing data attribute. Base's name-only key and current's null-namespace key select the same source attribute here. No competing namespaces, unknown prefix or same-name alias exists. |
| Branch tombstone admission | `cascade.rs::visit_value_references` uses contains_attr instead of absent-value lookup before fetching | Direct numeric attribute is acyclic and valid; missing attribute simply fails loading. No invalidated/tombstoned attribute is re-entered. Not needed for current cases; cyclic attr tests would require separate review. |
| Branch typed occurrence eligibility | `AttributeData::parse_typed_value` and graph primary-valid check distinguish typed-invalid primary from valid fallback | Present `data-value` is `42`, valid `<number>` under either implementation. Missing attr fallback is literal `42`, with no nested fallback dependencies. Primary absence already triggers fallback in base. The new typed-invalid graph check is not necessary for these fixtures. Do not generalize to invalid typed primary with dependent/cyclic fallback. |
| Branch nested attribute preload | `Cascade::update_attributes_map` scans fallback references recursively | The only fallback is the numeric literal `42`, so there is nothing additional to preload. |
| Branch registered/non-custom dependency graph refinements | `cascade.rs` retains longhand/property context and no longer exits early for attr-only non-custom references | These keyframes animate a registered custom number. No font-size/line-height/color-scheme dependency, shorthand context, or non-custom graph node is exercised. |
| Branch resolved-token dependency summaries | `VariableValue::new_resolved`, `resolved_token_dependencies` at two persistence sites | Resolved payload `42` contains no Dimension token. Both old empty summary and new scanner summary are empty. No unresolved function is persisted in the successful endpoint. |
| Branch token-category classifier fix | Declaration scanner counts unit flags only for Dimension tokens | Numeric payloads and calc operands here do not carry unit-like identifier/string/URL text. It does not supply the endpoint's numeric typing. |
| Branch quoted-EOF fixes | Parser tracks removed backslash and quote/slash parity, adjusts reference ends | All test expressions are closed, contain no quoted strings/backslashes and have normal ends. No repaired recovery path is used. |
| Branch attr unit-token validation | Unit form verifies a single number and slices it before appending a unit | Test uses `type(<number>)`, not the unit form. |
| Branch property-context substitution wrapper | `animated_properties.mako.rs` WithVariables calls declaration-level wrapper | Proposed new path handles a Custom declaration. This longhand WithVariables arm does not type the custom endpoint. Existing fallback behavior is left unchanged. |
| Other branch glue changes | Accumulation iteration field, nth-of invalidation and a distinct substitution helper's attr map | None modifies the base/HEAD-identical `Servo_GetComputedKeyframeValues` or the static replace-composition midpoint input. |
| Declaration-block updates | Publication/all-order changes in `declaration_block.rs` | Its normal iterator and animation iterator are identical across revisions; the keyframe custom single-property blocks do not depend on all-shorthand or link-parameters fixes. No broad parser-history equivalence claim. |

## Case-specific provider paths

`var(--endpoint)` reads the base element's computed unregistered `--endpoint:42`, converts the resulting numeric text using the registered `<number>` syntax, then the candidate clones that typed endpoint. The builder, lookup, original raw reparse bug, registration converter and numeric animation variant all pre-exist in the standalone base.

`attr(data-value type(<number>))` causes the builder to load the null-namespace attribute, parse its numeric text and install the typed registered value. Base already has the typed attr loading/substitution path. The candidate consumes the installed value instead of reparsing the raw attr expression. The missing-attribute fallback has no graph edges in its literal replacement and uses the existing base fallback path.

Invalid typed raw text and `var(--missing)` reach the unchanged `handle_invalid_at_computed_value_time`: non-inherited values compute the registration initial, inherited non-root values copy the parent's registration-selected map value. Both paths replace the target's seeded base value. The direct CSS-wide endpoints stay on unchanged `from_declaration`, avoiding the distinct seeded-map defaulting hazard described in the earlier static report.

Both literal controls use already-supported numeric syntax; `calc(40 + 2)` requires no expanded unit dependencies. The 16-case WPT contains no self-cycle, nested fallback reference, fallback-to-CSS-wide, registration mutation or dynamic attribute edit. Those must not be counted as standalone coverage.

## Remaining gates and packaging

The endpoint fix can be packaged as its two native files plus the focused WPT without including the dirty `cascade.rs` or `syntax/data_type.rs`, or unrelated earlier branch fixes. Exact compile/runtime confirmation on base remains NOT_RUN. This source audit supports proceeding with an isolated base pair if root needs stronger standalone execution evidence; it does not relabel combined-tree passes as that pair.

The previously sealed `css-registered-keyframe-substitution-static-v1` remains unchanged. Its source snapshot is historical and its known seeded-CSS-wide/fallback-wrapper and dynamic dependency boundaries remain open. The animation-map identity component still needs only the existing name-preserving input premise; this endpoint repair changes value representation and must not be described as proved by that identity theorem.
