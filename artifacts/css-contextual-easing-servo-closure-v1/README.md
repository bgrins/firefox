# Isolated full Servo style dependency closure

Dependency resolution succeeds offline for both `baseline/` and `candidate/`.
They contain 412 files each and differ only in the seven exact style source
captures listed in `SOURCE-ROLES.json`. The Gecko glue eighth capture is outside
this Servo crate. No repository source/manifests, root Git/index, app, canonical
epoch, or committed prerequisite note was modified.

This resolves the dependency setup gap from the prerequisite note. It does not
establish compilation success: only `cargo metadata` ran, and no target exists.
There are 152 packages in the resolved graph; `style` enables `servo` and does
not enable `gecko`. The shared lockfile SHA256 is
`c71226ac9ba1fb7a13b7f724df5bd22ec9f6ffa67d6d7a6738c718a8a1f27387`.

## Actual compatibility adaptations

`MANIFEST-ADAPTATIONS.patch` records all changes to copied crate manifests.
No copied native Rust source or imported API implementation was changed or
stubbed. The baseline and candidate use identical adaptations:

- Remove unused `servo_config`; the current source has no references to it.
- Remove `arrayvec/use_union`; the available arrayvec 0.7.6 has no such feature.
- Remove disabled Gecko dependencies and use the real `stylo_static_prefs`
  0.22.0 package in place of Gecko's build-dependent static-prefs package.
- Use Servo's `thin-vec/serde` configuration in place of `gecko-ffi`.
- Supply the real published `stylo_atoms` 0.22.0 source, with its manifest pinned
  to `string_cache = 0.8.9` and `string_cache_codegen = 0.5.4`. Its `lib.rs` and
  `build.rs` are byte-identical to the published 0.7.0 package that declares
  those dependency major versions. Its newer atom table supplies required names
  such as `pointer`, `hover`, and `match-element` absent from 0.7.0. This changes
  only the support manifest, retaining real atom generation and concrete types.
- Pin `web_atoms = 0.1.0`, which uses string_cache 0.8. The currently newest
  0.1.4 release uses string_cache 0.9 and would introduce incompatible atom types
  for the local malloc-size/to-shmem implementations.

The standalone root manifest also carries existing Firefox shims for itertools,
ICU segmenter data, hermit-abi, Windows targets, Redox, getrandom, and WASI. These
are existing dependency implementations, not replacements invented for this
check. Gecko-only manifests and imports remain disabled by the selected feature.

The published support revisions are:

- `stylo_atoms 0.22.0`: `34d25f741765a0bdb894f8271852e633299352d8`.
- `stylo_static_prefs 0.22.0`: the same revision.
- Dependency compatibility comparator `stylo_atoms 0.7.0`:
  `64d8521f1b8509a0160a89e24d0ace2883fa3269`.

The downloaded `.cargo_vcs_info.json` files and crate checksums record these
identities. `DOWNLOADS.json` records 167,400 compressed crate bytes in total,
including inspected versions that were not selected. Public manifests/history
were also fetched with bounded reads. No full repository was downloaded.

## Reproducible inputs and verification

`BASELINE-FILES.json` and `CANDIDATE-FILES.json` pin the two workspace trees.
`RESOLVED-SOURCES.json` pins every file of every selected package. Existing
vendored crates are exposed by read-only symlinks; fetched and cached additions
reside in the owned `vendor/`. `CACHED-COPIES.json` records copied cache sources.
The older `BASELINE-SOURCE-HASHES.json` records initial copy inputs before
manifest adaptation; the final workspace manifests are in `BASELINE-FILES`.

`metadata-attempt-11.json` and `candidate-metadata.json` are the successful
resolution outputs. The candidate used `--locked --offline`; both selected
`--no-default-features --features servo`. Earlier attempt logs explain the
dependency additions, including an enforced cache-copy size limit. Run the
read-only verifier with:

```sh
python3 -I -S -B artifacts/css-contextual-easing-servo-closure-v1/verify.py
```

## Compile command after root resource review

Do not start this until the root owner has admitted a target/disk budget after
the active Firefox experiment. Setup occupies about 16 MiB of owned regular
files, below the requested 100 MiB ceiling. No further network access is needed
for the currently resolved graph. The existing build Python successfully imports
Mako 1.3.10.

From the `baseline/` directory, with `SERVO_REVIEWED_TARGET` set to the target
directory selected by the root owner and an owned log path:

```sh
env CARGO_HOME=/Users/bgrins/code/firefox/artifacts/css-contextual-easing-servo-closure-v1/cargo-home \
  CARGO_NET_OFFLINE=true RUSTUP_AUTO_INSTALL=0 \
  RUSTC=/Users/bgrins/.rustup/toolchains/stable-aarch64-apple-darwin/bin/rustc \
  PYTHON3=/Users/bgrins/.mozbuild/srcdirs/firefox-4cbffe2ae3f2/_virtualenvs/build/bin/python \
  PYTHONDONTWRITEBYTECODE=1 CARGO_INCREMENTAL=0 CARGO_PROFILE_DEV_DEBUG=0 \
  /Users/bgrins/.rustup/toolchains/stable-aarch64-apple-darwin/bin/cargo check \
  --locked --offline -p style --lib --no-default-features --features servo \
  --jobs 1 --target-dir "$SERVO_REVIEWED_TARGET" > "$SERVO_BASELINE_LOG" 2>&1
```

After a successful baseline check, use the same command/environment from
`candidate/`, redirecting to a distinct candidate log. Both use the complete
style library and actual Servo animation callers. Preserve both logs and their
exit statuses. A baseline failure must be classified before attributing any
error to the contextual-easing candidate. Generated property/atom code and
procedural macros have not yet been compiled, so additional compatibility
issues may still surface. No runtime behavior is established by this check.

Compiler elapsed time, peak memory, and target growth remain unmeasured. One
job, no incremental cache, and no debug information constrain output; the full
style crate still needs a separately admitted resource budget. Cargo metadata
does not establish that budget.
