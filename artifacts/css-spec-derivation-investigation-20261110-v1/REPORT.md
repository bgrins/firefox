# Mechanical CSS specification derivation: feasibility and pilot

Investigation date: 2026-11-10. No Firefox source, canonical CSS Lean library, shared build directory, Git index, or Git history was changed. This directory contains the entire experiment.

## Recommendation

Pursue **source-linked, partially automated formalization**, starting with small CSS Syntax algorithms. Do not make general English-to-Lean translation the foundation of the correctness claim. A useful system can extract document structure, compile a deliberately limited vocabulary, preserve unresolved clauses, and require explicit semantic review before admitting a model.

The useful near-term result is an executable companion to the specification whose definitions, assumptions, generated code, proofs, and tests are traceable to particular source passages. A completely automatic, trusted translation of all existing CSS prose is not established by this investigation or the cited prior art.

| Layer | Feasible automation | What still needs justification |
| --- | --- | --- |
| Source acquisition | Pin source commits, hashes, anchors, definitions, cross-references and algorithm containers | Choosing normative versions and assembling the relevant transitive context |
| Structural extraction | Recover paragraphs, branches, lists, grammar fragments, property metadata and source spans | Missing or ambiguous markup; normative operations embedded in introductions and prose |
| Restricted compilation | Recognize approved statement forms and produce a typed intermediate representation and Lean functions | The meaning assigned to each language construct and external operation |
| Proof generation | Produce obligations and proof candidates; Lean checks proofs against formal definitions | The intended theorem, domain and assumptions must be reviewed independently |
| Specification faithfulness | Compare interpretations, audit clause coverage, generate counterexamples, test browsers and involve spec editors | Prose is not already a formal semantics against which a universal equivalence theorem can be checked |

The final distinction is fundamental. A verified compiler can preserve the semantics of a formally defined input language. To apply that result to ordinary CSS prose, somebody still has to justify that the prose belongs to that language and has the assigned interpretation. Agreement by two LLMs, a successful Lean proof, or browser agreement alone does not discharge that obligation.

The main failure modes are semantic, not just parsing failures:

| Failure mode | Required response |
| --- | --- |
| Ambiguous prose or omitted exceptions | Preserve alternatives or stop for interpretation; do not select a meaning silently |
| Cross-spec references or version drift | Pin the dependency closure and inspect changes to referenced definitions, not only the local paragraph |
| Circular validation | Keep the reference relation independent of generated code; do not generate both from the same mistaken translation and call their agreement evidence |
| Vacuous proofs | Check that assumptions have witnesses and that intentionally wrong behavior violates the specification |
| Partial models presented as complete | Publish excluded inputs, state effects, caller obligations and unresolved clauses alongside every claim |

## Relevant prior art

