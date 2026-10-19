# Typed attr fallback eligibility: isolated implementation proposal

Status: source-reviewed draft, not compiled or browser-tested. This package proposes a narrow repair; root owns native application, independent review and acceptance. Run `python3 check.py` for authentication, exact patch apply/reverse in a temporary directory, and JavaScript syntax checking. It requires Python 3, patch and Node; it does not need the live repository or a browser.

`fix.patch` contains three Rust changes and the new twelve-case WPT. `native.patch` and `wpt.patch` split those parts. `original/` and `candidate/` retain complete exact files. `BASE.json` identifies the root-applied recursive-preload base, including namespace, tombstone and source-aware shorthand-cache repairs. The patch does not contain those earlier repairs. No clean historical-base applicability claim is made.

## Behavior and source correspondence

The old graph decision accepts any resolved, reference-free attribute, even when the particular attr() occurrence requests an incompatible syntax. Final substitution already rejects that syntax. Consequently the graph can omit a used fallback dependency, allowing its consumer to run before an attribute in that fallback resolves. The retained after-preload receipt still has three relevant failures: one diagnostic custom-property case and the warmed/unwarmed readiness cases. These are prior browser observations, not results for this proposal.

`AttributeData::parse_typed_value` extracts the existing final primary parse. It preserves the input parser, syntax, occurrence URL, absent namespace map, permission for computational dependence, default AttrTaint and optional property ID. Converting parser errors to `()` preserves the old caller's discarded-error behavior. Final substitution still serializes the parsed value and marks its substitution attr-tainted. Container-query handling remains on its existing branch.

`visit_value_references` first visits the primary dependency and retains its non-custom reference observations. It then performs the shared parse only when the existing ready-value test succeeds and the occurrence has `AttributeType::Type`. A failed parse queues that occurrence's fallback. It does not tombstone or replace the cached primary: another occurrence can validly request `type(*)`. Pending values cannot become ready merely because universal syntax accepts their tokens. Missing/unknown namespace and tombstone branches are unchanged. Unit, raw-string and omitted-type behavior is outside this change.

The graph and final substitution both obtain the primary CSS through `to_variable_value()`. Final substitution additionally checks the live DOM attribute before its cache lookup. Agreement therefore still relies on provider/cache stability; this proposal supplies no proof of that assumption.

## Occurrence context

The non-custom collection now stores `(v.id, Arc<UnparsedValue>)`. The shared `UnparsedValue::substitution_property_id` chooses the shorthand when present and otherwise the originating longhand. Both graph validation and final `VariableDeclaration::substitute_variables` call it. Deriving the ID from the graph node would lose information because line-height values are also recorded under font-unit dependencies. Source-aware shorthand-cache identity checks and writes are preserved byte-for-byte outside the extracted context expression.

Custom and attribute roots pass `Some(PropertyIdRef::from(name))`, matching the existing substitution consumer, including its attribute-name convention. This preserves existing context; it does not establish that every aspect of that convention is correct. The pinned registered-value parser forwards property IDs through `ParserContext::with_property_declaration`; the helper returns a specified value and does not call `to_computed_value`.

## Specification and test expectations

The retained primary CSS Values 5 snapshot was fetched successfully on 2026-10-19 and is bound by its FETCH record. The attr substitution algorithm resolves the primary, validates the requested type, and uses the fallback on failure. An unused fallback is not substituted. Thus a resolved identifier may succeed for `type(*)` while requiring fallback for `type(<length>)`; a cyclic fallback matters only when used. The generic substitution rules supply the cycle-invalid result used by the custom-property assertions.

The twelve WPT cases cover the three retained failures, both orders of different syntaxes on one attribute, successful typed/universal primaries with unused self-cycles, failed typed primary with a used cycle, literal/missing controls, line-height and font shorthand. Raw custom-property readback accompanies relevant width checks. The last two cases exercise context paths; they do not demonstrate a syntax whose acceptance differs between those property IDs. Test expectations are predictions until root runs the WPT.

## Limits and required gates

The signed eligibility model is retained as design evidence. Its parser remains a parameter; this source change has not turned it into a full native parser proof. No new Lean theorem, Tarjan proof, provider admission or full C1–C13 closure is claimed.

The helper takes no DOM tracker, computed context or fallback worklist. Nevertheless the added parse can allocate and invoke transitive parser code. No universal side-effect, randomness, preference, resource, observer or taint noninterference proof is supplied. Keeping the old parse arguments and final taint branch is source correspondence, not such a proof. The additional validation parse also has a performance cost that has not been measured.

The reference vector gains an originating LonghandId per entry. Layout/padding and memory effects are unmeasured. No FFI structure is intentionally changed, but no compiled layout/ABI assertion is claimed. Rust compilation, formatting/lint, baseline/candidate WPT pairing, existing attr/property regression tests and independent native review are required before acceptance.

The source-only checker verifies packaging and exact patch correspondence, not semantics. `INPUTS.json` authenticates the package; `FREEZE.json` authenticates that manifest. The fresh checker receipt is separate to avoid a self-referential seal.
