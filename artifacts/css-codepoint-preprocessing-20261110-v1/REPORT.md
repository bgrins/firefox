# CSS input preprocessing over Unicode code points

2026-11-10. This artifact fills a concrete domain gap in the existing CSS Lean model: its `List Char` input cannot contain surrogate code points, so it cannot express their required preprocessing replacement. The new executable accepts every Unicode code point, including surrogates, and returns scalar values. The canonical library and previous artifacts remain unchanged.

## Coverage added

[CodePointInput.lean](CodePointInput.lean) defines `CodePoint := Fin 0x110000`, representing values U+0000 through U+10FFFF inclusive. It implements finite-list preprocessing and separately states `Point` and `Preprocess` relations. These relations describe individual replacements, ordinary preservation, and CRLF pairing without calling the executable functions.

The model covers the two filtering requirements in the current pinned [CSS Syntax preprocessing section](https://drafts.csswg.org/css-syntax-3/#input-preprocessing): normalize CR/FF/CRLF to LF, and replace NUL/surrogate code points with U+FFFD. Its code-point range and surrogate classification follow the pinned [Infra definitions](https://infra.spec.whatwg.org/#code-points). A CRLF pair is consumed together; the relation's single-element rule explicitly excludes that pair, preventing an alternative two-LF derivation.

The executable `point` handles individual values, and `preprocess` gives CRLF priority before applying it. The relation's ordinary rule requires an output scalar with the same numeric value as the input. `Char` validity therefore excludes a surrogate from the ordinary rule. Output scalar validity is likewise guaranteed by the `List Char` type, while the explicit `Normalized` predicate excludes CR, FF and NUL.

`ofNat?` and `filterValues` provide checked admission from natural-number values. Values above U+10FFFF are rejected; `none` here is an out-of-domain result, not a modeled CSS parse error. Use those admission functions for external numbers: ordinary `Fin` numeral construction can reduce modulo its bound and is not an input decoder.

## Domain boundaries

The input is a **finite list of already identified Unicode code points**, of arbitrary finite length. The model does not decode bytes, select an encoding, process byte-order marks at the decoding layer, or implement WebIDL/DOMString/UTF-16 conversion. It also does not model a live stream, asynchronous delivery, chunk state or infinite input.

In particular, `[U+D83D, U+DE00]`, supplied as two code points, becomes two replacement characters. U+1F600 supplied as one scalar is preserved. This does not say that an actual DOMString containing the corresponding valid UTF-16 pair becomes two replacements: converting those code units into code points is a separate, unmodeled operation. The source note about DOMString-originated surrogates is retained in the clause map, not silently treated as a proved conversion algorithm.

Chunk boundaries need separate work. Filtering `[CR, LF]` yields one LF, while separately filtering `[CR]` and `[LF]` and concatenating yields two. The current theorems do not justify stateless per-chunk processing; a streaming implementation would need to retain pending-CR state and prove its relation to the whole-list model.

Noncharacters, U+FEFF supplied as a code point, and Unicode line/paragraph separators are preserved by this filtering step. This is scoped to preprocessing, not a claim about earlier decoding or every subsequent CSS operation.

## Checked properties

[Correctness.lean](Correctness.lean) proves:

- `point_iff` and `preprocess_iff`: the executable result holds exactly when the separately stated relation holds.
- Existence and uniqueness of relational output for every admitted list.
- Output normalization and non-increasing length.
- `surrogate_cons`: every surrogate code point becomes one replacement scalar without merging it with the following code point.
- `ofNat?_none_iff`: numeric admission rejects exactly values at or above U+110000.

[Refinement.lean](Refinement.lean) connects the model to the older scalar-only `CssInput` semantics. The key theorem is:

```lean
theorem scalar_refinement (source : List Char) :
  preprocess (source.map embed) = CssInput.preprocess source
```

Thus the new input domain adds surrogate behavior while preserving the previous semantics on every scalar-only list. The proof lifts the older declarative preprocessing derivation into the new relation; it does not merely compare a collection of sample strings.

Normalized scalar lists are exactly the fixed points after embedding. Idempotence is stated with that necessary type conversion:

```lean
theorem preprocess_idempotent (source : List CodePoint) :
  preprocess ((preprocess source).map embed) = preprocess source
```

This is not a theorem about running an unmodeled decoder twice. Ordinary normalized scalar input is also proved preserved. The core correspondence/normalization proofs are independent of the older library; that library is imported only for refinement and its consequences.

The audited dependencies are standard `propext`, `Classical.choice` and `Quot.sound` where needed. The driver rejects unexpected audit output, including `sorryAx` and custom axioms. The proofs are checked formal statements relative to the authored model, not a machine proof that English has been interpreted correctly.

## Current source snapshots and interpretation

[SOURCES.json](SOURCES.json) records a fresh acquisition of the latest GitHub commit touching each source path at retrieval time:

- [CSS Syntax source at `c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67`](https://github.com/w3c/csswg-drafts/blob/c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67/css-syntax-3/Overview.bs), SHA-256 `4a4a5a3994bda10a56885e66776169d0e05d5a7515b0def4e8859c20e3fd4afc`.
- [Infra source at `c67ae1fb1d161b23d0f8c9bf9917ea1993f7b19a`](https://github.com/whatwg/infra/blob/c67ae1fb1d161b23d0f8c9bf9917ea1993f7b19a/infra.bs), SHA-256 `687e65669b9d85c2147a139513fe319097cf84af1005f5c9d7cb3d2ade0c1aed`.

These match the previously used revisions; the acquisition checks current path history rather than assuming those earlier snapshots remain current. “Current” is scoped to this retrieval, not future revisions. The copied reference `CssInput.lean` is pinned in [LIBRARY.json](LIBRARY.json) at library revision `162b20fb7c53a0ab89b20875a965baee98fb66bb`.

[CLAUSES.json](CLAUSES.json) provides seven exact source-byte links to the filtering rules, domain definitions and DOMString boundary note. [input-preprocessing.bs](input-preprocessing.bs) retains the whole selected section. [source_links.py](source_links.py) verifies snapshot hashes and uniquely locates the reviewed clauses.

**The mapping is manually authored.** CRLF precedence, preservation of other points, finite-list interpretation, the relation rules and their links to source text were chosen and reviewed. The extraction script supplies traceability, not derived Lean semantics or a prose-correspondence theorem. No general DSL, parser generator or new numeric parsing model was added.

The `webspec-index` live fetch failed; its diagnostics are retained. It reported installed version 0.14.0 and available version 0.15.0. No tool update or installation was performed. The rendered specification was consulted and immutable source bytes were fetched directly. Proof/replay commands require no network.

## Examples and controls

The ordinary run passed with **21 examples and 11 controls**. [RESULT.json](RESULT.json) records exact commands, hashes and outcomes; [check.log](check.log) summarizes them. Examples cover CRLF overlaps, CR/FF/NUL, all four surrogate subrange endpoints, adjacent scalar boundaries, noncharacters and the Unicode maximum, supplementary scalars, out-of-domain values and decoding boundaries.

Eight executable-only mutations leave the relation unchanged. Each mutant first typechecks, then fails both the relational proof and a concrete witness:

| Mutation | Witness |
| --- | --- |
| Fail to collapse CRLF | `[CR, LF]` must yield one LF |
| Collapse an unrelated pair | `[A, LF]` must preserve A |
| Fail to convert CR | A lone CR becomes LF |
| Fail to convert FF | A lone FF becomes LF |
| Fail to replace NUL | NUL becomes U+FFFD |
| Exclude surrogate endpoints | U+D800 and U+DFFF both become U+FFFD |
| Replace a noncharacter | U+10FFFF remains U+10FFFF |
| Treat code points as UTF-16 units | U+D83D followed by U+DE00 remains two replacement outputs at this layer |

The remaining controls reject a direct construction above the admitted code-point range and changed CSS/Infra source bytes. The negative witnesses import the mutant executable directly, not a stale successful correctness module. This establishes that the tested errors are real semantic differences, rather than only failures of a particular proof tactic.

All checker rejection guards use explicit `if`/`raise`; they do not rely on Python `assert`, which optimization can remove. No bug in Firefox was discovered or fixed by this artifact.

## Reproduction and next use

From this directory with Lean 4.35.0-rc4:

```sh
python3 -I -B check.py --lean /absolute/path/to/lean
python3 -I -B replay.py --lean /absolute/path/to/lean
```

The first command validates sources, rebuilds the model/reference, checks proofs and examples, and runs the controls. The second copies only the explicit source allowlist into a fresh directory and repeats the check without generated or compiled inputs. `SOURCE-ONLY.json` records that allowlist and hashes; `REPLAY-RESULT.json` records replay outcomes. Failed runs remove the preceding acceptance record and retain their failed temporary copy for inspection. Successful owned build/replay directories are removed.

The clean replay passed using exactly **11 source/manifest files**, reproducing all 21 examples and 11 controls. An independent reviewer can copy just [SOURCE-ONLY.json](SOURCE-ONLY.json)'s allowlist to a fresh directory and run its `check.py` with the absolute toolchain path.

After review, this module could extend the standalone library as the code-point-domain preprocessing layer, with `scalar_refinement` preserving compatibility with existing scalar consumers. A separate follow-up could prove a pending-CR streaming adapter or an explicitly chosen UTF-16-to-code-point conversion. Neither is a prerequisite for the bounded claim completed here, and neither is currently proved.

No canonical library or native source was edited, no browser/native build was run, and no Git staging or commits were performed.
