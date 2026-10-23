# Installed Firefox column-probe attempt

Incomplete startup; no test verdict. The isolated WPT browser never reached readiness and emitted no subtest or test-end events. After the harness reported forcibly terminating its runner without finishing, root sent SIGINT only to the authenticated owned mach process. WPT exited with a BrokenBarrierError; this is retained as an infrastructure failure, not a column-query result.

The eight-case ordinary-block/table-width fixture was unchanged. The temporary WPT was removed, all input hashes stayed stable, and a final process-group inspection found no members. The installed application's application.ini and binary hashes identify the attempted browser. The run_info's other build flags partly describe the local harness/build and must not be treated as installed-browser feature evidence.

This attempt does not establish an independent release-browser trigger, absence of one, or a native hang. It ran during the local restoration build and contains no timing measurement. The separate compact local experiment's completed WPT outcomes are unaffected.
