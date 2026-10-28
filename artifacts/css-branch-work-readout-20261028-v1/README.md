# CSS/Stylo branch work — 28 October 2026

**140 accepted native fixes are committed locally**, plus **2 test-only repairs**. Numbered IDs run through 141; held fix 120 is excluded. Snapshot HEAD: `fd4b301f80b0aaed9f198a978f00ab2e99300147`. Every listed native commit and recorded evidence/test-only commit was verified as an ancestor of this HEAD.

This is a current readout, not a concatenation of historical checkpoints. Separate fix commits do not imply arbitrary clean-upstream cherry-pick independence: per-fix prerequisites and validation limits remain in the [source ledger](../stylo-bloom-tools/CURRENT-COMMITS.json). No severity or security ranking is assigned. These are local fix counts, not a count of filed Bugzilla reports.

| Area | Accepted native fixes |
|---|---:|
| Selectors, Bloom filters and scoping | 11 |
| Cascade, layers and shorthands | 6 |
| Parsing, tokens and CSS math | 26 |
| Attributes and custom properties | 19 |
| Animations, timelines and transitions | 16 |
| Text and fonts | 16 |
| Layout, sizing and positioning | 22 |
| Container queries | 3 |
| Colors, images, SVG and shapes | 8 |
| CSSOM geometry and hidden layout | 13 |
| **Total** | **140** |

The older grouped readout supplies 138 accepted fixes; page-selector fix 140 adds one to selectors/scoping, and contextual line-height fix 141 adds one to text/fonts. Fix 132 is joined by identity, not queue position.

## All accepted native fixes

Subjects below come from the actual commit (reviewer suffix and “No bug” prefix omitted for readability). [fixes.json](fixes.json) retains full subjects, hashes, all recorded evidence commits, ancestry results and source pins. “Not recorded” means the older ledger has no separate research commit; it does not mean no research happened.

### Selectors, Bloom filters and scoping

| ID | Commit subject | Native/WPT | Research/evidence |
|---:|---|---|---|
| 1 | Account for prior saturation when clearing StyleBloom | `d855b3483b49` | Not recorded |
| 2 | Build relative-selector Bloom filters with an iterative traversal | `93a062cded54` | Not recorded |
| 5 | Order nested scope roots by proximity | `075be5516374` | Not recorded |
| 6 | Match scope-end selectors when reaching a shadow host | `a46e5310cd60` | Not recorded |
| 7 | Exclude scope roots from scope-limit matching | `78c11c75170a` | Not recorded |
| 8 | Include the scope element in relative selector cache keys | `d4a2b600f078` | Not recorded |
| 9 | Include the scope element in filtered nth-index cache keys | `92c013c16908` | Not recorded |
| 10 | Follow relative dependencies when invalidating scope limits | `64ac54569f1c` | Not recorded |
| 11 | Propagate filtered nth invalidation from relative anchors | `b1b1bacb9406` | Not recorded |
| 12 | Avoid style sharing for scope-dependent nth filters | `f4b34bf7fef1` | Not recorded |
| 140 | Match page selector names when computing specificity | `c13f212eb284` | `e4ba214e3286` |

### Cascade, layers and shorthands

| ID | Commit subject | Native/WPT | Research/evidence |
|---:|---|---|---|
| 3 | Exclude false-supports imports from effective rule iteration | `5d3638a91adf` | Not recorded |
| 4 | Sort important user and UA rules by cascade priority | `e28cb48d656b` | Not recorded |
| 16 | Preserve shorthand source identity when reusing substituted values | `11482ee213bf` | Not recorded |
| 23 | Order physical shorthands before logical shorthands of equal size | `e27beeac5129` | `f5b175e01f21` |
| 38 | Recompute nesting specificity from expanded selector components | `c57d0c806d94` | `ab6513e805c7` |
| 69 | Preserve logical-group order when setting the all shorthand | `074086719e44` | `bad8f7998dbb` |

### Parsing, tokens and CSS math

