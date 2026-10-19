# Validation research capsule

Read `REPORT.md`. This is a proposed assurance program, not an implementation or proof acceptance.

`python3 -I -S check.py` authenticates the closed local file inventory, copied historical evidence and retained receipt counts. Run from any directory using the script's path. It does not execute a browser, compile code or revalidate the web sources. `SOURCES.json` records primary-source retrieval references checked on 19 October 2026; editor drafts remain mutable and a future formal profile must archive exact content/revisions.

`LOCAL-INPUTS.json` identifies historical project sources and byte-identical copies. The display excerpt has a whole-file provenance hash but is only discovery evidence. Neither whole-file equality with future live code nor native correctness is asserted.

`FREEZE.json` binds `MANIFEST.json`, which binds every other file. External review should pin the freeze digest before executing this checker. Generated checker output belongs outside this sealed directory.
