# Fallback preparation proof and independent review

Read REPORT.md for proof scope and source admissions. Native-review-v1 is separately sealed for bounded native acceptance and retains exact paired test receipts.

`python3 replay.py` checks integrity, native patch reconstruction and source bindings. Fresh proof replay: `python3 replay.py --lean /absolute/path/to/lean --output /new/output/directory`.

The pinned Lean 4.35.0-rc4 Darwin aarch64 executable is under artifacts/stylo-bloom-tools. Replay needs Python and system patch; proof mode additionally needs that Lean binary. All proof source dependencies are included. Temporary compilation and patch application never read or mutate live native files.
