# Independent review: substituted registered inheritance

Verdict: accept the bounded native repair and conditional model component. No whole-restyle, substitution, cache, or traversal proof is claimed. Parent owns final acceptance.

## Authentication and execution

Externally supplied source-review FREEZE 90713b6bb8e8f84847499a1afc95626a8856f915dace187b5d7296e815a1b88e and proof FREEZE 3153795ecec91c30b7e9134c06a688be7a5f7d5c1066582862514cd9841b1f04 were authenticated before execution, together with their manifests and every listed input. The retained proof is a manifest-only relocation, with 21 inputs and two seals. Fresh `python3 -I -S proof/check.py --output <new external directory>` passed: 14 exact named audits, 13 source bindings, exact native patch application/reversal and four semantic mutants. Kernel audit uses only propext where needed; no new axioms or proof holes. The retained TOOLCHAIN identifies the executable and its hash.

Every mutant's original concrete witness passes, altered definitions compile, then that same witness fails because `decide` proves the proposition false. They detect omitted marker, marking only a present parent, reversed registration guard, and dropped conditional hint consumption. These are Lean mutations, not compiled native mutations. Four independent integrity challenges reject modified Lean, missing source, extra file and symlink before creating output. A missing file raises FileNotFoundError; the other challenges raise AssertionError. No guard is counted as a semantic mutant.

## Native and WPT review

The only native semantic addition ORs INHERITS_RESET_STYLE in the nonroot CSS-wide inheritance arm when the registration does not inherit. Among the combined match alternatives this selects explicit Inherit for reset registrations. It precedes the parent Option match, covering both Some insertion and None removal. Root initial selection, inherited registrations, attr processing, substitution failure, generic value conversion, taint and values remain unchanged. The source extractor retains complete selected definitions, including excluded branches; hashes are correspondence evidence, not compiler verification.

The flag is consumed by reset-only child recascade logic. The source chain includes ordinary style-difference classification, custom inherited/reset map comparisons, conditional child hints, flag check, fresh StyleBuilder construction and publication. Later restyle-kind and animation conditions remain outside the selected projection. `is_root_element` is derived from absence of pseudo plus actual element root; inheritance reads the style parent, not an invented layout parent.

Raw root-owned logs independently establish baseline 3 FAIL / 41 PASS and candidate 44 PASS, with five OK harnesses on each side. Seven new tests and 37 adjacent tests have complete identities and terminal suite records. Exactly three new test failures become PASS; the other 41 subtests and five harness observations are unchanged. Both builds exit zero; selected source/test/binary pins remain stable. Formatter and lint pass, with one reported lint warning. The test checks parent readback and direct inherit/unset controls, simultaneous padding changes, and an absent/present/absent universal parent history. No browser was run by this reviewer.

Final patch SHA 6f46b194803d831a3b4606b0d53a52cfd611c69dfd80ae51ea5919bfeeb1c873 contains exactly custom_properties.rs and registered-substituted-inherit-restyle.html. Root standalone packaging reports exact application/reversal on branch and upstream 976279105b2e78b8666a959eb3f25c9176cefaf8a. The source-review capsule separately retains upstream correspondence. The minimal marker addition has no semantic need for fixes 71/72; shared-tree tests include those changes. No isolated upstream browser execution is claimed.

## Model review and essential qualifications

The independent `expected` folds supplied parent Options without consulting the marker, change bits or scheduler. EventReady permits conservative invalidation but excludes an unchanged report that actually changes the selected parent. HistoryReady checks this at every prefix. The history induction derives the marker from initial corrected publication rather than assuming it independently. Changed events refresh to current parent; unchanged ready events retain that same value. Payload equality is not assumed decidable.

`refresh` is a caller abstraction: it assumes the relevant gate causes fresh selection under the same effective Inherit declaration and registration. It does not prove DOM mutation delivery, map equality semantics, traversal, cache freshness or animation scheduling. False change-provider reports are explicitly demonstrated by unchanged_event_requires_soundness.

**Important frame limitation:** local `resolve` genuinely preserves the unrelated flags passed to that invocation. The model's history also preserves `otherFlags` because `refresh` reuses its previous State. Actual `apply_declarations` creates a fresh StyleBuilder, deriving and recomputing flags; no source theorem establishes identity with the old style's unrelated flags. Consequently the history theorem's otherFlags conjunct is accepted only as a model frame assumption. It must not be advertised as native whole-restyle flag preservation. Selected-value/resetDependency projection does not need that unrelated-flags identity.

Remaining admissions include successful substitution and sole keyword recognition, correct parent/root inputs, registration stability, Option/map selection and clone/removal, style difference providers, fresh-value refresh behavior, heap/normal completion, native representation/compiler, and actual scheduler delivery. The model deliberately covers selected Inherit handling, not all CSS-wide alternatives or CSSWG issue 9131.

## Evidence and cleanup

PAIR-REVIEW.json retains independently classified raw changes. runtime/ contains exact raw logs, driver, pinning, tests and packaging; source-review/ and proof/ retain frozen inputs. replay/ retains all command outputs, exact audits, result and generated Lean witnesses. GUARDS.json retains rejection causes. Generated replay and temporary guard copies were removed only after receipt retention: 4,486,858 bytes total, exact paths in CLEANUP.json. No shared build output or live source was removed.
