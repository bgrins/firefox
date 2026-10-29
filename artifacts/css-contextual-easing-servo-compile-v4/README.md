# Servo check with authoritative support tables

This runner targets sealed `css-contextual-easing-servo-closure-v3`. Runtime2
reached style, then baseline exited 101 on three missing preference macro arms
and the missing `part` local name; candidate was skipped. The successor adds
three explicitly sourced boolean preferences through the unchanged real
generator and selects unmodified published web_atoms 0.1.3. All native Rust
remains unchanged. See closure-v3/README.md and SUPPORT-PROVENANCE.json.

`run.py` is byte-identical to compile-v3. `POLICY-DELTA.patch` changes only the
closure location, its seal, and the output directory to the initially absent
`artifacts/css-contextual-easing-servo-compile-runtime-3`. The compile command,
environment, lint policy, resource limits, and process cleanup are unchanged.
This capsule has not executed Cargo or queried tool versions. Six simulated
race tests passed without compiler execution or actual process signals.

After root review, the runner captures actual tool versions, verifies both
source trees and all selected dependencies, then checks the complete baseline
style library using `--locked --offline -p style --lib --no-default-features
--features servo --jobs 1`. It checks the candidate only after baseline success.
There is no lint cap, incremental cache, or debug information. The two roles
reuse one owned target outside the sealed closure. Owned Cargo home and temp
directories, command receipts, combined logs, exits, and resource samples all
remain in runtime2. Existing runtime directories are refused.

Each compile phase has a 900-second deadline. Samples every 0.5 seconds stop
the owned process group below 24 GiB free space or above 1.5 GiB target size
(the larger of apparent and allocated regular-file bytes). These sampled
limits are not filesystem quotas. The runner sends TERM then KILL if needed,
waits, and asserts group absence; disappearing temporary files are tolerated
only during live polling. Initial and final resource samples remain strict.

The closure verifier checks exact inventories and source roles, support input
hashes, the repository manifest and patched-file provenance, and all 127 directory-source packages'
checksums before/after each phase and during final cleanup. Its output describes
verification only; phase results separately establish compilation. Preservation
failure prevents success. A baseline failure establishes no candidate claim.

This checks the captured local configuration, not clean upstream. Both roles
retain the shared held `servo/components/style/custom_properties.rs` at
`2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774`,
and differ only in the seven captured contextual-easing style files. That
shared change remains unaccepted; the result keeps `native_fix_acceptance`
false. No runtime behavior is established. The runner does not write native
source, Git/index, app, or canonical epoch paths, and refuses the source
transition lock required absent by policy.

Authenticate without execution:

```sh
python3 -I -S -B artifacts/css-contextual-easing-servo-compile-v4/run.py --check <FILES-sha256>
```

After reviewing the capsule and available resources, root may substitute
`--run` with the same seal. The result will be
`artifacts/css-contextual-easing-servo-compile-runtime-3/RESULT.json`.
Targets are retained after either success or failure for inspection.

The prior runtime2 target remains untouched. A fresh target in runtime3 avoids
migrating evidence or changing the reviewed lifecycle; the previous full check
used about 178 MB and reached its baseline error in 39.46 seconds. That is an
observation, not a prediction or a relaxed limit. Support-table adaptations
are explicit full-type-check inputs and do not validate runtime behavior.
