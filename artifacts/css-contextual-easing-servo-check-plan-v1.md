# Contextual easing: Servo compile-check plan

Read-only investigation of the eight-source candidate described by
`artifacts/css-contextual-easing-activation-prototype-v2/SOURCE-ROLES.json` and
`native.patch`. All eight candidate capture hashes matched that manifest.
No build, Cargo command, browser operation, native edit, Git operation, target
creation, dependency installation, or download was performed. This note neither
changes candidate acceptance nor counts a new bug.

## Required coverage

The smallest meaningful compiler gate is `cargo check` of the complete `style`
library with only its `servo` engine feature enabled. `style/lib.rs` gates the
`servo` module and animation re-export on that feature; `matching.rs` also gates
the modified animation processing methods on it. `build.rs` requires exactly
one of `servo` and `gecko`. The comment in `servo/animation.rs` claiming it is not
compiled out in Gecko does not describe the current module gating.

The inspected `selectors-check` and `ancestor-helper-gate` manifests and existing
`storage-port-debug-common.log` cover selectors/extracted bloom logic, not the
full style crate or these animation callers. Their passing results cannot close
this gate. A stubbed signature probe would likewise leave actual trait bounds,
generated properties, and cross-module integration unchecked.

The existing `servo/tests/unit/style/Cargo.toml` is not a ready alternative. Its
actual local contents declare `style = {path = "../../../components/style"}`
without selecting an engine feature, and also require absent `atoms`, `config`,
`url`, `size_of_test`, and `std_test_override` component directories. It adds
dependencies beyond a library-only check. Its SHA256 is
`e04ae9ac1d0bbfe5b3867c5f4290496eabf1dbd323f9881cc547d0fab8377c30`.

## Present prerequisites and gaps

- After locating it through Searchfox, the actual local
  `servo/components/style/Cargo.toml` was read directly. Its SHA256 is
  `5421775e978794f47520e9d9120edf07692bc9e16b43b0fc5cff5525b7afe3c0`.
  It declares optional path dependencies
  `../atoms` (`stylo_atoms`) and `../config` (`servo_config`) for Servo. Both
  are explicitly selected by its `servo` feature, and both directories are
  absent in this checkout. A direct Servo check must resolve these missing
  dependencies before candidate code is type-checked. Cargo resolution was not
  run. The existing Gecko build's selected dependency graph is different, as
  established below.
- That same actual local manifest requests `web_atoms = 0.1` and
  `string_cache = 0.8` as optional dependencies selected by `servo`.
  Neither exists under the checked `third_party/rust` paths. The default Cargo
  source cache contains `web_atoms-0.2.3`, `web_atoms-0.2.6`, and
  `string_cache-0.9.0`, which do not satisfy those requirements. The owned
  `artifacts/stylo-bloom-tools/cargo/registry` contains only `CACHEDIR.TAG`.
  The other inspected upstream-enumeration registry has none of those source
  packages. A complete dependency closure has not been established.
- Property generation invokes Python and imports Mako. A suitable existing
  interpreter must be selected and verified before the check. The generator
  writes generated properties and documentation under the chosen Cargo target.
- Installed toolchain directories include `1.97.1-aarch64-apple-darwin` and the
  owned `nightly-2026-09-17-aarch64-apple-darwin`. Neither was invoked here.
  Do not allow rustup to auto-install a missing toolchain.
- `searchfox-cli` fetched unchanged crate definitions and signatures from its
  default Firefox index. The two manifests above were then checked directly
  against the local filesystem; dependency directory/cache existence was also
  checked locally. Other signature observations are not a hash certification of
  unchanged local support sources. No comparison with the active overlay was
  made.

## Actual Gecko build spec and command composition

Direct inspection of the local files confirms both pins in the active easing
policy: `.cargo-library-spec.json` has SHA256
`3fc41f4cbc608f048b4a02e5db03493a213b3a5203412d42533a677d6c8f8894`, and
`python/mozbuild/mozbuild/rust_commands.py` has SHA256
`11fc6bde0bbc76782b3711c739dc367155e6b68d6c7ce727fe54afe818b9be47`.
The local implementation was inspected separately from Searchfox because their
current contents differ.

The spec at `objdir-full.noindex/toolkit/library/rust/.cargo-library-spec.json`
selects `/Users/bgrins/.rustup/toolchains/stable-aarch64-apple-darwin/bin/cargo`,
the source manifest `toolkit/library/rust/Cargo.toml`, working directory
`objdir-full.noindex/toolkit/library/rust`, release profile, `--frozen`, and
target `aarch64-apple-darwin`. `compose_cargo_build_edge_argv` adds the recorded
gkrust-shared features and `mozilla-central-workspace-hack`.
`compose_env` sets `CARGO_TARGET_DIR` to `objdir-full.noindex`, the recorded Rust
compiler, and the existing build-virtualenv Python. The local
`mozbuild/action/run_cargo.py` loads that spec, composes the command/environment,
and executes Cargo in the recorded working directory. None of these functions
rewrites manifests or supplies replacement dependency sources.

