# CSS and Stylo work readout

**149 accepted native fixes are committed locally**; tracked IDs run through 150, excluding held fix 120. Prior 148 records are preserved exactly. Two test-only repairs remain separate.

Snapshot HEAD: `2d18f8b4a4d7ac7f29b1f8b4b1f3ded57e792e72`. Ancestry checks cover local history; they do not certify upstream landing or clean-upstream execution.

After the verified standalone signed native commit, pow repair 150 brings accepted native fixes to 149 across tracked IDs through 150, excluding held fix 120. The exact three-path payload is generic calc, the 24-case WPT and deletion of twelve obsolete expected-FAIL annotations. Original and final runs complete 147 callbacks: all 18 targets improve, all 24 authored callbacks pass, and 129 control plus two ending signatures remain unchanged. Final installed execution has no failures or unexpected results. Historical Hypot 149 and round 145 source/commit metadata remain unchanged; current calc b291d6e9 explicitly supersedes b7a6ac85. Shared-branch validation retains the held provider. Abstract guard/folding, binary32 classification and scalar checks support bounded claims; they do not establish native powf correctness, correct rounding, full CSS conformance, clean-upstream execution or canonical coverage credit.

| Area | Accepted native fixes |
|---|---:|
| Selectors, Bloom filters and scoping | 12 |
| Cascade, layers and shorthands | 6 |
| Parsing, tokens and CSS math | 31 |
| Attributes and custom properties | 19 |
| Animations, timelines and transitions | 18 |
| Text and fonts | 16 |
| Layout, sizing and positioning | 23 |
| Container queries | 3 |
| Colors, images, SVG and shapes | 8 |
| CSSOM geometry and hidden layout | 13 |
| **Total** | **149** |

