# Firefox CSS verification: committed bugfix catalogue

Branch: stylo-bloom-verification-2. Verified HEAD: `883d620fdbd6b66d4df871d660ee9612d1c20985`.

171 committed browser repair entries, each an ancestor of HEAD. Research, proof, test-only and alternative commits are excluded. ID 120 is held and excluded; IDs continue through 172.

A = first review: demonstrated crashes or attribute-provenance boundary. B = next review: rendering, dynamic updates and API correctness. C = later review: narrower triggers, extreme arithmetic or restricted exposure. These are recommendations, not official Mozilla priorities or security severities.

Fix 160 remains included as a committed repair entry but is explicitly held for revision before landing. Tier totals retain it in B; the hold is a readiness decision, not a new severity classification. No pre-160 runtime ablation or release attribution is claimed.

Release exposure and standalone prerequisites vary. An ancestor check is not a new browser test or clean-upstream validation. Formal results generally cover conditional components, not whole-implementation correctness.

Reconciled the October 29 readout (147 fixes) with 24 subsequent native/test commits. All include WPT changes; fix 4 uses a Mozilla-specific WPT with SpecialPowers for privileged stylesheet installation.

| Area | Fixes | A | B | C |
|---|---:|---:|---:|---:|
| Selectors, Bloom filters and scoping | 14 | 1 | 10 | 3 |
| Cascade, layers and shorthands | 10 | 0 | 9 | 1 |
| Parsing, tokens and CSS math | 33 | 1 | 3 | 29 |
| Container queries | 4 | 0 | 3 | 1 |
| Animations, timelines and transitions | 23 | 4 | 13 | 6 |
| Colors, images, SVG and shapes | 8 | 0 | 3 | 5 |
| Attributes and custom properties | 23 | 4 | 10 | 9 |
| Layout, sizing and positioning | 23 | 0 | 16 | 7 |
| Text and fonts | 19 | 0 | 10 | 9 |
| CSSOM geometry and hidden layout | 14 | 0 | 11 | 3 |

## Selectors, Bloom filters and scoping

| ID | Priority | Commit | Fix | Impact / rationale |
|---|---|---|---|---|
| 1 | C | `d855b3483b49` | Account for prior saturation when clearing StyleBloom. | Debug assertion and stale filter state; retained saturation alone is conservative, so release rendering or performance harm is not established. |
| 2 | A | `93a062cded54` | Build relative-selector Bloom filters with an iterative traversal. | Demonstrated process crash; assess reachability and affected builds first. No memory-corruption or exploitability claim. |
| 5 | B | `075be5516374` | Order nested scope roots by proximity. | Wrong styles from ordinary nested-scope proximity;4baseline failures. |
| 6 | C | `a46e5310cd60` | Match scope-end selectors when reaching a shadow host. | Scope and shadow-host interaction;6baseline failures. |
| 7 | C | `78c11c75170a` | Exclude scope roots from scope-limit matching. | Spec-update conformance;5baseline failures and existing expectations updated. |
| 8 | B | `d4a2b600f078` | Include the scope element in relative selector cache keys. | Cache key omits matching context;7baseline failures, so style can depend on evaluation order. |
| 9 | B | `92c013c16908` | Include the scope element in filtered nth-index cache keys. | Cache key omits matching context;10baseline failures. |
| 10 | B | `64ac54569f1c` | Follow relative dependencies when invalidating scope limits. | Dynamic relative-selector invalidation misses enclosing rule subject;32baseline failures. |
| 11 | B | `b1b1bacb9406` | Propagate filtered nth invalidation from relative anchors. | Relative anchor fails to invalidate non-subject tail;5initial baseline failures. |
| 12 | B | `f4b34bf7fef1` | Avoid style sharing for scope-dependent nth filters. | Incorrect shared styles for different filtered positions;10baseline failures. |
| 146 | B | `7501711ae4a1` | Avoid caching reset styles that depend on sibling-count(). | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 147 | B | `ebb5d4fc489e` | Invalidate old-parent styles during moveBefore(). | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |

| 168 | B | `8ffd094be532` | Preserve stylesheet indices in shared implicit-scope cache keys. | Shared contents with different inactive prefixes resolve scopes against the wrong owner. Two failures become passes in the current local build; ten prior passes and the two separate host-context failures are preserved. Also reproduces in installed Nightly. One Rust file and three WPT resources; exact patch uses the preceding media collector API. |
| 169 | B | `8424404304d6` | Include implicit-scope host context in shared cascade cache keys. | Same-index shared sheets compiled for a shadow host versus a nested owner use different selector buckets. Two failures become passes; all 14 combined assertions pass. Also reproduces in installed Nightly. One Rust file and two WPT resources. No release-channel, isolated-upstream-build or memory-safety claim. |

## Cascade, layers and shorthands

