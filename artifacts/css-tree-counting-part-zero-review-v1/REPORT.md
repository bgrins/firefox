# Failed tree-counting scope match

Status: artifact-only source and WPT proposal; no native overlay, compiler, browser, acceptance, or count increment by this reviewer.

## Spec trace and history

[CSS Values 5 tree counting](https://drafts.csswg.org/css-values-5/#tree-counting) resolves a real element-backed pseudo against that element, makes the function a loosely matched tree-scoped reference, and defines a failed match as zero. Its explicit outer `::part()` example yields zero pixels. [CSS Shadow 1 name matching](https://drafts.csswg.org/css-shadow-1/#shadow-names) allows the automatic name on the element to match a reference from the same or a descendant tree, not a containing tree. Therefore a document rule targeting a shadow element through `::part()` fails this match: **REACHED, expected index/count zero**. Same-tree and inner-tree `:host` references remain ordinary DOM counting.

[CSSWG issue 9573](https://github.com/w3c/csswg-drafts/issues/9573#issuecomment-2622696411) resolved the exposure restriction on 29 January 2025. [Commit 51430580](https://github.com/w3c/csswg-drafts/commit/51430580f1c65ed7fb93e52738510f92c907f0e9), dated 10 March 2025, introduced the zero text and example. Its message explicitly distinguishes the restriction resolution from the editorial zero choice based loosely on the minutes. SPEC-HISTORY.json saves this primary commit's relevant metadata and patch. This is not a newly introduced October 2026 rule.

Current upstream WPT still expects one. UPSTREAM-WPT.html, fetched directly from the WPT repository, equals the captured local test. This proposal aligns implementation and test with the current published draft; it does not claim the original implementation lacked a supporting test. No separate resolution specifically choosing zero was established here. webspec-index remains unavailable from the earlier tooling investigation; current official CSSWG pages and primary repository history supplied the trace.

## Narrow implementation

`Context::resolve_tree_counting_result` already detects containing-tree references, but returns `TreeCountingResult::default()` (1,1). Only this branch becomes `TreeCountingResult::new(0, 0)`, with its directly related comment corrected. Query dependency flags, caches, same-tree resolution, and all other default callers remain unchanged. `ShadowCascadeOrder::is_in_same_or_containing_tree` has a misleading name but tests positive order, excluding same-tree zero; this proposal does not change that predicate.

The global default also serves missing/dummy-element contexts. Their specification and behavior are outside this patch. No contextual easing guards, selection algorithms, or animation invalidation behavior changes.

## Diagnostic and WPT

`await observeTreeCountingPartZero()` returns support checks, authored outer rule, and all three snapshots before cleanup. A separate holder guarantees actual index/count 2/3, then 3/4 after prepend, then 2/3 after removal. Same-tree margin/padding measure those values; an outer literal 7px border proves the part selector applies. Outer width/height should remain zero. Each snapshot has repeated reads. Unsupported syntax is a failed calibration, never a successful repair.

The candidate updates the existing outer-scope test from one to zero, retains the existing `:host` 3/5 control byte-for-byte, and adds two dynamic tests, one per function. All snapshots and calibrations precede expected-zero assertions. The four-test page uses ordinary computed CSS values and does not depend on contextual easing activation. Current Searchfox StaticPrefList has `layout.css.tree-counting-functions.enabled: true`; runtime support still must be measured.

Root ran the exact diagnostic on System Firefox 158 (b197d1/0). Independent saved-result recount found all three support/mutation/literal/repeat calibrations satisfied, while outer width and height were 10px in all phases (six differing measurements, not six bugs). CHECK.json pins the raw tool response. Root reports the owned tab closed. No current local160 or candidate observation is claimed. No standalone formal model is added: encoding the constant fallback alone would not establish source/spec equivalence or meaningful new coverage.

## Contextual easing scope review consequences

The earlier handoff review described implementation fallback one, not a normative oracle; future tests must use this corrected distinction. Transporting the selected keyframe's scope can preserve existing selection while still failing normative selection: CSS Shadow captures the reference root in animation-name and starts global lookup there, whereas the existing element/name lookup does not receive that root. These are separate obligations.

Required scope matrix: ordinary same-tree keyframe, outer part keyframe, one/two nested assigned slots, an exported part across an intermediate tree with no relevant rules, duplicate inner/outer keyframe names with an outer declaration, document fallback, and actual user/UA origin selection. Keep identity and origin assertions separate from numerical results: counting only distinguishes positive outer scope from allowed same/inner scope, so it cannot prove exact negative slot depth or exact positive ancestor identity. Empty rule data must not compress physical tree distance. Three-bit scope saturation and SVG-use normalization need explicit limits, not universal identity claims. User/UA injection needs privileged test plumbing; ordinary WPT author styles cannot certify those origins.

Actual animation input may be animated style. Normal-restyle reconstruction excludes animation-only updates, and self-dependency/animated-font behavior remains unresolved. This proposal does not label the supplied style guaranteed unanimated base or solve those gaps.

A conditional transport invariant is sufficient for this inactive scope prototype: projecting `(selected_rule, selected_scope)` to `selected_rule` preserves the existing lookup result and callback order; the scope denotes the selected rule's origin and declaring tree relative to the target; dependency collection and actual easing computation use that same pair; reusable caller scope is restored afterward. This is not an invariant proving the existing lookup's conformity to animation-name reference-root selection.

For a future easing activation test, use keyframe-local `steps(calc(1 + sibling-index()), end)` on opacity 0→1, paused at 750ms of a 1000ms animation. Same-tree index2→3→2 predicts opacity 2/3→3/4→2/3; a failed outer scope predicts zero throughout (current fallback1 would give1/2). Keep the animation running object installed while mutating siblings, rather than recreating effects, so the test checks invalidation. Calibrate with independent literal steps(3), steps(4), and steps(1). This expectation requires contextual parsing to be enabled and is not a passing test claim for the current guard-closed build. Duplicate-name winner tests should use distinguishable literal endpoint values, independently of tree-counting easing, to avoid conflating selection with evaluation scope.

The bounded downstream audit found exactly one caller for each Context query: TreeCountingFunction::to_computed_value returns the u32 unchanged. Its two evaluation consumers (specified calc leaf and computed length-percentage leaf) cast directly to f32 numeric leaves. No decrement, positive assertion, or array indexing occurs on these paths. The failed-match return precedes the tree-counting cache, so zero is not inserted into DOM sibling caches. Existing flags remain conservative. This is source inspection of these direct consumers, not a whole-engine proof or compiled result.
