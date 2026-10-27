# Accepted calculated cubic-bezier range repair

Fix 134 clamps context-free calculated x coordinates to [0,1] at computation. Literal range rejection and unrestricted y coordinates are preserved. The standalone commit contains one Rust file, one 36-case WPT and two expectation-file updates.

Original/candidate/restored outcomes were 82 PASS/31 FAIL, 110 PASS/3 FAIL, and the exact original 82 PASS/31 FAIL. All 38 targets pass, repairing 28 observations; all 75 controls and all 113 restored results match. The final installed build reproduces all 113 candidate observations while changing only the four expected fields for the two easing fixes. This patch removes only its two cubic expectations; fix 133's two steps expectations are already folded into that fix.

The complete final build, browser lifecycle, process cleanup and source/binary/index preservation passed independent terminal review. The installed binary includes this candidate. One unrelated stale expectation for calculated start steps remains associated with fix 121; its correction is tracked separately. Three context-dependent failures remain expected. No claim is made to fix all of bug 2037743 or to have run a clean upstream-only browser.

Discovery came from source/specification audit and browser reproduction. Existing real-number clipping and censorship models support conditional laws; they do not prove the native parser, IEEE implementation or full CSS semantics. No new proof or canonical coverage credit is added. Triage is tentatively P3 conformance, with no demonstrated security or measured performance impact.
