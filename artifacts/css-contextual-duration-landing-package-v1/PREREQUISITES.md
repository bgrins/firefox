The exact tested branch includes these previously accepted changes, recorded in the individual commit ledger:

| 129: css-duration-reactivation-keyframe-properties | `d13af8f7e9fd232b3d950f4f9bb59436ec6ef29f` | `7626b6ca8866ba2e6288a9b070b5e8d880ede2d1` |
| 119: relative-length-nonfinite-intermediates | `6a363fc372c9cc0734faee64ab20f03bc762e97c` | `49862ae74751926b2c3600fe6cf1625e5b31c691` |

Accepted 129's existing effect-property reactivation behavior is preserved in the captured matching.rs base; this proposal augments its animation-only scheduling path. Accepted 119's nonfinite relative-length transport is present in every tested build. It has not been shown necessary for the finite contextual duration arithmetic in these four pages, and this package does not prove independence from it. Neither existing fix is added to or removed by this patch.

The four authored WPTs use typed length division and require the captured inherited css/__dir__.ini preference layout.css.calc-typed-arithmetic.enabled:true. The existing inherited metadata is referenced, not added to the seven-file diff. The pages use no custom property or scroll timeline. The actual shared branch nevertheless includes the held custom_properties provider and accepted 150 and other fixes; absence of custom properties in these pages is not provider-free execution evidence. The broader base-response regression also exercises custom properties. No clean-upstream, dependency-free cherry-pick, or convergence claim is made.

The original ledger records are read-only provenance, not a new Git-object verification. Final installation must authenticate the three native preimages and four intended new WPT path absences on its actual admission state. The eight-source contextual-easing overlay and diagnostic logger are excluded.
