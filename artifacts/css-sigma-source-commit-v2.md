# Sigma companion source commit, refreshed packaging

Commit the 72 files in `css-sigma-source-only-v2` selected by its 70-entry `MANIFEST.json`, plus `MANIFEST.json` and `FREEZE.json`, and this guide. The exact 73-path inventory is `css-signing-resume-20261019/sigma-source-only-addendum/companion-paths.txt`. Exclude `development/` and all generated replay directories, objects and executables. The frozen source capsule includes the historical proof and native/browser acceptance records; no original live-tree dependency or old build object is needed.

Manifest SHA-256: `e16a137ba21cbca48d461e8a91f79002916cccd18b62ce46bff453b6ec455924`.

From the capsule directory:

```sh
python3 -I -S -B check.py --manifest-sha256 e16a137ba21cbca48d461e8a91f79002916cccd18b62ce46bff453b6ec455924 --lean /absolute/path/to/lean --output /absolute/path/to/new-output
```

Use the accepted Lean 4.35.0-rc4 and Apple clang toolchain identities described in its README. `--authenticate-only` checks pins without compilation. Replay compiles complete pinned ICU sources, invokes unchanged accepted helper/proof routines, and checks equality of all original semantic results. The final isolated replay passed; helper and ICU table tampering are rejected before imports. Full result and packaging evidence remain in the signing addendum, separate from the source commit inventory.

After root reviews this refreshed package, commit it before the separate minimal native/WPT patch `css-sigma-fix-v1/fix.patch` (SHA-256 `a9a1e0dbbc4f89200e5bdd4238e0d51068f593bd7ea0be76152bf45a89162e02`). That repair's original formal/browser acceptance remains unchanged. This refresh makes no new caller, whole-Gecko, platform or performance claim. Do not modify or replace the original sealed v1 artifacts.
