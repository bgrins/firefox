# Replay and inventory

After checking the externally supplied review FREEZE/MANIFEST hashes:

```sh
python3 artifacts/css-parser-depth-recovery-formal-independent-v1/check.py
python3 artifacts/css-parser-depth-recovery-formal-independent-v1/check.py --replay-output /private/tmp/depth-formal-review-new
```

Use a previously nonexistent output path. The second command authenticates all source inputs, creates a source-only relocation, and runs the complete producer replay. It requires Python 3 and the exact Rust 1.92.0, Lean 4.35.0-rc4 and Node binaries in producer TOOLCHAIN.json. No network, browser, Mach, Git or retained compiler products are required.

PRODUCER-COMMIT-FILES.txt is the exact 178-file source/evidence roster. REVIEW-COMMIT-FILES.txt is this review's exact roster. PRODUCER-PINS.json authenticates the first roster. Final browser/WPT review is separate; FINAL-SOURCE-BINDING.json binds the root's final source snapshots to this formal candidate.