| ID | Priority | Commit | Fix | Impact / rationale |
|---|---|---|---|---|
| 3 | B | `5d3638a91adf` | Exclude false-supports imports from effective rule iteration. | A conditionally disabled import changes later cascade outcomes;4baseline failures. |
| 4 | B | `e28cb48d656b` | Sort important user and UA rules by cascade priority. | User/UA origin ordering;10baseline failures using privileged sheet installation. Real-world prevalence of layered user/UA sheets is unknown. |
| 16 | B | `11482ee213bf` | Preserve shorthand source identity when reusing substituted values. | Lost declaration identity gives wrong substituted longhands;20baseline failures. |
| 23 | C | `e27beeac5129` | Order physical shorthands before logical shorthands of equal size. | Conflicting equal-sized physical/logical animation shorthands receive the wrong precedence. Requires overlapping shorthands in a keyframe; ordinary nonconflicting animation declarations are unaffected. |
| 38 | B | `c57d0c806d94` | Recompute nesting specificity from expanded selector components. | Nesting expansion updates packed specificity arithmetically and gets the winning rule wrong for functional selectors containing the parent selector. Core cascade relevance for nested :is/:not/:has/nth forms. Separate specificity saturation/boundary defects remain unchanged; no crash demonstrated. |
| 69 | B | `074086719e44` | Preserve logical-group order when setting the all shorthand. | CSSOM all assignment preserves stale logical/physical declaration order, so opposite insertion histories do not converge as required. CSSOM setProperty(all) with mixed mappings; oracle is relational pair order, not an asserted absolute canonical order. |
| 158 | B | `e86b64866cdc` | Preserve prioritary declarations after large unrelated cascades. | A large unrelated cascade loses declarations in high-priority property processing. Central cascade correctness, with a larger-input trigger. |
| 163 | B | `e63fc6b1892b` | Preserve cumulative cascade rollback exclusions. | Coherent important-inline predicate and accumulated-exclusion repair: 74 PASS / 6 FAIL became 80 PASS, with every prior pass and existing controls preserved. Two interacting mechanisms share required state; this is one delivery entry, not six bugs. Source-applicable to the retained pre-project ancestor; isolated upstream runtime and release-default exposure remain unclaimed. |
| 164 | B | `0f18d294fbac` | Exclude same-rule declarations during property rollback. | Wrong styles when logical/physical aliases or substituted declarations from one rule survive revert-rule. Retains 190 correctness and six occurrence passes; controls unchanged. Requires #163. Dense synthetic Rule256 remains 2.31–2.47× baseline; release exposure and isolated upstream readiness are unestablished. |

| 166 | B | `0aec45242b12` | Track stylesheet media applicability per collection entry. | Shared stylesheet contents conflate distinct link media conditions, leaving stale styles after viewport changes. Four failures reproduce in local baseline and installed Nightly; all eight target assertions and 39 nearby controls pass after repair, plus a rendering reference test. Three Rust files and five WPT resources. Source applies to indexed upstream; no isolated upstream build. |

## Parsing, tokens and CSS math

| ID | Priority | Commit | Fix | Impact / rationale |
|---|---|---|---|---|
| 13 | C | `708b914901ee` | Preserve zero signs when simplifying round with infinite steps. | Numerical corner case with relative lengths/infinite steps;6valid original failures. Separate literal-zero wording dispute retained. |
| 20 | C | `a4fe7dd06fd7` | Preserve NaN operands when simplifying clamp. | clamp simplification can discard NaN-producing operands and return the wrong computed value. Exceptional arithmetic and mixed/relative-unit simplification are required; CSS WPT enables typed arithmetic and release reachability needs separate confirmation. |
| 21 | C | `bfbce1cc7e9a` | Preserve finite dividends for valid infinite mod and rem divisors. | mod/rem with a finite dividend and an allowed infinite divisor returns NaN instead of the finite dividend. Requires exceptional infinity arithmetic; evidence establishes computed-value correctness, not a crash. |
| 35 | C | `83bc2bd39226` | Preserve escaped delimiters during bad URL recovery. | Bad unquoted-URL recovery consumes an escape introducer too early and exposes or swallows subsequent declaration tokens incorrectly. Malformed URL plus escaped delimiter is required. This is tokenizer/declaration-boundary correctness; no sanitizer bypass or security exploit is demonstrated. |
| 59 | C | `26e0fa16e89e` | Only classify dimension tokens as relative-unit dependencies. | Identifiers/strings/URLs resembling unit names are mistaken for dimension dependencies and can spuriously invalidate registered values. Specific token names such as relative-unit spellings; ordinary real Dimension behavior is unchanged. |
| 60 | C | `09b008b3320f` | Reject escaped newlines after leading hyphens in CSS identifiers. | A hyphen followed by an escaped newline is misclassified as an identifier start, changing CSS tokenization and parsing. Unusual malformed escape input; same predicate defect is already upstream issue440. |
| 62 | C | `4391deb4751a` | Preserve CSS numbers with compensating exponents. | Large mantissas and compensating exponents lose representable numeric values through intermediate overflow/underflow. Long/extreme numeric literals; not a general floating-point correctness repair; measured token micro-overhead, browser cost unmeasured. |
| 63 | A | `2d658a9c5aa4` | Keep fallback endpoints aligned with quoted EOF recovery. | Demonstrated process crash; assess reachability and affected builds first. No memory-corruption or exploitability claim. |
| 64 | C | `89bad2d8b526` | Preserve paired backslashes at quoted EOF. | Quoted EOF recovery drops a backslash even when the trailing run is paired, changing string semantics. Malformed/unfinished quoted CSS input; separate from the endpoint crash fixed by #63. |
| 65 | C | `ed9505d25ee4` | Recognize escaped terminal quotes during EOF recovery. | An escaped quote at EOF is mistaken for a real closing quote, producing wrong recovered strings/substitution output. Malformed/unfinished quoted CSS input; standalone version intentionally does not include #63/#64. |
| 66 | C | `55d251b7a900` | Consume rejected blocks at the CSS parser nesting limit. | At the parser nesting limit, rejected block contents can escape into following declaration parsing and change cascade results. Reproduced with 76 nested functions; correctness/recovery defect, not a demonstrated crash or injection exploit. |
| 67 | B | `095c5be548a2` | Validate the whole declaration value before substitution fallback. | Substitution fallback validates only the suffix after a failed normal parse, accepting forbidden top-level curly structure and changing cascade behavior across APIs. Malformed declarations with substitution trigger it; not evidence of a sanitizer/security bypass. |
| 68 | C | `780495d90a85` | Clear ordinary declarations before substitution fallback. | Abandoned successful parsing publishes duplicate declarations; CSSOM length and removal leave inconsistent observable entries. Concrete producer is link-parameters, Nightly-default pref and WPT-forced enabled; release-default exposure/rendering impact not established. |
| 81 | B | `34e4e755cb81` | Preserve registered custom property token boundaries | Registered custom property serialization loses token boundaries, changing downstream interpretation. 37-case WPT: ten baseline failures become passes; no release or isolated upstream runtime claim. |
| 84 | B | `bccea9c1fffc` | Keep custom property token metadata aligned with trailing whitespace trimming | Trimming stored whitespace leaves trailing token metadata inconsistent with the actual bytes. 28 baseline failures become passes in a 40-case WPT. General serialization correctness remains outside the proof. |
| 85 | C | `fff2d758ef6b` | Preserve escaped whitespace in custom property token values | Trimming escaped trailing whitespace changes identifier contents. 16 failures become passes in a 20-case WPT; escaped space/tab inputs are required. |
| 86 | C | `246f1ff43250` | Preserve newlines after backslash delimiters in custom properties | Removing a newline after a backslash delimiter turns an invalid animation name into an identifier. 30 final cases pass against a baseline subset with 16 failures; no release reproduction claimed. |
| 117 | C | `33ae2e8349e9` | Preserve the reserved counter value through computed integer math. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 118 | C | `d68543e601c4` | Round computed CSS integers after promoting the half-unit addition. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 119 | C | `6a363fc372c9` | Preserve nonfinite relative lengths inside CSS math. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 121 | C | `b218397700bd` | Apply stored integer ranges when resolving CSS math. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 123 | C | `0f68c5c1a7a5` | Resolve calculated counter range bounds when exporting membership. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 124 | C | `656b54ea29ef` | Compare and export additive counter weights by resolved nonnegative value. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 125 | C | `a9b7886a5f47` | Propagate NaN before resolving round() infinity cases. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 126 | C | `4c4ff0d440cd` | Preserve negative zero in finite round() upper bounds. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 128 | C | `10b6eabed271` | Preserve finite mod() and rem() remainders. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 142 | C | `25e423a1a810` | Preserve random cache indices across rejected CSS parses. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 144 | C | `c63be5163f2e` | Defer infinite-step rounding until the value is resolved. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 145 | C | `eb5208648811` | Preserve finite multiples when resolving round(). | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 149 | C | `36b693fee75e` | Avoid intermediate overflow and underflow in hypot(). | Extreme finite magnitudes overflow or underflow in intermediate arithmetic. Numerical robustness; strict conformance is unsettled because precision/range is implementation-defined. |
| 150 | C | `2d18f8b4a4d7` | Handle CSS pow exceptional values consistently in calculation and simplification. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 151 | C | `bc0853a77a44` | Preserve contextual infinity operands when simplifying CSS min and max. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 152 | C | `bf9b4d1a12ee` | Handle explicit-base log() exceptional values consistently. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |

## Container queries

| ID | Priority | Commit | Fix | Impact / rationale |
|---|---|---|---|---|
| 14 | B | `238710ff9db7` | Track dependencies for name-only container queries. | Name-only query dependency omitted;12baseline failures. |
| 27 | C | `16ff45a117b1` | Track attribute references through container-query operators. | Attribute changes fail to invalidate style container queries when an attr reference is nested under boolean query operators. The CSS WPT directory explicitly enables layout.css.style-queries.enabled; typed attr and style-query release availability must be confirmed. |
| 28 | B | `ef3d32280505` | Invalidate container queries when content-box size changes. | Container size queries become stale when padding/borders change the content box while the outer frame size stays fixed; dependent styles and container units can stay wrong. Strong dynamic layout relevance. Recorded full run exits 1 because of unchanged pre-existing unexpected passes, not failures of the new cases. |
| 170 | B | `90e0949346b5` | Restyle style-query consumers after animated custom-property changes (bug 2085413). | Animated named/unnamed style queries stay stale despite changed custom values. Known upstream S3/P3 report; feature-enabled Nightly reproduced. Two Rust files + one WPT; final 13-case comparison improves 3 PASS / 10 FAIL to 13 PASS with four Stylo threads requested. Broader 26-case comparison preserves twelve font controls. Existing #160 font/drain hold unchanged; clean-upstream context adaptation and release exposure remain unverified. |

## Animations, timelines and transitions