| ID | Commit subject | Native/WPT | Research/evidence |
|---:|---|---|---|
| 13 | Preserve zero signs when simplifying round with infinite steps | `708b914901ee` | Not recorded |
| 20 | Preserve NaN operands when simplifying clamp | `a4fe7dd06fd7` | `7b2f125756a2` |
| 21 | Preserve finite dividends for valid infinite mod and rem divisors | `bfbce1cc7e9a` | `033c4ac60d39` |
| 35 | Preserve escaped delimiters during bad URL recovery | `83bc2bd39226` | `366b0542b559` |
| 59 | Only classify dimension tokens as relative-unit dependencies | `26e0fa16e89e` | `2e1f5f62c8a6` |
| 60 | Reject escaped newlines after leading hyphens in CSS identifiers | `09b008b3320f` | `b69763a1817a` +1 linked in JSON |
| 62 | Preserve CSS numbers with compensating exponents | `4391deb4751a` | `ddb1799ad54e` |
| 63 | Keep fallback endpoints aligned with quoted EOF recovery | `2d658a9c5aa4` | `5faa99644ddc` |
| 64 | Preserve paired backslashes at quoted EOF | `89bad2d8b526` | `5e0f8696a8de` |
| 65 | Recognize escaped terminal quotes during EOF recovery | `ed9505d25ee4` | `1b9022a98dc3` |
| 66 | Consume rejected blocks at the CSS parser nesting limit | `55d251b7a900` | `19ca0c3c68c2` |
| 67 | Validate the whole declaration value before substitution fallback | `095c5be548a2` | `320a3d100d76` |
| 68 | Clear ordinary declarations before substitution fallback | `780495d90a85` | `53e30d418ef7` |
| 81 | Preserve registered custom property token boundaries | `34e4e755cb81` | `76d470797453` |
| 84 | Keep custom property token metadata aligned with trailing whitespace trimming | `bccea9c1fffc` | `35c04a321697` |
| 85 | Preserve escaped whitespace in custom property token values | `fff2d758ef6b` | `3029d557014c` |
| 86 | Preserve newlines after backslash delimiters in custom properties | `246f1ff43250` | `45721455b1e4` |
| 117 | Preserve the reserved counter value through computed integer math | `33ae2e8349e9` | `2f1085d3c8ee` |
| 118 | Round computed CSS integers after promoting the half-unit addition | `d68543e601c4` | `1690a8cd5886` |
| 119 | Preserve nonfinite relative lengths inside CSS math | `6a363fc372c9` | `49862ae74751` |
| 121 | Apply stored integer ranges when resolving CSS math | `b218397700bd` | `3b1fc453848b` |
| 123 | Resolve calculated counter range bounds when exporting membership | `0f68c5c1a7a5` | `53989ac9bd08` +1 linked in JSON |
| 124 | Compare and export additive counter weights by resolved nonnegative value | `656b54ea29ef` | `b4592416a12e` +1 linked in JSON |
| 125 | Propagate NaN before resolving round() infinity cases | `a9b7886a5f47` | `f8b9a6bc48b8` |
| 126 | Preserve negative zero in finite round() upper bounds | `4c4ff0d440cd` | `0b3d341c8367` |
| 128 | Preserve finite mod() and rem() remainders | `10b6eabed271` | `3d889a609235` |

### Attributes and custom properties

