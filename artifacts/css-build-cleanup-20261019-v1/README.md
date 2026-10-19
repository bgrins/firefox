# Completed build-target cleanup

Removed four inactive Ahom validation Cargo targets totaling 1,228,864 KiB
(1.172 GiB of allocated output reported by du). This is not a measurement of
net filesystem free space during concurrent work.

The frozen inventory identifies ownership, source manifests, regeneration
commands and retained result receipts. Root checked process command lines and
open files, found no active users, verified no tracked files were inside the
targets, then removed only the four exact output directories. All 14,994 retained
source/evidence files checked before and after match their authenticated hashes.
Active Firefox object directories, parser replays, vendor caches, toolchains,
source capsules and execution receipts were preserved.

`LIVENESS.json` and `RESULT.json` record the checks and completed removal. The
inventory is `../css-completed-target-inventory-v1/`. Its report describes the
pre-removal observation; this completed record supersedes its pending-action
status without rewriting the frozen inventory.
