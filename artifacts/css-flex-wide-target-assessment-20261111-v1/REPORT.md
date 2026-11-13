# Wide flex targets change which items freeze

The 48-case WPT has 18 failures and 30 passing controls on the measured-base v1 candidate. The harness completes with OK. Actual run 11743 ended at 683d1e with exit 1. The retained structured report records two secondary items at 1000px instead of the expected 500px. All three writing modes and both column directions reproduce the failure with large content and a primary shrink factor of 1000000; small-content and shrink-factor-2 controls pass.

Each secondary item's automatic flex base comes from two ordinary block children. With 15000000px children, each base is 30000000px. The primary item has a 1000px base and a sufficiently large scaled shrink factor that its first requested target falls below signed32 storage. The container is only 1000px. The secondary items have maximum sizes of 1000px and all minima are zero.

[CSS Flexbox, resolving flexible lengths](https://drafts.csswg.org/css-flexbox-1/#resolve-flexible-lengths) uses the sum of min/max adjustments to select which items freeze. In this configuration the primary must freeze at zero; the two equally weighted secondary items then share the container at 500px each. Saturating the primary's requested negative target before computing its violation removes part of its positive adjustment. This changes the total's sign and prematurely freezes both secondary items at their maxima.

This is a native-reachable instance of the beyond-signed32 concern recorded by the earlier mathematical outside32_aggregate_sign lemma. It does not invalidate that lemma or the caller theorem's explicitly restricted signed32 input domain. It demonstrates that the domain does not cover the whole native distribution path.

The earlier measured-base repair remains a validated focused checkpoint, not a complete repair of wide-target semantics. This extension belongs with that pending repair; it is not counted as a separately committed or fixed bug. The v1 source/build/test identities are retained in BEFORE-INPUTS.json. Native repair and new validation are tracked in the separate measured-base v2 directory. Tentative P3 extreme-size layout correctness; no security claim.
