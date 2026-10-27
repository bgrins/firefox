# Scroll conversion reproduction

Eight cases and all 32 phases calibrate exactly. First, repeated and restored scroll dimensions match six cases and fail the two large-plus-nine cases: scrollWidth/scrollHeight report 8388610 instead of 8388609. Resetting padding recovers all eight. Client dimensions and client origins match all cases in every phase. Repeat and restored observations are stable.

Session 17339 exited zero. The run used the restored mixed working browser, with no native changes, rebuild or WPT installation. Source/resource/binary/index snapshots are unchanged; process-group cleanup and profile removal succeeded. This is not a release-browser or clean-upstream comparison.

The result confirms the shared final integer-conversion defect family. Consolidate with the still-unaccepted offset repair rather than count an additional bug. The expanded native patch and 32-case WPT still require build and paired browser validation.
