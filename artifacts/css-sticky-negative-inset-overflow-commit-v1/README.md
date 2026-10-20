# Negative sticky insets: local commit queue

Evidence and formal companions precede the three-file Gecko/WPT fix. Signing remains required. Set each recipe's expected parent only after the preceding signed commit has been verified, then use `commit-item-v2.py`. Record the resulting IDs in the main bugfix ledger.

`PACKAGING.json` verifies the original standalone patch and the queued variant on both retained bases using temporary indexes. The queued variant widens the already normalized inset components and preserves logical-end selection from the preceding fixes. The original standalone patch remains available in `css-sticky-negative-inset-overflow-fix-v1`.

The queued CPP differs from the frozen shared browser source only in the separate geometric-sentinel position guards. Those guards are not included in this repair. No new browser run or isolated upstream execution is implied by packaging.

Acceptance covers the eight stated conditional formal obligations and the reviewed native/WPT change. Geometry providers, compiler/source interpretation, and explicit arithmetic domains remain boundaries; the retained preexisting range-clamp overflow is not fixed here.
