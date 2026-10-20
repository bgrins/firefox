# Sticky explicit-offset alias: corrected source-role companion

Producer result: PASS within the original integer/provider and extracted-native scope. Independent review and acceptance of this v3 correction remain pending. The sealed v2 producer and v1 independent review are preserved. This work changes only the new v3 artifact; it does not read mutable native source for replay, modify production/WPT/Git, run a browser, or build Firefox.

## Correction and exact source roles

The v1 independent review correctly found that v2 used the final formatted file for both candidate roles. V2 therefore did not execute the claimed exact browser-tested source. This version restores the distinct original tested snapshot rather than waiving that requirement through formatting equivalence.

| Role | Exact full-file SHA256 |
|---|---|
| Before | `38d14faa60bfe3180e87904f5085fdbbee5aa47746a38df77f4edb50360af40c` |
| Tested repair | `51e60438c405a4163cd0f8c43a669ee712d06dc6d202ccefa7519b968ea7925c` |
| Final formatted repair | `2a0794213ffad4d35d96b915b0fc858e2bfb18ddf74b20e4884a2d6b6f0f3b4b` |

The restored candidate comes from the original native fix artifact, authenticated against the independently sealed review copy. SOURCE-TRANSFER records that provenance. The role gate authenticates fixed hashes for CANDIDATE, BUILD, FORMAT-TRANSFER, and the original baseline/candidate browser RUN receipts. It derives each role from those records, requires three distinct identities, requires the build's compiled source to equal the tested candidate, and joins the original canonical before/after live-source pins to the corresponding roles. It then checks actual source bytes and SOURCE-PINS against those identities. No mutable live-source state is consulted.

The core extractor now expects the authentic preformat return expression. It still extracts and compiles the complete helper from all three sources, enforces the helper-only repair and unchanged surrounding file bytes, and independently checks the formatted helper has the same non-whitespace sequence. BINDINGS was regenerated for the actual tested body. Each native command now records both its complete frozen input identity and generated compilation-unit identity. NATIVE-SOURCE-ROLES confirms three different compilation units and exact original/tested/formatted mappings at both optimization levels.

The added role-substitution control copies the formatted file over the tested file, updates the ordinary SOURCE-PINS and BINDINGS records, and reseals the manifest. It reaches and fails `source role: exact input candidate.cpp` before output creation or compilation. It does not rely on a generic stale-file hash or extraction mismatch. Separate controls reject a resealed wrong source-role pin and a forged canonical CANDIDATE receipt. Checker code and the externally supplied manifest remain trusted entry points; arbitrary replacement of both is not a meaningful integrity guarantee.

## Preserved obligations and results

PRESERVATION authenticates all three unchanged Lean modules, the complete 236-case corpus and original 216-case prefix, original theorem roster, provider record, native facade, source constants, theorem documentation, and full toolchain/header inventories against v2. No theorem or provider obligation was removed to achieve these results.

Both canonical and manifest-only relocated replays exited zero. All 57 compared portable streams are byte-identical, including results, all eleven native source/row streams, generated calibration/driver/audit sources, full Lean rows, audit output and source-role records. Commands and dependency files retain their real location-specific paths.

| Gate | Each complete replay |
|---|---:|
| Audited named results | 31 |
| Original integer encoding results | 12 |
| Source-observer results | 12 |
| Kernel mutant witnesses | 5 |
| Whole-corpus kernel calibration results | 2 |
| Cases, including original 216 | 236 |
| Correct native configurations | 6 |
| Paired compiled native / executed Lean mutations | 5 |
| Rejected provider/schema cases | 11 |

The six correct configurations use the three genuine source bodies at -O0 and -O2, with UBSan. All compiled and executed successfully and agree with the separately executed Lean rows and independent boundary oracle. The five compiled mutations also agree with their corresponding Lean mutations and differ from the correct result in respectively 112, 112, 28, 44 and 236 cases. Compilation failure is never mutation evidence.