| ID | Commit subject | Native/WPT | Research/evidence |
|---:|---|---|---|
| 22 | Require a complete number token for attr units | `499c0c6b72ac` | `607a4fcfbab3` |
| 52 | Preserve attribute namespaces in substitution caches | `3aa7d25635ff` | `adde61d9742f` |
| 53 | Preserve invalid attribute entries during substitution | `fd9c07e1130b` | `76bda27b8dfd` |
| 54 | Prepare typed attribute references in substitution fallbacks | `7822bb6d17b1` | `31265260cc3d` +1 linked in JSON |
| 56 | Visit typed attribute fallbacks when primary parsing fails | `e3ba54f6f826` | `30c8dfeb4b74` +1 linked in JSON |
| 57 | Track property dependencies through attribute-only declarations | `3892ab844694` | `0db19774e6f2` |
| 58 | Preserve relative-unit dependencies in resolved custom property values | `58200fa81a6f` | `03bad7f70832` +2 linked in JSON |
| 71 | Use computed registered initial values when defaulting custom properties | `6aa2138c144a` | `3d194d59545c` |
| 72 | Preserve guaranteed-invalid registered values during explicit inheritance | `3a01fc986c79` | `2e0f9f6b9ee5` |
| 73 | Track reset-property inheritance after custom property substitution | `60bf34f48ac6` | `1ad6ea9740aa` |
| 74 | Exclude guaranteed-invalid custom properties from computed-style enumeration | `0cac5c270615` | `d9d1047dd4b1` |
| 75 | Skip shadowed ancestors when iterating custom properties | `90ffac0a5e40` | `215c881ef243` |
| 76 | Preserve attribute taint when replacing equal custom-property values | `e04d672a735e` | `01c98e4fd49e` +2 linked in JSON |
| 77 | Use half-open ranges when checking attribute-tainted URLs | `8c04b6787e36` | `91e709f931ab` |
| 83 | Normalize custom property whitespace before recording reference offsets | `ad608a212bd8` | `1d4940ff2211` |
| 130 | Prepare attributes for ordinary keyframe declarations | `e91224fd2e9e` | `e40adf1616f3` |
| 137 | Include used non-type attr fallbacks in dependency cycles | `aa3f05885388` | `38c1b6093c7b` |
| 138 | Keep nested raw attribute reads out of typed dependency cycles | `3c29fefb0548` | `3e9f8cff13ec` |
| 139 | Compute registered CSS values without applying zoom twice | `0f40801f1418` | `66cd18c62e7b` |

### Animations, timelines and transitions

| ID | Commit subject | Native/WPT | Research/evidence |
|---:|---|---|---|
| 15 | Keep animation iteration identity separate from accumulation counts | `0a81e1f36ab0` | Not recorded |
| 19 | Preserve deferred transform operations during composition | `c92749721241` | `4c401192c6ae` |
| 43 | Resolve scroll timeline axes from the scrolling frame | `0af700c67a5a` | `5388c30dc8ec` |
| 46 | Include composition when comparing keyframes | `6b8dc654e8d0` | `7ee385b8404b` |
| 70 | Interpolate registered keyframes using substituted computed values | `188644f6d983` | `1cf91c4def90` |
| 78 | Preserve attribute taint when replacing animation endpoints | `4b4a00e70758` | `922272780824` |
| 79 | Restyle animations when underlying attribute taint changes | `2c09cb2e4ff8` | `91d47c020cb9` |
| 80 | Preserve attribute taint from both interpolated custom values | `ede7ceb101d8` | `a9b8e799ce97` |
| 82 | Preserve guaranteed-invalid animated custom properties | `d63735091bf8` | `5e540197f9af` |
| 87 | Deduplicate initial view-transition types | `2db943802038` | `baa7f955bacd` |
| 88 | Restyle after active view-transition type changes | `c67505af9aae` | `85ed2f301cf0` +1 linked in JSON |
| 129 | Recompute keyframe values after CSS animation reactivation | `d13af8f7e9fd` | `7626b6ca8866` |
| 131 | Recompute active keyframe values after attribute changes | `65355573964a` | `e9b759281bca` |
| 132 | Refresh contributing keyframes before commitStyles | `d477d0c33105` | `ca65cf6d142d` |
| 133 | Clamp calculated jump-none step counts at computation | `e414c8f7cfcd` | `be4240e9d1cc` |
| 134 | Clamp calculated cubic-bezier x coordinates at computation | `70cc9c30ef44` | `906c05d72653` |

### Text and fonts

