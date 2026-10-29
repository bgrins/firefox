# Servo check after correcting vendor patch declarations

This runner targets sealed `css-contextual-easing-servo-closure-v2`. The prior
baseline stopped with Cargo exit 101 on Firefox's patched autocfg directory
source; the candidate was skipped. The successor closure carries the seven
genuine root path-patch declarations omitted by v1, with tracked provenance
and an audit of all selected directory-source checksums. No source or vendor
checksum was rewritten. See the closure's `PRIOR-FAILURE.json`,
`TRACKED-PATCH-PROVENANCE.json`, and `DIRECTORY-SOURCE-AUDIT.json`.

`run.py` is byte-identical to compile-v2. `POLICY-DELTA.patch` changes only the
closure location, its seal, and the output directory to the initially absent
`artifacts/css-contextual-easing-servo-compile-runtime-2`. The compile command,
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

The closure verifier checks exact inventories and source roles, the repository
manifest and patched-file provenance, and all 127 directory-source packages'
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
python3 -I -S -B artifacts/css-contextual-easing-servo-compile-v3/run.py --check <FILES-sha256>
```

After reviewing the capsule and available resources, root may substitute
`--run` with the same seal. The result will be
`artifacts/css-contextual-easing-servo-compile-runtime-2/RESULT.json`.
Targets are retained after either success or failure for inspection.
