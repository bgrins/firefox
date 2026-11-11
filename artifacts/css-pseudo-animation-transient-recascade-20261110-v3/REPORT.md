# Transient pseudo recascade prototype

This is a maps-in/style-out prerequisite experiment for bug 1615083, not a public CSSOM repair. Native compilation and browser execution remain unrun.

`native.patch` changes ServoStyleSet.cpp, ServoStyleSet.h and glue.rs. `driver.patch` adds the temporary map factory, privileged driver/XPIDL method, manifest entry and fixture. `extension.patch` composes both over the authenticated query-v4 prerequisite. The existing query 208-assertion fixture is unchanged. `check.py` authenticates 12 Git inputs and 11 prerequisite files, replays the combined patch forward/reverse and both split patches, parses XPIDL/TOML, checks inert JavaScript, exact assertions, scoped ESLint and Prettier idempotence. XPIDL types/generated bindings, genuine installed lint and native compilation remain gates. Scoped ESLint disables only import-globals because the fixture is not installed. C++ additions use clang-format 22.1.8 with real source filenames; Rust additions use rustfmt 1.8.0, edition 2024.

## Contract and implementation

The entry takes an originating element, before/after/marker request, pseudo rule style, originating primary style, and separate already-composed Animation and Transition maps. It rejects non-dynamic/disconnected/foreign-document requests, traversal reentry, dirty stylist, unsupported/identified pseudo requests, generated pseudo elements, wrong pseudo tags, and a primary pointer that does not match the element's stored primary style. Pointer equality establishes stored-style correspondence, not unique provenance of a shared allocation. The caller still supplies the coherent pseudo rule style for the same target/epoch and current layout ancestry; a same-pseudo base from another element cannot be detected here.

Rust clones CascadeInputs from the base, retaining its flags and existing visited path. It replaces/removes exactly the Animation and Transition levels on the normal and existing visited paths. Other levels, including important rules, remain. Empty maps remove the corresponding level. The existing cascade_style_and_visited_for_pseudo_with_default_parents resolver receives the explicit pseudo tag and originating primary style; it selects the actual layout parent when the originating style is display:contents.

Owned declaration blocks and returned style retain rule references. The new context/cache is local. This seam does not match selectors, acquire/sample effects, convert endpoints, update animation rules or publish ElementData/style. Global rule-tree allocation and AutoSetInServoTraversal post-traversal tasks still occur: this is not a global-purity, no-callback or arbitrary-reentrancy proof. Caller freshness, provider coherence and current synchronous native conventions remain premises. Existing visited inputs/machinery are retained, but public CSSOM sanitization/privacy is not established; the fixture uses ordinary unvisited elements and no history-dependent oracle.

## Direct fixture and oracles

The temporary driver flushes and completes lazy resolution before entering the seam. Ordinary donor computed styles supply one property per map, avoiding animation sampling and endpoint conversion. It reports admission, pseudo identity, stored origin-style pointer preservation, generated-pseudo existence, adjusted display and a serialized result. Flag 4 recascades the first returned style with empty maps to exercise actual removal from a populated path.

The exact inventory is 100 assertions in six tasks: six setup checks, 68 admission/preservation observations and 26 result/rejection checks. Setup failures and missing callbacks invalidate the experiment separately from behavior mismatches.

| Task | Assertions | Oracle |
| --- | ---: | --- |
| cascade_origins | 28 | normal author 10px < animation 50px < important author 30px < transition 70px; transition-only and overlapping maps |
| disjoint_maps_and_no_publication | 17 | disjoint margin/opacity survive; public style unchanged; empty maps remove both prior origins |
| inheritance_and_authored_relative_values | 22 | originating and changed font inheritance, authored em after font-map cascade, RTL logical mapping |
| custom_property_provider | 7 | authored var fallback and custom-map substitution with independently checked donor |
| pseudo_layout_parent | 11 | inline pseudo under block origin versus flex blockification through display:contents |
| supported_and_rejected_identity | 15 | before/after/marker identity; ordinary/wrong-primary/wrong-pseudo/generated rejection |

The generated negative first requires noPseudoCreated === false. Donor/base setup checks precede relevant comparisons. The absent-pseudo display observation is an internal resolver-consistency oracle, not a universal public CSSOM resolved-value claim.

Primary contracts: [cascade origin priority](https://drafts.csswg.org/css-cascade-5/#cascade-sort), [tree-abiding inheritance](https://drafts.csswg.org/css-pseudo-4/#treelike), [generated content and box creation](https://drafts.csswg.org/css-pseudo-4/#generated-content), and [display:contents layout substitution](https://drafts.csswg.org/css-display-3/#valdef-display-contents). Searchfox discovery and primary observations are retained in discovery; SOURCES.json pins exact local implementation at ec467c0219d3d5daf70f42fcc53677cf8a262173.

## Execution and remaining gates

Root should build the cumulative query-v4 plus extension, run installed lint, then the new 100 assertions, unchanged query 208 assertions, and existing 130-record WPT vector as separate gates. A retained browser without the new XPIDL method is not a meaningful direct-driver baseline. Full callback inventory, no crashes/errors/duplicates/task aborts, and complete restoration are required.

Passing establishes only these maps-to-pseudo-style cases. Coherent animated custom-property/font/writing-mode providers for endpoint conversion, timing/ranges/order/base/mask/sample coherence, public CSSOM cache/generation/admission and visited exposure remain open. The raw unanimated base is not promoted to an endpoint provider. The historical missing-pseudo debug transform/change-hint gate remains mandatory for final repair acceptance. No new bug or completed bug 1615083 fix is claimed.

## Revision 2 compile amendment

The first native compilation found lowercase pseudo enumerators in the temporary driver. Source follow-up identified the same issue in the production admission guard. This revision changes exactly four enumerators in two native files to Before/After/Marker, recorded in ENUM-AMENDMENT.patch; fixture and 100 assertions are byte-identical. Revision 1 remains frozen. No successful compile or semantic runtime result is inferred from that failure.

## Revision 3 lazy-marker branch

Independent review found Marker does not have IS_EAGER, so the originally shared resolver would hit its eager-only debug assertion. After replacing both origin rule paths, Marker now uses the existing Stylist::compute_pseudo_element_style_with_inputs convention with the explicit primary parent and originating element. Before/After retain the layout-parent-aware eager resolver. The lazy helper preserves visited inputs but uses the primary style as both inheritance and layout parent, with an existing source TODO; no new claim about Marker display:contents layout adjustment is made. The Marker font/identity fixture and all 100 assertions remain unchanged. This fixes the identified assertion precondition without waiving the final public missing-pseudo debug gate.