| ID | Commit subject | Native/WPT | Research/evidence |
|---:|---|---|---|
| 25 | Use Unicode final sigma context across text-transform boundaries | `8e78ffd376c4` | `5dc0849a15e8` |
| 40 | Reset text-overflow marker widths for each line | `c34843600365` | `e32b6ba35b6e` |
| 41 | Ignore zero-width tabs when measuring intrinsic sizes | `eca9efde2991` | `ba9ebc9d81b7` |
| 42 | Use the eleven-degree threshold for oblique font matching | `9da730d5ebd6` | `153b0e8d9bf3` |
| 44 | Preserve width and style priority in fractional font matching | `9cca10125782` | `0cafb3375954` |
| 45 | Avoid applying CSS zoom twice to root line-height units | `43afd2c6f350` | `635b8995326d` |
| 47 | Allow text emphasis on private-use characters | `bbf5a4095f85` | `75401fe29831` |
| 48 | Keep partial ligature advances signed | `8ee543a6ff23` | `3f61a60e15b3` |
| 49 | Preserve supplementary scalars in UTF-16 complex line breaking | `39ce7571a610` | `28d9e8cc1065` |
| 50 | Rebuild worker font families after FontFaceSet removals | `32ba35ffb9a1` | `07dc1d273432` |
| 51 | Compare hyphenation word boundaries in text-run coordinates | `18871240dc7d` | `a1eed2e249ae` |
| 55 | Align MathML token leading whitespace for text measurements | `f843fd7568f3` | `6eb5a90e3fa3` +1 linked in JSON |
| 61 | Refresh loaded FontFace providers after descriptor changes | `6bd0b00dcff5` | `ae298df56390` |
| 135 | Recalculate contained quotes after appending a parent quote | `0d27cb839f01` | `d2e8f520eb1f` |
| 136 | Recalculate contained counters after appending a parent change | `37bc9b06f034` | `7cc4b9b3f524` |
| 141 | Resolve contextual leaves in numeric line-height computation | `975e651729ba` | `d0bc4ce02cba` +1 linked in JSON |

### Layout, sizing and positioning

| ID | Commit subject | Native/WPT | Research/evidence |
|---:|---|---|---|
| 24 | Preserve out-of-range absolute positions in subgrids | `7f5a1105253e` | `739139c30e53` |
| 26 | Apply grid stretch sizing only to automatic inline sizes | `2a61f0b74336` | `4a696e8c980f` |
| 29 | Clamp negative minimum contributions from spanning table cells | `98fd7a22a327` | `799efd5a456f` |
| 33 | Preserve auto inset state when resolving absolute-position margins | `f67ddfaa3dc3` | `1c9e80b2228a` |
| 34 | Prevent margin collapse through blocks with resolved positive sizes | `e09ffb35c0b4` | `8621e83c9142` |
| 39 | Exclude fixed-positioned frames from scroll anchors | `e606244c4546` | `e0494649157d` |
| 89 | Reserve the auto offset code for auto sticky insets | `fdd7dcb11653` | `de1fa6e8539a` +1 linked in JSON |
| 90 | Treat automatic sticky insets as zero when sizing the view rectangle | `983931aa5fad` | `402fc4d824b0` +3 linked in JSON |
| 91 | Use the containing block writing mode for sticky end-inset reduction | `67bcf64fc28f` | `05b8cda1a77c` |
| 92 | Use wide arithmetic and direct sticky range edges | `d3c505adc9e9` | `b0d56f61ff11` +2 linked in JSON |
| 93 | Use wide sums for flex baseline cross sizes | `71a523a4c526` | `edd86929946a` +2 linked in JSON |
| 94 | Apply sticky position constraints only for specified insets | `68686da75759` | `8ce52f459152` +2 linked in JSON |
| 95 | Use wide saturated sums for flex line cross sizes | `958e63a947e4` | `5c3d2e1ec59a` +1 linked in JSON |
| 96 | Use normal flex item positions for exported baselines | `b4894d6329df` | `2ba42b38c655` +2 linked in JSON |
| 97 | Convert scroll-container last baselines through block-start coordinates | `9980b7b7a0fb` | `2dc0fa3aa371` +2 linked in JSON |
| 98 | Include border and padding in flex item measurement cache keys | `f5926c6dab50` | `55ca79bc149d` +1 linked in JSON |
| 99 | Position flex overflow containers using the final fragment size | `a6c78d950250` | `052dc13ae43d` +1 linked in JSON |
| 100 | Apply relative positioning to overflow continuations | `2b769488eef1` | `dcdf5a89d358` +1 linked in JSON |
| 101 | Include containing-block size in flex measurement cache keys | `6cf27eadddf9` | `4d0749e7d3c4` +1 linked in JSON |
| 111 | Synthesize central baselines from the requested origin | `ee836eba6ca6` | `54e8683a6dfb` |
| 122 | Saturate subgrid line-name counts and guard remaining capacity | `8d0eb95794eb` | `7abb33ffcb24` |
| 127 | Bug 2037744 - Resolve subgrid name-repeat counts during style computation | `f946a0921b8b` | `79f8d7f1ea56` |

