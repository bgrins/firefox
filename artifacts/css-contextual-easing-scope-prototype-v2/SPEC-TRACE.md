# Corrected failed-reference result

[CSSWG issue13736, resolution24June2026](https://github.com/w3c/csswg-drafts/issues/13736#issuecomment-4791604896) chooses one for sibling-index()/sibling-count() when there is no matching thing to count. The issue remains Open/Needs Edits; the draft's earlier zero wording has not been updated. [The26June comment](https://github.com/w3c/csswg-drafts/issues/13736#issuecomment-4806617328) links the WPT update. Captured primary records and implementation history are pinned in REFERENCES, including [bug2050171](https://bugzilla.mozilla.org/show_bug.cgi?id=2050171), [D308700](https://phabricator.services.mozilla.com/D308700) and [WPT commit418c211](https://github.com/web-platform-tests/wpt/commit/418c211b1c850d5c1c7d44aab41c78aff026bdce).

Accordingly an outer failed-reference easing steps(1+sibling-index(),end) computes steps(2,end); at0.75 progress its output is0.5. A same-tree index2 gives steps3 and2/3; index3 gives steps4 and3/4. The literal reference animations implement those comparisons. This corrects the old oracle, not native scope transport.

The separate Shadow1 declaring-root/global-name lookup rules remain relevant and unchanged. Preserving current lookup winners does not prove those rules implemented. No context-free Web Animations policy is inferred.
