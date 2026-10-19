# Replay

Externally authenticate FREEZE.json, MANIFEST.json and check.py before execution. Run `python3 -I -S check.py --output /absolute/fresh/external/directory`. TOOLCHAIN.json and its pinned library inventory identify the installed Lean executable. All source inputs are in the manifest. No live Firefox tree, Git, browser, network or predecessor output directory is required. Source-only manifest relocation is supported.

IMPORTS.json records exact retained module origins; provenance contains the sealed predecessor manifests and freezes, not their complete capsules. The checker verifies imported module membership/hash against those manifests and the manifest hash against each retained freeze. External authentication of this capsule remains necessary. This does not rerun or impersonate predecessor checkers.
