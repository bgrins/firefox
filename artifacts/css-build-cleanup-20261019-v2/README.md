# Second completed-target cleanup

Removed six inactive Cargo targets totaling701,792KiB (685.344MiB): two from
the completed root Ahom replay and four from historical URL component replays.
Exact target paths, completed receipts and regeneration commands are retained
in `../css-completed-target-inventory-v2/`.

Root authenticated the inventory, source manifests and completed receipts,
confirmed no matching processes or open files, and verified no tracked files
were inside the targets. It removed only those six generated target directories.
All9,252 distinct source/evidence files checked before and after remain identical.
`LIVENESS.json` and `RESULT.json` retain the completed operation.

Together with batch1, root removed ten Cargo target directories representing
1,930,656KiB (about1.84GiB) of allocated outputs. Net filesystem free space was
not measured. Active Firefox builds, ongoing parser replays, source, toolchains,
vendor caches, logs and result receipts were preserved.
