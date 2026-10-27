# Local signing checkpoint

- animation-research: `54d577935aef6e99d4074716475ca32cfde55abd` (signature verified).
- followup-research: `788a0fc1ed630512a8553aa1e0c8baa70d26f760` (signature verified).
- quote-research: `d2e8f520eb1f1f66d69ad5568b092b9b05fdf9a4` (signature verified).
- quote-fix: `0d27cb839f013f214973215cd0a8ce8a87c4b780` (signature verified).

Quote fix 135 contains exactly two Gecko files and one WPT; its research is the immediate parent. The controlled browser comparison passes 64 cases with the fix, reproduces 12 failures without it, and passes all 64 again after restoration. All 18 existing regressions are unchanged. Both builds and WPT lint passed. The ledger now lists 134 committed fixes, with held repair 120 excluded.

The new ordered-scope Lean results remain standalone research, not an increase in canonical CSS-spec coverage. Animation integration and counter/language proposals remain unfinished. All 131 source/fixture/proof bodies in the committed v4 recovery snapshot still match; three are now the standalone quote commit, and the other 128 remain in the working tree. No duplicate snapshot is needed.

Nothing was pushed. Generated staged patches and redundant per-commit epoch copies are omitted; Git objects, signing receipts, the initial/ledger epochs and sealed comparison evidence preserve the relevant state. The current mutable continuation epoch is CURRENT-EPOCH.json in this directory.
