# CSS and Stylo branch work

At signed native HEAD `8870962db02b006791085b73f9e270942e145365`: **156 committed native fixes** — 149 historical entries plus seven signed publications. Held ID 120 remains excluded. The newest is **ID 157: hyphenation limit ownership across inline text**.

| Signed publication | ID | Commit |
|---|---:|---|
| min()/max() with contextual infinities | 151 | `bc0853a77a445de27e6c5ba1653c60f077a5a7f4` |
| log() exceptional values | 152 | `bf9b4d1a12ee559e98cf464689c5c327ac2e4f6d` |
| Registered color-scheme dependencies | 153 | `eb7c6fe8105700d7e1df5e6419c59df64fcdd493` |
| Registered image font dependencies | 154 | `bc7defd8eefec531c1e57e1866b77fb04d637724` |
| Honor nowrap suppression when publishing inline line breaks | 155 | `28bbc39fb8fec210ff9ee9880eeedc77be3f6d52` |
| Preserve language context across line-break partitions | 156 | `2435535e6f09be35da5c5cd3d0afac7d0dd60d6d` |
| Preserve hyphenation limit ownership across inline text | 157 | `8870962db02b006791085b73f9e270942e145365` |

Actual native terminal: 39180 / 8a137d / 069c6b / exit 0. The [verified six-file receipt](../css-hyphenation-ownership-publication-ownership-runtime-2/COMMIT-RESULT.json) joins signed research parent `f0578910f9287dde3742e34086278b27d27c7b0b`. Root's independent postcheck authenticated all six source/test postimages and clean tracked/staged state.

The hyphenation pair improves 54 callbacks for one scoped fix: 843 PASS/54 FAIL becomes 897 PASS/zero FAIL, with 23 endings per role. All 289 ownership targets pass; the 608 other callbacks and endings are preserved using the existing narrowly authenticated four-reftest port correction. Raw evidence remains archived. The signed commit contains exactly three source files and three unchanged adopted WPTs. Dynamic and pseudo tests are preservation controls. Source review and the formal companion do not prove all native hyphenation behavior.

| Remaining work | Evidence and next boundary |
|---|---|
| Hyphenation publication | Completed as ID 157. Installed WPT lint has zero errors and a genuine three-page manifest. The app was not rebuilt during publication. |
| Font-metric readiness | Published-native 13-case matrix remains 3 PASS/10 FAIL. Retained provider/synthesis research and a strict Cargo-result assessor are prepared; actual Stylo typechecking and full metric repair remain pending. The parser's three positive/twenty negative saved checks are not a compilation result. |
| Selected declarations and fallback timing | Appearance worsening and two portable typed-attr PASS-to-FAIL regressions remain unresolved; unused fallback-unit timing remains inconclusive. |
| Untracked WPTs | The November 2 audit found 50 archived working copies. Root removed two superseded syntax variants, leaving 48 before publication. The signed adoption of the three hyphenation tests leaves 45: 24 broader completed-associated, 12 pending, 8 unresolved and one control. Root independently checked the exact remaining 45 WPT paths and 555 total untracked paths after signing. These are file counts, not bug counts. |

The prior 149 historical entries and six publication records remain unchanged; only ID 157 is appended. The canonical historical accepted ledger remains 149; publication drivers increment it by zero. No incomplete metric candidate is counted. Root's two-file cleanup preserved committed recovery copies and the landed combined test. No unrelated content was read by this readout author.

## Previously catalogued fixes by area

### Selectors, Bloom filters and scoping

| ID | Fix | Commit |
|---:|---|---|
| 1 | Account for prior saturation when clearing StyleBloom. | `d855b3483b49` |
| 2 | Build relative-selector Bloom filters with an iterative traversal. | `93a062cded54` |
| 5 | Order nested scope roots by proximity. | `075be5516374` |
| 6 | Match scope-end selectors when reaching a shadow host. | `a46e5310cd60` |
| 7 | Exclude scope roots from scope-limit matching. | `78c11c75170a` |
| 8 | Include the scope element in relative selector cache keys. | `d4a2b600f078` |
| 9 | Include the scope element in filtered nth-index cache keys. | `92c013c16908` |
| 10 | Follow relative dependencies when invalidating scope limits. | `64ac54569f1c` |
| 11 | Propagate filtered nth invalidation from relative anchors. | `b1b1bacb9406` |
| 12 | Avoid style sharing for scope-dependent nth filters. | `f4b34bf7fef1` |
| 146 | Avoid caching reset styles that depend on sibling-count(). | `7501711ae4a1` |
| 147 | Invalidate old-parent styles during moveBefore(). | `ebb5d4fc489e` |

