# Ahom narrow-backport companion inventory

Use `companion-paths.txt`: the complete 7,497-file candidate replay capsule, 21-file primary-source adjudication capsule, this report/guide, and root's completed full-replay receipt/log. Do not stage whole research parents or generated build trees. The full language proof is not accepted by this companion.

Candidate manifest: `336dffbe6116e4e0c6233467019ab3e0ebcc0b3d860ac563937aaa4252c31e0c`.
Adjudication manifest: `3006affbbffae8bed60d1b508e6fb732e83ec98908e41a3081015a11bef67db0`.

Copy exactly each capsule manifest's `files` plus its MANIFEST.json/FREEZE.json to a fresh directory, preserving relative paths. From outside the repository:

```sh
python3 -I -S -B /absolute/fresh/ahom-candidate-native-v1/check.py --manifest-sha 336dffbe6116e4e0c6233467019ab3e0ebcc0b3d860ac563937aaa4252c31e0c --replay
```

Without `--replay`, this command authenticates and source-binds only. Complete replay builds original and candidate offline Cargo dependencies, actual ICU/Gecko providers and complete breakers, reuses the fixed corpus and runs both Lean gates. It writes only generated directories inside the copied capsule. Do not substitute an existing generated build tree.

The exact tool paths and hashes are pinned in `imports/complex-encoding-diagnostic-v1/TOOLS.json`: stable aarch64-apple-darwin cargo/rustc, Apple clang, and Lean 4.35.0-rc4. Their installed distributions and the SDK/system libicucore plus CoreFoundation/Security frameworks are external dependencies. The capsule vendors Rust source and uses `--locked --offline`; it does not use a Gecko objdir or live source. Tool path relocation would require a separately authenticated adaptation, not silent manifest editing.

Root's independent complete replay passed. After root records scoped acceptance, commit this companion before `css-ahom-lf-partition-probe-v1/fix-utf16-complex-v1.patch`, SHA-256 `b666b8ab3f4a1d02a07682b5d273e76820c81a35fcee79ff4230078d27b6d595`. The native commit contains only line.rs, its Cargo checksum and complex-prefix-lf-partition.html. Describe it as a narrow correction of the vendored mechanism already structurally fixed by ICU4X PR 8144. Do not combine it with language, hyphenation or other pending native repairs.
