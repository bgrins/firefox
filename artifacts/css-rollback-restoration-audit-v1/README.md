# Independent rollback restoration audit

Actual audit `f30b09/session28561/19dfb4` exited 0 after native owner `f447ff/session38186/3e06a3` exited 0.

Independently verified the two restored source hashes and inode identities, all three intentional ArcSlice working-file hashes, unchanged stylist context, current HEAD, index entries, staged binary diff, and unrelated working diff against the fresh experiment records.

The audit rescanned all 9,378 application entries and three extra files; their semantic inventories match APP-BEFORE and EXTRAS-BEFORE. File contents, modes and symlink targets are preserved; replacement-file inodes and hard-link counts are not asserted. The source-transition lock and owned backup directory are absent.

Elevated read-only process censuses before and after the file audit found no recorded PID or member of groups 56666, 56667, 62219, and 62650: build, wake helper, primary WPT, and control WPT. Each census calibrated against the audit process itself.

Recorded primary observation is 80 PASS. Controls retain 5 PASS and the same 2 FAIL callbacks. These recorded outcomes do not replace the separate raw-event comparison or establish fix acceptance. No obsolete canonical epoch was consulted. No source, application, index, roadmap or previous artifact changed.

`audit.py`, `RESULT.json`, `audit.log`, and `EXECUTION.json` retain the checks and actual execution evidence.
