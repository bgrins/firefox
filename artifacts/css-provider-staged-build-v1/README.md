# Staged provider build

Disabled while the actual partial-v5 source transition is pending. This prepares the existing guarded `mach build binaries -j2` workflow with the exact staged36 epoch guard, not an empty-index projection. Actual v5 source pins and installed epoch must be bound after the root transition completes. One dirty native path is expected; ownership retains the restored cascade path. No build is executed here. Build errors and binary/epoch publication failures require truthful recovery rather than claiming the old binary is intact. Old v26 signing helpers remain historical.
