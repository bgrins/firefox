# Signed local work, 2026-10-27

| Commit | Contents |
|---|---|
| `6c9522c03630036124756945d44fcc2e4e4d4e9e` | compact-borrow-research |
| `feaec25f9647bc603994ce1c864e36107f23c7b2` | compact-borrow-native |
| `366551d71eeaa911948b28b56f6bc647d0dc7079` | steps-research |
| `75271a173ba0dda9d63728fa21aa12c91ddd85d1` | steps-native |

All four signatures and exact committed trees were verified. Research precedes each native commit. Fix 133 contains only one Rust file and three WPTs; the Arc API includes its unit and compile-fail tests. There are 132 accepted committed browser fixes; held repair 120 is excluded.

The jump-none comparison repaired 20 failures, passed all 22 targets, preserved 55 controls and exactly reproduced all 77 baseline outcomes after restoration. Tests ran on the experimental owner tree, not a clean upstream-only build. Source/specification audit found the issue; the standalone Lean model proves conditional consumer laws. Raw index drift in the comparison has no established cause; semantic staging was preserved.

The remaining prototypes are preserved by the accompanying recovery patch. They remain applied for continued development and are not counted as accepted fixes. The installed browser binary still contains the restored original steps implementation; signing installs the tested candidate source but does not rebuild it. Canonical Lean counts remain 11,830 audits, 12,424 examples and 170 expected-false cases. Nothing was pushed or submitted.

[Recovery patch](../css-unfinished-work-checkpoint-20261027-v2/unfinished.patch) preserves 131 remaining project working files, including 75 new files. Its exact forward/reverse tree roundtrip passed using temporary Git objects and index; unrelated untracked files were excluded.
