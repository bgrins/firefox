# Declaration scratch publication audit

Date: 2026-10-19. Status: source-derived defect reproduced by root's browser; isolated repair proposal only. No production changes or new universal theorem in this package.

## Finding

`link-parameters: param(--a, var(--x, red))` follows a real successful ordinary parser path while the shared cssparser observer records substitution. `LinkParameters::parse` delegates each parameter value to the actual `VariableValue::parse`, accepts it, and returns. The generated longhand callback then pushes the ordinary declaration. `parse_non_custom_property_declaration_value_into` abandons this successful result for substitution fallback but retains its scratch declaration, then appends a second `WithVariables` declaration of the same property.

`PropertyDeclarationBlock::extend`/`push` deduplicate this sequence during declaration-list parsing. CSSOM `prepare_for_update`, however, computes both entries against the unchanged destination: for a fresh property both become `Append`. `update` appends both. `remove_property` removes the first longhand and returns, leaving a declaration whose property-id membership bit has been cleared.

Root's retained browser run confirms fresh assignment length 2 instead of 1 and removal length 1 instead of 0 for var/env/attr: **6 FAIL, 19 PASS, one harness OK**. Existing-property updates, cssText publication, empty parameter, `none`, and invalid-var controls pass. The observation is declaration storage/CSSOM behavior, not a demonstrated rendering defect or security conclusion.

## Normative oracle and feature boundary

CSSOM's [set a CSS declaration](https://drafts.csswg.org/cssom/#set-a-css-declaration) requires a unique declaration for the target name and preserves unrelated declarations. Its removal algorithm operates on that unique declaration. The [linked parameter grammar](https://drafts.csswg.org/css-link-params-1/#funcdef-param) accepts arbitrary parameter values, including empty values; substitution functions resolve in the element context. `evidence/SPEC-WEB.json` retains the current primary-source retrieval and identities. No complete specification-to-native refinement is claimed.

The content property is pref controlled: `layout.css.link-parameters.enabled` defaults to `@IS_NIGHTLY_BUILD@`; its WPT directory forces true. `enabled_in="chrome"` also permits chrome contexts, but does not make the pref-enabled property chrome-only. The root run is a local Nightly build with the WPT pref. Release default exposure is not claimed. Root's baseline input/before/after and raw output are copied under `evidence/root-browser` and checked against source/test hashes.

## Complete inspected chain

1. `PropertyDeclaration::parse_into` requires empty `SourcePropertyDeclaration`. Longhand callbacks publish only after `parse_entirely` succeeds. Generated shorthand `parse_into` similarly delays all pushes until the whole shorthand succeeds; `all` uses its separate scratch field.
2. The complete noncustom helper enables observation, handles CSS-wide keywords, runs ordinary parsing, retains the observed boolean after the query disables tracking, rewinds for full-value curly validation, then reparses with `VariableValue::parse` before publication.
3. `SourcePropertyDeclaration::{push,clear,drain,is_empty}`: push does not deduplicate; clear resets both the ArrayVec and `all_shorthand`; drain consumes both. Fixed-capacity overflow is not demonstrated: no reachable large shorthand success-plus-observation path was found.
4. `DeclarationParserState::parse_value` publishes through `extend` only after value, priority and exhaustion checks. `did_error` clears scratch. CSSOM `set_property` uses a fresh scratch value and returns before publication on error. A populated error scratch is not by itself a published defect.
5. Complete `set_property_to_declarations` calls `prepare_for_update` then `update`; full `extend`, `push`, preparation, update, removal and supporting index handling are retained. Existing-property update overwrites the same slot, so that control does not reproduce duplication.
6. `nsDOMCSSDeclaration::{ParsePropertyValue,ModifyDeclaration,Length,IndexedGetter}` and `nsDOMCSSAttributeDeclaration::{SetCSSDeclaration,GetOrCreateCSSDeclaration}` bind actual CSSOM to the Rust block. `nsStyledElement::SetInlineStyleDeclaration` wraps the passed block in `nsAttrValue`, without serialization/reparse. Later style access reparses only non-declaration attribute values. The exact full C++ files are retained.

## Source-only native witness