### Cascade, layers and shorthands

| ID | Fix | Commit |
|---:|---|---|
| 3 | Exclude false-supports imports from effective rule iteration. | `5d3638a91adf` |
| 4 | Sort important user and UA rules by cascade priority. | `e28cb48d656b` |
| 16 | Preserve shorthand source identity when reusing substituted values. | `11482ee213bf` |
| 23 | Order physical shorthands before logical shorthands of equal size. | `e27beeac5129` |
| 38 | Recompute nesting specificity from expanded selector components. | `c57d0c806d94` |
| 69 | Preserve logical-group order when setting the all shorthand. | `074086719e44` |

### Parsing, tokens and CSS math

| ID | Fix | Commit |
|---:|---|---|
| 13 | Preserve zero signs when simplifying round with infinite steps. | `708b914901ee` |
| 20 | Preserve NaN operands when simplifying clamp. | `a4fe7dd06fd7` |
| 21 | Preserve finite dividends for valid infinite mod and rem divisors. | `bfbce1cc7e9a` |
| 35 | Preserve escaped delimiters during bad URL recovery. | `83bc2bd39226` |
| 59 | Only classify dimension tokens as relative-unit dependencies. | `26e0fa16e89e` |
| 60 | Reject escaped newlines after leading hyphens in CSS identifiers. | `09b008b3320f` |
| 62 | Preserve CSS numbers with compensating exponents. | `4391deb4751a` |
| 63 | Keep fallback endpoints aligned with quoted EOF recovery. | `2d658a9c5aa4` |
| 64 | Preserve paired backslashes at quoted EOF. | `89bad2d8b526` |
| 65 | Recognize escaped terminal quotes during EOF recovery. | `ed9505d25ee4` |
| 66 | Consume rejected blocks at the CSS parser nesting limit. | `55d251b7a900` |
| 67 | Validate the whole declaration value before substitution fallback. | `095c5be548a2` |
| 68 | Clear ordinary declarations before substitution fallback. | `780495d90a85` |
| 81 | Preserve registered custom property token boundaries | `34e4e755cb81` |
| 84 | Keep custom property token metadata aligned with trailing whitespace trimming | `bccea9c1fffc` |
| 85 | Preserve escaped whitespace in custom property token values | `fff2d758ef6b` |
| 86 | Preserve newlines after backslash delimiters in custom properties | `246f1ff43250` |
| 117 | Preserve the reserved counter value through computed integer math. | `33ae2e8349e9` |
| 118 | Round computed CSS integers after promoting the half-unit addition. | `d68543e601c4` |
| 119 | Preserve nonfinite relative lengths inside CSS math. | `6a363fc372c9` |
| 121 | Apply stored integer ranges when resolving CSS math. | `b218397700bd` |
| 123 | Resolve calculated counter range bounds when exporting membership. | `0f68c5c1a7a5` |
| 124 | Compare and export additive counter weights by resolved nonnegative value. | `656b54ea29ef` |
| 125 | Propagate NaN before resolving round() infinity cases. | `a9b7886a5f47` |
| 126 | Preserve negative zero in finite round() upper bounds. | `4c4ff0d440cd` |
| 128 | Preserve finite mod() and rem() remainders. | `10b6eabed271` |
| 142 | Preserve random cache indices across rejected CSS parses. | `25e423a1a810` |
| 144 | Defer infinite-step rounding until the value is resolved. | `c63be5163f2e` |
| 145 | Preserve finite multiples when resolving round(). | `eb5208648811` |
| 149 | Avoid intermediate overflow and underflow in hypot(). | `36b693fee75e` |
| 150 | Handle CSS pow exceptional values consistently in calculation and simplification. | `2d18f8b4a4d7` |

### Attributes and custom properties

