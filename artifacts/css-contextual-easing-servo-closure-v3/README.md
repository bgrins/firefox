# Servo support tables matching the captured baseline

Runtime2 reached style in 39.46 seconds, then baseline Cargo exited 101 on
three missing preference macro arms and `local_name!("part")`. Candidate was
skipped; source preservation passed and all owned process groups were absent.
`PRIOR-FAILURE.json` binds that observed failure. All four use sites are identical
in baseline/candidate and match observed HEAD, but HEAD contains local fixes:
this establishes a shared-baseline support gap, not upstream origin or a
candidate bug.

Both workspaces retain the actual `stylo_static_prefs` 0.22.0 generator and
implementation. Their preference input receives only three boolean entries:

- `layout.css.always_underline_links = false`, from the actual root
  `modules/libpref/init/StaticPrefList.yaml` entry, typed RelaxedAtomicBool with
  Rust exposure. Its full input hash and exact entry are recorded.
- `layout.css.display-grid-lanes.enabled = false` and
  `layout.css.random.enabled = false`, copied from the authoritative
  [Stylo preference input at bd4e3176](https://github.com/servo/stylo/blob/bd4e31763a4991a7b11768650cca4b8febb389bb/stylo_static_prefs/preferences.toml).
  Root Firefox uses nightly-dependent defaults for these two; this isolated
  harness explicitly chooses the upstream Servo defaults, not an inferred
  Firefox build configuration.

`SUPPORT-PROVENANCE.json` pins the source inputs, values, and shared use sites.
There are no catchall macros, replacement API stubs, or native Rust edits.
Other existing preference values remain unchanged. This is a documented
adapted support configuration for full type checking, not behavioral validation
of either preference setting.

`web_atoms` changes from published 0.1.0 to published 0.1.3. Versions 0.1.1 and
0.1.2 were checked and lack `part`; 0.1.3 contains it and already declares
compatible string_cache 0.8.8, string_cache_codegen 0.5.4, and PHF 0.11
dependencies. Its crate SHA256 is
`57ffde1dc01240bdf9992e3205668b235e59421fd085e8a317ed98da0178d414`.
All source files and its manifest remain unmodified. No dependency adaptation
or atom-table edit is needed. `FETCHES.json` records bounded published-archive
and upstream-input fetches; no repository checkout or large download occurred.

`LITERAL-AUDIT.json` inventories 73 distinct pref literals, 135 atom literals,
and 13 local_name literals across both copied native Rust trees and the prior
baseline's generated properties. All selected Servo literals are available;
the remaining entries are explicitly reviewed Gecko cfg exclusions or Mako
placeholders whose generated output was scanned. The audit is lexical, not a
substitute for compiler expansion/type checking. `audit_literals.py` reproduces
it while the recorded runtime2 generated file exists. Generator inputs are
unchanged between roles. Runtime2's target is retained untouched.

Both successor roles resolve with `--locked --offline` to 152 packages. The
only version change is web_atoms 0.1.0 to 0.1.3; package names, features, and
dependency edges are otherwise identical. All 127 selected registry packages
pass every one of their 6,662 file checksums. Existing genuine Firefox path
patches and tracked provenance are preserved from v2.

`SUCCESSOR-DELTA.patch` shows every workspace change: vendor location, atom
version and lock entry, and the three preferences. All native Rust files are
byte-identical to v2. Baseline/candidate still differ in exactly the seven
captured style files. The shared held custom_properties.rs hash remains
`2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774`.
This is the captured local configuration, not clean upstream, and accepts no
native change.

`verify.py` checks exact workspace/dependency inventories, directory-source
checksums, the seven source roles, tracked path-patch provenance, and support
input hashes. It performs no compilation. The successor runner retains the
existing compile flags, no lint cap, one job, no debug/incremental output, and
the reviewed time/disk limits. No compiler has run against this closure.

```sh
python3 -I -S -B artifacts/css-contextual-easing-servo-closure-v3/verify.py
```
