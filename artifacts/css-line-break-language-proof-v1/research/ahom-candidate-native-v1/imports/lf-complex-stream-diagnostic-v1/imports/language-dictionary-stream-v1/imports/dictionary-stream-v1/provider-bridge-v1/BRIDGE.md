# Development native bridge checkpoint

This is an immutable development export for the independent hyphenation companion. It is not formal acceptance or a completed source-only replay capsule.

Authentic native algorithms: full original/language-only-candidate nsLineBreaker, full LineBreaker and cache/hash/MruCache, complete locale parser and likely-subtag dispatch and relevant canonicalization with full LocaleGenerated CLDR 48.2, complete Unicode category/lowercase mapping, full StaticRefPtr class, complete BreakSink and glyph filtering/bitfield setter, actual mapped_hyph and pinned en-US dictionary.

The source-copy nsLineBreaker candidates are language-only, not the hyphenation ownership repair. Consumers must bind their own exact original/candidate/standalone snapshots and record every adaptation. The two repairs are separate.

Build: create development-cargo-home, development-build, evidence directories; from icu/, run Cargo +stable build --locked --offline with CARGO_HOME set to this export's development-cargo-home and --target-dir set to this export's development-build/icu. Then run python3 build-development.py from the export root. The script compiles complete source units with UBSan. No Firefox build or browser is involved.

ICU4X code/data are vendored here. ICU4C is the explicitly foreign system libicucore provider, observed version 78.1.0.0; do not claim a proof of ICU/CLDR or that system ICU4C source is pinned. The copied Firefox ICU headers are used with symbol renaming disabled. Existing utf8_iter checksum metadata adaptations are recorded under evidence; source bytes were unchanged.

Incomplete boundaries: container/refcount adapters require final validation; scanner/skipchars/style facades are not yet independently validated; the capture runner is for development; trace coverage and source-authentication driver are unfinished; no semantic mutation gate or final model/native correspondence has run. StaticRefPtr AddRef-before-release uses the extracted actual class; atom pooling and main-thread shutdown scheduling are explicit facades. Native namespace adaptations isolate C++ facade types across translation units.

Initial actual native tests include both encodings and language-sensitive Latin-1, full glyph sink results, cache/provider traces, and dictionary calls. LF partition discrepancy is retained for caller admission analysis, not hidden. ASan startup hung in this environment; successful development executions used UBSan.
