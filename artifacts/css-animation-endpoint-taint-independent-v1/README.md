# Replay

Externally authenticate FREEZE.json, MANIFEST.json and check.py before executing. Run `python3 -I -S check.py` to authenticate the closed package and validate retained baseline evidence. Add `--replay` to rerun the authenticated proposal checker (Node syntax plus temporary source patch application/reversal only). It performs no Firefox build or browser run. The complete proposal dependency is copied under proposal/ with original seals unchanged. The supplement files were separately read from the review checkout and are not historical-upstream claims.
