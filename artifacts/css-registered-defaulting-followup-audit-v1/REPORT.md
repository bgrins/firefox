# Registered defaulting follow-up audit

## Finding and status

**One distinct, browser-reproduced source defect:** explicit inherit on a noninherited registered universal property can retain the child's initial value when the parent's computed value is guaranteed-invalid. Root executed the frozen ten-case probe on the unchanged fix71 shared-tree build: **2 FAIL, 8 PASS, harness OK**. Both failing tests first pass an explicit parent computed-value prerequisite. The child then reports initial-token for both its custom property and var() consumer instead of empty / fallback-token.

The two inputs use an undefined variable and a self-cycle on the parent. Substituted inherit and the remaining defaulting controls pass. This is a native source finding validated by browser evidence, not a discovery attributed to a new formal verifier theorem.

`native.patch` is an uncompiled artifact-only proposal. `registered-inherit-invalid-v2.html` preserves the original ten tests and adds a root-element inheritance control. `registered-defaulting-readiness-controls.html` has three further root/registration transition controls. Neither new file nor the candidate has been browser-tested by this worker. Root owns integration and runtime acceptance.

## Normative trace

Scenario: universal registered property with inherits false and initial-value initial-token; parent explicitly uses var(--missing) or a cycle; child explicitly declares inherit.

