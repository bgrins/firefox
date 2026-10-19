# Private-use text emphasis: raw dispatch companion v2

This artifact connects Unicode flagging to ordinary emphasis draw calls through raw glyph words, UTF-16 units, font-run selection, ligature shrinking, spacing providers and signed advances. It preserves the original approved [SCOPE](SCOPE.md). The original companion remains immutable.

**Freeze rule:** this directory is a prepared implementation until `FREEZE.json` records successful canonical and relocated authenticated replays. Independent acceptance is a separate root/reviewer decision.

- [REPORT.md](REPORT.md): contracts, evidence and limits.
- [BRIDGE.md](BRIDGE.md): exact native/model/provider boundaries.
- [V1-DELTA.md](V1-DELTA.md): the missing v1 dispatch theorem and its correction.
- [TextInput.lean](TextInput.lean): original raw inputs through the complete dispatch contract.
- [SignedLigature.lean](SignedLigature.lean): separately named signed apportionment contract.
- [negative-review/REPORT.md](negative-review/REPORT.md): independent review of root's separate negative-advance repair.

## Replay

Read the externally supplied manifest and checker hashes from the handoff. Authenticate `check.py` itself before executing it. Then run:

```
python3 -I -S -B check.py --manifest-sha MANIFEST_SHA --output FRESH_OUTPUT
```

The checker rejects unlisted files, shadow packages/modules/bytecode, aliases, duplicates, path escapes and symlinks before importing project code. It copies only authenticated bytes into a fresh read-only source capsule and rechecks the exact inventory there. Every native executable and Lean object is rebuilt from source. Toolchain identities are checked against `TOOLCHAIN.json`; the external compiler/Lean distribution and SDK remain trusted tools.

No browser, Firefox build, Git operation or network access is needed for replay. Root's retained browser receipts are evidence reviewed offline; replay does not reproduce those browser executions. `development/` and `replay-v2/` are excluded from source authentication and never imported into the capsule.

The input corpus includes 887 preserved ordinary cases, 784 signed/legacy geometry cases per four classifier/arithmetic variants, 17 preserved native semantic mutants and five separate arithmetic mutants. Arithmetic fragment rows are counted separately from complete ordinary consumer entries. Full Unicode/ICU and UTF-16 checks remain intact.
