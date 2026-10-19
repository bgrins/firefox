Authenticate FREEZE.json and MANIFEST.json against the handoff, then run:

```
python3 check.py --output /absolute/new/directory
```

This authenticates before executing helper scripts, replays the imported source checks, regenerates independent runners and executes the 504-case challenge. Add `--benchmark` for a new timing run; timings have no pass/fail threshold and do not measure Firefox. Compiler identity is pinned in TOOLCHAIN.json; the sysroot/linker/OS remain trusted. All mutations/build outputs stay under the requested new output directory.
