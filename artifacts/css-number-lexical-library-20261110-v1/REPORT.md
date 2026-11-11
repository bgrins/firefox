# Standalone number lexical integration

Ready for independent review and application to canonical base `b3d6ef2c643b848851d5e860c836abf2120e56af`. The final source-only replay passes. No canonical source, Git commit or build cache was intentionally changed; the canonical HEAD/status and preexisting `.DS_Store` bytes match the initial receipt, and all 2,577 archived tracked files were independently compared with the canonical files after verification. The copied development archives and all owned compiled scratch were removed.

`integration.patch` changes only the existing README and adds 52 files. The additions include 14 previously separate byte-reference modules, seven bridge modules, three executable-support modules, one test module, the opt-in `CssDerivation.NumberLexical` facade, its standalone checker, fixtures and provenance. Every accepted Lean source is unchanged except import module names. The 46 shared canonical modules remain byte-identical. The existing `CssDerivation.lean`, `CssSemantics.lean`, main facade registry and CSS coverage registry are unchanged.

The 457 audited declarations are **295 already-canonical declarations + 103 previously separate byte-reference declarations + 59 bridge declarations**. Thus 162 declarations become newly available in the library, while the accepted artifact's 398-preserved/59-new accounting is retained. This is not 457 newly proved CSS requirements, and it does not increase the main CSS feature coverage claim.

The source-only replay reconstructs the exact pinned library in an isolated temporary directory, checks and applies the patch, verifies every changed byte, executes the installed checker, reverses the patch and checks the entire restored source tree. It then removes that temporary directory. The installed checker needs only its own library files, Python and the supplied Lean toolchain; it does not read a parent Firefox checkout, sibling artifacts, native source repositories or native executables. Historical paths are retained only in provenance records.

Validation in `source-replay/verification/report.json`:

- Cold accepted-source replay and separate cold installed-module build pass. The public import excludes runtime and test modules.
- All 457 exact axiom records agree with the accepted checker, allowing only `propext`, `Classical.choice` and `Quot.sound`; 22 new kernel boundary cases compile.
- The installed actual-file and reference runners each match 62 rows; the changed valid document matches two distinct rows. The installed runner executes the supplied document rather than substituting the fixed fixture.
- Accepted-source replay rejects five malformed documents, three compiled semantic mutations with their exact false witnesses, and three provenance changes. The installed-facade checks reject a missing dependency and a changed dependency.
- The main coverage-only checker retains exact registration for 11,923 declarations. This is not a full CSS-library rebuild or browser gate.
- Three legacy modules retain nine known unused-simp warnings. Their complete output hashes must match after normalizing only relocated module filenames; all other diagnostics remain strict.

`verification-1` records the successful initial integration run before the compatibility registry was narrowed and final documentation/provenance was completed. `source-replay` is the accepted final run and binds the frozen patch, checker, 78-file compatibility registry and documentation. Its command log hashes and the accepted-source command hashes were rechecked after completion.

The public claim concerns normalized ASCII satisfying number-entry recognition, exact numeric prefix/remainder and digit runs, sign presence and syntactic integer classification. Source-shaped functions such as `NumericLexical.native` remain **Lean algorithms**, not verified Rust code. The fixed JSON fixture and manually mapped CSS Syntax revision are explicit; arbitrary typed documents need not implement CSS. Numeric remainder differs from full percentage/dimension token remainder. UTF-8 decoding, native error-field correspondence, JSON text parsing/quotation, floating-point conversion, integer clamping, full native token semantics and mechanical prose derivation remain outside this integration.

The installed native evidence retains the accepted default-feature v3 calibration: 196 native cases, 180 admitted model rows, 284 lexical comparisons and three compiled mutation rejections. It is historical finite evidence, not a Rust refinement theorem, full Gecko configuration equivalence or a floating-point oracle. The newer expanded corpus was deliberately not folded into these frozen inputs.

Reproduce from this capsule with an independent canonical repository containing the pinned base:

```sh
python3 -B artifacts/css-number-lexical-library-20261110-v1/replay.py \
  --canonical artifacts/css-spec-lean \
  --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --out /tmp/css-number-lexical-integration-replay
```

The output directory must be absent. `SOURCE-ONLY.json` authenticates the 56 required capsule inputs. `overlay/` contains only the changed/new library files. The replay archives the base using read-only Git commands and never applies the patch to the canonical repository.