| ID | Priority | Commit | Fix | Impact / rationale |
|---|---|---|---|---|
| 15 | C | `0a81e1f36ab0` | Keep animation iteration identity separate from accumulation counts. | Finite indices alias infinity after integer saturation;12baseline failures. Requires extreme iteration/timing values. |
| 19 | B | `c92749721241` | Preserve deferred transform operations during composition. | Repeated/composite transform animation can turn deferred percentage-dependent transforms into identity, producing incorrect motion or geometry. The recorded observer is computed transform matrices; compositor painting and release prevalence were not established. |
| 43 | C | `0af700c67a5a` | Resolve scroll timeline axes from the scrolling frame. | A pseudo-element scroll timeline resolves logical axes using its originating element writing mode instead of the actual scrolling frame, producing wrong or inactive animation progress. WPT explicitly enables layout.css.scroll-driven-animations.enabled. Requires a scrolling pseudo-element with differing writing mode; check target release support before elevating priority. |
| 46 | B | `6b8dc654e8d0` | Include composition when comparing keyframes. | setKeyframes changes that only alter composite mode are treated as no change, leaving animation composition stale. Direct WAAPI update path; complex scheduling, CSS animation augmentation and compositor rendering remain outside the formal claim. |
| 70 | B | `188644f6d983` | Interpolate registered keyframes using substituted computed values. | Registered keyframes using var()/attr() are reparsed as unresolved text and interpolate discretely instead of using computed numeric values. Typed registered keyframes; literal/calc controls work; one adjacent expected failure remains and reaches a later assertion. |
| 78 | A | `4b4a00e70758` | Preserve attribute taint when replacing animation endpoints | Attribute provenance affects URL restrictions. Prioritize security-boundary review. Only #80 has the recorded CSS-only release actual-request experiment; arbitrary-secret exfiltration is not established. |
| 79 | A | `2c09cb2e4ff8` | Restyle animations when underlying attribute taint changes | Attribute provenance affects URL restrictions. Prioritize security-boundary review. Only #80 has the recorded CSS-only release actual-request experiment; arbitrary-secret exfiltration is not established. |
| 80 | A | `ede7ceb101d8` | Preserve attribute taint from both interpolated custom values | Attribute provenance affects URL restrictions. Prioritize security-boundary review. Only #80 has the recorded CSS-only release actual-request experiment; arbitrary-secret exfiltration is not established. |
| 82 | B | `d63735091bf8` | Preserve guaranteed-invalid animated custom properties | Animation publication replaces guaranteed-invalid registered values with initial values, changing required fallback/inheritance behavior. Ten reproduced failures improve in a 343-check matrix; two pre-existing expected failures remain. Six final controls are candidate-only. |
| 87 | B | `2db943802038` | Deduplicate initial view-transition types | Deleting an initially duplicated view-transition type leaves native selector membership behind. Five baseline failures become passes; all 21 candidate cases pass. The separate cached-style invalidation repair is not counted yet. |
| 88 | B | `c67505af9aae` | Restyle after active view-transition type changes | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 129 | B | `d13af8f7e9fd` | Recompute keyframe values after CSS animation reactivation. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 131 | B | `65355573964a` | Recompute active keyframe values after attribute changes. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 132 | B | `d477d0c33105` | Refresh contributing keyframes before commitStyles. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 133 | C | `e414c8f7cfcd` | Clamp calculated jump-none step counts at computation. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 134 | C | `70cc9c30ef44` | Clamp calculated cubic-bezier x coordinates at computation. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 143 | A | `22f97187e9f0` | Check both linear easing stop positions before conversion. | Demonstrated process crash; assess reachability and affected builds first. No memory-corruption or exploitability claim. |
| 148 | B | `9e99cf9e4c88` | Preserve move context through shadow-root traversal. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 159 | B | `334937d9ef85` | Refresh animated font-relative values after ancestor font changes. | Ancestor font changes or cancellation leave descendant animation or ordinary styles stale. Deeper dependency settlement remains separate unfinished work. |
| 160 | B | `2409a410a264` | Retain normal descendant restyling after animated font changes. | Held for combined producer/drain review. The completed producer-only comparison retained 137 PASS / 27 FAIL; the combined candidate reached 164 PASS. The historical stall trace identifies productive normal readmission and repeated changed-property requeue. Native global convergence remains unproved; no release regression attribution. |

| 165 | B | `664b08bcb7ce` | Preserve root identity when computing animation values. | Root font-size/line-height rem and rlh values use the wrong metrics. Installed Nightly and local baseline both reproduced nine failures; the repair passes all 21 target assertions and 26 nearby controls. Ordinary-size rendering correctness. One Rust file plus four WPT resources; source applies to indexed upstream, but no isolated upstream build or release-channel validation. |

| 171 | C | `7382007a82b4` | Allow additive clip rectangles with matching auto components. | Narrow deprecated-clip visual/computed-style arithmetic. Four expected-failure improvements share one native cause; all 5,061 SMIL assertions and 12 SVG observations are preserved. Current-source composition APIs are ungated; release exposure and debug execution are untested. Three native files, one nine-case WPT and one expectation update. |

| 172 | C | `883d620fdbd6` | Preserve earliest group order when merging percentage keyframes. | Known bug 1778402: repeated offset/easing/composition groups appear in the wrong getKeyframes() order. Two cases improve across 95 results while later declaration winners and all 93 other records are preserved. Narrow API correctness; no demonstrated security issue or release-channel validation. Two native files, strengthened WPT with one added case, and targeted metadata removal. Named-range grouping remains a separate follow-up within this issue. |

## Colors, images, SVG and shapes

| ID | Priority | Commit | Fix | Impact / rationale |
|---|---|---|---|---|
| 17 | B | `82b254686378` | Preserve analogous missing components across RGB and XYZ color conversion. | Color mixing loses missing-channel information during RGB/XYZ conversion, changing computed colors. Uses cross-space color-mix with none components; related WPT failure family was already known, so novelty is not claimed. |
| 18 | C | `591b3e125678` | Preserve zero-weight prefixes during normalized color mixing. | A normalized color-mix fold discards zero-weight prefix information that later missing components need. Requires a multi-item mix, zero-total prefix and relevant component behavior; assess current multi-color syntax availability on the target channel. |
| 30 | B | `06be3d7e722c` | Avoid overflow when computing polygon shape intercepts. | Polygon shape-outside intersection multiplies signed nscoord differences without widening, overflowing and placing wrapping content incorrectly. Flag for arithmetic-hardening review. Signed overflow is concrete, but inspected evidence does not establish memory corruption, a crash or exploitability; finite resolved coordinates and bounded differences remain premises. |
| 31 | C | `96e0ad8c6a0a` | Use the border box for stroke-box transforms on CSS boxes. | transform-box: stroke-box on ordinary CSS boxes leaves the reference dimensions unset instead of using the border box, breaking percentage transforms. Explicit stroke-box on CSS layout boxes; SVG dispatch and its geometry provider are unchanged. |
| 32 | B | `66fb24648a15` | Honor object-fit with partial intrinsic dimensions. | object-fit ignores none/scale-down sizing when an image has partial natural dimensions and no intrinsic ratio, visibly stretching content. Requires partial intrinsic image dimensions, typically a vector/resource edge case. General decode and all two-dimension/no-ratio cases are not proved. |
| 36 | C | `065183ac8449` | Compose empty SVG mask regions as transparent black. | An empty SVG mask region is skipped rather than composed as transparent black, incorrectly revealing pixels for intersect/subtract composition. Requires multi-layer mask composition and an empty SVG mask region; rendering failure is deliberately distinct. Visibility error alone is not a security-boundary violation. |
| 37 | C | `6bb2557507bc` | Compose zero-sized mask images as transparent black. | A ready mask image with zero paint area is skipped instead of participating as transparent black, producing wrong mask-composite output. Requires empty/zero-size/outside-clip image-mask geometry with nontrivial composition; resource readiness is checked separately. |
| 115 | C | `fa9dff982cec` | Correct SVG quarter-millimeter conversion factors. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |

## Attributes and custom properties

| ID | Priority | Commit | Fix | Impact / rationale |
|---|---|---|---|---|
| 22 | C | `499c0c6b72ac` | Require a complete number token for attr units. | Numeric attr units accept trailing attribute tokens or build the wrong numeric text instead of using the required fallback. Requires typed attr syntax and malformed/nontrivial numeric attribute text. The URL tests are controls; no security bypass is established. |
| 52 | C | `3aa7d25635ff` | Preserve attribute namespaces in substitution caches. | Typed attr() cache aliases equal local names from different namespaces, yielding the wrong attribute value. Namespaced attribute path; overlaps known bug 2021110; chained namespace support is not completed by this patch. |
| 53 | C | `fd9c07e1130b` | Preserve invalid attribute entries during substitution. | Reloading an explicitly invalid attribute resurrects a value that should stay invalid, changing fallback/cycle outcomes. Repeated invalid/chained typed attr() case; stack patch follows namespace repair. |
| 54 | B | `7822bb6d17b1` | Prepare typed attribute references in substitution fallbacks. | Typed attributes in fallback trees are not prepared, so otherwise valid fallback values fail in ordinary and custom declarations. Typed attr()/nested fallback usage; occurrence-specific eligibility is a separate fix; preparation cost unmeasured. |
| 56 | B | `e3ba54f6f826` | Visit typed attribute fallbacks when primary parsing fails. | A typed attribute present in the cache but failing this occurrence’s syntax incorrectly suppresses fallback dependencies. Typed attr() with a syntax mismatch and chained fallback; relies on earlier namespace/preparation stack repairs. |
| 57 | B | `3892ab844694` | Track property dependencies through attribute-only declarations. | Attribute-only normal declarations omit dependency edges, producing incorrect font/property cycle resolution. Requires attr() dependencies, often font-size or line-height cycles; separate metadata-loss fixes remain necessary. |
| 58 | B | `58200fa81a6f` | Preserve relative-unit dependencies in resolved custom property values. | Resolved attribute/universal values lose relative-unit dependencies, causing wrong cycle handling and computed values. Relative units through substitution chains; no claim that all dependency scheduling is proved. |
| 71 | B | `6aa2138c144a` | Use computed registered initial values when defaulting custom properties. | Defaulting a registered custom property inserts its raw initial tokens instead of its computed value, changing substitution and animation results. Computed registered initial values; supplemental animation diagnostic depends on #70 and is excluded from standalone WPT. |
| 72 | C | `3a01fc986c79` | Preserve guaranteed-invalid registered values during explicit inheritance. | Explicit inherit can replace a parent’s guaranteed-invalid registered value with the child’s registered initial value. Non-inheriting registration, invalid parent and explicit inherit; ordinary root initial behavior is retained. |
| 73 | B | `60bf34f48ac6` | Track reset-property inheritance after custom property substitution. | Substitution that yields inherit on a non-inheriting registered property omits the dependency flag, leaving stale child values after parent changes. Requires substituted CSS-wide inheritance; dynamic invalidation defect rather than a general map repair. |
| 74 | C | `0cac5c270615` | Exclude guaranteed-invalid custom properties from computed-style enumeration. | Computed-style custom-property length/item enumeration counts guaranteed-invalid entries as live properties. CSSOM enumeration observer; fixes count/filter, with iterator shadowing separately repaired by #75. |
| 75 | C | `90ffac0a5e40` | Skip shadowed ancestors when iterating custom properties. | Custom-property iteration exposes shadowed ancestor entries and duplicate/resurrected names. CSSOM enumeration; stack uses #74 support and the standalone alternative includes that prerequisite. |
| 76 | A | `e04d672a735e` | Preserve attribute taint when replacing equal custom-property values. | Attribute provenance affects URL restrictions. Prioritize security-boundary review. Only #80 has the recorded CSS-only release actual-request experiment; arbitrary-secret exfiltration is not established. |
| 77 | C | `8c04b6787e36` | Use half-open ranges when checking attribute-tainted URLs. | Inclusive interval comparison taints adjacent nonoverlapping URL text and incorrectly blocks clean URLs. Overblocking correction, not a demonstrated taint bypass; empty and touching interval cases matter. |
| 83 | A | `ad608a212bd8` | Normalize custom property whitespace before recording reference offsets | Demonstrated process crash; assess reachability and affected builds first. No memory-corruption or exploitability claim. |
| 130 | B | `e91224fd2e9e` | Prepare attributes for ordinary keyframe declarations. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 137 | C | `aa3f05885388` | Include used non-type attr fallbacks in dependency cycles. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 138 | C | `3c29fefb0548` | Keep nested raw attribute reads out of typed dependency cycles. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 139 | B | `0f40801f1418` | Compute registered CSS values without applying zoom twice. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 153 | B | `eb7c6fe81057` | Derive registered color dependencies from the selected syntax value. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 154 | B | `bc7defd8eefe` | Resolve registered image dependencies before computation. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 161 | A | `9afff49c042b` | Preserve explicit attribute taint during typed recascade. | Attribute provenance affects URL restrictions. Prioritize security-boundary review. Only #80 has the recorded CSS-only release actual-request experiment; arbitrary-secret exfiltration is not established. |
| 162 | A | `a6f39620516a` | Preserve attribute taint on selected attr fallbacks. | Attribute provenance affects URL restrictions. Prioritize security-boundary review. Only #80 has the recorded CSS-only release actual-request experiment; arbitrary-secret exfiltration is not established. |

