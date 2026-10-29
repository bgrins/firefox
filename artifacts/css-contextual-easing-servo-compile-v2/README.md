# Full Servo compile runner

Prepared for root execution after the 315-test Firefox pair has restored its
sources/app and released its source-transition lock. This capsule has not run
Cargo, queried tool versions, or created its runtime/target.

This checks the captured local style configuration, not clean upstream. Both
copies retain the shared held `servo/components/style/custom_properties.rs`
payload with SHA256
`2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774`.
The baseline/candidate comparison still differs only in the exact seven
contextual-easing source roles. The shared held payload is checked explicitly
before/after and recorded in the final result; it is not newly accepted here.

The runner authenticates the sealed dependency closure, captures actual Cargo,
Rust compiler, Python, and Mako versions, then runs full `cargo check` of the
baseline style crate. It runs the candidate only if the baseline succeeded.
Both commands use `--locked --offline -p style --lib --no-default-features
--features servo --jobs 1`, no incremental cache, and no debug information.

All outputs go to the initially absent sibling directory
`artifacts/css-contextual-easing-servo-compile-runtime-1/`. Its `target/` is reused
between baseline and candidate; its Cargo home and temporary directory also
live there. The sealed closure remains unchanged. The runner refuses an
existing runtime and retains its output for review; it does not clean up or
reuse a previous invocation's directory.

Each compile phase has a 900-second deadline. A resource sample every 0.5 seconds
stops the owned process group if free space falls below 24 GiB or the target
exceeds 1.5 GiB, using the greater of apparent and allocated regular-file bytes.
The target begins absent, so that cap bounds growth for the whole invocation,
including both phases. These are sampled limits, not filesystem quotas; a write
can briefly cross a limit before the next sample terminates the group. TERM is
followed by KILL after five seconds if necessary, and group absence is checked.
SIGINT/SIGTERM to the runner also stop its owned group. No unrelated process is
intentionally signaled.

The authenticated closure verifier checks both exact workspace trees and all
resolved dependency source pins before and after each compile phase and during
final cleanup. It also checks that default targets inside the closure remain
absent. Large inventories are referenced from the closure rather than copied.
The runner itself writes no native source, repository manifest, Git/index, app,
or canonical-epoch path. Source preservation failures are explicit in the final
result and cannot produce success.

Each command records its argv, working directory, explicit environment changes,
process-group receipt, combined log, resource samples, exit, stop reason, and
cleanup status. Tool-version logs are kept separately. The root `RESULT.json`
reports candidate skipping and keeps `native_fix_acceptance` false. A failed
baseline establishes no claim about the candidate. Target files are retained
after success or failure for root inspection and eventual cleanup.

Authenticate without execution:

```sh
python3 -I -S -B artifacts/css-contextual-easing-servo-compile-v2/run.py --check <FILES-sha256>
```

After root resource review and Firefox-pair restoration, root may substitute
`--run` with the same seal. Version queries have 30-second deadlines. The final
result path is
`artifacts/css-contextual-easing-servo-compile-runtime-1/RESULT.json`.

## Version 2 corrections

`RUN-DELTA.patch` records the two race fixes and the receipt clarification.
During active Cargo polling, a file that disappears between directory traversal
and `lstat` is skipped only on `FileNotFoundError`. Initial and final post-exit
resource samples remain strict. A group disappearing between the liveness probe
and signaling is tolerated only on `ProcessLookupError`; process waiting and
the final group-absence assertion still run. Other errors remain failures.

The sealed verifier text is unchanged. Each caller receipt explicitly scopes
its output to the verifier's own behavior; compile execution and success are
reported separately in the phase results. Resource, command, and lint policy
are byte-identical to v1, including the same initially unused runtime1.
`test_races.py` exercises simulated disappearing files and process groups without
invoking Cargo, a compiler, or actual process-group signaling.
