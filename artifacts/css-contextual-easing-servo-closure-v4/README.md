# Servo dependencies matching the captured atom API

Runtime3 reached style and baseline Cargo exited 101 after 49.9567 seconds:
five unresolved mime errors and two unstable str_as_str errors. Candidate was
skipped, source preservation passed, and owned groups were absent.
PRIOR-FAILURE.json pins the actual log, result, and root terminal708963/1.

These are two distinct shared-baseline dependency mismatches. The original
Firefox style manifest has no mime declaration; the isolated adaptations did
not remove one. The previously captured upstream Stylo style manifest declares
optional mime0.3.13 and includes it in the servo feature. This successor
carries that declaration in both copied manifests; native vendor mime0.3.16
satisfies it without a download or source modification.

The two custom_properties.rs calls were introduced by upstream bug2076755,
commit9164248aff3897679d687022ef74e35e14c3f84a, importing
[Stylo PR460](https://github.com/servo/stylo/pull/460). They are outside the held
provider modifications. Name is an Atom, and the intended string_cache0.11
provides the stable inherent `Atom::as_str(&self) -> &str` method. The earlier
harness selected string_cache0.8.9, which lacks that method, so lookup reached
the unstable str method through Deref. This does not establish a held-provider
or candidate source defect. No Rust source was changed to suppress the errors.

The successor follows the captured upstream manifest's coherent versions:
string_cache0.11 and web_atoms0.3.0. The copied style, malloc_size_of, and
to_shmem manifests all select string_cache0.11, preserving one concrete atom
type for the existing trait implementations. The stylo_atoms0.22.0 manifest
is restored to its published string_cache/string_cache_codegen0.11 requirements.
All package source and implementation files are unchanged. The three fetched
archives total56,220 bytes and match their published checksums.

The resulting offline graph has150 packages. It selects mime0.3.16,
string_cache0.11.0, string_cache_codegen0.11.2, web_atoms0.3.0, and
phf_codegen0.14.0; obsolete PHF0.11 packages leave the graph. Every one of the
125 selected directory-source packages passes all6,645 listed file checksums.
Both roles pass locked offline metadata resolution with identical locks.
The literal audit reproduces the previous records and counts using the retained
generated properties; it does not access the removed/obsolete runtime2 target.

DEPENDENCY-API-PROVENANCE.json and research/ATOM-API-UPGRADE.patch record the
cause and authoritative inputs. SUCCESSOR-DELTA.patch contains the complete
workspace delta: six manifest/configuration/lock files, no native Rust edits.
The seven baseline/candidate source differences and shared held provider hash
2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774 remain
unchanged. Earlier preference adaptations are retained with their explicit
provenance in SUPPORT-PROVENANCE.json.

No compiler has run against this successor. It still checks an adapted captured
local configuration, not clean upstream or runtime behavior. No source bug fix,
native acceptance, lint cap, unstable Rust feature gate, or RUSTC_BOOTSTRAP setting was added.
Baseline must succeed before candidate checking. Actual compile results remain
pending; metadata and API inspection alone do not establish success.

```sh
python3 -I -S -B artifacts/css-contextual-easing-servo-closure-v4/verify.py
```