**JISET / ESMeta is the closest positive example.** JISET uses rules to compile ECMAScript's structured algorithm language into an intermediate representation. Its ASE 2020 report gives 95.03% average algorithm-step compilation across four versions, followed by manual completion; the completed ES10 model passed 18,064 applicable tests. These are the paper's reported results, not a CSS estimate or a proof of every translation rule. ESMeta continues the approach with interpreters, conformance-test synthesis and specification analysis. The lesson is to build an explicit metalanguage and a visible unsupported remainder, rather than treating prose as arbitrary prompts. [JISET paper abstract](https://conf.researchr.org/details/ase-2020/ase-2020-papers/77/JISET-JavaScript-IR-based-Semantics-Extraction-Toolchain), [ESMeta repository](https://github.com/es-meta/esmeta).

**Bikeshed and W3C Reffy/Webref provide structural infrastructure.** Bikeshed identifies algorithms and scopes marked variables, but that is not an executable semantics. Reffy's algorithm extractor retains steps and introductory prose and explicitly documents extraction limitations, including missed steps, branch handling and normative/informative ambiguity. Reuse these sources for inventories and provenance; do not assume an extracted step list is complete or already meaningful to Lean. [Bikeshed documentation](https://speced.github.io/bikeshed/), [Reffy algorithm extractor](https://github.com/w3c/reffy/blob/main/src/browserlib/extract-algorithms.mjs), [Webref](https://github.com/w3c/webref).

**Cassius shows standalone CSS semantics can be useful.** It formalizes a CSS layout fragment and reduces layout reasoning to SMT, supporting verification, debugging and synthesis. Its evaluation includes browser comparisons and explicitly scoped behavior. It is evidence for the usefulness of a separately maintained CSS semantics, not evidence of mechanically deriving all CSS prose or of a CSS-to-Lean pipeline. [Panchekha and Torlak, OOPSLA 2016](https://sandcat.cs.washington.edu/papers/Torlak-cassius-oopsla-2016.pdf).

**WebSpec shows how models and native tests can reinforce each other.** It combines a Coq browser-security model, invariants, SMT-based analysis and executable browser tests derived from traces. The useful analogy is the separation between a mathematical model, checked properties and implementation evidence. It is not a CSS extraction system. [WebSpec paper](https://arxiv.org/abs/2201.01649).

**LLM autoformalization is a candidate-production mechanism.** Research demonstrates translation of some mathematical statements into formal languages. That supports using agents to propose formalizations and proofs, but does not establish semantic faithfulness for CSS's cross-referenced, stateful prose. The cited work targets mathematics in Isabelle/HOL, not CSS or Lean; transferring its success rates would be unjustified. [Wu et al., 2022](https://arxiv.org/abs/2205.12615).

## Working pilot

The pilot uses CSS Syntax's [valid-escape algorithm](https://drafts.csswg.org/css-syntax-3/#starts-with-a-valid-escape), already represented by an after-backslash predicate in our library. It is intentionally very small: two conditional returns and a final return, with a referenced definition of newline. The linked definition excludes carriage return because preprocessing handles it separately. This makes the example useful for exposing caller assumptions even though its branch logic is simple.

The input is the actual Bikeshed source, not a rewritten English prompt:

- Repository revision: `c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67`.
- Source: [`css-syntax-3/Overview.bs`](https://github.com/w3c/csswg-drafts/blob/c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67/css-syntax-3/Overview.bs).
- SHA-256: `4a4a5a3994bda10a56885e66776169d0e05d5a7515b0def4e8859c20e3fd4afc`.
- Acquisition record: [SOURCE.json](SOURCE.json); source bytes are retained under `inputs/`.

`extract.py` selects the heading-bounded section, retains its five paragraphs, recognizes the three decision paragraphs, resolves the newline constant from its definition, and emits [algorithm.json](algorithm.json) with byte spans. It generates [Generated.lean](Generated.lean) from that intermediate representation. It is a purpose-built prototype for this grammar shape, not a general Bikeshed parser. No LLM runs inside the extraction or verification commands.

### What was automatic and what was authored

| Part | Origin and trust boundary |
| --- | --- |
| Source bytes, section boundaries and constants | Extracted from the pinned source; digest changes are rejected |
| Statement and definition recognition | Manually authored Python grammar rules; unsupported decision prose or extra paragraphs is rejected |
| Intermediate representation and Lean function | Deterministically generated from recognized operators, positions, constants and return values |
| Meaning of the operators | Manually chosen: ordered fallthrough, equality/inequality, Boolean returns and a two-observation interface |
| Input domain | Manually chosen `Option Char`: a Unicode scalar or EOF. This is not an encoding or arbitrary UTF-16 model |
| Introduction and note | Retained in the output, not translated into a proved stream interface or non-consumption theorem |
| Existing reference | Read-only snapshots of `CssInput.lean` and `CssEscape.lean` from library commit `162b20fb7c53a0ab89b20875a965baee98fb66bb`, rebuilt locally |
| Bridge statements and proofs | Authored for this experiment and checked by Lean against the separately existing reference |

The main theorem in [Bridge.lean](Bridge.lean) is:

```lean
theorem afterBackslash (source : List Char) :
    validEscape (some '\\') source.head? =
      CssSemantics.CssEscape.validAfter source
```

A second theorem connects the generated result to the existing declarative `ValidAfter` relation. This is not a proof comparing two identical newly generated definitions: the right-hand implementation and relation predate this experiment and use a list-domain formulation, whereas the extracted predicate uses two optional scalar observations. The theorem quantifies over every list in that model domain; it is not just a handful of examples. Nevertheless, its semantic content is small, and agreement between these two formalizations does not itself prove the interpretation of the English.

The theorem covers the after-backslash interface. It does not establish the whole tokenizer, input acquisition, stream-position correctness, or that arbitrary callers pass preprocessed data. Five explicit examples include EOF, a newline, a non-backslash first input, and carriage return before/after preprocessing. The latter pair changes the result as expected and illustrates why an isolated algorithm can be correct while its caller is wrong.

### Actual results

`check.py` completed successfully with the existing Lean `4.35.0-rc4` toolchain. It rebuilt the two reference modules, compiled the generated function, checked both bridge theorems and five examples, and recorded their standard axiom dependencies as `propext` and `Quot.sound`. No `sorry` or custom axiom is admitted in the successful bridge. [RESULT.json](RESULT.json) records commands, hashes and outcomes; [check.log](check.log) summarizes the controls.

| Control | Observed outcome |
| --- | --- |
| Unsupported conditional wording | Extraction rejects the unrecognized statement |
| Additional body paragraph | Extraction rejects the changed paragraph inventory |
| Changed pinned source bytes | Actual extractor rejects the input before generation |
| Mutated branch accepts newline | Generated function still compiles; correspondence proof and explicit newline example fail |

The last control directly demonstrates that typechecking an algorithm is weaker than checking its correspondence to an independent reference. It does not demonstrate compiler correctness for all possible intermediate representations. The extraction grammar, JSON representation and Python-to-Lean generator remain unverified parts of this experiment.

No browser tests were run, no bug was found, and no current library theorem was changed. Temporary Lean outputs were removed after success. `webspec-index` was used with an investigation-local database; its definition-only query omitted the following decision paragraphs, while the enclosing heading query included them. Both query outputs are retained; the temporary database and HTML cache were removed. This is a concrete reason not to confuse a definition anchor with a complete algorithm. The tool reported installed version 0.14.0 and available version 0.15.0; it was not updated.

## Practical next experiment

Extend this to a small, declared benchmark of three algorithms: this predicate, the three-code-point number-start predicate, and escaped-code-point consumption. The latter adds bounded consumption, replacement rules and parse-error/EOF behavior. Hold at least one algorithm out while designing extraction rules so the result measures reuse, not only a template tailored to the demonstration.

For each algorithm, require:

1. A source/definition dependency closure with immutable versions, exact spans and explicit normative/informative classification. Any unrecognized clause remains unavailable rather than silently becoming a no-op.
2. A reviewed typed intermediate representation with input/output, mutation, error and termination semantics. Keep extraction coverage separate from semantic coverage.
3. A proof against the independently existing library relation, plus positive witnesses and intentionally wrong branch, boundary and state-effect controls. Review assumptions for satisfiability and avoid proving a weakened relation chosen just to fit the generated code.
4. A deliberately edited specification snapshot that produces a focused semantic diff or an explicit refusal. Rechecking a source hash alone detects change but cannot classify it.
5. Separate browser comparison evidence where a faithful observable adapter exists. A shared browser bug, a wrong adapter or underspecification can explain agreement/disagreement; none makes browser output an unquestionable oracle.

If that succeeds, formalize the small IR interpreter and verify the lowering into executable Lean, or use Lean definitions directly as the IR interpreter. That would reduce the trusted translation machinery. It would still leave extraction and the interpretation of the admitted source-language phrases as explicit obligations.

For less algorithmic CSS, use relations and sets of permitted outcomes rather than forcing a deterministic program. Layout constraints, implementation-defined choices, host hooks, resource loading, dynamic invalidation and cross-module exceptions need explicit domains and composition contracts. The small Syntax pilot provides no estimate of the cost of those tasks or of total CSS coverage.

## Evolving alongside the specification

A useful standalone artifact could maintain sidecar contracts keyed by spec commit and anchor, with generated source maps, checked Lean semantics, examples and unresolved interpretations. A spec-change check could show the exact affected clauses, formal definitions, proofs and tests. Agents could propose updates; reviewers would approve semantic changes. Avoid inferring that unrelated unchanged paragraphs imply an unchanged algorithm: referenced definitions and applicability rules also matter.

The strongest long-term arrangement would be collaboration with spec editors on a controlled semantic notation whose Lean meaning is defined, with prose and executable examples produced from the same reviewed representation. That reduces a translation gap by changing the authoring process. It is not a claim that existing W3C prose already has that status, and such a companion should not present itself as normative without the standards process adopting it.

## Reproduce

Run from this directory with Python 3 and the existing toolchain; no network or additional package installation is needed:

```sh
python3 -I -B check.py --lean /path/to/lean-4.35.0-rc4/bin/lean
```

The command writes only this directory, leaves no successful-run build target behind, and fails on altered pinned source or library snapshots. A failed run removes the previous acceptance result and leaves its local build outputs for inspection. `SOURCE.json` and `LIBRARY.json` identify the input snapshots; [extract.py](extract.py), [Bridge.lean](Bridge.lean) and [check.py](check.py) are the review entry points.
