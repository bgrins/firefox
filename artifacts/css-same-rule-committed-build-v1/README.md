# Browser built from the committed same-rule fix

The bounded local build completed successfully at source commit 0f18d294fbacd5eb2fdb3b8cea07f8fe4a7e831b. The application at objdir-full.noindex/dist/Nightly.app is intentionally left at this committed implementation, replacing the earlier restored A+B+D baseline application. Run it with ./mach run or open that app for manual testing.

Actual execution: launch876591, session64253, terminaleb9919, exit0. RESULT.json pins the resulting executable, XUL and application.ini, and confirms selected source/test bytes, HEAD/index and tracked diff were preserved. Both owned build/wake groups were cleaned up and the exclusive build lock removed. No recovery backup or temporary source overlay was used. The underlying builder reported successful compilation with zero compiler warnings; the pre-existing Mach export-monitor callback traceback remains in the full log.

The committed Rust source bytes are identical to the earlier candidate that passed 190 regression checks, six occurrence checks and unchanged controls. The final build did not repeat those tests: this operation installs the already validated source into the local application. Synthetic performance limits and the explicit #163 source prerequisite remain documented in the preceding research. No remote action occurred.
