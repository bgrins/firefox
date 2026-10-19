# Independent registered explicit-inheritance review

## Verdict and scope

The two-hunk native change is correct for the reviewed ordinary style-cascade path. Both hunks are necessary. No source blocker was found. The corrected root paired run supports bounded acceptance: three failures repaired, all twelve new subtests passing, twenty-eight adjacent/readiness subtests unchanged PASS, and five harnesses OK. The earlier pair with a returning cleanup callback is not an acceptance gate.

This is an independent source/spec/test review, not a universal proof of custom-property evaluation, restyle scheduling, or every style-construction caller. No native source, live WPT, index, build or browser was modified or executed by this reviewer.

## Normative result

The current [Properties and Values API calculation rules](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation) retain universal-syntax custom-property token/GIV behavior. [Values 5 invalid substitution](https://drafts.csswg.org/css-values-5/#invalid-substitution) gives a universal registered property the guaranteed-invalid value when substitution fails. This differs from typed invalid-value defaulting. [Cascade 5 inheritance](https://drafts.csswg.org/css-cascade-5/#inherit) copies the parent's computed value for explicit inherit, including for properties that ordinarily do not inherit. The root's inherited value is its initial value. [Variables 2 guaranteed-invalid values](https://drafts.csswg.org/css-variables-2/#guaranteed-invalid) specifies empty-string serialization; its var() substitution uses the fallback on GIV.

REACHED: the child of the invalid parent must retain GIV, so the direct computed read is empty and its var() consumer yields fallback-token. It must not retain initial-token. The separate root case must retain root-initial. Primary web results retrieved during this review are retained. No automatic spec-anchor validator or novelty guarantee is claimed.

## Complete relevant source flow

`Cascade::init_custom_properties` initializes the child's non-inherited map from the current registration initial-values cache. For inherited properties it initializes from the supplied parent map, except for the root special case. The old `value_may_affect_style` returned false for explicit inherit precisely when a reset property's parent entry was absent, despite the child having a seeded initial value. The caller then marked the declaration seen and returned. The native patch replaces that absence shortcut with the actual root predicate.

Removing the shortcut alone is insufficient: `cascade_custom_property` previously inserted on parent Some and left the seeded child entry on None. The new else invokes the existing registration-aware `remove_var`. `ComputedCustomProperties::map_mut` selects the non-inherited bucket for this route. `CustomPropertiesMap::remove` writes None through its copy-on-write insertion path. `Inner::get` stops on an own None instead of falling through to an ancestor. Thus the registration's shared initial cache is not mutated and cannot reappear through the map's ancestor chain.

Present-parent inheritance continues to clone the full computed registered value; payload and taint are preserved. Parent None has no payload or taint to transfer. Inherited registrations remain on their earlier already-parent-seeded fast path. Unset, Initial, revert processing, registration lookup, typed parsing and substitution are unchanged. Seen handling still selects exactly the winning declaration; the repair does not expose lower-priority declarations. Root separately reproduced a missing substituted-inherit restyle dependency flag after this review; that unchanged substitution route is outside this direct-inherit repair. The passing static substituted-inherit control must not be generalized to dynamic correctness.

### Root, pseudo and style-parent meaning

The ordinary cascade computes `is_root_element` from `pseudo.is_none() && element.is_some_and(|e| e.is_root())`; it does not infer rootness from an empty parent map. Gecko's element root predicate requires document attachment and no content parent. `Context::is_root_element` returns the builder's explicit root flag. With a seeded initial value, the root keeps it; without such a value, removal of an absent entry preserves GIV.

Pseudo styles have a false root flag even on the document element. Their inherited custom-property map comes from `StyleBuilder::inherited_style`, populated by the supplied parent computed style. `with_default_parent_styles` distinguishes the inheritance parent from a layout parent through display:contents; the custom-property accessor uses the former. Therefore the repair does not substitute layout ancestry or treat a root pseudo as a parentless document root. Searchfox-discovered complete caller/provider files are retained separately from the exact candidate source snapshots. They are discovery evidence, not a claim that every indexed byte equals this local build.

Parentless derived/anonymous/internal style constructors have distinct contracts; this review establishes the ordinary element/pseudo cascade path, not universal reachability or correctness for arbitrary manually constructed Context values. No concrete additional counterexample was established for those callers.

### Restyle dependency

`INHERITS_RESET_STYLE` is set before both Some and None branches in direct reset inheritance. The repaired absence path now reaches that flag, whereas the faulty fast path skipped it. `compute_style_difference` requests `RECASCADE_SELF_IF_INHERIT_RESET_STYLE` for reset-only changes unless an unconditional reason applies; `needs_to_recascade_self` tests the flag. The new dynamic test invalid→present→invalid is therefore materially useful, not just another static duplicate. Full scheduler and sharing-cache correctness remain external source/runtime contracts.

## Tests and evidence

The final twelve-case test retains the original ten cases, adds root inheritance, and adds dynamic parent changes. Parent computed-value prerequisites discriminate setup failure. Observing both the child's property and a var() consumer distinguishes GIV from valid empty tokens. The expected-value expression uses an empty string only for known GIV cases. There is no animation timing, font resource, or asynchronous frame dependency; computed-style reads force each needed style update.

The first root cleanup callback returned the string from removeProperty. Root detected its testharness cleanup error and archived that pair. The corrected final test and separate readiness controls use a braced callback returning undefined. Historical producer v2 is retained as historical, not the accepted final test. The three readiness controls cover root, stylesheet-registration bucket changes, and script-registration precedence; they are extra regression observations, not part of the minimal independently applicable native/WPT fix.

PAIR-REVIEW.json records the independently inspected corrected pair; the checker reads both complete raw event streams and verifies all forty subtests, five harnesses, and the three exact changed observations. Both builds exited zero. Formatting and scoped lint exited zero; the lint log reports zero errors and one ignored WPT eslint warning. Original ten-case browser evidence reproduced two failures with eight controls passing; it is not a repair result.

## Standalone applicability and dependency

`STANDALONE.json` retains an independent exact no-fuzz application and reversal of the same native.patch to upstream base `976279105b2e78b8666a959eb3f25c9176cefaf8`. The complete original cascade source was obtained by read-only git show. Both hunks apply without offsets; reversal restores identical bytes. FINAL-STANDALONE.json independently repeats exact apply/reverse for the final two-file native/WPT patch and checks the resulting WPT bytes. Root STANDALONE-PACKAGING.json additionally retains branch-base application/reversal. Original SHA256 is `016576207a8dcae6803b98ac85fc9210f4e340532208742b0bf46264b86df11e`; patched SHA256 is `4d687bd1ddce0fe3e371ecbd70667b355eb0d74bc5b7f649bf31268d4b22e201`.

The fix uses existing root-context, selected-map insertion/removal and reset-inheritance flag APIs. It does not call the keyframe conversion entry point or depend on its visibility changes. Its standalone WPT uses ordinary declarations and universal registrations, with simple typed 7px/21px controls; it has no keyframes. Thus there is no source/API or test-semantic dependency on the earlier numeric keyframe repair. Shared-tree runtime may contain that repair and other earlier fixes. No isolated upstream build or browser run was performed, so standalone source applicability must not be described as isolated runtime validation.

## Prior art and remaining limits

Bug 1855946 concerns typed invalid-at-computed-value defaulting; its record is retained. It explains relevant history but does not prove novelty of this universal reset-property explicit-inheritance witness. No regression revision or comprehensive duplicate search is asserted.

The reviewed change introduces no new allocation structure, iteration over all properties, parser, arithmetic, ABI, or provider representation. It can perform the existing map removal and flag publication in cases previously skipped incorrectly. No performance neutrality claim is made. Native compilation, browser behavior and lint are root-owned gates. The root driver pins the changed native source, selected tests, tracked pre-existing working changes and two binaries across each run; it is not a proof of immutable entire repository, configuration, metadata or toolchain state. Model, allocator/compiler, full substitution, all map iteration, and complete restyle/caller correctness are outside this bounded review.