## Layout, sizing and positioning

| ID | Priority | Commit | Fix | Impact / rationale |
|---|---|---|---|---|
| 24 | B | `7f5a1105253e` | Preserve out-of-range absolute positions in subgrids. | Absolutely positioned subgrid descendants can clamp an out-of-range line into the subgrid instead of preserving the intended auto/outside behavior. Requires subgrid and out-of-range absolute placement. Extreme UA limits and separate equal-endpoint issues are excluded. |
| 26 | B | `2a61f0b74336` | Apply grid stretch sizing only to automatic inline sizes. | Grid stretch incorrectly overrides non-auto intrinsic inline sizing of replaced elements, distorting dimensions/aspect ratios. Replaced grid items with intrinsic sizing and stretch; later clamp promotion remains outside the patch. |
| 29 | B | `98fd7a22a327` | Clamp negative minimum contributions from spanning table cells. | A spanning first-row table cell can contribute a negative minimum width when border spacing exceeds its apportioned size, under-sizing fixed-layout tables. Definite-length WPT coverage; percentage and residual-distribution behavior is unchanged. |
| 33 | B | `f67ddfaa3dc3` | Preserve auto inset state when resolving absolute-position margins. | Absolute-position auto margins lose the original auto-inset state and mishandle fixed-margin excess, shifting positioned content. Broad positioning relevance, but exact anchor-fallback providers and separate negative-containing-block defects remain outside this repair. |
| 34 | C | `e09ffb35c0b4` | Prevent margin collapse through blocks with resolved positive sizes. | A block whose nonmonotonic calc resolves to positive size can still be treated as empty, incorrectly collapsing margins through it. Requires calc expressions that evade endpoint emptiness tests; fragment consumption and whole layout emptiness remain outside the proof. |
| 39 | B | `e606244c4546` | Exclude fixed-positioned frames from scroll anchors. | A locally contained fixed-position element can become a scroll anchor, causing an inappropriate scroll adjustment when content changes. Requires a fixed element with a local containing block; a separate scroller-margin issue is unchanged. |
| 89 | C | `fdd7dcb11653` | Reserve the auto offset code for auto sticky insets | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 90 | B | `983931aa5fad` | Treat automatic sticky insets as zero when sizing the view rectangle | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 91 | B | `67bcf64fc28f` | Use the containing block writing mode for sticky end-inset reduction | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 92 | C | `d3c505adc9e9` | Use wide arithmetic and direct sticky range edges | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 93 | C | `71a523a4c526` | Use wide sums for flex baseline cross sizes | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 94 | C | `68686da75759` | Apply sticky position constraints only for specified insets | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 95 | C | `958e63a947e4` | Use wide saturated sums for flex line cross sizes | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 96 | B | `b4894d6329df` | Use normal flex item positions for exported baselines | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 97 | B | `9980b7b7a0fb` | Convert scroll-container last baselines through block-start coordinates | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 98 | B | `f5926c6dab50` | Include border and padding in flex item measurement cache keys | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 99 | B | `a6c78d950250` | Position flex overflow containers using the final fragment size | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 100 | B | `2b769488eef1` | Apply relative positioning to overflow continuations | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 101 | B | `6cf27eadddf9` | Include containing-block size in flex measurement cache keys | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 111 | B | `ee836eba6ca6` | Synthesize central baselines from the requested origin. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 122 | C | `8d0eb95794eb` | Saturate subgrid line-name counts and guard remaining capacity. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 127 | B | `f946a0921b8b` | Bug 2037744 - Resolve subgrid name-repeat counts during style computation. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 140 | B | `c13f212eb284` | Match page selector names when computing specificity. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |

## Text and fonts

