# Ownership refinement replay receipts

Canonical and manifest-only relocation both compile the frozen 35-input source capsule, audit 74 declarations and reject five semantic falseclaims. Eleven integrity negatives reject before output creation. Development logs preserve the initial indentation failure and deprecated-name warnings; final canonical and relocated builds are clean. The preflight used an earlier omitted-length mutant definition; final executions use the frozen definition and pins in SOURCE-PINS.json.

The relocated source copy is retained exactly. Completed owned Lean outputs were removed only after logs and results were retained; CLEANUP.json records 32 files and 9,414,560 bytes. A new replay needs no generated outputs from this directory: run relocated-capsule/check.py with its external manifest hash and a fresh external output.

This receipt verifier authenticates retained evidence, not a new kernel run. Invoke with `python3 -I -S /absolute/verify.py --files-sha256 EXTERNAL_RECEIPT_FILES_SHA256`. Native representation/event completeness and captured-pointer lifetime remain open.