| Fix | Change | Native commit |
|---|---|---|
| 1 | No bug - Account for prior saturation when clearing StyleBloom. r?#firefox-style-system-reviewers | `d855b3483b493c7e596b5d1d30d613fa7b7e2db5` |
| 2 | No bug - Build relative-selector Bloom filters with an iterative traversal. r?#firefox-style-system-reviewers | `93a062cded54c974dff03ce2618aaf612a9c8d61` |
| 3 | No bug - Exclude false-supports imports from effective rule iteration. r?#firefox-style-system-reviewers | `5d3638a91adf7b662041e192d121c7fd91c86f0a` |
| 4 | No bug - Sort important user and UA rules by cascade priority. r?#firefox-style-system-reviewers | `e28cb48d656ba83097fb0960734e4317252e7d81` |
| 5 | No bug - Order nested scope roots by proximity. r?#firefox-style-system-reviewers | `075be5516374d31c55a1e0f71b3fa80591042503` |
| 6 | No bug - Match scope-end selectors when reaching a shadow host. r?#firefox-style-system-reviewers | `a46e5310cd604adff10e914e82e8a326b9fb7957` |
| 7 | No bug - Exclude scope roots from scope-limit matching. r?#firefox-style-system-reviewers | `78c11c75170af5480a88fd9682db41183760f652` |
| 8 | No bug - Include the scope element in relative selector cache keys. r?#firefox-style-system-reviewers | `d4a2b600f078d4c29e6dd8e0f1668121941a64e5` |
| 9 | No bug - Include the scope element in filtered nth-index cache keys. r?#firefox-style-system-reviewers | `92c013c16908bd30593ca7385b24dad1be4288dc` |
| 10 | No bug - Follow relative dependencies when invalidating scope limits. r?#firefox-style-system-reviewers | `64ac54569f1cc202172ded92ee23ba749cd3284e` |
| 11 | No bug - Propagate filtered nth invalidation from relative anchors. r?#firefox-style-system-reviewers | `b1b1bacb9406d75f35648d40a70ce9ad0fc3ab69` |
| 12 | No bug - Avoid style sharing for scope-dependent nth filters. r?#firefox-style-system-reviewers | `f4b34bf7fef125857979a210616d201e28eefded` |
| 13 | No bug - Preserve zero signs when simplifying round with infinite steps. r?#firefox-style-system-reviewers | `708b914901eeb7a2d348855c2efcf099e6003317` |
| 14 | No bug - Track dependencies for name-only container queries. r?#firefox-style-system-reviewers | `238710ff9db7f54449c075bf80c7c3d40b43387a` |
| 15 | No bug - Keep animation iteration identity separate from accumulation counts. r?#firefox-style-system-reviewers | `0a81e1f36ab08a6d67ddd0bdd590e4661ff9b0a1` |
| 16 | No bug - Preserve shorthand source identity when reusing substituted values. r?#firefox-style-system-reviewers | `11482ee213bf63c749b6d205c2c7591d783bdaa8` |
| 17 | No bug - Preserve analogous missing components across RGB and XYZ color conversion. r?#firefox-style-system-reviewers | `82b254686378e57711759c238b975cdf4678a287` |
| 18 | No bug - Preserve zero-weight prefixes during normalized color mixing. r?#firefox-style-system-reviewers | `591b3e12567865c7e047530753e510c54d18b3db` |
| 19 | No bug - Preserve deferred transform operations during composition. r?#firefox-style-system-reviewers | `c9274972124198e8f8466ddcd667d1c23cb044ec` |
| 20 | No bug - Preserve NaN operands when simplifying clamp. r?#firefox-style-system-reviewers | `a4fe7dd06fd7dac3924b2dc9aea4f57103eb1b98` |
| 21 | No bug - Preserve finite dividends for valid infinite mod and rem divisors. r?#firefox-style-system-reviewers | `bfbce1cc7e9a5b53d5cc00317a265d7141428997` |
| 22 | No bug - Require a complete number token for attr units. r?#firefox-style-system-reviewers | `499c0c6b72ac4bc0a6396bffa3fa0d71665409ce` |
| 23 | No bug - Order physical shorthands before logical shorthands of equal size. r?#firefox-style-system-reviewers | `e27beeac5129d7331f8aca9babbe6bfc199d7d24` |
| 24 | No bug - Preserve out-of-range absolute positions in subgrids. r?#layout-reviewers | `7f5a1105253e60b283174ea890862b1943e8702a` |
| 25 | No bug - Use Unicode final sigma context across text-transform boundaries. r?#layout-reviewers | `8e78ffd376c4d478b5d614f568f3bf09d894ad8b` |
| 26 | No bug - Apply grid stretch sizing only to automatic inline sizes. r?#layout-reviewers | `2a61f0b7433628e8a77159b968ca570632591b8e` |
| 27 | No bug - Track attribute references through container-query operators. r?#firefox-style-system-reviewers | `16ff45a117b149ec95fc633c7ac18d8a1c38ca0b` |
| 28 | No bug - Invalidate container queries when content-box size changes. r?#layout-reviewers | `ef3d32280505b7fb6c1b35989d7e74c56f1aee0a` |
| 29 | No bug - Clamp negative minimum contributions from spanning table cells. r?#layout-reviewers | `98fd7a22a32744ab429828d609cf5bfb3affc4a5` |
| 30 | No bug - Avoid overflow when computing polygon shape intercepts. r?#layout-reviewers | `06be3d7e722c55ffbff97e6be237bd39a4920295` |
| 31 | No bug - Use the border box for stroke-box transforms on CSS boxes. r?#firefox-style-system-reviewers | `96e0ad8c6a0ae58b9ce8c47579c9bc06f67fc1e2` |
| 32 | No bug - Honor object-fit with partial intrinsic dimensions. r?#layout-reviewers | `66fb24648a15769f80c2adf37030e68598dae68f` |
| 33 | No bug - Preserve auto inset state when resolving absolute-position margins. r?#layout-reviewers | `f67ddfaa3dc328d7359c7fca56e61a1249e1ee96` |
| 34 | No bug - Prevent margin collapse through blocks with resolved positive sizes. r?#layout-reviewers | `e09ffb35c0b47c6c29c43c64d887fb524b5e7423` |
| 35 | No bug - Preserve escaped delimiters during bad URL recovery. r?#firefox-style-system-reviewers | `83bc2bd3922697d44a602bf48902e821796a60e3` |
| 36 | No bug - Compose empty SVG mask regions as transparent black. r?#firefox-svg-reviewers | `065183ac8449800f0dbef3c23a15be3863ca60ae` |
| 37 | No bug - Compose zero-sized mask images as transparent black. r?#layout-reviewers | `6bb2557507bcd6346664e539f9f4b9628d8e6078` |
| 38 | No bug - Recompute nesting specificity from expanded selector components. r?#firefox-style-system-reviewers | `c57d0c806d94c6e6dd56e23acdeed847c5ea1571` |
| 39 | No bug - Exclude fixed-positioned frames from scroll anchors. r?#layout-reviewers | `e606244c4546e522cf4a6e86dac98e216305003b` |
| 40 | No bug - Reset text-overflow marker widths for each line. r?#layout-reviewers | `c348436003653a08b6766339d9e0c8f89084d062` |
| 41 | No bug - Ignore zero-width tabs when measuring intrinsic sizes. r?#layout-reviewers | `eca9efde2991b5a458d23efd1c6d33d58fdf4a77` |
| 42 | No bug - Use the eleven-degree threshold for oblique font matching. r?#gfx-reviewers | `9da730d5ebd6cb59a0a5b2a666d6679808d58889` |
| 43 | No bug - Resolve scroll timeline axes from the scrolling frame. r?#firefox-style-system-reviewers | `0af700c67a5aef6048b19b72350320cd1fe82346` |
| 44 | No bug - Preserve width and style priority in fractional font matching. r?#gfx-reviewers | `9cca10125782ebe2bf076a5e5d8becdacae5ff16` |
| 45 | No bug - Avoid applying CSS zoom twice to root line-height units. r?#firefox-style-system-reviewers | `43afd2c6f3500cee4a2dd07d07eb14aca723fae3` |
| 46 | No bug - Include composition when comparing keyframes. r?#firefox-style-system-reviewers | `6b8dc654e8d017562533308571af23c3099fd5cc` |
| 47 | No bug - Allow text emphasis on private-use characters. r?#layout-reviewers | `bbf5a4095f85fb250ea442695a311f2547ffdc19` |
| 48 | No bug - Keep partial ligature advances signed. r?#gfx-reviewers | `8ee543a6ff23cc097f54f1c3e984f7d5f7e56fea` |
| 49 | No bug - Preserve supplementary scalars in UTF-16 complex line breaking. r?#platform-i18n-reviewers | `39ce7571a61097a80d5bf07adbc3ae48a2f0262e` |
| 50 | No bug - Rebuild worker font families after FontFaceSet removals. r?#firefox-style-system-reviewers | `32ba35ffb9a17f5e91df5c56f01a06a452dfdc8a` |
| 51 | No bug - Compare hyphenation word boundaries in text-run coordinates. r?#gfx-reviewers | `18871240dc7d077bf223822013e7a50cf581e2d1` |
| 52 | No bug - Preserve attribute namespaces in substitution caches. r?#firefox-style-system-reviewers | `3aa7d25635ff9dc3bc105269dd9b7b13b5f80cb0` |
| 53 | No bug - Preserve invalid attribute entries during substitution. r?#firefox-style-system-reviewers | `fd9c07e1130bcb68684c25e7527f5b0ff3c3bd73` |
| 54 | No bug - Prepare typed attribute references in substitution fallbacks. r?#firefox-style-system-reviewers | `7822bb6d17b1381cdb3e56deb20c5ec3e078adec` |
| 55 | No bug - Align MathML token leading whitespace for text measurements. r?#layout-reviewers | `f843fd7568f30e14e664c37c36544d8d88e8c1bb` |
| 56 | No bug - Visit typed attribute fallbacks when primary parsing fails. r?#firefox-style-system-reviewers | `e3ba54f6f826fe265eb5bc4731f66f64465dd47c` |
| 57 | No bug - Track property dependencies through attribute-only declarations. r?#firefox-style-system-reviewers | `3892ab844694fedd987f5ce1dd2165f53fc2dbed` |
| 58 | No bug - Preserve relative-unit dependencies in resolved custom property values. r?#firefox-style-system-reviewers | `58200fa81a6f92f92a1898ba2866a2fbcbac0daa` |
| 59 | No bug - Only classify dimension tokens as relative-unit dependencies. r?#firefox-style-system-reviewers | `26e0fa16e89eacd9fd9cab0ce6bb1be813d9e406` |
| 60 | No bug - Reject escaped newlines after leading hyphens in CSS identifiers. r?#firefox-style-system-reviewers | `09b008b3320fa29fcbcf081b252053e3721c5e10` |
| 61 | No bug - Refresh loaded FontFace providers after descriptor changes. r?#firefox-style-system-reviewers | `6bd0b00dcff5514a3234423787920ed44491a4bc` |
| 62 | No bug - Preserve CSS numbers with compensating exponents. r?#firefox-style-system-reviewers | `4391deb4751a8be2be98e838360f00c94808c5d5` |
| 63 | No bug - Keep fallback endpoints aligned with quoted EOF recovery. r?#firefox-style-system-reviewers | `2d658a9c5aa4139dc7f196933511abf4a594163f` |
| 64 | No bug - Preserve paired backslashes at quoted EOF. r?#firefox-style-system-reviewers | `89bad2d8b5260ad5fc9d5660a3a18a09433902e3` |
| 65 | No bug - Recognize escaped terminal quotes during EOF recovery. r?#firefox-style-system-reviewers | `ed9505d25ee4333c1764acc173f95f9517ca9b07` |
| 66 | No bug - Consume rejected blocks at the CSS parser nesting limit. r?#firefox-style-system-reviewers | `55d251b7a90003546994f6576e5ee78e8fa07cb2` |
| 67 | No bug - Validate the whole declaration value before substitution fallback. r?#firefox-style-system-reviewers | `095c5be548a2bddf5f3ff01e01da66c6098a8ee5` |
| 68 | No bug - Clear ordinary declarations before substitution fallback. r?#firefox-style-system-reviewers | `780495d90a85052cff69713f1086180253cb9730` |
| 69 | No bug - Preserve logical-group order when setting the all shorthand. r?#firefox-style-system-reviewers | `074086719e445ca72d3056f7fbf793af5e69d6f6` |
| 70 | No bug - Interpolate registered keyframes using substituted computed values. r?#firefox-style-system-reviewers | `188644f6d9833b485f35c2abcfad23cef2c5e9f7` |
| 71 | No bug - Use computed registered initial values when defaulting custom properties. r?#firefox-style-system-reviewers | `6aa2138c144aa6eee8e07aac77e7a68a8c7f7617` |
| 72 | No bug - Preserve guaranteed-invalid registered values during explicit inheritance. r?#firefox-style-system-reviewers | `3a01fc986c7974161aadf4bfafe65c234b036b07` |
| 73 | No bug - Track reset-property inheritance after custom property substitution. r?#firefox-style-system-reviewers | `60bf34f48ac63ca595d519c1e0c2b4a2fa731b66` |
| 74 | No bug - Exclude guaranteed-invalid custom properties from computed-style enumeration. r?#firefox-style-system-reviewers | `0cac5c270615d04239bd4a4024a3ab5ffd0d24ae` |
| 75 | No bug - Skip shadowed ancestors when iterating custom properties. r?#firefox-style-system-reviewers | `90ffac0a5e4076b6117ca152249f342a13995ee3` |
| 76 | No bug - Preserve attribute taint when replacing equal custom-property values. r?#firefox-style-system-reviewers | `e04d672a735edcf0e6529c854207b5ee9555ea7c` |
| 77 | No bug - Use half-open ranges when checking attribute-tainted URLs. r?#firefox-style-system-reviewers | `8c04b6787e36c9ee42fec440103cf33372c097f1` |
| 78 | No bug - Preserve attribute taint when replacing animation endpoints r?#firefox-style-system-reviewers | `4b4a00e707583382f4773039f13a4f335f48f41a` |
| 79 | No bug - Restyle animations when underlying attribute taint changes r?#firefox-style-system-reviewers | `2c09cb2e4ff81bbc4af65d1d069517420b9c1529` |
| 80 | No bug - Preserve attribute taint from both interpolated custom values r?#firefox-style-system-reviewers | `ede7ceb101d83f0c4044585a5a687f5286b072c9` |
| 81 | No bug - Preserve registered custom property token boundaries r?#firefox-style-system-reviewers | `34e4e755cb81332819e56457f5fb68b9b305c394` |
| 82 | No bug - Preserve guaranteed-invalid animated custom properties r?#firefox-style-system-reviewers | `d63735091bf8dc469d900ddba56e8a43bcac26d7` |
| 83 | No bug - Normalize custom property whitespace before recording reference offsets r?#firefox-style-system-reviewers | `ad608a212bd8d7f77a2f0b9df62df18d33c12b96` |
| 84 | No bug - Keep custom property token metadata aligned with trailing whitespace trimming r?#firefox-style-system-reviewers | `bccea9c1fffc59e41a9f9bef16fcaf0056ff1f10` |
| 85 | No bug - Preserve escaped whitespace in custom property token values r?#firefox-style-system-reviewers | `fff2d758ef6bb39b4465cb072767bc5db6d5e09f` |
| 86 | No bug - Preserve newlines after backslash delimiters in custom properties r?#firefox-style-system-reviewers | `246f1ff43250ec24e177f03cde923c9d11ee86e9` |
| 87 | No bug - Deduplicate initial view-transition types r?#dom-reviewers | `2db94380203863bced9e3a7147505beabaaf7599` |
| 88 | No bug - Restyle after active view-transition type changes r?#dom-reviewers | `c67505af9aae8c06150d74d81a67011e7921d3cd` |
| 89 | No bug - Reserve the auto offset code for auto sticky insets r?#layout-reviewers | `fdd7dcb11653c3c3808557708969c7e1eb803b82` |
| 90 | No bug - Treat automatic sticky insets as zero when sizing the view rectangle r?#layout-reviewers | `983931aa5fad14b5d86120cfd66635be7f1b844f` |
| 91 | No bug - Use the containing block writing mode for sticky end-inset reduction r?#layout-reviewers | `67bcf64fc28f181859c6dc726e532430475e49e7` |
| 92 | No bug - Use wide arithmetic and direct sticky range edges r?#layout-reviewers | `d3c505adc9e99a293a44bde5a3f04557aac255d0` |
| 93 | No bug - Use wide sums for flex baseline cross sizes r?#layout-reviewers | `71a523a4c5267ba4c07a59329e57317fafc31f1b` |
| 94 | No bug - Apply sticky position constraints only for specified insets r?#layout-reviewers | `68686da757592b0de4d1b064966d81f8b9265fc1` |
| 95 | No bug - Use wide saturated sums for flex line cross sizes r?#layout-reviewers | `958e63a947e4a97dd224d60c5699b42061af5422` |
| 96 | No bug - Use normal flex item positions for exported baselines r?#layout-reviewers | `b4894d6329df7b9cae8f81cbd72e89d61f1b4adc` |
| 97 | No bug - Convert scroll-container last baselines through block-start coordinates r?#layout-reviewers | `9980b7b7a0fb894c963a69c0ef0e17b12e6d6350` |
| 98 | No bug - Include border and padding in flex item measurement cache keys r?#layout-reviewers | `f5926c6dab500569fc2345aade1a43aebc7e3796` |
| 99 | No bug - Position flex overflow containers using the final fragment size r?#layout-reviewers | `a6c78d9502504d07432fd0c81c168847bbfa25a4` |
| 100 | No bug - Apply relative positioning to overflow continuations r?#layout-reviewers | `2b769488eef1e2ae18ed27d014402591110e3ed1` |
| 101 | No bug - Include containing-block size in flex measurement cache keys r?#layout-reviewers | `6cf27eadddf9e63d9bfbcc87ff2bf354e091ae7c` |
| 102 | No bug - Preserve double precision in layout DOMRect coordinates r?#layout-reviewers | `c0e8c7fd1deb9320b0bae747c043c100ac842f49` |
| 103 | No bug - Preserve app-unit precision for untransformed client rectangles. r?#layout-reviewers | `7309af28e360d5d9544eb04dbbbe7f74a102e164` |
| 104 | No bug - Preserve dirty children when hidden flex layout is skipped r?#layout-reviewers | `29611cb584fdd0e54d5e7f7e0d70ad47cfff1653` |
| 105 | No bug - Mark hidden absolute children dirty before reflow input initialization r?#layout-reviewers | `f8104759d383bd324cdda1e78e3229902e97fb39` |
| 106 | No bug - Refresh hidden column queries from dirty table providers. r?#layout-reviewers | `29e2df85a4a979f7aab73485b7d77ce4b1ea6bf4` |
| 107 | No bug - Preserve query readiness for skipped block line children. r?#layout-reviewers | `e6c73b63765376dbf74daaa0d4f489ea615a2888` |
| 108 | No bug - Preserve query readiness for skipped grid children. r?#layout-reviewers | `a578671e967f9eac837497481d2012b288b98b5b` |
| 109 | No bug - Preserve query readiness for skipped float-owner subtrees. r?#layout-reviewers | `8a5df95cf9d56c8d0dfde9939f2a7c92151f092c` |
| 110 | No bug - Preserve query readiness for skipped MathML subtrees. r?#layout-reviewers | `aaca499a3257e1f196b9dacace42041ab523f399` |
| 111 | No bug - Synthesize central baselines from the requested origin. r?#layout-reviewers | `ee836eba6ca6070cec5c8a25208fd51d9df0a7f0` |
| 112 | No bug - Preserve integer precision in element offset, scroll, and client geometry. r?#dom-reviewers | `b616622d2cd7fa69376261c600f3c9a2ba1e4da4` |
| 113 | No bug - Resolve skipped SVG viewport layout before matrix queries. r?#firefox-svg-reviewers | `cc52e66ca64a4afde2f5d078f1326249ff106033` |
| 114 | No bug - Refresh SVG length context before resolving and converting units. r?#firefox-svg-reviewers | `53adf727ea052bb6a08b60be8bbec76c8abccc74` |
| 115 | No bug - Correct SVG quarter-millimeter conversion factors. r?#firefox-svg-reviewers | `fa9dff982cecc234294981fb8f668767816f1652` |
| 116 | No bug - Refresh hidden embedding frames for SVG viewport lengths. r?#firefox-svg-reviewers | `9c2257a80e3ff6c97080657f5c9a08b717f34cfa` |
| 117 | No bug - Preserve the reserved counter value through computed integer math. r?#firefox-style-system-reviewers | `33ae2e8349e96d1778603385d39cdb74b26a12df` |
| 118 | No bug - Round computed CSS integers after promoting the half-unit addition. r?#firefox-style-system-reviewers | `d68543e601c40bf64d1777dfa6b7c79b838f21ae` |
| 119 | No bug - Preserve nonfinite relative lengths inside CSS math. r?#firefox-style-system-reviewers | `6a363fc372c9cc0734faee64ab20f03bc762e97c` |
| 121 | No bug - Apply stored integer ranges when resolving CSS math. r?#firefox-style-system-reviewers | `b218397700bd4ad701a232fad806cf99dd8f9f7b` |
| 122 | No bug - Saturate subgrid line-name counts and guard remaining capacity. r?#firefox-style-system-reviewers,#layout-reviewers | `8d0eb95794ebcd0b0dd5585047c9316ae075df92` |
| 123 | No bug - Resolve calculated counter range bounds when exporting membership. r?#firefox-style-system-reviewers | `0f68c5c1a7a556dd3907fdf7caf2d97110c53c12` |
| 124 | No bug - Compare and export additive counter weights by resolved nonnegative value. r?#firefox-style-system-reviewers | `656b54ea29efd83de6873663882afa0cab6b0e39` |
| 125 | No bug - Propagate NaN before resolving round() infinity cases. r?#firefox-style-system-reviewers | `a9b7886a5f470942b5e8e9d5863237b301d64425` |
| 126 | No bug - Preserve negative zero in finite round() upper bounds. r?#firefox-style-system-reviewers | `4c4ff0d440cd3d1ffd1021e831258043dbb926ed` |
| 127 | Bug 2037744 - Resolve subgrid name-repeat counts during style computation. r?#firefox-style-system-reviewers | `f946a0921b8b5ee87661284a827208b00cee5398` |
| 128 | No bug - Preserve finite mod() and rem() remainders. r?#firefox-style-system-reviewers | `10b6eabed27195aa21e41f62d8179af3a065a1dc` |
| 129 | No bug - Recompute keyframe values after CSS animation reactivation. r?#firefox-style-system-reviewers | `d13af8f7e9fd232b3d950f4f9bb59436ec6ef29f` |
| 130 | No bug - Prepare attributes for ordinary keyframe declarations. r?#firefox-style-system-reviewers | `e91224fd2e9e163bfb73d8e3fcdd4a1017b34ef1` |
| 131 | No bug - Recompute active keyframe values after attribute changes. r?#firefox-style-system-reviewers | `65355573964a31a08b3ae3e133c224cbab46e098` |
| 132 | No bug - Refresh contributing keyframes before commitStyles. r?hiro | `d477d0c331057847673d3e25646b3f39cd38c1a5` |
| 133 | No bug - Clamp calculated jump-none step counts at computation. r?#firefox-style-system-reviewers | `e414c8f7cfcd64ccca1a944b5f8e901ec3db2feb` |
| 134 | No bug - Clamp calculated cubic-bezier x coordinates at computation. r?#firefox-style-system-reviewers | `70cc9c30ef4420d8dba76ce3e5aab10504339ceb` |
| 135 | No bug - Recalculate contained quotes after appending a parent quote. r?#layout-reviewers | `0d27cb839f013f214973215cd0a8ce8a87c4b780` |
| 136 | No bug - Recalculate contained counters after appending a parent change. r?#layout-reviewers | `37bc9b06f034c191be50aa4949b072bbf7d5a64e` |
| 137 | No bug - Include used non-type attr fallbacks in dependency cycles. r?#firefox-style-system-reviewers | `aa3f0588538800300df20a2f7de40ce8ac2ffec1` |
| 138 | No bug - Keep nested raw attribute reads out of typed dependency cycles. r?#firefox-style-system-reviewers | `3c29fefb054855bd2b9d55587ac88e8e895067b8` |
| 139 | No bug - Compute registered CSS values without applying zoom twice. r?#firefox-style-system-reviewers | `0f40801f1418318e51f81b4e273c758a9a24b3e4` |
| 140 | No bug - Match page selector names when computing specificity. r?#firefox-style-system-reviewers | `c13f212eb28476eb31940f62299c4b4a3ae8750e` |
| 141 | No bug - Resolve contextual leaves in numeric line-height computation. r?#firefox-style-system-reviewers | `975e651729bacb7daf4aca7d4b75432ca2acfa7e` |
| 142 | No bug - Preserve random cache indices across rejected CSS parses. r?#firefox-style-system-reviewers | `25e423a1a81000541fb56c24066596943f039534` |
| 143 | No bug - Check both linear easing stop positions before conversion. r?#firefox-style-system-reviewers | `22f97187e9f062f76211c6c01b07cbc49e71232b` |
| 144 | No bug - Defer infinite-step rounding until the value is resolved. r?#firefox-style-system-reviewers | `c63be5163f2e0a05a27c6b022e9f388597f1c381` |
| 145 | No bug - Preserve finite multiples when resolving round(). r?#firefox-style-system-reviewers | `eb52086488112d1809062cf369f5e8feda6c2c38` |
| 146 | No bug - Avoid caching reset styles that depend on sibling-count(). r?#firefox-style-system-reviewers | `7501711ae4a105980cde23db588e582f41b77daa` |
| 147 | No bug - Invalidate old-parent styles during moveBefore(). r?#firefox-style-system-reviewers,#layout-reviewers | `ebb5d4fc489e1a5affdb8f2c1ae2d4dd50884bf9` |
| 148 | No bug - Preserve move context through shadow-root traversal. r?#dom-reviewers | `9e99cf9e4c886efb9232d90ed13f0c587e240da9` |
| 149 | No bug - Avoid intermediate overflow and underflow in hypot(). r?#firefox-style-system-reviewers | `36b693fee75e828f87b0c34df156caac903810c8` |
| 150 | No bug - Handle CSS pow exceptional values consistently in calculation and simplification. r?#firefox-style-system-reviewers | `2d18f8b4a4d7ac7f29b1f8b4b1f3ded57e792e72` |

Complete records and limitations: [ACCEPTED-FIXES.json](ACCEPTED-FIXES.json). Historical group assignments, held fix 120 record, test-only repairs and formal-library checkpoint remain unchanged. No canonical Lean increment or universal IEEE/native proof is claimed.
