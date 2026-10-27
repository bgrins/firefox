# Compact animation owner host validation

The already-applied owner/borrow composition passes the actual Gecko dependency metadata, header export, binary build and all 17 selected native tests. No source patch was reapplied. APPLIED.json binds the composed 18 changed files and ten preserved prerequisite files. The corrected borrowed source retains the existing 32-byte ApplicableDeclarationBlock assertion.

The selected tests cover arena arithmetic and differential behavior, retained sample lifetime/identity, compact owned/borrowed layout, endpoint association, bulk metadata and the two live-presentation regressions. Every selected name has a paired TEST_START/TEST_END PASS event. Both GTest-library copies match. Source, nested-library and root-index preservation checks pass; normal and GTest binaries intentionally change to this build. The known mach build-monitor KeyError export tracebacks remain in the successful binary-build log.

This is an experimental concrete-owner milestone. It does not implement current-provider recipe resolution, close animated-cycle or memory-reporting obligations, establish non-Gecko compilation, or add an accepted browser fix. The exact 166-subtest and two-crash browser comparison is the next gate. Arc primitive tests are separately recorded in compact-borrow-unit-runtime-v3; their success is an explicit prerequisite of this host run.