| ID | Fix | Commit |
|---:|---|---|
| 22 | Require a complete number token for attr units. | `499c0c6b72ac` |
| 52 | Preserve attribute namespaces in substitution caches. | `3aa7d25635ff` |
| 53 | Preserve invalid attribute entries during substitution. | `fd9c07e1130b` |
| 54 | Prepare typed attribute references in substitution fallbacks. | `7822bb6d17b1` |
| 56 | Visit typed attribute fallbacks when primary parsing fails. | `e3ba54f6f826` |
| 57 | Track property dependencies through attribute-only declarations. | `3892ab844694` |
| 58 | Preserve relative-unit dependencies in resolved custom property values. | `58200fa81a6f` |
| 71 | Use computed registered initial values when defaulting custom properties. | `6aa2138c144a` |
| 72 | Preserve guaranteed-invalid registered values during explicit inheritance. | `3a01fc986c79` |
| 73 | Track reset-property inheritance after custom property substitution. | `60bf34f48ac6` |
| 74 | Exclude guaranteed-invalid custom properties from computed-style enumeration. | `0cac5c270615` |
| 75 | Skip shadowed ancestors when iterating custom properties. | `90ffac0a5e40` |
| 76 | Preserve attribute taint when replacing equal custom-property values. | `e04d672a735e` |
| 77 | Use half-open ranges when checking attribute-tainted URLs. | `8c04b6787e36` |
| 83 | Normalize custom property whitespace before recording reference offsets | `ad608a212bd8` |
| 130 | Prepare attributes for ordinary keyframe declarations. | `e91224fd2e9e` |
| 137 | Include used non-type attr fallbacks in dependency cycles. | `aa3f05885388` |
| 138 | Keep nested raw attribute reads out of typed dependency cycles. | `3c29fefb0548` |
| 139 | Compute registered CSS values without applying zoom twice. | `0f40801f1418` |

### Animations, timelines and transitions

| ID | Fix | Commit |
|---:|---|---|
| 15 | Keep animation iteration identity separate from accumulation counts. | `0a81e1f36ab0` |
| 19 | Preserve deferred transform operations during composition. | `c92749721241` |
| 43 | Resolve scroll timeline axes from the scrolling frame. | `0af700c67a5a` |
| 46 | Include composition when comparing keyframes. | `6b8dc654e8d0` |
| 70 | Interpolate registered keyframes using substituted computed values. | `188644f6d983` |
| 78 | Preserve attribute taint when replacing animation endpoints | `4b4a00e70758` |
| 79 | Restyle animations when underlying attribute taint changes | `2c09cb2e4ff8` |
| 80 | Preserve attribute taint from both interpolated custom values | `ede7ceb101d8` |
| 82 | Preserve guaranteed-invalid animated custom properties | `d63735091bf8` |
| 87 | Deduplicate initial view-transition types | `2db943802038` |
| 88 | Restyle after active view-transition type changes | `c67505af9aae` |
| 129 | Recompute keyframe values after CSS animation reactivation. | `d13af8f7e9fd` |
| 131 | Recompute active keyframe values after attribute changes. | `65355573964a` |
| 132 | Refresh contributing keyframes before commitStyles. | `d477d0c33105` |
| 133 | Clamp calculated jump-none step counts at computation. | `e414c8f7cfcd` |
| 134 | Clamp calculated cubic-bezier x coordinates at computation. | `70cc9c30ef44` |
| 143 | Check both linear easing stop positions before conversion. | `22f97187e9f0` |
| 148 | Preserve move context through shadow-root traversal. | `9e99cf9e4c88` |

### Text and fonts

| ID | Fix | Commit |
|---:|---|---|
| 25 | Use Unicode final sigma context across text-transform boundaries. | `8e78ffd376c4` |
| 40 | Reset text-overflow marker widths for each line. | `c34843600365` |
| 41 | Ignore zero-width tabs when measuring intrinsic sizes. | `eca9efde2991` |
| 42 | Use the eleven-degree threshold for oblique font matching. | `9da730d5ebd6` |
| 44 | Preserve width and style priority in fractional font matching. | `9cca10125782` |
| 45 | Avoid applying CSS zoom twice to root line-height units. | `43afd2c6f350` |
| 47 | Allow text emphasis on private-use characters. | `bbf5a4095f85` |
| 48 | Keep partial ligature advances signed. | `8ee543a6ff23` |
| 49 | Preserve supplementary scalars in UTF-16 complex line breaking. | `39ce7571a610` |
| 50 | Rebuild worker font families after FontFaceSet removals. | `32ba35ffb9a1` |
| 51 | Compare hyphenation word boundaries in text-run coordinates. | `18871240dc7d` |
| 55 | Align MathML token leading whitespace for text measurements. | `f843fd7568f3` |
| 61 | Refresh loaded FontFace providers after descriptor changes. | `6bd0b00dcff5` |
| 135 | Recalculate contained quotes after appending a parent quote. | `0d27cb839f01` |
| 136 | Recalculate contained counters after appending a parent change. | `37bc9b06f034` |
| 141 | Resolve contextual leaves in numeric line-height computation. | `975e651729ba` |

### Layout, sizing and positioning

