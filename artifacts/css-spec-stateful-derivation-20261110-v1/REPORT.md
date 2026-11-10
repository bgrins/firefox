# Stateful CSS specification derivation: escape consumption

2026-11-10. All work is confined to this directory. Earlier experiments, the canonical CSS Lean library and Firefox remain unchanged.

## Result

The reviewed escape-consumption source now generates a typed Lean effect program. Its interpreter is proved to produce the same **character, remaining input and EOF-error flag** as the pre-existing `CssEscape` relation, for every finite list of Unicode scalars. Eighteen boundary/domain examples and twelve controls passed. The held-out number-consumption algorithm was refused by the frozen translator; it produced no implementation or proof.

This is a complete small development example, not evidence that the translator generalizes to arbitrary CSS algorithms. It establishes correspondence for the generated program against our older formal model. It does **not** prove the Python translator correct for all inputs, nor mechanically prove that its interpretation of the prose is faithful.

## Source and freeze records

The pinned inputs are:

- CSS Syntax source: [`w3c/csswg-drafts` at `c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67`](https://github.com/w3c/csswg-drafts/blob/c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67/css-syntax-3/Overview.bs), SHA-256 `4a4a5a3994bda10a56885e66776169d0e05d5a7515b0def4e8859c20e3fd4afc`. This copies the prior benchmark's bytes and acquisition record, not a different draft.
- Infra source: [`whatwg/infra` at `c67ae1fb1d161b23d0f8c9bf9917ea1993f7b19a`](https://github.com/whatwg/infra/blob/c67ae1fb1d161b23d0f8c9bf9917ea1993f7b19a/infra.bs), SHA-256 `687e65669b9d85c2147a139513fe319097cf84af1005f5c9d7cb3d2ade0c1aed`. It supplies the leading/trailing surrogate definitions and their union.
- Reference library revision `162b20fb7c53a0ab89b20875a965baee98fb66bb`. Only `CssEscape.lean` and `CssInput.lean` are copied and rebuilt locally. [LIBRARY.json](LIBRARY.json) pins their hashes.

[SOURCE.json](SOURCE.json) and [INFRA.json](INFRA.json) identify the retained input files. The Infra snapshot is explicitly pinned as this experiment's cross-spec interpretation; it is not claimed to be the dependency version resolved by a historical CSS build.

[PROTOCOL.json](PROTOCOL.json) declared escape consumption as development and consume-number as held out before grammar work. Prior exposure to CSS number parsing and earlier source snippets is disclosed. This is a frozen-rule transfer experiment, not a blind evaluation or an externally preregistered study.

After the escape bridge and examples compiled, [FREEZE.json](FREEZE.json) froze the translator, IR, mapping document and manifests at **20:14:37 UTC**. [HELD-OUT-FIRST.json](HELD-OUT-FIRST.json) records the first number-consumption evaluation at **20:14:46 UTC**. The frozen files have not changed since. The local hashes detect byte drift; they are not an external timestamp or protection against rewriting the whole record.

A live `webspec-index` query failed to fetch CSS Syntax; its diagnostics are retained. It reported installed version 0.14.0 and available version 0.15.0. No tool was installed or updated. The pinned CSS source was already available, and the public Infra source was fetched separately. Verification/replay requires no network.

## What is mechanical, and what is authored

| Layer | What happens | Trust boundary |
| --- | --- | --- |
| Source selection | Hash-check source bytes; select a unique heading-bounded section | Choosing relevant source versions and dependencies is reviewed |
| Recognition | Match the complete escape interface and normalized operative body; retain exact section/body/definition byte spans | The accepted grammar and metadata classification are manually authored |
| Extraction | Recover the hex limit, replacement scalars, digit/hex ranges, whitespace, maximum scalar and Infra surrogate ranges | Interpretations of source operators and phrases are reviewed mappings |
| Generation | Emit predicates, positional arithmetic and a typed `Program Char` | Python lowering is unverified; this program's output is checked by Lean |
| Execution | Interpret typed read/scan/branch/error/sequencing effects in Lean | State abstraction and primitive meanings are authored Lean definitions |
| Correspondence | Prove this program's full result agrees with an older implementation and declarative relation | Correctness is relative to those formal definitions, not automatically to English |

[translate.py](translate.py) is intentionally a narrow recognizer with parameter extraction. It is not a general natural-language parser. It consumes the whole operative body; extra or unknown clauses are refused. The introductory caller contract must match exactly. The known algorithm note and WPT block are retained as reviewed non-operative metadata, and unfamiliar algorithm metadata is refused. Definition markup also contains explanatory notes/test metadata that the extractor strips from its operative definition text; the full source spans remain available for review.

In particular, unfamiliar note/WPT blocks inside dependency definitions are **not independently rejected**. Only the remaining operative definition text and the pinned-source digest constrain that case. Exact metadata-inventory checking covers the algorithm body, not every referenced definition. The frozen rules are retained unchanged; this narrower coverage is a limitation to address in a later version.

[GRAMMAR.md](GRAMMAR.md) records the manual meanings: maximal bounded scanning, exactly one optional terminator, base-16 positional arithmetic, letter values 10–15, inclusive ranges and alternatives, replacement conditions, input advancement and EOF/error behavior. Individual nested instruction spans are not yet emitted. There is no LLM inside the reproducible commands.

The generated code imports only [StatefulIR.lean](StatefulIR.lean). It does not call `CssEscape.consume` or any reference helper. The reference library appears only in the separately authored proofs/examples. Both models belong to this research project: their different generation paths and older definitions avoid comparing identical newly generated artifacts, but they can still share a mistaken interpretation of the spec.

## Typed state and caller domain

The IR has typed return, read, bounded scan, single conditional skip, error, branch and bind instructions. Its interpreter is total Lean code. A scan budget decreases on recursion. Continuations and pure predicates are Lean functions, so this is a higher-order embedded IR, not a first-order serializable language with a verified compiler. The generated escape program implements its optional terminator as a one-element bounded scan.

State consists of the **next unread scalar list** and an accumulated error flag. The backslash has already been consumed. The initial read binds the spec's current observation; subsequent reads operate on the residual list. EOF is `none` and does not advance an empty list. `execute` begins with no error and returns all three observable fields together. A Boolean records whether this invocation raised its EOF parse error; it does not model native error reporting or a sequence of diagnostic events.

The spec-facing `CallerReady` predicate requires normalized input and an already validated escape: CR, form feed and null have been removed by preprocessing, and an initial LF is excluded. EOF is allowed. `Char` contains Unicode scalars, so decoding, DOMString code-unit conversion and surrogate replacement must already have happened. The copied `CssInput` preprocessing model operates on scalar lists and cannot itself represent raw surrogate input. Neither that model nor this experiment proves a native tokenizer cursor/reconsume adapter.

The core program is total on other scalar lists as well, and the universal correspondence theorem covers them. Its agreement with the total reference on such inputs is not a CSS conformance claim outside the caller contract. The raw-CR versus preprocessed-CR examples make this boundary visible. Nonempty and EOF caller-ready witnesses prevent the domain conditions from being merely vacuous.

## Checked claims

[Bridge.lean](Bridge.lean) checks character-class/arithmetic agreement, bounded scanning for all budgets and scalar lists, and the optional terminator. It then proves:

```lean
theorem escape_spec (source : List Char) (result : Result) :
  execute escape source = result ↔
    CssSemantics.CssEscape.Escaped source (toReference result)
```

`toReference` only renames the character, remainder and error fields; its injectivity is proved. The theorem therefore preserves all three fields rather than projecting away an inconvenient difference. `eof_exactly` proves the fresh error flag is true exactly for empty input. `valid_call` connects caller-ready input to `ValidEscaped`, and `preprocessing_boundary` states its explicit normalization/validation preconditions.

The main correspondence audit depends only on standard `propext`; the preprocessing-boundary audit additionally uses `Quot.sound`. The driver rejects `sorryAx`, custom axioms or unexpected audit output. Typechecking the generated function alone is deliberately insufficient: the negative controls below produce type-correct but wrong programs.

There is no general theorem that arbitrary accepted source text lowers faithfully, no source-language semantics against which the Python translator has been proved correct, and no generic correctness theorem for every IR program. These are distinct future tasks. Kernel checking confirms the supplied formal claims, not the source interpretation or the correctness of Firefox.

## Observed controls

The ordinary run passed. [RESULT.json](RESULT.json) records exact commands, hashes and exit codes; [check.log](check.log) summarizes results. [Examples.lean](Examples.lean) covers EOF, literal input, hex EOF, a seventh hex digit, one/two whitespace characters, case-insensitive hex, zero, both surrogate endpoints and their neighbors, the Unicode maximum and successor, preprocessing and invalid caller input.

| Deliberate mutation | Concrete witness | Observation |
| --- | --- | --- |
| Consume seven total hex digits | `0000417` | Wrong character/remainder detected |
| Consume two whitespace terminators | `41  Z` | Lost space detected |
| Do not replace zero | `0!` | Wrong character detected |
| Do not replace surrogates | `d800!` | Wrong character detected |
| Reject the inclusive Unicode maximum | `10ffff!` | Wrong character detected |
| Suppress EOF error | Empty input | Wrong error flag detected |
| Read without advancing input | `z!` | Wrong remainder detected |

Every semantic mutant compiles; its bridge fails and a separate concrete witness is proved false by kernel reduction. Witness files import the mutated generated implementation directly, not a previously compiled successful bridge. The interpreter mutant rebuilds the generated program against the mutated interpreter before checking it. This avoids validating a changed implementation through stale imported proof artifacts.

Five additional controls reject an extra operative instruction, unreviewed algorithm metadata, changed CSS bytes, changed Infra bytes and changed frozen interpreter bytes. These controls demonstrate particular failures are detected; they do not establish completeness of the checker or translator correctness.

## Held-out result and next decision

The frozen grammar rejected consume-number's numeric-value/type/sign return interface. No code was emitted. [HELD-OUT.json](HELD-OUT.json) and [held-out.bs](held-out.bs) retain that outcome and the source section. Observed coverage is **one development algorithm supported, zero of one held-out algorithms supported**. The refusal occurs at the interface; it is not a demonstrated ability to analyze or reject all later numeric operations.

After the evaluation, inspection shows the next semantic requirements: a typed compound result, sign/type state, decimal and exponent accumulators, multi-observation lookahead, loops justified by decreasing input, and a precise numeric domain. An unbounded `while` should not be assigned an arbitrary fuel limit just to make Lean accept termination. Decimal value semantics also need an explicit choice about exact mathematical values versus native floating-point rounding and limits.

Before expanding again, I recommend reviewing the current mappings and replacing the higher-order/pure-expression portions with a small first-order typed expression/statement representation where that would permit an interpreter or lowering correctness theorem. Keep source interpretation as a separately reviewed boundary. Consume-number can now become development material, but another algorithm must be declared before the next freeze if a transfer measurement is desired. Neither this artifact nor the prior refusal should be rewritten to make the held-out result look successful.

## Clean reproduction

From this directory, using the existing Lean 4.35.0-rc4 toolchain:

```sh
python3 -I -B check.py --lean /absolute/path/to/lean
python3 -I -B replay.py --lean /absolute/path/to/lean
```

The first command verifies pinned/frozen bytes, regenerates the program, rebuilds local reference copies, checks proofs/examples, repeats the held-out refusal and runs all controls. The second creates a fresh copy of the explicit source/manifest set, with no generated Lean, IR JSON, prior results, logs or compiled inputs. It retains `REPLAY-RESULT.json` and `replay-logs/` and removes its temporary source/build directory on success. A failure removes the previous acceptance record and retains the failed temporary copy for inspection.

Both runs passed. The clean replay copied exactly 15 files, listed with hashes in [SOURCE-ONLY.json](SOURCE-ONLY.json), and reproduced all twelve controls and the held-out refusal. [REPLAY-RESULT.json](REPLAY-RESULT.json) records the copied inputs and command outcomes. To replay independently without the helper, copy just that allowlist into a fresh directory and run its `check.py` with the absolute toolchain path.

No browser tests or native builds were run, no Firefox bug was found, and no Git staging/commits were performed. Successful build directories and the owned specification cache are removed before handoff. This directory can be retained as a standalone, source-linked research artifact without depending on the canonical library's current build outputs.