The objdir `.cargo/config.toml` redirects crates.io and listed Git dependencies
to `third_party/rust`; it does not redirect absent Servo path dependencies.
Its SHA256 is
`a19f92b863ac44667a7c1c4f83c01aa4c03c4f1f992af02115cf3a126ad6f6ac`.
The actual source `servo/ports/geckolib/Cargo.toml` enables `style/gecko`.
The root workspace excludes `servo`, and its actual `Cargo.lock` style package
does not list `stylo_atoms`, `servo_config`, `web_atoms`, or `string_cache`;
none of those packages has a lockfile entry. This establishes why the observed
successful Gecko graph does not require these disabled Servo dependencies.
The Gecko unit-test manifest `servo/ports/geckolib/tests/Cargo.toml` also
explicitly selects `style/gecko` and does not close Servo coverage.

Reusing the command/environment composer can retain known compiler and Python
paths, but cannot repair the missing enabled Servo dependency closure. The
existing library spec itself must not be reused as a Servo check: its selected
Gecko graph would remain active, and enabling Servo alongside Gecko is rejected
by the style build script. A separate owned style-only manifest/spec must select
only Servo, omit gkrust/workspace-hack features, and override the inherited
`CARGO_TARGET_DIR` and Gecko-specific flags. A compatible offline source closure
and lockfile remain necessary; no ready materialized Servo workspace was found
in the inspected artifacts. Do not run the existing spec or command composer
as a purported Servo validation without these changes.

## Conditional command for the root owner

First provision or identify an already-owned, compatible complete style
workspace with the missing Servo source dependencies and offline dependency
closure. Preserve all seven style candidate files from `SOURCE-ROLES.json`
byte-for-byte in its style crate; the eighth file, `geckolib/glue.rs`, belongs to
the separate Gecko check. Record support-source identities and any manifest
adaptations. Do not substitute upstream animation or matching files for the
captured files. A baseline assembled from the corresponding base captures should
check in the same setup before attributing failures to the candidate.

The following is a proposed invocation, not a runnable setup delivered by this
investigation. Run from the owned workspace directory after the root owner
selects an existing authorized target, creates an appropriate offline lockfile,
and verifies the interpreter and toolchain. The variables must name that
workspace's manifest, target, interpreter, and an owned artifact log.

```sh
RUSTUP_AUTO_INSTALL=0 CARGO_NET_OFFLINE=true PYTHON3="$SERVO_CHECK_PYTHON" \
  cargo +1.97.1-aarch64-apple-darwin check \
  --offline --locked --manifest-path "$SERVO_CHECK_MANIFEST" \
  -p style --lib --no-default-features --features servo \
  --jobs 1 --target-dir "$SERVO_CHECK_TARGET" \
  > "$SERVO_CHECK_LOG" 2>&1
```

Confirm that no other workspace member/dependency unifies the `gecko` feature
onto `style`. Stop on dependency/lockfile setup failures; they are not evidence
against the candidate. The root owner must sequence this after the active
experiment and preserve the existing target ownership rules.

This avoids a browser build, linking Servo, and test execution. It still builds
build scripts/procedural macros and generates/type-checks the full style crate.
Cold elapsed time, peak memory, and disk growth are unmeasured; `--jobs 1` limits
parallel work but does not eliminate the style crate's own memory cost. It must
not be described as a cheap selectors-only check.

## Inspection result and remaining evidence

No obvious newly introduced compile error was identified by inspection.
`with_default_parent_styles` is `pub(crate)` and passes
`Option<&ComputedValues>` to the closure. `StyleBuilder::for_derived_style` accepts
the new parent-style argument; `Context::new_for_animation` accepts the supplied
builder, conditions, container query, element context, and counting caches.
`ContainerSizeQuery::for_element` accepts `(element, parent_style, is_pseudo)`.
The captured animation module imports the newly used types. This is limited
signature inspection, not a compiler result or runtime validation.

Required completion evidence: candidate hash manifest, complete support-source
and dependency identities, successful baseline check, exact command/environment,
and candidate compiler exit status/log showing the Servo-feature style library
was checked. A successful check would establish type checking only; contextual
easing behavior in Servo remains a separate runtime question.
