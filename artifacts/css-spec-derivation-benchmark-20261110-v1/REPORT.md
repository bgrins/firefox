# Frozen-rule CSS derivation benchmark

2026-11-10. This experiment extends the [first pilot](../css-spec-derivation-investigation-20261110-v1/REPORT.md) without changing that artifact, the canonical CSS Lean library or Firefox.

## Result and recommendation

The shared translator handles both selected training predicates, and Lean checks their agreement with previously written library models. It refuses the held-out consuming algorithm before generating code. Continue with a small, separately versioned stateful IR experiment; do not describe this result as automatic formalization of CSS generally.

| Algorithm | Role | Extraction / generation | Checked result |
| --- | --- | --- | --- |
| Valid escape | Training | Three Boolean returns, ordered conditions, resolved newline constant | Agreement with the existing after-backslash predicate and relation for every `List Char` |
| Number start | Training | Four switch cases, seven Boolean returns, resolved inclusive digit range | Agreement with the existing number-start predicate and relation for every `List Char` |
| Consume escaped code point | Held out | Rejected at the first input-consumption instruction; no generated Lean | No derived implementation or correspondence theorem |

The observed outcome is **2/2 selected training algorithms and 0/1 held-out algorithm**. This is neither a CSS-wide coverage estimate nor evidence of broad extraction accuracy. Ten recognized Boolean returns omit the introductions' semantics; statement counts are not semantic coverage. The two list adapters also have checked state-preservation theorems, within the explicitly chosen list abstraction.

The frozen grammar adds switch cases and ASCII character-range tests to the earlier pilot. That modest extension works for another observational predicate. The held-out outcome shows that translating a parser operation requires additional semantics, not just recognizing a familiar function name and calling our existing parser.

## Protocol and provenance

[PROTOCOL.json](PROTOCOL.json) declared valid escape and number start as training, and escape consumption as held out. I already knew CSS and had seen consumption snippets while searching during the pilot and benchmark setup. This was **not a blind or independently preregistered evaluation**. It tests whether an explicitly frozen rule set transfers without adaptation.

After both training bridges compiled, [FREEZE.json](FREEZE.json) recorded hashes of `translate.py`, the vocabulary document, protocol and source/library manifests at **18:48:57 UTC**. [HELD-OUT-FIRST.json](HELD-OUT-FIRST.json) records the first held-out invocation at **18:49:05 UTC**, its exact command, refusal and empty generated-file list. The translator has not changed since that freeze. The driver rechecks the frozen bytes before and after every full run. These local hashes detect drift; they are not an external timestamp or a defense against someone rewriting the whole experiment record.

The source is the same pinned CSS Syntax Bikeshed snapshot as the first pilot:

- [`w3c/csswg-drafts`, revision `c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67`, `css-syntax-3/Overview.bs`](https://github.com/w3c/csswg-drafts/blob/c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67/css-syntax-3/Overview.bs).
- SHA-256: `4a4a5a3994bda10a56885e66776169d0e05d5a7515b0def4e8859c20e3fd4afc`.
- [SOURCE.json](SOURCE.json) preserves the original acquisition record; this benchmark copied those bytes without fetching a different draft.
- Independent reference: CSS Lean commit `162b20fb7c53a0ab89b20875a965baee98fb66bb`; [LIBRARY.json](LIBRARY.json) pins the copied modules and their dependencies. Copies are rebuilt inside this directory.

A fresh `webspec-index` query for number start failed to fetch the live draft; its output/error are retained. This did not affect the pinned-source experiment. The tool also reported installed version 0.14.0 and available version 0.15.0; no installation or update was performed. No current-draft equivalence is claimed.

## What the machine checks

[translate.py](translate.py) extracts heading-bounded source, keeps byte spans and the unmodeled introduction, recognizes the restricted body forms, resolves newline/digit definitions and produces a JSON tree. It emits Lean Boolean functions and observational list adapters from that tree. The introduction and body have source spans; nested nodes do not yet have individual clause spans. Source snapshots and the complete extracted training sections are retained under `inputs/` and `generated/`.

[GRAMMAR.md](GRAMMAR.md) states the manual choices: ordered fallthrough, equality, inequality, conjunction, switch-label disjunction, inclusive scalar ranges and `Option Char` for scalar/EOF observations. The compiler is unverified Python. Pinning source bytes does not prove that these interpretations are correct.

[Bridge.lean](Bridge.lean) proves two correspondence chains:

1. Generated `validEscape`, when supplied a backslash and the list head, equals the pre-existing `CssEscape.validAfter`; its true result is equivalent to the pre-existing `ValidAfter` relation.
2. Generated `observeNumberStart` returns the same Boolean as pre-existing `CssNumberParts.startsNumber`; its true result is equivalent to the independently existing `StartsNumber` relation, which describes an optional sign and unsigned start.

The reference definitions predate this experiment and are not emitted by the same translator. The bridge proofs are authored separately. These are universal proofs over finite lists of Unicode scalars, not exhaustive testing of a selected alphabet. They do not cover all arbitrary triples of independent optional observations, decoding, UTF-16 input, preprocessing, tokenizer cursor state or the native browser.

The non-consumption note is informative prose. We manually interpret it, together with the observational body, as preserving a supplied list. `escape_preserves` and `number_preserves` check that the generated adapters return that list unchanged. They do not independently establish a refinement of CSS's current/next-input-point machinery, and the list model does not encode a reconsume flag.

The successful proof audit lists only Lean's standard `propext`, `Classical.choice` and `Quot.sound` dependencies for correspondence, and no axioms for the two state-preservation theorems. The driver rejects unexpected audit output, including `sorryAx`. Eight concrete examples also cover EOF, LF, signed fractions, digit boundaries, missing lookahead, a non-ASCII digit and retained input. Successful kernel checking remains relative to the formal statements and reference models; it is not a theorem about English meaning.

## Controls

[RESULT.json](RESULT.json) records exact commands, exit codes, hashes and outcomes. [check.log](check.log) summarizes the run.

| Deliberate change | Required observation |
| --- | --- |
| Unknown conditional wording | Extraction refuses it |
| Extra operation after a return | Extraction refuses it |
| Non-consumption note changed to consumption | Extraction refuses the unsupported effect |
| Changed source bytes | Actual command rejects the source before generation |
| Changed translator bytes | Integrity check rejects the mismatch against the frozen digest |
| Newline branch changed to return true | Generated Lean typechecks; correspondence and newline witness fail |
| Source digit lower bound changed from zero to one | Extraction and generated Lean typecheck; correspondence and zero witness fail |
| List adapter advances input by one | Generated Lean typechecks; preservation theorem and retained-input witness fail |

The boundary mutation invokes the extractor on an intentionally modified in-memory source to exercise the semantic checker. It does not bypass the pinned-source requirement of the normal command. The state mutation changes emitted code, not the frozen generator. The three semantic mutants illustrate why typechecking a generated function is insufficient. They do not establish that every wrong translation will be detected, or prove the Python compiler correct.

## What consumption still requires

[HELD-OUT.json](HELD-OUT.json) and [held-out.bs](held-out.bs) retain the refusal and exact section. The first unsupported instruction is input consumption. The following inventory was written **after** the frozen evaluation by reading the source and existing reference; these are proposed obligations, not automatically extracted or proved coverage:

| Operation or condition | Existing reference to compare against | Missing translator capability |
| --- | --- | --- |
| Backslash already consumed; next observation validated | `ValidAfter` / `ValidEscaped` | Caller preconditions and an explicit current/next-input adapter |
| Initial consumption and literal return | `CssEscape.consume`, `Escaped.literal` | Input-state transition and character-valued results |
| Up to five additional hex digits, maximally | `scanHex`, `HexRun` | Bounded repetition, stopping conditions and accumulation |
| One optional whitespace terminator | `skipWhitespace`, `Terminator` | Conditional consumption and source character-class dependencies |
| Hex value and invalid scalar replacement | `magnitude`, `decode` | Numeric interpretation, surrogate bounds and maximum-code-point references |
| EOF parse error and replacement | `Escaped.eof`, `Result.eofError` | EOF behavior and observable error output |

The reference parser already provides these operations, but substituting it by name would erase the derivation question. A next version should define a small typed stateful IR, give its interpreter a Lean meaning, and translate reviewed clauses into it. Prove output character, remaining input and error behavior together against `Escaped`, while exposing valid-input/preprocessing assumptions. Test mutations at the sixth/seventh hex digit, optional whitespace, EOF, zero, surrogate boundaries and the maximum Unicode value.

There are structural gaps too: the held-out section ends with a WPT metadata block that the training grammar does not classify. The observed refusal identifies the first unsupported operation, not an exhaustive machine-generated inventory of every later obstacle. Recognizing metadata separately from normative operations should precede any broader coverage claim.

Because consumption has now been inspected, it cannot honestly remain held out in that next version. Use it as development material and predeclare another algorithm, such as consuming a number, before freezing the extended grammar. Report unsupported constructs again rather than expanding the grammar during the measurement.

## Reproduction and scope

From this directory:

```sh
python3 -I -B check.py --lean /path/to/lean-4.35.0-rc4/bin/lean
```

The command needs no network or additional packages. It verifies frozen/source/library hashes, regenerates the two training functions, builds isolated reference copies, checks the proofs, repeats the held-out refusal and runs the controls. It removes its own temporary build directory after success; failure removes the previous acceptance result and leaves outputs for inspection. It does not modify the first pilot, canonical library, Firefox source, shared objdir, Git index or history. No browser tests or native builds were run, and this benchmark found no new Firefox bug.

For an independent replay starting with only source, frozen manifests and proof files:

```sh
python3 -I -B replay.py --lean /path/to/lean-4.35.0-rc4/bin/lean
```

This copies an explicit source set into a newly created subdirectory. It copies no generated Lean, IR, results, logs or compiled files, runs the same checks, retains `REPLAY-RESULT.json` and `replay-logs/`, and removes the temporary source/build copy after success. A failed replay retains its copy for inspection. The generated list of copied paths and hashes lets another reviewer audit what the replay actually used.

Both the ordinary run and the source-only replay passed with Lean 4.35.0-rc4. The replay copied 14 source/manifest files, reproduced all eight controls and the held-out refusal, and removed its temporary directory. [REPLAY-RESULT.json](REPLAY-RESULT.json) and [replay.log](replay.log) retain the evidence. No build or spec database cache remains in this artifact.

A standalone companion could keep these pinned source maps, reviewed vocabulary, generated code, proof obligations and refusals alongside each spec revision. The next useful result is a trustworthy small stateful slice, not a percentage claiming to cover the whole CSS specification.
