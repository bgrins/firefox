# Typed fallback eligibility component

Artifact-only source design and small universal Lean component; no native/WPT edits or browser/build actions by this agent.

Read DESIGN.md for the proposed shared primary parser, exact occurrence context, readiness refutation and remaining admissions. Existing root browser evidence is retained separately. Complete locally frozen custom/cascade sources plus indexed and actual local parser/caller sources are pinned, with their differences and provenance explicit.

Run `python3 replay.py` for integrity/source binding. For a fresh kernel check, use `python3 replay.py --lean /absolute/path/to/lean --output /new/output/directory`. The pinned Lean 4.35.0-rc4 Darwin aarch64 binary is available in artifacts/stylo-bloom-tools. Replay compiles source in an isolated temporary directory, checks 15 theorem audits, and rejects two semantic mutations. It does not execute a native parser or claim native proof extraction.
