# Checkpoint: invalid custom-property enumeration

Status: source/spec lead; both proposed browser files are unexecuted by this worker. Parent owns subsequent runtime comparison. Work paused for whole-CSS feasibility research. No native changes, compilation, browser execution or Git mutations occurred.

## Normative oracle

For connected ordinary elements in a rendered document, CSSOM getComputedStyle builds declarations from supported longhands and custom properties whose computed value is not guaranteed-invalid. Length and indexed names expose those declarations. Custom-property order is unspecified; both probes sort names. See https://drafts.csswg.org/cssom/#dom-window-getcomputedstyle and https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-item (checked 2026-10-19).

CSS Variables initial resets an unregistered custom property to guaranteed-invalid. Failed variable substitution and self-cycles also produce that state. It serializes as empty, but a valid empty token sequence is distinct and remains enumerable. See https://drafts.csswg.org/css-variables/#guaranteed-invalid-value (checked 2026-10-19). The proposal includes that distinction as a control.

## Complete retained source path

The authenticated historical source capsule supplies complete custom_properties_map.rs, custom_properties.rs, properties/cascade.rs, geckolib/glue.rs and nsComputedDOMStyle.cpp. Imported source identity is recorded in IMPORTED-SOURCES.json; the map precedes candidate74. No producer helper was imported or executed.

- Cascade initializes the inherited map from the actual parent. Initial on an inherited present value reaches remove_and_insert_initial_value. No unregistered initial value is reinserted.
- Missing substitution reaches handle_invalid_at_computed_value_time; universal registration takes remove_var. Direct self-cycle goes through graph failure/removal; full graph/caller execution remains a runtime prerequisite.
- ComputedSubstitutionFunctions.remove_var -> ComputedCustomProperties.remove -> CustomPropertiesMap.remove -> do_insert(name,None).
- Inner.insert retains None entries and does not decrement len for Some->None. The <=8 own-entry path clones rather than extending the ancestor chain. Thus parent target+sentinel -> child initial can expose the defect with no ancestor traversal.
- Servo_GetCustomPropertiesCount sums inherited/non_inherited len. property_at uses get_index; get_index takes raw iterator nth; Servo_GetCustomPropertyNameAt ignores the Option value. nsComputedDOMStyle Length/IndexedGetter publish that count/name.
- Named get uses nearest-owner Option lookup, so it can correctly serialize an absent value while enumeration retains its name.

## Separate chain interaction

Grandparent has target+8 valid names. Middle resets target to initial and adds8 new names: its own map has9 entries and stored len17. Leaf restores target. Chain expansion increments len to18 because parent.get(target) is None, even though unique stored keys remain17. Candidate74's corrected iterator can therefore exhaust before len; property_at then computes index-inherited.len on a smaller index. Release wrapping may lead to a bare '--' name, while checked subtraction may fail. This is a source prediction, not a reproduced browser observation here.

The separate two-case probe compares this restoration against the same chain with a present middle override. It asserts all actual named values before enumeration. Original74 comparison is necessary; the original duplicate iterator may obscure the count inconsistency.

## Proposed repair ordering for parent adjudication

One coherent independent order is live-count repair before iterator repair: Inner.insert compares old effective presence self.get(name).is_some() before mutation with new value.is_some(), then adjusts count by the Boolean difference; get_index filters None, while raw Iter/tombstones remain. This closes flat guaranteed-invalid exposure without claiming to fix ancestor duplicates. Accurate lookup makes live counts independent of iterator correctness. Candidate74 then restores unique nearest-owner iteration against that count. Inspect every caller and run both pairs before accepting this design. Do not simply erase tombstones: they mask ancestral values. Filtering empty CSS serialization is also incorrect.

## Tests and discovery

- invalid-custom-property-enumeration.html:8 cases, target+sentinel only, parent prerequisite, ambient-property prerequisite, exact value/name/count snapshots; initial/missing-var/cycle, no-parent controls, valid-empty/inherit controls and dynamic reset/reinherit.
- resurrected-custom-property-enumeration.html:2 cases,17 effective names on leaf; tombstone versus present parent control.
- Both scripts passed node --check only. External WPT dependencies are /resources/testharness.js and /resources/testharnessreport.js. Root cleanup callbacks return undefined.
- Existing CSSOM custom-property WPT covers one valid unregistered property; registered test covers absent universal initial but not Some->None tombstones. Retained Android/fission metadata alternatives do not establish current execution results.
- Bounded ledger scan found no accepted matching counting repair; PLAN-OF-RECORD explicitly keeps tombstone/counting separate from duplicate iteration.
- Searchfox discovery succeeded for Servo_GetCustomPropertiesCount, CustomPropertiesMap, get_index and existing WPT. Public primary search identified related bug1855629, Handling of custom properties when enumerating getComputedStyle, and CSSWG1316 (closed). Full bug1855629 discussion/patch still needs review before a novelty claim. Do not report exhaustive duplicate clearance.

## Remaining work

Parent runtime for both exact proposed files; full bug1855629/relevant upstream history check; final report and closed seal; any approved repair source design and caller audit. This checkpoint is not formal verification or bug acceptance. No frozen source capsule has been edited.