### Container queries

| ID | Commit subject | Native/WPT | Research/evidence |
|---:|---|---|---|
| 14 | Track dependencies for name-only container queries | `238710ff9db7` | Not recorded |
| 27 | Track attribute references through container-query operators | `16ff45a117b1` | `3dc4259d2dd0` |
| 28 | Invalidate container queries when content-box size changes | `ef3d32280505` | `dc96c3763a4d` |

### Colors, images, SVG and shapes

| ID | Commit subject | Native/WPT | Research/evidence |
|---:|---|---|---|
| 17 | Preserve analogous missing components across RGB and XYZ color conversion | `82b254686378` | `a75f70c97b15` |
| 18 | Preserve zero-weight prefixes during normalized color mixing | `591b3e125678` | `519f2b2a7569` |
| 30 | Avoid overflow when computing polygon shape intercepts | `06be3d7e722c` | `1a86773b4a5e` |
| 31 | Use the border box for stroke-box transforms on CSS boxes | `96e0ad8c6a0a` | `b709247b5f33` |
| 32 | Honor object-fit with partial intrinsic dimensions | `66fb24648a15` | `ff354bf3100d` |
| 36 | Compose empty SVG mask regions as transparent black | `065183ac8449` | `629771d9fd8c` |
| 37 | Compose zero-sized mask images as transparent black | `6bb2557507bc` | `c767ea97fb25` |
| 115 | Correct SVG quarter-millimeter conversion factors | `fa9dff982cec` | `e7ec30d7d159` |

### CSSOM geometry and hidden layout

| ID | Commit subject | Native/WPT | Research/evidence |
|---:|---|---|---|
| 102 | Preserve double precision in layout DOMRect coordinates | `c0e8c7fd1deb` | `752c83eb2834` +3 linked in JSON |
| 103 | Preserve app-unit precision for untransformed client rectangles | `7309af28e360` | `5c3fe8efdb1d` +5 linked in JSON |
| 104 | Preserve dirty children when hidden flex layout is skipped | `29611cb584fd` | `2c27b25853ff` +1 linked in JSON |
| 105 | Mark hidden absolute children dirty before reflow input initialization | `f8104759d383` | `2c27b25853ff` +1 linked in JSON |
| 106 | Refresh hidden column queries from dirty table providers | `29e2df85a4a9` | `9cab8f29f688` |
| 107 | Preserve query readiness for skipped block line children | `e6c73b637653` | `9cab8f29f688` |
| 108 | Preserve query readiness for skipped grid children | `a578671e967f` | `b6871ca3458e` |
| 109 | Preserve query readiness for skipped float-owner subtrees | `8a5df95cf9d5` | `6b9f50396a7b` +1 linked in JSON |
| 110 | Preserve query readiness for skipped MathML subtrees | `aaca499a3257` | `d492f0944056` |
| 112 | Preserve integer precision in element offset, scroll, and client geometry | `b616622d2cd7` | `c67102a4c8f6` |
| 113 | Resolve skipped SVG viewport layout before matrix queries | `cc52e66ca64a` | `bf0a7cb4a980` |
| 114 | Refresh SVG length context before resolving and converting units | `53adf727ea05` | `a5a6c6545471` |
| 116 | Refresh hidden embedding frames for SVG viewport lengths | `9c2257a80e3f` | `01bd90af2829` |

## Test-only repairs — excluded from the 140

| Test repair | WPT commit | Evidence commit |
|---|---|---|
| identifier-roundtrip-test-completion | `ae4db18e4b3e` | `8d1658d8e674` |
| registered-animation-consumer-calibration | `5cdd697e02d2` | `1131d9b73f09` |

## Held and pending work — not additional accepted fixes

The rows below describe workstreams, not additional bug counts. Historical candidate statuses are kept distinct from current acceptance.

