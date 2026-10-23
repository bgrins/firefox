# Hidden flex child-subtree proof

REPORT.md and capsule/SCOPE.md describe the bounded result and open caller obligations. The candidate is the single MarkPrincipalChildrenDirty call at the hidden ReflowChildren return, not the earlier direct dirty mark.

Authenticate the outer artifact using its externally supplied FILES pin:

```sh
python3 -I -S verify.py --manifest-sha <outer FILES sha256>
```

Replay from the canonical capsule or a manifest-only relocated copy:

```sh
python3 -I -S capsule/replay.py --manifest-sha e93989395671b1edb1b9586d77a9898596c526ef4a8b1f0a18df12ccbaf25452 --out /absolute/fresh/outside/output
```

The local Lean and clang binaries/versions are pinned; installed libraries and SDK remain dependencies. The runner verifies its closed 22-payload roster, regular files, source roles, imported model identity, proof escape restrictions and exact audit roster. It removes owned executable/olean products after recording evidence. It does not modify native source or run a browser/build.
