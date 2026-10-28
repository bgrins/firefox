# Page-selector fix and research checkpoint

Fix 140 is committed as `c13f212eb28476eb31940f62299c4b4a3ae8750e` after verification research `e4ba214e3286b7a2307795c2c1f72c07706a528d`. Page-selector matching and specificity now use the matching name and pseudo-classes on the same selector. The paired 24-print-test run changes 10 failures to passes and preserves 14 passing controls/regressions. The standalone commit contains two Rust files and three WPT/reference pairs. Six scoped Lean claims and two false controls support the bucket-filtering argument; no native-refinement or canonical CSS coverage increment is claimed. Accepted fixes: 139; tracked: 140; held fix 120 remains excluded.

The remaining live provider experiment is unaccepted. Earlier recovery snapshots remain unchanged. Accepted page sources must survive future prototype restoration.
