# Corrected isolated Servo dependency closure

This successor addresses the observed baseline dependency-source failure from
`css-contextual-easing-servo-compile-runtime-1`: Cargo exited 101 on the autocfg
checksum before checking style; candidate compilation was skipped. This was
not a candidate bug. `PRIOR-FAILURE.json` pins the original logs and result.

The first closure exposed Firefox's already-patched vendor sources as ordinary
registry directory sources. An audit of every selected registry package found
170 mismatches across seven packages. The actual repository `Cargo.toml`
already declares all seven as `[patch.crates-io]` path dependencies:
autocfg, icu_collections, icu_normalizer, icu_normalizer_data, icu_properties,
icu_properties_data, and utf8_iter. Both successor workspace manifests now
carry those same declarations, using the actual repository source paths.

`TRACKED-PATCH-PROVENANCE.json` records HEAD
`caf58ba581539636290644696936c80d45e01ebf`: all 167 present discrepant files
match their committed bytes; the other three paths are absent in both HEAD
and the working tree. The root manifest also matches HEAD. No native vendor
file or `.cargo-checksum.json` was rewritten. The seven path dependencies are
pinned file by file, retaining the existing Firefox implementations.

Both roles resolve offline to the same 152 packages as before, with identical
names, versions, features, and dependency edges. The only source-identity
changes are the seven registry-to-path patches. Cargo regenerated the shared
lockfile, whose SHA256 is
`4aa7160b195d99dd3b28ba8336b5cb63d2f93466029b16594d9050130c39e183`.
All 127 remaining selected registry packages pass checksums for all 6,662
listed files. The eight selected owned registry packages also match their
cached/downloaded crate archives, including the archive checksums. The only
extra files are checksum metadata and the cached getrandom `.cargo-ok` marker.
The audit records are `DIRECTORY-SOURCE-AUDIT.json` and
`OWNED-ARCHIVE-AUDIT.json`. No downloads were needed for this successor.

`SUCCESSOR-DELTA.patch` shows the complete workspace delta from v1: vendor
directory location, seven root patch declarations, and their lockfile source
identities. All Rust sources and copied support implementations remain
byte-identical to v1. Both workspaces still differ in exactly seven captured
style sources. Earlier manifest adaptations remain documented in the sealed
v1 README and copied `MANIFEST-ADAPTATIONS.patch`.

This checks the captured local configuration, not clean upstream. Both roles
include the shared held `servo/components/style/custom_properties.rs` at
`2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774`.
A successful check would not accept that shared change or establish runtime
behavior. No compiler has run against this successor, and no target was
created. The prior checksum failure supplies no evidence about later lints
or type checking; compile flags and lint policy remain unchanged.

`BASELINE-FILES.json`, `CANDIDATE-FILES.json`, and `RESOLVED-SOURCES.json` pin
the complete workspace and selected dependency files. `verify.py` checks
those inventories, the seven exact source roles, every selected directory
source checksum, and the tracked patched-file bytes or absences. It performs
no compile and creates no files:

```sh
python3 -I -S -B artifacts/css-contextual-easing-servo-closure-v2/verify.py
```

Full baseline then candidate checks remain gated on root review of the
successor runner. The original closure, runner, runtime, repository source,
Git/index, app, and canonical epoch have not been modified by this setup.
