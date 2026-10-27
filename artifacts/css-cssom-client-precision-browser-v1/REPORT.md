# Larger client-size reproduction

All eight cases and 32 phases calibrate exactly. In both large-plus-17 cases, clientWidth/clientHeight report 16777218 instead of the independently calibrated 16777217. First, repeated and restored measurements reproduce the two mismatches; reset recovers all eight. The current unmodified scroll path has the same two observed mismatches. Client origins pass all zero controls; no large client-origin witness was tested.

Session 9538 exited zero. Source/resource/binary/index snapshots are unchanged, with successful process-group cleanup and profile removal. This is the restored mixed working browser, before installing fix 112; it is not a release-browser or clean-upstream comparison. The 14-result proposed integer model preserves the client tie policy, but no client native repair is installed or accepted. This follow-up does not increment the accepted-fix count.