| ID | Fix | Commit |
|---:|---|---|
| 24 | Preserve out-of-range absolute positions in subgrids. | `7f5a1105253e` |
| 26 | Apply grid stretch sizing only to automatic inline sizes. | `2a61f0b74336` |
| 29 | Clamp negative minimum contributions from spanning table cells. | `98fd7a22a327` |
| 33 | Preserve auto inset state when resolving absolute-position margins. | `f67ddfaa3dc3` |
| 34 | Prevent margin collapse through blocks with resolved positive sizes. | `e09ffb35c0b4` |
| 39 | Exclude fixed-positioned frames from scroll anchors. | `e606244c4546` |
| 89 | Reserve the auto offset code for auto sticky insets | `fdd7dcb11653` |
| 90 | Treat automatic sticky insets as zero when sizing the view rectangle | `983931aa5fad` |
| 91 | Use the containing block writing mode for sticky end-inset reduction | `67bcf64fc28f` |
| 92 | Use wide arithmetic and direct sticky range edges | `d3c505adc9e9` |
| 93 | Use wide sums for flex baseline cross sizes | `71a523a4c526` |
| 94 | Apply sticky position constraints only for specified insets | `68686da75759` |
| 95 | Use wide saturated sums for flex line cross sizes | `958e63a947e4` |
| 96 | Use normal flex item positions for exported baselines | `b4894d6329df` |
| 97 | Convert scroll-container last baselines through block-start coordinates | `9980b7b7a0fb` |
| 98 | Include border and padding in flex item measurement cache keys | `f5926c6dab50` |
| 99 | Position flex overflow containers using the final fragment size | `a6c78d950250` |
| 100 | Apply relative positioning to overflow continuations | `2b769488eef1` |
| 101 | Include containing-block size in flex measurement cache keys | `6cf27eadddf9` |
| 111 | Synthesize central baselines from the requested origin. | `ee836eba6ca6` |
| 122 | Saturate subgrid line-name counts and guard remaining capacity. | `8d0eb95794eb` |
| 127 | Bug 2037744 - Resolve subgrid name-repeat counts during style computation. | `f946a0921b8b` |
| 140 | Match page selector names when computing specificity. | `c13f212eb284` |

### Container queries

| ID | Fix | Commit |
|---:|---|---|
| 14 | Track dependencies for name-only container queries. | `238710ff9db7` |
| 27 | Track attribute references through container-query operators. | `16ff45a117b1` |
| 28 | Invalidate container queries when content-box size changes. | `ef3d32280505` |

### Colors, images, SVG and shapes

| ID | Fix | Commit |
|---:|---|---|
| 17 | Preserve analogous missing components across RGB and XYZ color conversion. | `82b254686378` |
| 18 | Preserve zero-weight prefixes during normalized color mixing. | `591b3e125678` |
| 30 | Avoid overflow when computing polygon shape intercepts. | `06be3d7e722c` |
| 31 | Use the border box for stroke-box transforms on CSS boxes. | `96e0ad8c6a0a` |
| 32 | Honor object-fit with partial intrinsic dimensions. | `66fb24648a15` |
| 36 | Compose empty SVG mask regions as transparent black. | `065183ac8449` |
| 37 | Compose zero-sized mask images as transparent black. | `6bb2557507bc` |
| 115 | Correct SVG quarter-millimeter conversion factors. | `fa9dff982cec` |

### CSSOM geometry and hidden layout

| ID | Fix | Commit |
|---:|---|---|
| 102 | Preserve double precision in layout DOMRect coordinates | `c0e8c7fd1deb` |
| 103 | Preserve app-unit precision for untransformed client rectangles. | `7309af28e360` |
| 104 | Preserve dirty children when hidden flex layout is skipped | `29611cb584fd` |
| 105 | Mark hidden absolute children dirty before reflow input initialization | `f8104759d383` |
| 106 | Refresh hidden column queries from dirty table providers. | `29e2df85a4a9` |
| 107 | Preserve query readiness for skipped block line children. | `e6c73b637653` |
| 108 | Preserve query readiness for skipped grid children. | `a578671e967f` |
| 109 | Preserve query readiness for skipped float-owner subtrees. | `8a5df95cf9d5` |
| 110 | Preserve query readiness for skipped MathML subtrees. | `aaca499a3257` |
| 112 | Preserve integer precision in element offset, scroll, and client geometry. | `b616622d2cd7` |
| 113 | Resolve skipped SVG viewport layout before matrix queries. | `cc52e66ca64a` |
| 114 | Refresh SVG length context before resolving and converting units. | `53adf727ea05` |
| 116 | Refresh hidden embedding frames for SVG viewport lengths. | `9c2257a80e3f` |
