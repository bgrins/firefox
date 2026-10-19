# Namespace candidate v3: glue migration review

## Verdict

No blocking defect found in the v3 glue migration. Static review accepts these exact bytes for root's build and runtime gates. This is an append-only supplement to the sealed v2 review, not a replacement of its evidence or a claim that its two-file review covered every repository constructor. The missed nonempty constructor in geckolib demonstrates that the previous call-site coverage was incomplete.

No production file, test, Git state, or browser was changed or executed by this reviewer. Root reported build13818 linking; this report does not independently certify its result.

## Exact delta and proof compatibility

- `properties__cascade.rs` is byte-identical to reviewed candidate v2 (`be204d2bbdef0ec5130139eaeb56adf8fb869d09565f9b7b4c70e5ad3f61d425`).
- `custom_properties.rs` is `06c1dc6195e9adb0d32b69cfcaabc88fe34a0f4b222cfa2ce4009c046174207e`. Relative to v2 it only makes `ComputedSubstitutionFunctions::insert_attr` and `AttributeData::namespace` public and adds their documentation. Their bodies, the nested map, accessors, parser, graph representation and apply APIs are unchanged.
- `glue.rs` is `f850eec636e6740d5582c1dcea66f69f8b50c59f8f576167e2bcab6fb080cf9a`. Its only change from the frozen original is `compute_arbritrary_substitution_functions`' construction of the attribute map.

The qualified-key component's namespace buckets, tombstones, Option namespace distinction, and SCC identity model remain applicable at the same stated abstraction boundary because the modeled bodies did not change. No Lean theorem was rerun or extended here. The prior component's full-repository caller admission was explicitly open; this review supplies the additional constructor inspection, not a universal proof of all evaluator/provider behavior.

## Glue equivalence and qualified identity

Previously the helper parsed each top-level typed attribute, collected successful `(local name, Some(value))` pairs into `OwnMap`, and supplied that nonempty map to the constructor. V3 starts with the same cloned custom properties and an empty attributes map. For the same ordered references, successful queries call `insert_attr(name, resolved namespace, value)`.

The namespace is borrowed from the same `AttributeData` passed to `get_attr_value_for_cycle_resolution`. Unknown namespaces are skipped explicitly; previously that helper returned Err before a DOM query, so this preserves the rejection path. The null namespace is `Some(Namespace::default())`, never confused with Unknown. The parser initializes unprefixed attrs with exactly that namespace. A known successful value is stored in the matching namespace bucket. Existing same-qualified-key last-successful insertion behavior is preserved; failed later occurrences do not erase previous successful entries. Different namespaces no longer collide.

`style::custom_properties_map::OwnMap` remains an IndexMap of name to optional value inside each namespace bucket. The new outer namespace atom is cloned for owned storage. The loop does not retain references into temporary DOM data; its value is owned by the map. Public method visibility is necessary for geckolib, a different crate, and introduces no new WebIDL interface.

The helper does not traverse the SCC graph or resolve chained attribute values itself. It still iterates only top-level references. Existing nested-fallback/preparation and chained-value limitations therefore remain unchanged and are outside this migration's acceptance. It also leaves the property-context TODO for random() unchanged. These limitations must not be called fixed by a passing namespace WPT.

## Complete discovered constructor ledger

Searchfox discovery found these consumers; the pinned local files confirm their actual arguments:

| Location | Occurrences | Attributes argument / initialization |
|---|---:|---|
| properties/cascade.rs | 2 | None, both |
| properties/properties.mako.rs | 1 constructor + 1 default | None / empty default |
| queries/condition.rs | 2 | None, both |
| queries/feature_expression.rs | 1 | None |
| ports/geckolib/glue.rs | 1 | V3 None, then qualified insertions |

No remaining nonempty constructor caller was found in this discovery scope. No external consumer struct literal was found. This is a source search plus exact local inspection, not compiler-generated whole-program reachability evidence. Query paths still retain their documented container-query bypass; passing None there is not a newly introduced bug.

All existing insertions discovered by Searchfox and checked locally carry the namespace after v3: the apply helper in custom_properties; eager preload and recursive attr discovery in cascade; and the glue helper. The unchanged v2 map reads, SCC invalidation, index keys and dispatch were already reviewed and retain their exact bytes.

## Actual public callers and relevant tests

Both `Servo_GetSubstitutedValue` and `Servo_GetComputationSteps` call this helper. Their `ContextForSubstitution` and C++ InspectorUtils callers still obtain a clean computed style and maintain the existing pseudo handling, failure/null semantics, and borrowed document/style ownership. The migration does not change those paths.

Both callers use `dummy_author_style_rule_context`, whose namespace map is empty. The API accepts an expression and element, not a stylesheet namespace context. Thus the immediate regression target is existing unprefixed typed attrs; a stylesheet's prefix declaration is not automatically admitted to this privileged API. CSS Values 5 supplies the underlying attr identity/substitution rules, but these InspectorUtils methods are Firefox-specific developer tooling, as their chrome WebIDL shows. A standards WPT cannot directly call them.

Recommended existing gates, run by root if needed:

1. `layout/inspector/tests/test_getSubstitutedValue.html`: directly exercises typed number/color attrs, invalid typed values, unit/raw attrs, absent attrs, custom properties and env, including pseudo handling. Its typed tests execute the changed preload path and are the strongest existing focused regression coverage.
2. `layout/inspector/tests/test_getComputationSteps.html`: covers the second caller, mixed var/attr-unit/env expressions and output-step ordering. Its existing attr example uses a unit rather than type(), so it complements but does not replace the first gate.

Both are listed in `layout/inspector/tests/mochitest.toml` with no entry-specific skip. That is a configuration observation, not execution evidence. The source snapshots preserve exact current test bytes. `test_getComputationStepsSupportedCSSFunctions.html` only enumerates supported names and is not needed to validate this change.

A possible future focused case would combine two top-level typed attrs in one InspectorUtils expression plus an unknown prefix fallback and explicit null namespace; no new test is required solely to establish the existing API migration if the targeted current tests and root's build pass. This review does not expand the requested browser corpus.

## Evidence and replay

`ACQUISITION.json` pins full original/v2/v3 files and supplemental callers/tests. `*.diff` preserves the exact deltas. `prior-review` and `prior-proof` retain the previously authenticated review/scope documents; proof reports are not freshly rerun. The primary spec snapshot and retrieval metadata are authenticated copies from the prior sealed probe.

Initial Searchfox discovery succeeded in this turn (33 attribute-map hits, 58 API/test hits, 14 constructor/OwnMap hits). Later attempts to preserve fresh raw search output failed DNS; those failures are retained as `SEARCHFOX-*.txt`, not represented as successful fetches. The exact discovered file/symbol ledger is in this report and the complete local sources are pinned. Searchfox indexing also differs from local source, so actual arguments are taken from the local snapshots.

`check.py` first authenticates the manifest and every input, then regenerates the exact diffs, verifies the only custom-properties delta is visibility/docs, verifies cascade identity, checks the qualified glue sequence and constructor argument inventory, and checks the existing test registrations. A relocated run and deliberate source tamper check are recorded separately. No build, browser execution, Rust semantic proof, allocation guarantee, or whole-program caller proof is claimed.
