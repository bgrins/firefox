# Until-after independent review

Verdict: accept the stated conditional delimiter-continuation component. No new browser bug, whole-parser correctness result, or universal Rust translation is established.

## Interpretation and mathematics

I read the complete new `UntilAfter`, `AfterAudit`, and `AfterChallenges` modules, the inherited until-before/alignment/cleanup/recovery contracts they use, and the complete ten retained native bodies. They agree with the earlier independently written `css-parser-until-after-audit-v1/CONTRACT.md`:

- Stop plus error returns the before-phase state, including any pending block. Success under Stop still continues.
- EOF and enclosing-owned boundaries remain unread. Ownership wins when masks overlap.
- Requested-only punctuation advances one ASCII byte. Requested-only curly starts a raw block walk, preserving nested function observations and annotation writes.
- Direct advance retains the existing cache. Coherence is transferred under the inherited immutable-reader/cache admission; it is not a claim that native reset replays every side effect.

The reference continuation performs a source token read; the native-shaped continuation advances a byte. `DelimiterLaw` connects these operations locally. It does not assume the final states agree. `until_ready` derives the boundary and pending-none facts from before-phase recovery and `Progress`. The requested mask is explicitly restricted to the four public delimiters. Outer closing delimiters remain separately admitted native masks.

`Aligned` deliberately omits URL annotations. The separate continuation write equations cover them; the main refinement must not be advertised as complete URL-history equality. Likewise, the control-field theorem concerns the represented callback language, which cannot arbitrarily change native depth or nesting limits. Native callbacks can have effects outside this language.

Ten additional kernel checks are retained in `Challenges.lean`. They construct an inhabited progress/provider contract and instantiate the full refinement with all premises discharged, check actual successful consumption, distinguish Stop-success from Stop-error, exercise empty and duplicate requested masks, preserve outer-curly ownership, and exhibit failed recovery without progress. The constructed reader is a mathematical witness, not a new tokenizer implementation proof. All ten checks passed; their reported axioms are limited to `propext`, `Classical.choice`, and `Quot.sound`.

## Source and executable evidence

External seals authenticated all 236 source-capsule files before execution. The fresh manifest-only relocated replay passed:

| Gate | Result |
|---|---|
| General results / root finite kernel challenges | 22 / 11 |
| Compiled modules for the audit target | 57 |
| Complete retained source-body bindings | 10 |
| Native histories / snapshots per build mode | 27 / 138 |
| Native modes | Debug and optimized release |
| Compiled semantic mutants | Six detected; 25, 41, 22, 7, 11, 5 differing snapshots |
| Producer integrity controls, freshly rerun | 18 negative, one positive |
| Additional independent integrity controls | Five negative |

The native calibration compiles the retained cssparser crate and dependency sources. Its added adapter selects zero or one callback read and records private state; it does not replace the parser with an expected-result provider. The independent extra six native histories pass in both modes: empty-mask draining, Stop-success punctuation and curly, bang/comma overlap, and an enclosing semicolon inside a requested curly block. Expected result and cursor values were recorded separately from the native output.

I checked byte-identical transfer of all 59 imported modules and 134 source/vendor files against the externally pinned predecessor manifest. The ten native bindings match their complete source slices; parser mutation anchors select the free `parse_until_after` function. Mutants compile and exit normally before their semantic output is compared; rejected builds are not counted as kills.

The renderer erratum is correct. Actual closing-curly, square, and parenthesis bits are 32, 64, and 128; opening curly is 2. I authenticated both retained predecessor traces and independently counted 91 rows each, all with stop mask zero. Thus those older traces supplied no nonzero-mask evidence. New histories explicitly exercise all three closing delimiters and overlapping opening/punctuation masks. Duplicate mathematical mask lists are set-like in the model; the finite renderer's additive encoding is used only on unique lists constructed from native bits.

## Replay integrity and limitations

Authentication checks closed regular-file and directory rosters, hashes and sizes, duplicate JSON keys, canonical paths, and seals before loading local helper code. Fresh unsafe-shadow tests covered all four executable Python entry points and rejected before importing a nearby `json.py`. A duplicate seal key also rejected. Producer controls additionally cover optimized/nonisolated modes, symlinks, FIFO, extra directories, mutation, path escape, and internal output. These are integrity checks, not semantic theorem claims.

The unchanged predecessor remains a scoped dependency. Native lexical/provider correctness, UTF-8 and cursor validity, bound/overflow correspondence, allocation/compiler behavior, arbitrary callbacks, borrowed lifetimes, full error payloads and source-coordinate metadata remain external. The finite driver rejects unsupported numeric/string/hash/at-keyword provider families rather than silently substituting lengths. The model's progress premise alone does not imply native bounded token endpoints; that separate source correspondence remains admitted. Executable hashes do not pin every installed standard-library or toolchain runtime file.

No production files, Git state, browser, or Firefox build were changed. Completed owned compiler outputs were removed after copying raw receipts; their identities are recorded in `CLEANUP.json`.

## Reproduction

Authenticate this review's externally supplied seals before running `python3 -I -S recheck.py`. That command rechecks the closed review and retained receipts. Add `--replay /absolute/new/external/output` to rerun the complete producer replay and the ten independent kernel checks. `capsule/check.py` is the unchanged authenticated producer entry point. The recorded native commands regenerate the six additional concrete probes; retained raw inputs and outputs identify their exact fixtures.
