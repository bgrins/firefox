# Signed easing fixes and current build

| Work | Commit |
|---|---|
| Shared easing evidence, including corrected steps expectations | `56c3cda25c7c6e167db523cb4365ab20dc716422` |
| Fix 133: jump-none Rust/WPT/metadata | `ea6cde0db70c1fc85baf4fb8d0adc35b83545477` |
| Cubic final validation | `df58b1c6808b1cf4c77403c5b99a60487fec88ce` |
| Fix 134: cubic Rust/WPT/metadata | `8ccca4c4901cc778c30485a3b85c69c0aa62724f` |

All signatures and exact committed file contents were verified. The local browser contains both fixes. There are 133 accepted committed fixes; repair 120 remains held and excluded. The earlier history is retained on `refs/heads/backup-easing-metadata-20261027-62cc7a837a22`. Unfinished source work and binaries were preserved during the rewrite.

The cubic comparison repaired 28 observed failures; all 38 targets pass, 75 controls remained exact and all 113 baseline outcomes returned after restoration. The final installed build reproduces 110 PASS/3 FAIL with the corrected expectations. One unrelated stale expectation belongs to fix 121 and is queued for correction. These runs used the experimental owner branch; no clean upstream-only browser result is claimed.

The steps library transfer and provider host recipe are prepared and remain unapplied. Canonical Lean counts are unchanged. Nothing was pushed or submitted.

The [unfinished-work recovery snapshot](../css-unfinished-work-checkpoint-20261027-v3/README.md) preserves 131 remaining project files with verified patch application, exact bodies and reversal. These prototypes remain uncommitted in their native locations for continued development.
