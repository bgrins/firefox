# Installed release font-metric observation

Runs the three calibrated font-demand callbacks against installed Firefox158 using the existing executed installed-browser lifecycle. Only fixture paths, input pins, expected callback count and temporary prefix change; the stale prior-run restoration receipt is replaced by requiring no active native transition. No native code or application update is performed. The installed application is identified by critical file hashes and metadata, with a fresh WPT stable profile. Raw run_info may retain local harness mozinfo; only browser-specific fields identify the installed release.

Input staging reuses the existing prepare_inputs helper with six exact resources and a genuine manifest. Font files are served locally. Complete FAIL callbacks are retained, and font-loading/calibration failures must be distinguished from metric mismatches. No browser outcome is predicted. Root executes run.py --run and retains the terminal evidence.
