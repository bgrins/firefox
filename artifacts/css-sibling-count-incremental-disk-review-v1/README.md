# Incremental sibling-count build disk budget

The completed one-source build used the existing 30 GiB admission / 15 GiB running stop. Ninety-two actual samples show a 1,809,805,312-byte peak draw (about 1.686 GiB), exceeding the older 1.438 GiB history. Its successful terminal does not justify silently changing future guards.

Root proposes an experiment-local 29 GiB post-backup admission for the same one-source binaries -j2 incremental job, retaining the 15 GiB running stop. At that admission threshold the 14 GiB gap is more than eight times this observed peak draw. This is a bounded planning estimate, not a guarantee. No policy or helper has been changed or executed here; a future reviewed successor must align every owner admission check and its private builder helper before execution.

A metadata-only check of the already inventoried symbol paths found only the remaining entries listed in OBSERVATION. Their combined size does not cover the current 30 GiB-plus-backup shortfall. This does not establish that no other obsolete output exists. No broad directory search, deletion or new target directory was performed. The earlier exact two-bundle cleanup is retained separately; no full objdir cleanup is proposed.
