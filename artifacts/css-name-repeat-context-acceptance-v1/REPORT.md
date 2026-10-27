# Accepted repair 127: contextual subgrid name-repeat

Subgrid repeat counts now resolve using the element's computed style before their expanded-name cache is built. The specified expression is retained; computed counts determine saturating cache arithmetic. This addresses the subgrid portion of existing bug 2037744, not a newly discovered issue or complete ordinary track-repeat support. The minimal patch contains two Rust files and one ten-case WPT; research and tooling must precede its native commit.

Full Gecko compilation and the 1,532-assertion/eight-rendering-test comparison pass their acceptance policy. All ten landing cases pass, repairing exactly eight admission failures. Every other normalized outcome is preserved. The original sources are restored, rebuilt and retested to the exact baseline. Independent source and terminal review pass. A root scratch apply/reverse check confirms that this exact three-path patch produces the tested bodies. Scratch files are removed. The candidate is accepted but is not currently installed or committed.

The tested parent retains fix 122's saturation and full-width native capacity guard. The selected patch is an independently reviewable Gecko/WPT delta on that parent; it is not claimed independently cherry-pickable or runtime-tested on bare HEAD90. The older HEAD90 transport alternative is not the accepted patch.

Existing Lean cache and prefix results are reused conditionally after the supplied Context computation. The adapter demonstrates why specified/stale caches cannot substitute for rebuilding from final counts. This is neither universal native refinement nor proof of every provider or invalidation history. The WPT reaches font mutations, positive clamping, empty groups and truncation, computed inheritance, sibling insertion/removal and structural safeguards. No security impact is established.

The reviewer tool selects #firefox-style-system-reviewers. A fresh Bugzilla lookup confirms bug 2037744 covers computed-value-time grid repeat support; the ordinary track-repeat portion remains separate. No external submission or push occurs.
