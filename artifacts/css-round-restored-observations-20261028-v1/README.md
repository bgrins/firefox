# Restored Round observations

The saved local Firefox 160.0a1 MCP observation contains eight parse-bound numeric rows and 224 nonfinite snapshots (14 operand pairs, four strategies, four font states). Independent replay reproduces the existing ANALYSIS.json exactly: five numeric differences, 37 known nonfinite differences, no calibration failures, and no resolved-reference differences. All probe frames were removed.

Run `python3 -I -S -B artifacts/css-round-restored-observations-20261028-v1/analyze.py` from the repository root. The analyzer validates the exact roster, authored/resolved expressions, encoded nonfinite oracle, calibration fields, repeated reads, difference rows, probe hashes, and saved PRE/POST equality. It reads saved artifacts only.

BROWSER.json identifies the local headless Nightly binary. TOOL-RESULT.json records the MCP result provenance; raw.json is the root-captured full result. PRE.json and POST.json agree on eleven selected source, binary, configuration, probe and epoch records, including the application.ini symlink. This is selected recorded preservation, not a new live index or process census. Generic calc.rs is the restored b9a36918 base, not the proposed arithmetic candidate.

The numeric differences are precision-qualified comparisons against the probe references, including an exact dyadic multiplication reference; they do not establish a universal CSS binary32 precision requirement. The nonfinite differences reproduce known open classification boundaries: 16 contextual-infinity, five contextual-finite/infinite-step, and 16 infinite/contextual-step observations. They are not 37 distinct bugs. Prior-art reconciliation is recorded in css-round-numerical-prior-art-reconciliation-v1.

This is a diagnostic browser observation, not WPT execution, native candidate acceptance, a new discovery claim, or an accepted-fix count increase. Existing raw evidence and analysis files were preserved unchanged.
