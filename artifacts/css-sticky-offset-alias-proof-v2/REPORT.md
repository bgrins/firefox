# Sticky explicit-offset alias: completed producer companion

Producer replay result: PASS within the stated integer/provider scope. Independent review and root acceptance are pending. No production, WPT, Git or browser changes were made, and no Firefox build was run. The original proof-v1 checkpoint and all sealed earlier companions were preserved.

## Immutable replay source

`capsule/` contains 28 source inputs. Authenticate these externally supplied hashes before executing:

- FILES.json: `1ee421e14ca92e166927ce78f6be14a02fc8308cd61cef5fb20a18b588430a39`
- FREEZE.json: `330ca76a08b3f48fe4c101737e8300cb17ca34969f9fd019fa7fcde95a4aacea`
- check.py: `ba3a03b0f7b45cf0173a7a107231c40eeb42e305f428f49d28b4b358d8e9c7b6`

Run `python3 -I -S <capsule>/check.py --manifest-sha 1ee421e14ca92e166927ce78f6be14a02fc8308cd61cef5fb20a18b588430a39 --out <absent external directory>`. The two terminal replays used ordinary Unix paths without whitespace/colon; the compiler dependency-file parser is scoped to that path profile. It is not a general Make dependency parser.

The Lean installed bin/lib inventory is independently reusable data at `capsule/LEAN-TOOLCHAIN.json`, SHA256 `f1ad96d1e41dbf587664a02e9f11cf3630afa2d591de17aaebd53312f99ef3b5`. It pins 15,308 entries, three symlink targets and 309 directories, including the entire transitive compiled Init/Std closure. This is pinned trusted library input, not a fresh proof of all Std. The separate CPP-HEADERS.json pins the exact 794 compiler-consumed headers and every native compilation must emit that same dependency closure. Compiler/Lean executables and versions are pinned. System loader/runtime, compiler dynamic libraries, Python and OS remain trusted.

## Results

Both original and relocated final replays exited 0. All 19 compared result/table/log streams are byte-identical across locations, including all 11 native result streams, the executed Lean rows, and generated kernel calibration source.

| Gate | Result |
|---|---:|
| Audited named results | 31 |
| Original encoding results preserved byte-for-byte | 12 |
| Source-observer results | 12 |
| Kernel mutant witnesses | 5 |
| Kernel whole-corpus calibration results | 2 |
| Concrete inputs | 236, including all original 216 |
| Correct native configurations | 6 |
| Paired native/Lean semantic mutations | 5 |
| Rejected provider/schema inputs | 11 |
| Tooling integrity controls | 26 |
| Custom-axiom and sorry controls | 2 |

The six correct native configurations are exact original, tested repair and final formatted repair, each at -O0 and -O2 with UBSan. They agree with the independently executed Lean observations and separate boundary oracle. Each semantic mutation compiles successfully, agrees with its corresponding executed Lean mutation, and differs from the correct observation: actual-auto misclassification 112 cases, max/min reversal 112, two-unit reservation 28, negative-value loss 44, wrong-side selection 236. Failed compilation is never mutation evidence. Complete first witnesses are retained in MUTANTS.json.

Tooling controls cover pre-import rejection for unsafe/optimized Python invocation, import shadows, closed roster violations (including nested seals, empty directories, FIFOs and links), changed/missing source, invalid output locations, resealed corpus/binding/compiler and installed-library mismatches. Controls that intentionally change proof source re-bind disposable transfer metadata to reach the axiom gate; custom axioms and sorry are then rejected without any native source compilation or successful RESULT.json. These are producer controls, not independent review.

## What is established, and what remains assumed

The original integer library is unchanged. The new source-shaped model follows the complete native helper's actual-auto branch, original side/basis forwarding, one resolution call for explicit values, and reserved-boundary min operation. It connects these observations to encoding/decoding theorems and proves the constant subtraction is signed32-safe. Two generated kernel-decided results check the full old/new concrete observation tables. Native calibration extracts full helper bodies and actual constant declarations, authenticates the helper-only repair and formatting-only transfer, and compares the complete value/query/resolution rows.

The core no-alias conclusion is that the reserved code denotes actual auto after anchor resolution; explicit resolved values remain explicit. For resolver values within its admitted normal range, nonreserved values are preserved and the original maximum changes by one app unit. A kernel counterexample shows why the upper-bound premise is necessary for the one-unit claim. This supplies the encoding premise required by the separate finite-sentinel positional consumer proof.

`actual auto` means the anchor-resolved inset, not necessarily literal authored syntax. Anchor resolution, style lifetime, correct provider selection, numeric FP/percentage/Rust calc resolution and downstream geometry remain explicit admissions. The real numeric helper asserts that an unconstrained basis has no percentage; maximum-basis calibration additions are interpreted as pure-length cases. The source-to-model interpretation and facade fidelity are calibrated rather than a mechanized proof of arbitrary C++ semantics. No global sticky/timeline/layout or all-CSS correctness is claimed. See capsule/SOURCE-CONTRACT.md and THEOREMS.md for exact boundaries and all theorem signatures.

Native browser/build/standalone-patch evidence is retained from the parent fix artifact in checkpoint/: its receipts report 80 paired WPT rows, 32 improvements and 48 unchanged passes, a successful build, and source-only two-file applicability. This task did not rerun or independently adjudicate those browser/build gates.

## Cleanup and historical receipts

After terminal checks, 87 owned compiler products totaling 11,684,112 bytes were removed, including the initial partial Lean development output and axiom-negative outputs. The temporary relocated source copy was removed after exact-copy and replay evidence was retained. CLEANUP.json records all hashes; generated sources, dependency files, commands, logs, rows and terminal results remain. The initial local tactic failure is retained and was resolved before successful replays. No shared toolchain, another agent's output, or earlier artifact was removed.

Suggested independent review: authenticate and inspect the three proof modules, source/extraction bindings, provider contract and complete toolchain gates; replay into a fresh directory; challenge actual-auto versus explicit maximum, numeric upper-bound necessity, forwarding/skip traces, and custom-axiom rejection; retain the C++ interpretation and FP/Rust provider admissions when deciding acceptance.