`native/build.py` builds the retained actual cssparser and dependencies directly, then extracts complete current definitions: VariableValue/Reference records, flags/unit classification, `VariableValue::{empty,parse}`, `parse_name`, recursive declaration-value parsing, ParsedNamespace/resolver, complete LinkParameters parser, and complete noncustom helper. Extraction receipts record each complete body hash. Earlier EOF and depth repairs are retained; no old parser snapshot is substituted.

18 complete extracted definitions; 13 values per original/proposal exercise var/env/attr successful callbacks, multiple parameters, ordinary/empty/none/wide controls, pure fallback, invalid var name, empty var/env and nested priority rejection. Four original scratch duplicates become one replacement each; nine controls are unchanged. The invalid cases execute the real recursive VariableValue rejection, unlike the accepting gateway facade in the preceding curly audit.

Boundaries: String/Vec replace Gecko atom/ArcSlice/OwnedStr ownership; the scratch Vec records publication kind instead of compiling the complete declaration enum/ArrayVec; generated longhand callback structure is reproduced explicitly. The DashedIdent adapter is limited to the admitted ASCII names. Untyped attr parsing is a guarded adapter that rejects the witness if typed syntax appears; namespace parsing itself is extracted. CSS-wide handling covers only the admitted initial keyword. URL ownership, typed attr, all other property parsers, substitution evaluation, CSSOM update code and C++ are inspected, not compiled in this witness. Browser evidence closes only the concrete 25 test cases. There is no full Stylo build, universal native equivalence or rendering proof here.

## Minimal proposed repair

`proposed-native.patch` clears scratch at the successful ordinary parse transition after the no-observation early return, before fallback validation. This resets both ordinary declarations and special all storage before replacement. It leaves the ordinary-success/no-observation return, wide-keyword branch, observer query/reset order and outward validation failure behavior unchanged (discarded scratch is cleared earlier). Cost is a clear only when successful ordinary parsing observed substitution; there is no new input scan. It avoids relying on every publication consumer to deduplicate invalid scratch input. Candidate browser/build, broader regression gates and formal acceptance remain separate root-owned work.

## Coverage, negative findings and next contract

Inspected successful parsing candidates include image functions, content counters, font alternates, calc optional arguments and color speculation. Known-function dispatch, transactional `try_parse` and enclosing exhaustion reject the candidate swallowed-substitution paths; no second reachable ordinary success-plus-observation property was established. Strings and URL text do not establish nested function-token observation. This is a bounded audit, not exhaustive generated-property coverage.

Existing link-parameters computed/dynamic tests exercise substitution results but do not require CSSOM length/item uniqueness after fresh assignment. The artifact probe targets that gap. Bounded Bugzilla searches retained in `KNOWN-ISSUES-WEB.json` find feature tracking and parameter-name duplication work; these concern parameter lists and do not establish this CSSOM declaration-storage defect as known or novel. No novelty claim.

The next substantive formal contract should model speculative ordinary output and fallback as mutually exclusive publication transactions. Under empty initial scratch, callback atomicity on failure, and unique longhand identities within each generated expansion, accepted output contains exactly the selected branch's declarations; failure is never published. Compose this with a separate ordered block/list invariant: membership set agrees with vector identities, each identity occurs once, fresh/replace/remove updates preserve it. Include special `all` storage, priority, logical ordering and both declaration-list and CSSOM consumers before a broad native refinement claim. The original duplicate is a concrete counterexample to disjoint branch publication. This closes a source admission gap exposed by the previous curly proof; it does not retroactively expand that proof's theorem.

## Replay and roster

Authenticate the externally supplied MANIFEST/checker hashes, then run `python3 -I -S check.py --output /absolute/new/output`. The checker authenticates the exact input set before executing artifact code, rejects shadow files/symlinks/path escapes/duplicates, verifies source/browser bindings, and optionally rebuilds both native variants. The Rust toolchain is externally pinned in TOOLCHAIN.json. Canonical and relocated replay pass; retained receipts contain the relocated 199-input execution before adding its own replay/tamper receipts. The final manifest includes these passive receipts as well. Executed shadow-module and changed-driver controls are rejected before artifact execution. MANIFEST plus MANIFEST.json and FREEZE.json are the exact commit roster; binaries and working directories are excluded. Root's independent browser capsule is copied, not modified.