| Workstream | Current boundary |
|---|---|
| Held fix 120: contextual sign folding | Installation held; positive-font steps()/integer consumer contracts and context prerequisites remain open. Excluded from140 accepted. |
| flex-safe-overflow-scroll-origin | Native/WPT review accepted the candidate; full required formal obligations remain pending, so it is not in the committed accepted count. |
| collapsed-flex-exported-baseline | Native/WPT review accepted the candidate; full required formal obligations remain pending, so it is not in the committed accepted count. |
| collapsed-flex-scroll-overflow | Native/WPT review accepted the candidate; full required formal obligations remain pending, so it is not in the committed accepted count. |
| flex-cross-axis-packing-overflow | Initial candidate rejected at a fragment consumer; repair pending. |
| flex-natural-baseline-donor-selection | Candidate acceptance withdrawn after a provider regression. |
| flex-forced-break-final-fragment-size | Isolated candidate rejected for packing regressions; repair pending. |
| round-infinite-value-contextual-step | Browser reproduction with a conditional source draft; not accepted. |
| dormant-keyframe-cache-refresh | Normal-style recascade correctness verified in scope; performance remains inconclusive, so the candidate is held. |
| Random counter rollback across typed alternatives and enclosing grid parse | Local Nightly reproductions and46 focused WPT cases prepared. Corrected four-source v4 and enabled configured typecheck-v3 prepared, not executed; paired553-assertion/7-page runner prepared disabled. Signing requires a fresh execution binding afterward. |
| Registered provider readiness, defaults, SCCs and pending cascade integration | Earlier partial provider experiment remains the only tracked native worktree change and is unaccepted. Retained-AST/demand/ownership prototypes and scoped models advance the design; complete context scheduling, cycle policy and publication remain open. |
| Registered initial AST retention and computational independence | Retention passed configured Rust checking; linked-browser preservation and complete selected-value independence validation remain open. Erased-dependency and CSS-rule initial-value policy limits remain explicit. |
| Contextual easing and integer consumers | CSS keyframe dependency handoff passed Gecko Rust checking. Servo paths, lifecycle WPTs and generic element-dependent easing policy remain unresolved; parser guards remain necessary. |
| Relative atan2 and finite mod/rem/round at a zero basis | Browser-confirmed observations and scoped models/proposals; contextual integer/easing consumers prevent claiming a complete independently landable fix. No accepted ID allocated. |
| Registered logical-unit writing-mode scheduling | Acyclic browser reproductions, fixed-line-height controls and corrected bitflags/source proposals exist. Provider readiness and genuine-cycle policy remain acceptance constraints; no native fix accepted. |

## Formal library, Bloom work and tooling

| Work | Recorded result and limits |
|---|---|
| Original Bloom milestones 1–6 | Complete within the declared selector profiles and assumptions, per the [closing appendix](../stylo-bloom-tools/MILESTONE6-CLOSING-APPENDIX-draft.md) and original-requirement audit. General selector soundness, unrestricted callback behavior and whole-Gecko equivalence are not proved. |
| Canonical CSS Lean library | Last recorded full check: **11,840 declaration audits; 12,438 executable cases; 173 expected-false cases; 2,155 source fingerprints**, canonical revision `162b20fb7c53a0ab89b20875a965baee98fb66bb`. Verified against the [terminal review](../css-steps-origin-library-application-terminal-review-v1/CHECK.json); not a fresh checker run or percentage of CSS specified behavior. |
| Standalone formal research | Conditional models cover dependency projection, cycle/default ownership, selected admission, easing/calculation boundaries, random-state rollback, page-selector filtering and line-height leaf evaluation. Source correspondence and machine/context assumptions remain explicit; post-discovery witnesses do not receive discovery credit or automatic canonical coverage credit. |
| Validation and recovery tooling | Signed artifact inventories, exact source/epoch bindings, configured native checks, isolated WPT comparisons, reversible app/source experiments and owned cleanup support review and replay. Tooling is evidence infrastructure, not proof of complete CSS implementation correctness. |
| Current working state | Accepted fixes through 141 are committed. The held custom-properties prototype remains unaccepted; parked prototypes/recovery captures are separate from accepted fixes. New counter typecheck and paired-browser preparations have not run. |

Readout generation performed read-only Git ancestry/subject queries and ledger checks. It ran no compiler, browser, proof checker, staging, commit or canonical-ledger update.
