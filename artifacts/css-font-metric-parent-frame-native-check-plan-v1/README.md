# Bounded native typecheck plan

This is an unexecuted command recommendation for candidate `aa9089f3` in `css-font-metric-parent-frame-v1`. Root must first finish the text experiment, restoration and publication, then admit the exact candidate against the then-current sources. This note does not authorize an overlay or establish native compatibility. Local build implementation/configuration hashes and exact excerpts are in INPUTS.json; revalidate them before execution.

From the repository root, after the separately controlled source overlay:

```sh
/Users/bgrins/venvs/firefox/bin/python ./mach cargo check -p geckoservo -j 2 --message-format-json --locked --offline > artifacts/css-font-metric-parent-frame-native-check-v1.log 2>&1
```

`geckoservo` depends on `style` with the Gecko feature. Mach routes this non-top-level crate through the configured gkrust backend specification with explicit package/target arguments. The saved specification selects the release profile and aarch64-apple-darwin target; it retains configured generated Gecko bindings and build environment rather than substituting a standalone stub Context. The existing `.deps` directory skips the explicit export fallback, but `ensure_backend_current()` still runs. This is a feasibility assessment from code/configuration, not an observed invocation.

**Mach exit zero is insufficient.** Local `cargo-check.yaml` sets `continue_on_error: true`; the handler ORs it into the flag and `_run_cargo_command` can return zero for a failed Cargo process. Require one Cargo JSON `build-finished` record with `success: true`, no error-level compiler diagnostics, and library compiler-artifact records for both `style` and `geckoservo` (fresh artifacts are acceptable only for the exact admitted inputs). Missing/false terminal JSON, tool errors or interrupted output are not a successful typecheck. Retain the entire unfiltered log and all warnings. Even a successful check does not establish scheduler progress or browser behavior.

The retained-frame review found no concrete new lifetime mismatch from source inspection. Frames own Arc values, prepared values and cursors; they do not store temporary Context or AttributeTracker borrows. Nevertheless, extracted tests erase all four Context lifetimes and replace native maps, SmallVec, entry APIs and Gecko operations. Real borrow/type checking remains necessary. The production provider is always ready, while test pauses use finite injected schedules; neither provides the missing prerequisite producer or a liveness proof.

Likely writes, inferred from Cargo/Mach implementation rather than observed here:

- `objdir-full.noindex/aarch64-apple-darwin/release/{deps,.fingerprint,incremental,build}` for target check artifacts and build-script outputs.
- `objdir-full.noindex/release/` for host build scripts/procedural macros, plus Cargo target locks/cache and `.rustc_info.json`.
- Backend regeneration may update configured object-directory build files and `.cargo-library-spec.json`; an absent `.deps` would trigger pre-export/export. Existing Cargo/Mach tool metadata may also change. Locked/offline flags constrain resolution/network use, not all filesystem writes.

No Firefox link/install is requested, but build scripts and backend regeneration prevent assuming the app remains identical. Root should preserve and verify the established source identities, app/extras inventories, application metadata, pinned binaries/WPT runner configuration, canonical controls, HEAD, semantic/raw index and flags before/after, and restore the admitted source overlay. Keep any changed build artifacts separate from app provenance; do not relabel the old restored app as newly built. Do not overlap this check with a native build or experiment.
