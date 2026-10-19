# Candidate v2 independent native review

Reviewed exact files in candidate-v2/INPUTS.json and complete native-draft-v2.patch. The checker regenerates this diff against the authenticated baseline full sources and demands exact equality. Source hashes: custom_properties.rs `4c6bbf3ced241a0df98f90011871a4810d6306f7740e8c10411547b80e1ec92d`; cascade.rs `be204d2bbdef0ec5130139eaeb56adf8fb869d09565f9b7b4c70e5ad3f61d425`.

## Static verdict

No blocking issue found in the qualified-key changes. They implement the recommended namespace-bucket representation and thread it through all identified state transitions. Static source review accepts this draft for root's build/paired runtime gate. This is not yet build/runtime acceptance and is not a proof of the implementation.

- Computed attribute map and constructor accept namespace buckets. Borrowed get_attr selects namespace then local name. Insertion/removal clone atoms only for owned storage; tombstones remain per-qualified-key. OwnMap/custom-property behavior is unchanged.
- AttributeData::namespace returns None only for Unknown; a valid empty namespace remains Some.
- Eager typed preload skips Unknown, deduplicates within the known namespace, and writes its matching namespace. Existing can-chain/type rules are preserved.
- Attr graph nodes contain Name and Namespace; derived equality compares both and still distinguishes the Custom variant. The order map buckets per namespace; visit_link itself is unchanged. Root enumeration retains both atoms.
- Chained fill, traversal root read, primary-validity lookup and SCC removal use the node/reference namespace. Unknown explicitly queues its fallback before continuing in visit_value_references; it never creates a null-namespace node.
- Both apply sites pass var.namespace(). Custom calls pass None; the apply routine keeps existing custom registration/wide-keyword logic and uses Some(namespace) on attr success/failure. The removed Env arm was already unreachable by API contract. NonCustom nodes do not call apply. The unwraps are guarded by a branch that distinguishes Attr from Custom within that two-variant match.
- Final typed lookup now uses the same known namespace that enabled the DOM query. Namespace Option is a borrowed option, so the closure's `namespace?` does not require owned atom cloning. Unit/raw/container-query branches are unchanged.
- The patch leaves bug 2021110's missing nested namespace-map TODO and bug 2028861's container-query comment intact.

## Expanded WPT baseline

Root's authenticated baseline-v3 has 13 FAIL / 8 PASS / 1 OK for the 21-case test, plus existing attr-cycle.html 37 PASS and two namespace reftests PASS. The raw JSONL statuses are checked against the receipt, and before/after pins are equal. Final 21-case WPT hash: `992d8cd727fd6afcc5dea061da90f50e0fc9986deae59981e8de0c1a6a77b342`.

Failures cover both direct declaration orders, both null/named orders, explicit null namespace, both var-chain orders, qualified-to-null same-name chain, both cycle-isolation orders, invalid substitution, invalid type and the first assertion of mutation sequence. The missing-attribute, unknown-prefix, URI alias, single-namespace, distinct-name, identical-name and numeric-unit controls pass. A dynamic test failing its initial state does not supply execution evidence for its subsequent mutation steps; those await the candidate run.

Read the entire final WPT. Stylesheet insertion preserves the declared namespace context. Element IDs are unique, values are numeric absolute lengths, and tests remove their elements. The accumulated rules have unique ID selectors, so prior rules cannot affect subsequent cases. Both width and height declarations are checked as parsed. It does not assert every DOM readback in this revision, but uses standard setAttributeNS with explicit URIs; initial scout already calibrated those reads. No optional support exit. The cyclic case's outer fallback 5px is appropriate even though --loop also has a fallback: its primary attr/custom-property cycle invalidates that SCC; outer consumers use their own fallback. Original attr-cycle tests include the same fallback distinction.

Nonblocking improvement: use assert_array_equals([style.width,style.height],[width,height]) to retain the complete measured pair on failure. Existing assertions are sufficient to distinguish regression, so a source change solely for diagnostics is not required after a pinned gate.

## Pre-existing fallback preload gap (separate static lead)

The parser stores fallback references in nested VariableFallback.references and only bubbles flags. update_attributes_map iterates top-level refs.refs. Ordinary width/height declarations are not NonCustom graph roots; the seen.attr roots contain attribute *values*, not those declarations' fallback expressions. Therefore, with a:x=13px and no other typed use of a:x:

`width: attr(unknown|missing type(<length>), attr(a|x type(<length>), 5px)); height:7px`

appears to resolve the nested typed lookup from an unpopulated map and fall back to 5px rather than 13px. A missing known primary should expose the same gap. This predates v2 and is separate from namespace key identity; the candidate's Unknown graph fallback branch only applies when visit_value_references is actually reached. No browser execution of this proposed witness was performed here, so it remains a static lead. It does not block the targeted key repair, and it must not be silently represented as fixed by the 21-case gate.

Remaining approval gates: root's actual candidate compile and paired WPT, final source equality, lint/format/standalone isolation. No other native source edits are needed by this static review.
