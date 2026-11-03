# Integrated candidate: public flag documentation

This successor adds exactly four Rust doc comments to the public FONT_METRICS, ROOT_FONT_METRICS, FONT_ORIENTATION and ROOT_FONT_ORIENTATION constants. The native Cargo check of integrated-v1 reported these as missing-documentation warnings despite the crate's deny(missing_docs) declaration. This avoids relying on the check's warning downgrade for a subsequent full build. No lint suppression or executable code changed.

Removing these four exact lines recovers the sealed integrated-v1 provider byte-for-byte. cascade.rs and properties/mod.rs are unchanged. SOURCE-ROLES.json pins all three published bases, parent sources and candidate sources; PARENT-DELTA.patch is the four-comment change, and native.patch is cumulative from the published u32 base. check.py verifies the exact stripped-comment equivalence, both diffs and rustfmt.

The parent's 36 positive/18 compiled failing provider-size controls and 14 positive/seven graph controls remain historical integrated-v1 results. They were not rerun for comments. Root's actual integrated-v1 native check completed successfully (owner56841, terminalbf0e1a, exit0), with style/geckoservo newly checked, zero compiler errors and twelve warnings. That is native compilation of the parent, not a browser result or a separate native run of this successor. Independent restoration is root-owned and not certified here.

The other eight diagnostics concern unused imports, fields, variants or helper methods. They do not establish a new semantic error. In particular, native callers can retain a pending request without constructing a consumed SubstitutionLookupValue::Pending; the warning does not show that a scheduler wait became invalidity. All parent progress, native-effect and legacy-consumer limitations remain. No accepted native fix follows from compilation.

BROWSER-NEXT.md gives the next bounded browser matrix. All live source overlays, full builds, manifest staging, browser execution and restoration remain with the root owner.
