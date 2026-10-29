# Full Servo type check with an explicit documentation-lint exception

Runtime4 baseline Cargo exited101 on the sole reported style error:
missing_docs for the shared held handle_invalid_at_computed_value_time function.
It reported no type/API error in that attempt; candidate was skipped. The
original failure and all source/closure inputs remain preserved.

This successor uses the same sealed closure-v4 and unchanged run.py. The only
policy changes are fresh runtime5 and
RUSTFLAGS="--force-warn missing_docs". No native source, crate-level lint
attribute, global --cap-lints option, or RUSTC_BOOTSTRAP setting changes.
The policy converts the missing_docs lint into a warning while retaining type
checking and other error diagnostics. It does not establish that the original
strict baseline compiles.

Small isolated fixtures ran on the exact pinned rustc1.92.0 executable. A
deny(missing_docs) fixture fails without the flag and succeeds with a warning
under it. A genuine mismatched-type fixture still fails with E0308. A fourth
control confirms that force-warn also enables this warning over an explicit
allow(missing_docs). Exact source, argv, tool hash/version, diagnostics, and
exits are retained under fixtures/ and fixture-results/. All temporary metadata
was removed. These fixtures are not a full style compile.

The flag is lint-specific, not source-location-specific: RUSTFLAGS reaches
dependency compilations too and may expose additional documentation warnings.
WARNING-REVIEW.md is a required interpretation step after root execution.
Cargo exit0 and the runner's preservation success alone do not certify that
the warning comparison is acceptable. Only the already observed shared style
documentation warning is preaccepted; all candidate warnings require review.

Root alone runs the full baseline, then candidate only on baseline success.
The command remains --locked --offline -p style --lib --no-default-features
--features servo --jobs1, no debug/incremental output. Limits remain900 seconds
per phase,24 GiB minimum free space,1.5 GiB target growth, and0.5-second polling.
Owned process cleanup and exact source/dependency preservation checks remain
unchanged. Outputs and the shared phase target reside only in runtime5.

The seven baseline/candidate source differences and held provider SHA256
2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774 remain exact.
This is an adapted local-configuration type check under an explicit lint policy,
not native acceptance, clean-upstream validation, or runtime behavioral proof.

```sh
python3 -I -S -B artifacts/css-contextual-easing-servo-compile-v6/run.py --check <FILES-sha256>
```

After reviewing the policy and warning requirements, root may substitute
--run. No full compile or runtime5 creation occurred during preparation.