All 33 tooling integrity controls pass: the original 26 controls, four unsafe-invocation controls for the added role module, and the three source-role controls. Both custom-axiom/sorry controls pass, with disposal-copy transfer metadata deliberately rebound to reach the axiom/warning gate. The exact audited axiom policy remains propext, Classical.choice and Quot.sound. Original closed-roster checks, invalid output checks, compiler identity, installed Lean inventory and exact compiler-consumed header closure are retained.

The first command accidentally supplied an incorrect external manifest argument and was rejected before producer imports or output. Its traceback and incorrect argument are preserved in development-wrong-manifest.log and TERMINALS.json. It is not counted as a successful replay. The corrected command used the actual frozen manifest; no proof/source change was needed. TERMINALS records all terminal command exits.

## Scope and admissions

The complete helper's actual-auto branch returns the reserved code and skips numeric resolution. The explicit branch forwards the original side and percentage basis, resolves once, and returns min(reserved minus one, resolved). The unchanged Lean results establish the conditional integer no-alias/round-trip/range/preservation and full observer relations, including representability of the constant subtraction and a counterexample showing that the one-unit-change theorem needs its upper-bound premise.

Actual auto means the provider's anchor-resolved result, not necessarily literal authored auto. Stable style storage, object lifetime, valid side/provider selection, anchor semantics, floating-point conversion, percentages, Rust calc, rounding, saturation and the real LengthPercentage resolver remain explicit provider assumptions. The retained real ComputeCBDependentValue source asserts an unconstrained basis implies no percentage; maximum-basis calibration rows represent pure lengths. That assertion is not executed by the facade. The source-to-model interpretation is reviewed/calibrated rather than a fully mechanized C++ semantics proof.

The proof establishes the no-reserved-code-alias premise for the separate positional consumer work. It does not claim downstream sticky geometry, signed arithmetic of other helpers, scheduling, timeline behavior, H3, all CSS, security or performance results. Native/WPT evidence is the original independently reviewed evidence; this correction does not repeat or strengthen browser, build or isolated-base claims. The native patch remains the two-file patch identified by `4be581a216c84dc29887c54ee719edcafae40482b36926a2e8c03c0234e6cf0e`.

The full pinned Lean bin/lib inventory (15,308 entries, three symlink targets and 309 directories), exact 794 compiler-consumed headers, executable identities and versions remain unchanged. Installed compiled Lean libraries, compiler correctness and dynamic dependencies, system loader/runtime, Python and OS are trusted. Dependency parsing remains scoped to paths without whitespace or colon; it is not a general Make parser. See capsule/SOURCE-CONTRACT.md and THEOREMS.md for the unchanged full theorem/provider scope.

## Reproduce and authenticate

Authenticate the outer FILES/FREEZE with separately supplied handoff hashes before trusting this report. The immutable capsule has 34 source inputs and these pins:

- FILES.json: `f87c19fec82e9c9994b514e26296d64e6a55795e687ad3bd58677b32221b353f`
- FREEZE.json: `7bcc28a01a19255394ad07df6d21ef700f232a0d5606cd2b18de7a01da6e2aab`
- check.py: `cc1ba05b81be9b6838075ac6124855ff2400c4ac6057d0f4ca44f7956e8c8f39`
- source_roles.py: `86b38f49ec08249f97c8684ec3eeacad93647101f342f8ed2f1e38643cc7e3ed`

Run `python3 -I -S <capsule>/check.py --manifest-sha f87c19fec82e9c9994b514e26296d64e6a55795e687ad3bd58677b32221b353f --out <absent absolute external directory>`. A fresh manifest-only copy of the capsule can be used identically. To repeat negative controls, copy the sealed capsule and guard_controls.py/axiom_controls.py into a new otherwise empty directory, then invoke each script with Python -I -S; each creates its own absent output directory.

After terminal replay, 38 owned compiler products totaling 5,504,408 bytes were removed. The disposable relocated source copy (3,076,518 bytes) was also removed after preserving its file inventory and exact-copy receipt. CLEANUP records every removed hash. All sources, commands, dependency files, logs, rows, failure receipts and successful results remain. Earlier artifacts, shared toolchains and other agents' products were untouched.
