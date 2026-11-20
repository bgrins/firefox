# Benchmarking developer rebuilds

Use `./mach buildbench --list` to list the workloads. Run in a configured single-stage native Firefox checkout with a populated objdir, direct C++ and Rust compilers, and compiler-result caching disabled. Keep the checkout and objdir exclusive to this run. Save editor changes first. Two-stage PGO builds produce multiple profiles and are unsupported.

```sh
./mach buildbench no-change --repeat 3 -j 16
./mach buildbench image-alt-text --repeat 3 -j 16
./mach buildbench selector-invalidation --repeat 3 -j 16
./mach buildbench quota-interface --repeat 3 -j 16
./mach buildbench time-duration-header --repeat 2 -j 16
./mach buildbench zucchini-library-flags --repeat 2 -j 16
```

An edit workload first checks that its source fixture matches exactly once. If it does, the command prepares the existing objdir with an ordinary top-level build. The no-change workload also prepares the objdir. The no-change workload then times the same build again. Each build sets Cargo's two Rust compiler wrapper variables to empty strings to override wrapper paths in Cargo configuration files. Rust incremental compilation keeps its configured setting.

- `image-alt-text` changes the notification flag for image-document alt text from true to false.
- `selector-invalidation` removes the per-compound attribute reset from relative selector invalidation. It reverses the Rust change from bug 2090823 on a checkout that contains the fix.
- `quota-interface` adds an enum constant to nsIQuotaArtificialFailure.idl, exercising generated C++ and Rust interfaces and typelib generation. It isolates the interface portion of a change like bug 2058495.
- `time-duration-header` restores the debug-only BaseTimeDuration getter removed in bug 2000185. Editing this widely included header also exercises optimized builds where preprocessing omits the getter.
- `zucchini-library-flags` changes the Clang diagnostic suppressed in bug 2090625 into a nonfatal warning in the Zucchini library. On a Clang build this regenerates the backend, recompiles the library and relinks programs that use it. The CLI and GoogleTest sources keep their own flags. This isolates one of the three build definitions in the original change.

Each edit workload times a build after the edit and a second build with that edit still applied, restores the original file, and builds the restored tree. Preparation and restoration have separate phase labels. An unchanged build immediately after preparation can still do deferred work, such as a link. Compare its log and completed markers with later trials before treating it as a steady-state timing. The command stops if a phase would require clobbering the populated objdir. Filesystem caches are uncontrolled. Each child runs from the selected objdir with its configured mozconfig. The result records host and target, compiler commands, optimization and debug settings, and both configured and environment Rust incremental-compilation settings. A populated no-change rebuild and a full build starting with an empty objdir and warm filesystem cache are separate scenarios.

Buildbench prints the output directory under `buildbench/` in the checkout-specific Mach state directory. Use `--output PATH` to give a run a stable location, for example `./mach buildbench no-change --repeat 3 --output ../samples/upstream-1`. Choose a new directory outside the objdir for each run so the results and recovery files survive an automatic clobber. Its versioned `results.json` records the source revision, tracked changed paths, configuration, job setting and elapsed time per phase. Each invocation of Mach has its own verbose log and compressed Firefox Profiler profile. Elapsed time includes Mach startup and shutdown. The marker counts describe completed events in the saved profile. Use the verbose log to verify actual compiler or linker invocations when investigating invalidation.

Each sample copies available CPU model, physical and logical CPU counts, and OS target from its saved profile into `profile_machine`. Compare these fields across runs, especially when a virtual machine has restarted between measurements.

On platforms with Python's `resource` module, each sample records `child_usage` for children reaped during the build, including work those processes waited for. It includes user and system CPU seconds, major page faults and the operating system's input and output block counts. Compare block counts on the same platform. An empty object means those counters were unavailable.

Commit the candidate first so another checkout can reproduce it from the recorded revision. For a patch comparison, use the same workload, machine, job count, configuration and toolchains on both revisions. Alternate upstream and candidate order and keep individual samples. Check for a reproducible change in the work performed alongside the elapsed-time differences. For example, a dependency fix can be tested by checking whether the same header edit schedules a particular object. Test the affected Firefox behavior independently.

An edit workload keeps a copy of the original source in its result directory. On a normal exit or build failure it restores that file. If another process changes the file, the command preserves that version and reports the backup path. Before launching each build, Buildbench writes its phase, trial, and log name to `active_sample` in `results.json`. A successful measurement moves into `samples` and clears `active_sample`. A hard stop can leave the status as `running`; the saved active sample identifies the build to inspect. If the process is killed, inspect the checkout-specific `buildbench.lock` in the Mach state directory for the PID and output path. After confirming the process has exited, inspect the recovery phase in `results.json`. For a named workload it also identifies the temporary directory holding the displaced files. Reconcile all affected files with your editor changes and backups before removing the lock and rebuilding. An uncertain restoration retains the lock even after the command exits. If an edited build fails and the source is restored, run `./mach build` to bring the objdir back in sync before using its outputs.

## Replaying a patch

A multi-file edit can be measured directly in a Git checkout. Use a trusted patch, since the build executes code from the edited tree. Save a diff and run on a revision where the patch applies. For example, to replay an upstream change on its parent with an already populated objdir, use the following commands from the source root with Buildbench available on both revisions being compared.

```sh
git diff --binary "$change^" "$change" > ../edit.patch
./mach buildbench --patch ../edit.patch --repeat 2 -j 16 --output ../samples/edit-1
```

The `patch_setup` entry in `results.json` reports when Buildbench is preparing the private Git index and recovery patch. On completion or failure it records elapsed seconds and child resource usage. Setup runs once per invocation, before the preparation build and outside all build timings.

Each run saves the patch and its SHA-256 alongside the measurements. Buildbench checks applicability before preparation, applies the patch for each edit and following no-change build, reverses it, and builds the restored tree. It uses a private Git index based on HEAD. Keep the target paths at their committed contents. A patch touching the top-level `CLOBBER` file requires a separate full-build experiment. Keep the active mozconfig fixed throughout the run. A conflicting edit during the run stops restoration and leaves the files available for inspection. Buildbench also saves a `restore.patch` for patches that change the Git tree. It describes the changes needed to restore the original files, including removing files added by a Git copy operation. After an interruption, inspect the worktree and check the applicable patch with `git apply --check` before restoring any files and removing the checkout lock.

## Adding an edit workload

Choose a small edit that a developer might actually build. Cite a landed change when possible, explain which part the workload reproduces, and name the work you expect it to trigger. A quota enum addition, for example, changes the generated typelib data while leaving the list of interface IDs unchanged. That gives reviewers a specific question to check in the verbose build log and profile.

For a single-file workload, add a description to `WORKLOADS` and an exact path, original byte sequence and replacement to `EDITS` in `python/mozbuild/mozbuild/buildbench.py`. Pick an original sequence that occurs exactly once. If the source evolves and the edit stops applying, inspect the new code and update the workload description along with the fixture.

Run the harness tests from the source root.

```sh
./mach python-test python/mozbuild/mozbuild/test/test_buildbench*.py
```

The parameterized tests exercise each registered edit through repeated trials and source restoration, including interruption. Then run the new workload on a populated native objdir. Inspect the edit log to confirm it exercised the intended generator, compiler or linker. Inspect the following no-change log for work that spills into the next build. Save both profiles with the revision and configuration when reporting a result.

Use the observed rebuild decision as a regression test when it can be checked deterministically. For a generator that preserves unchanged output, test both a semantic edit that leaves that output identical and a control edit that changes it. Report end-to-end build time separately from the duration of a compiler invocation. A compile that overlaps other work can disappear without shortening the build by its full duration.