| ID | Priority | Commit | Fix | Impact / rationale |
|---|---|---|---|---|
| 25 | B | `8e78ffd376c4` | Use Unicode final sigma context across text-transform boundaries. | Greek lowercase sigma uses the wrong contextual form across transformation/style partitions and Unicode case-ignorable context. Language-specific visible text correctness; whole cross-text-run behavior and all-platform reachability are outside the proof. Not a demonstrated password disclosure. |
| 40 | B | `c34843600365` | Reset text-overflow marker widths for each line. | text-overflow marker widths leak from one line to the next, corrupting ellipsis clipping/placement after a differently sized preceding line. Needs differing line geometry or mutation; separate vertical/float defects remain unchanged. |
| 41 | C | `eca9efde2991` | Ignore zero-width tabs when measuring intrinsic sizes. | tab-size: 0 produces invalid/incorrect intrinsic widths because tab-stop arithmetic still divides by zero. Explicit zero-width tabs in intrinsic sizing. Floating division-by-zero here is not evidence of a process crash or integer memory-safety issue. |
| 42 | C | `9da730d5ebd6` | Use the eleven-degree threshold for oblique font matching. | Oblique/italic fallback font selection uses the default oblique angle instead of the eleven-degree search threshold and chooses the wrong face. Most sensitive to available oblique faces around the threshold; local downloadable-face evidence does not establish system-font prevalence. |
| 44 | B | `9cca10125782` | Preserve width and style priority in fractional font matching. | Weighted scalar font-distance scores let lower-priority weight/style differences override a better fractional width/style match, selecting the wrong face. Touches shared and nonshared font matching/fallback, but reproduced with calibrated downloadable faces; platform and real-site incidence remain unmeasured. |
| 45 | C | `43afd2c6f350` | Avoid applying CSS zoom twice to root line-height units. | Root rlh units apply CSS zoom twice, yielding incorrect dimensions and values when root zoom changes. Requires CSS zoom on the root together with rlh. This is CSS zoom, not a demonstrated browser UI zoom/accessibility regression. |
| 47 | C | `bbf5a4095f85` | Allow text emphasis on private-use characters. | Private-use characters are wrongly excluded from text emphasis, leaving emphasis marks missing in custom-font text. Requires private-use text with emphasis; useful typography correctness but narrower feature intersection. No security implication established. |
| 48 | C | `8ee543a6ff23` | Keep partial ligature advances signed. | A negative ligature advance is converted through unsigned division, producing enormous positive partial advances and wrong measured text widths. Valid fonts can supply negative advances, but the retained WPT uses a specially constructed font. Arithmetic review warranted; no crash or memory-safety defect established. |
| 49 | C | `39ce7571a610` | Preserve supplementary scalars in UTF-16 complex line breaking. | Supplementary scalars are truncated in complex UTF-16 line breaking, producing wrong breaks for affected scripts. Narrow Ahom/complex-script trigger; known ICU4X PR8144 backport, not a new upstream finding. |
| 50 | B | `32ba35ffb9a1` | Rebuild worker font families after FontFaceSet removals. | Worker FontFaceSet deletion/clear leaves removed fonts usable for canvas text; stale membership changes rendering and metrics. Worker/OffscreenCanvas path; no crash or lifetime exploit demonstrated. |
| 51 | B | `18871240dc7d` | Compare hyphenation word boundaries in text-run coordinates. | Mixed absolute/relative word-boundary coordinates select incorrect hyphenation candidates and text measurements. Requires nonzero text-run offsets and hyphenation; font/language-dependent layout impact, not a demonstrated crash. |
| 55 | C | `f843fd7568f3` | Align MathML token leading whitespace for text measurements. | MathML token leading whitespace shifts Range/text measurement origins away from displayed text. MathML geometry/measurement case; does not claim all token sizing or whitespace behavior is repaired. |
| 61 | B | `6bd0b00dcff5` | Refresh loaded FontFace providers after descriptor changes. | Changing descriptors on loaded FontFace objects retains stale providers, affecting matching, size adjustment, metrics and shared peers. Known bug1072149 family; isolated macOS upstream runtime passed, but Windows/Android/Linux native backends still need build/runtime review. |
| 135 | C | `0d27cb839f01` | Recalculate contained quotes after appending a parent quote. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 136 | C | `37bc9b06f034` | Recalculate contained counters after appending a parent change. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 141 | B | `975e651729ba` | Resolve contextual leaves in numeric line-height computation. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 155 | B | `28bbc39fb8fe` | Honor nowrap suppression when publishing inline line breaks. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 156 | B | `2435535e6f09` | Preserve language context across line-break partitions. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 157 | B | `8870962db02b` | Apply hyphenation limits from the contributing text. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |

## CSSOM geometry and hidden layout

| ID | Priority | Commit | Fix | Impact / rationale |
|---|---|---|---|---|
| 102 | C | `c0e8c7fd1deb` | Preserve double precision in layout DOMRect coordinates | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 103 | C | `7309af28e360` | Preserve app-unit precision for untransformed client rectangles. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 104 | B | `29611cb584fd` | Preserve dirty children when hidden flex layout is skipped | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 105 | B | `f8104759d383` | Mark hidden absolute children dirty before reflow input initialization | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 106 | B | `29e2df85a4a9` | Refresh hidden column queries from dirty table providers. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 107 | B | `e6c73b637653` | Preserve query readiness for skipped block line children. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 108 | B | `a578671e967f` | Preserve query readiness for skipped grid children. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 109 | B | `8a5df95cf9d5` | Preserve query readiness for skipped float-owner subtrees. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 110 | B | `aaca499a3257` | Preserve query readiness for skipped MathML subtrees. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 112 | C | `b616622d2cd7` | Preserve integer precision in element offset, scroll, and client geometry. | Narrower syntax, exceptional arithmetic, extreme sizes or specific feature combinations; lower expected exposure. |
| 113 | B | `cc52e66ca64a` | Resolve skipped SVG viewport layout before matrix queries. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 114 | B | `53adf727ea05` | Refresh SVG length context before resolving and converting units. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |
| 116 | B | `9c2257a80e3f` | Refresh hidden embedding frames for SVG viewport lengths. | Observable rendering or API correctness with dynamic updates or ordinary-size cases. |

| 167 | B | `ed8bce6fa5d7` | Preserve stylesheet CSSOM state during state-preserving moves. | moveBefore replaces the associated sheet and loses CSSOM edits/disabled state. Local baseline and installed Nightly reproduce 17 failures; exact selected candidate passes all 31 assertions and retains eight shared-media controls. Five native files and seven WPT resources; moved-shadow-host cases needing #148 are omitted. Upstream needs the retained context adaptation; no isolated upstream build. |

## Excluded ongoing candidates

Producer-local animation handoff, repeated dependency draining and certified-path optimization: the optimized candidate compiled and completed164PASS/0FAIL against137PASS/27FAIL. The new running-transition case reached the actual endpoint and observed a stale dependent value in the original. Independent restoration audit passed. The combined comparison does not isolate each component, prove global convergence or attribute a release regression. #160 remains held for revision; no additional fix count is inferred. See the [updated comparison assessment](../css-root-font-certified-path-validation-assessment-v1/README.md).

Canvas substitution: confirmed but unfixed in installed Firefox158. The exact WPT baseline completed six expected var-rejection failures and three valid-math passes with harnessOK. Stored effects show changed pixels/text metrics; failing tests stop at the preceding getter assertion. This is testharness-in-browser evidence, not full wptrunner or a fresh-profile result. No security impact or latest-release prevalence is claimed. See the [browser baseline](../css-canvas-substitution-wpt-browser-v1/README.md).

Shared-media #166 and stylesheet-move #167 are now committed separately after fresh current-stack comparisons. Shared-media research precedes its repair in `1635894bbdde`; exact-file move validation precedes its repair in `b86cd38915d8`. See ../css-shared-sheet-media-current-20261110-v1/README.md and ../css-stylesheet-move-current-20261110-v1/README.md.