1. [Properties and Values computed-value behavior](https://drafts.css-houdini.org/css-properties-values-api-1/#computed-value-time-behavior) retains unregistered-style token/invalid behavior for universal syntax. [Values 5 invalid substitution](https://drafts.csswg.org/css-values-5/#invalid-at-computed-value-time) expressly makes invalid substitution on universal registered properties guaranteed-invalid. This is not the typed property's unset/default behavior.
2. [Cascade 5 explicit inheritance](https://drafts.csswg.org/css-cascade-5/#inherit) makes the child's specified and computed value the inherited value, irrespective of the registration's ordinary inheritance flag. The parent computed value is transferred, including guaranteed-invalid.
3. [Values 5 substitution](https://drafts.csswg.org/css-values-5/#substitution-in-properties) makes a substituted sole inherit keyword act like direct inherit. Thus the passing substituted-inherit control and failing direct-inherit case should agree.
4. The expected consumer fallback distinguishes guaranteed-invalid from an empty but valid token string. Root's raw failure records preserve both observations.

**REACHED:** the two failing observations violate explicit inheritance. This does not depend on revert policy or animation dependency order. Primary drafts were retrieved through the web tool on 2026-10-19; webspec-index remains unavailable, so no automatic anchor validator was run.

## Complete source/caller chain

Full pinned source files are retained under source. custom_properties.rs/cascade.rs are exact post-fix71 runtime snapshots; source pins match root RUN. The stylesheet and registration providers were independently read in the immediately preceding initial-value review and are retained here.

`Cascade::init_custom_properties` seeds noninherited entries from the registration initial cache. Parent `var(--missing)` failure reaches `handle_invalid_at_computed_value_time`; because registration.is_universal(), it removes the parent's entry. Cycles reach the same invalid-value handler. `ComputedCustomProperties::get` exposes an absent/tombstone entry as None. The parent CSSOM prerequisite proves the expected guaranteed-invalid observation in this actual build.

When processing child direct inherit, `Cascade::value_may_affect_style` sees the existing initial entry. Its Inherit arm checks whether the parent's non_inherited map lacks that name, and returns false. The caller marks the custom property seen and returns, preserving the child initial entry. This is the immediate cause of the runtime failure.

There is a second necessary site in `Cascade::cascade_custom_property`: its direct Inherit arm inserts a parent entry only for Some. On None it leaves the initial entry untouched. Merely disabling the fast path therefore does not repair the result. In contrast, the substituted CSS-wide inherit branch already explicitly removes the selected child entry on parent None.

The helper/map operations use the actual registration's inheritance bucket; the proposal does not search the other bucket or merge inherited/reset maps. The inherited-properties direct inherit fast path remains valid because that map was seeded from the parent already.

## Minimal proposed repair and root constraint

Two edits, confined to properties/cascade.rs:

- In the existing-value Inherit fast path, skip only for the root element. The existing entry there is already the selected initial value, which is the inherited value for a root without a parent. For a nonroot child, absence of the parent entry must reach the publication branch.
- In the direct Inherit publication branch, add None→remove_var(registration, name), matching the existing substituted-inherit behavior.

Root inheritance cannot be fixed by indiscriminately copying the absent parent map: it must retain the registered initial entry. With no initial entry, the earlier None path may still reach removal of an absent value, which preserves guaranteed-invalid. With a present initial entry, the new root predicate retains it. The v2 root test guards against the obvious overcorrection. The existing `INHERITS_RESET_STYLE` flag continues to be set when the nonroot publication branch executes; newly affected absence cases now take the same dependency-marking path as present-parent inheritance.

No descriptor text, cached initial value, substitution taint policy, registration selection, stylesheet invalidation, parsed-value conversion or keyframe consumer is changed. Removal follows the existing copy-on-write custom-map implementation. The extra work is necessary selected-map removal and the existing inheritance flag publication on this case; no new global walk or parse is added.

## Negative coverage and boundaries

| Route | Source result / retained observation |
| --- | --- |
| Substituted unset, reset registration | Uses computed initial cache after fix71; universal control passes. |
| Substituted unset, inherited registration | Copies parent selected map or removes on None; invalid parent control passes. |
| Invalid typed value, reset registration | Invalid-value handler computes typed initial; length control passes. |
| Invalid typed value, inherited registration | Handler copies parent computed value; length control passes. |
| Universal invalid substitution | Removes selected map entry; parent prerequisites pass. |
| Direct inherit with a valid reset parent | Copies parent value; control passes. |
| Direct inherit on inherited registration | Uses parent-seeded map; invalid parent control passes. |
| Registration selection/cache readiness | No new discrepancy found statically: script registry precedes stylesheet registrations; cache and registration lookup use that order; stylesheet flush and script insertion rebuild cache. Additional three-case transition probe is proposed, not executed. |
| Descriptor original text | Cache computation leaves descriptors immutable; readiness probe checks 1in/4in descriptor strings separately from computed values. |
| Revert/revert-layer/revert-rule after substitution | Existing explicit TODO/policy ambiguity; not treated as this defect or repaired here. |
| Same-keyframe CSS-wide/custom-map dependencies | Previously documented animation dependency issue; excluded. |

Cache freshness still depends on actual stylesheet/style flush scheduling. No universal scheduler, map-lifetime or all-CSS theorem is claimed. The new proposal uses the same current computed registration/cache contracts as fix71.

## Existing tests and prior-art check

Searchfox discovered and local complete reads retained `invalid-at-computed-value-time.html`, `registered-properties-inheritance.html`, and `var-reference-registered-properties-cycles.html`. They cover universal invalidity, typed inheritance/defaulting and cycles separately. The inspected direct inherit tests use typed lengths, where an invalid parent correctly becomes its typed initial value; they do not expose a universal reset parent with guaranteed-invalid computed value. METADATA.json records whether each exact local metadata file exists; absence is not a claim of runtime PASS.

[Bug 1855946](https://bugzilla.mozilla.org/show_bug.cgi?id=1855946) fixed typed invalid-at-computed-value defaulting in Firefox120; the fetched Bugzilla record and test provenance are retained. [Bug 1855887 comment 4](https://bugzilla.mozilla.org/show_bug.cgi?id=1855887#c4) explicitly recognized ambiguity between missing entries and default/guaranteed-invalid values during an older representation refactor. It is relevant history, not evidence that the present explicit-inherit witness is already tracked. The bounded search found no exact open duplicate; no novelty guarantee or regression revision is claimed.

## Remaining gates

Root must review/apply the artifact candidate, run the v2 paired test including root control, preserve ordinary typed inheritance/defaulting tests, and check standalone packaging/build/lint. The original ten-case browser evidence is immutable and is not a paired candidate result. This capsule's checker only authenticates source/evidence, checks the exact proposed transformation via patch apply/reverse and validates JavaScript syntax. No native extraction or Lean proof is asserted. No build targets were created, so no cleanup is needed.
