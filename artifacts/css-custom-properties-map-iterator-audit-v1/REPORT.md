# Custom-property map shadowing iterator

## Result and status

The retained `Iter::next` body has a concrete control-flow error: a matching descendant executes `continue` on the inner descendant loop. It still returns the ancestral entry afterward. It therefore enumerates overridden names again. Direct `get` uses nearest-owner lookup and remains correct. The main identified observable consumer is indexed computed-style enumeration, which truncates this overlong iterator at the separately stored map length. A duplicate early name can displace an unrelated final name.

This is a source-confirmed defect with an unexecuted browser proposal. The Python witness is a finite source-shaped model, not native Rust execution, a universal proof, or a browser result. No novelty or accepted-bug count is claimed.

## Reachable copy-on-write path

1. `Cascade::init_custom_properties` clones the parent's inherited `CustomPropertiesMap`. The parent computed style retains the same Arc, so the child insertion has a shared map.
2. `cascade_custom_property` computes a differing simple unregistered value and reaches `ComputedSubstitutionFunctions::insert_var` → `ComputedCustomProperties::insert` → `map_mut` → map `insert`/`do_insert`.
3. With nine own parent entries and no ancestors, `should_expand_chain` is true: own length is greater than eight and ancestor count is below four. The new child node contains the override and references the old map. Reassigning an equal value returns early. At eight entries, make_mut copies the own map instead.
4. `finish_cascade_custom_properties` does not merge a differing map back into its parent; its structural/value equality test fails for this override.
5. `get_index(index)` checks index against stored length and then uses `self.0.iter().nth(index)`. `ComputedCustomProperties::property_at` routes inherited indices first. `Servo_GetCustomPropertyNameAt` returns the resulting name; `nsComputedDOMStyle::IndexedGetter` exposes it. `Length`/`Servo_GetCustomPropertiesCount` use the stored unique length, not actual iterator output length.

With nine ancestor names k0…k8 and child override k0, stored length remains nine while original iterator output is `[k0(child), k0(parent), k1,…,k8]`. CSSOM exposes only its first nine entries, duplicating k0 and dropping k8. The test chooses k0 from the independently checked parent enumeration, so no unspecified enumeration order is assumed. Named value lookups verify all nine effective values before checking enumeration.

The threshold refers to **own entries of the shared node**, not total DOM depth or total entries across its chain. A child node with one override will generally be copied at the next descendant until its own map grows past eight. The four-ancestor cap copies the current node rather than flattening the chain. No concrete flattening consumer was found in this bounded audit; the report does not claim wrong value substitution from iteration alone.

## Normative oracle

CSSOM's getComputedStyle algorithm appends every custom property with a non-guaranteed-invalid computed value to its declaration list. CSSStyleDeclaration length and indexed access expose that list. Custom-property ordering is explicitly unspecified, so the proposal compares sorted names and does not impose an order. All values in the focused cases are simple valid unregistered tokens; no removed/invalid entry or registered-property default is needed. See [getComputedStyle](https://drafts.csswg.org/cssom/#dom-window-getcomputedstyle) and [item](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-item).

## Proposed browser gate

`custom-property-enumeration-shadowing.html` is UNEXECUTED. Its seven tests are:

| Case | Static prediction |
| --- | --- |
| Eight parent names, one differing override | pass, flat copied map |
| Nine parent names, one differing override | fail, one duplicate and one omitted name |
| Nine parent names, two differing overrides | fail, duplicate ancestral names displace two names |
| Nine names, unchanged inheritance | pass |
| Nine names, equal-value override | pass |
| Nine names, one distinct new name | pass, no shadowed ancestor |
| Remove overriding declaration after a style read | pass, inherited values and names restored |

The tests create connected elements, calibrate the full parent name set, and select the first parent-enumerated name. `node --check` passed on the extracted script. This does not execute a DOM or validate runtime predictions. Test harness registration is seven cases (two loop iterations and five individual tests).

## Narrow repair proposal

`proposed-native.patch` changes only the outer loop label and the shadow-hit continue target. It consumes/rejects the ancestral entry and resumes the outer traversal. Names, values, insertion order, reference ownership, lookup, Arc cloning and chain thresholds are unchanged. It also prevents ancestral resurrection when a nearer node owns a None tombstone; it does not remove the nearer tombstone from iteration.

Before landing: run the proposed WPT pair and existing CSSOM custom-property tests, review counted/removed-entry invariants separately, and confirm the patch applies independently to the intended base. No production files were edited and no Git operation was performed.

## Prior art and coverage

The current BUGFIX-COMMITS ledger has no matching repaired iterator entry; PLAN-OF-RECORD explicitly lists this source lead as pending. Existing `cssstyledeclaration-custom-properties.html` has one custom property; `cssstyledeclaration-registered-custom-properties.html` checks inclusion/exclusion for a small map and does not stress shared-map override enumeration. Their retained metadata has Android/fission timeout alternatives; this is metadata, not execution evidence.

Bounded public searches for CustomPropertiesMap/iterator and custom-property/getComputedStyle duplicates found related implementation/performance history (bugs 1840478, 1864736, 1407246 and 2055744), not an established matching report. Bug 1857849 contains discussion of inherited enumeration but is a Typed OM implementation task, not evidence of this exact defect. Searchfox CLI discovery failed DNS; failures are retained. The primary GitHub main page retrieved through the web tool shows the same inner-loop continue, but its reported crawl is three weeks old and no exact current upstream revision was authenticated. Upstream-current and exhaustive duplicate checks remain open.

## Useful formal contract, if runtime confirms

Prove that iteration over a finite bounded chain returns each key exactly once, paired with its nearest owner's Option value, in descendant-first order. The source loop invariant must track all already-traversed descendant nodes and the current map iterator suffix; rejection must advance that suffix. Compose get_index with this enumeration and the stored-length invariant for valid Some-valued histories. Model tombstones/counting separately rather than assuming the live-value count equals all stored keys. Native IndexMap ordering, Arc uniqueness/cloning and machine limits remain provider premises until explicitly bound.

Inspected: complete map, relevant full cascade/insert/lookup/CSSOM source files, both existing WPTs and metadata, ledger, primary CSSOM clauses and bounded public searches. Uninspected: exhaustive downstream generated consumers, all removal/invalid-value count histories, non-inherited/registered combinations, Typed OM internals, native compiler/provider refinement and browser execution.