Security evidence: /Users/bgrins/code/firefox/artifacts/css-attr-taint-security-review-v1/REPORT.md.

## Additional committed library repair and current publication

`836b5a688284` preserves element alignment for empty ArcSlice allocations, with its Rust regression test in the same three-file commit. Research precedes it in `dfddd364baf6`. Miri, the in-crate test, scoped formatting and native build passed. No browser-reachable over-aligned caller was identified, so this is a separate generic-library repair and is not included in the 166 browser entries.

Cumulative rollback research precedes #163 in `407a423cb4e6b`. Same-rule rollback is now committed as #164, `0f18d294fbac`, with exactly two Rust files and three WPT changes. Its final supporting research immediately precedes it in `c1209aa91006`; earlier model/diagnostic milestones remain in the branch. It explicitly requires #163 and is not a standalone cherry-pick onto the retained pre-project ancestor. Arc and other branch repairs belong to the tested build context, not the five-file source patch.

The selected owner-map implementation retains all 190 prior correctness checks, six repeated-source checks and exact control signatures. Its original defect comparison was 162 PASS / 28 FAIL to 190 PASS; the additional cases are not additional bug counts. Fresh dense Rule256 is 25.27–25.80 microseconds/update against 10.43–10.94 baseline, while single-trigger256 is 8.61–9.00 against 8.44–8.85. These bounded local workloads do not establish release-page impact or performance acceptance. The twelve-theorem refinement removes a redundant table under explicit ownership/whole-block contracts; it does not prove all native memory behavior. See ../css-revert-rule-owner-map-dedup-assessment-v1/README.md and ../css-revert-rule-production-validation-v1/DECISION.md.

Signing resumed successfully on November 4. Earlier failed attempts remain historical records, not the current publication state. The repair-entry count does not claim 166 newly discovered upstream bugs, and #160 remains held.

Root identity (#165) is committed in `664b08bcb7ce`, preceded by retained evidence in `935c1e2916dc` and fresh validation in `acece22fa877`. See ../css-root-self-resume-20261110-v1/README.md. The local browser contains the tested native bytes; its build metadata predates the final commit.

The independent spec-derivation experiment is committed in `de2f6ccd1a1a`. It generates one CSS Syntax predicate from pinned Bikeshed source and proves agreement with an existing library relation. Independent clean replay passed, including rejection of a well-typed wrong branch. This is research, not a browser repair or a proof of arbitrary prose translation. See ../css-spec-derivation-investigation-20261110-v1/REPORT.md.

The derivation benchmark in `aadc64afe8b7` extends the separate source-linked experiment to two training predicates and one held-out consuming algorithm. Both training bridges check against pre-existing library relations; the frozen translator refuses consumption and generates no implementation. No browser bug is counted from this experiment. See ../css-spec-derivation-benchmark-20261110-v1/REPORT.md.

## November 10 query-handoff delivery

Fix 170 is a signed, three-file repair for existing bug 2085413. Source review,
independent review, native comparisons, the exact delivery fixture and its Lean
contract are committed separately before the repair. The handoff model has 37
laws, 25 observations and seven controls; its certified-path optimization proof
assumes a finite stable traversal subtree and does not prove native lifetime
safety or global animation convergence. See css-style-query-handoff-model-20261110-v1
and css-style-query-handoff-delivery-runtime-20261110-v1.

Animation-taint substitution remains one unfixed issue group, separate from 170.
Its policy-parametric model has 21 laws and explicitly leaves acquisition and
inheritance policy open. The independent number-parser extension is also signed,
with 212 audits including 30 new, 33 observations and ten controls. These research
results do not increase the browser repair count or establish whole-CSS coverage.

## November 10 clip composition delivery

Fix 171 is signed as `7382007a82b4`, preceded by research commit `302fe2b5ba00`.
The optimized build and complete independent comparison passed: exactly four
FAIL-to-PASS changes across 5,116 callback/harness rows. The frozen comparator's
first-Mochitest-callback key collision is documented; a corrected raw-log check
and four regression controls supply the complete acceptance gate. All nine new
WPT cases pass, all other statuses remain unchanged, and the final WPT lint passes.
The temporary candidate build and source were restored before the exact patch
was installed and committed. A subsequent committed-source build is separate
from that comparison; consult the current build receipt for manual testing.

The Lean guard-relocation model verifies a conditional compatibility argument;
source/spec investigation identified this known expected-failing behavior. It is
one additional repair entry, not four new bugs or a security finding. Debug,
sanitizer, direct native count-zero execution and isolated-upstream/release
validation remain unrun. See [acceptance](../css-clip-auto-acceptance-20261110-v1/README.md).

The independent CSS library is signed at `898fb45815c1`: opt-in derivation tooling
passed both library builds, installed/source-only checks and unchanged static
coverage registration. This tooling adds no CSS feature-coverage claim.

## November 10 percentage keyframe grouping delivery

Fix 172 is signed as `883d620fdbd6`, immediately preceded by runtime research
`3d55e8e0d364` and earlier contract/proof/candidate research `a4ead1512165`.
The real optimized build, WPT lint, exact 95-record comparison and independent
full restoration passed. Exactly two assertions improve; all other statuses and
messages match. The Lean model proves the generic reverse-fold/rotation order
under explicit key/invariant assumptions; it does not prove native declaration
semantics, pointer lifetimes or specification interpretation. This is a known
issue repair, not two newly discovered bugs. Debug, performance benchmarks and
isolated-upstream/release validation are not claimed.

The standalone library is now signed at `56c09405cd45`, integrating generic
document profiles and selected alias semantics with unchanged existing APIs.
Independent source replay, actual default/opt-in builds and 25 installed JSON-file
rows pass. This integration adds no normative CSS feature coverage. The earlier
first-order integration checkpoint remains historical evidence.
