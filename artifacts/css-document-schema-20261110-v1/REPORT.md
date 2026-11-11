# Generic document schema and alias environment

Implemented a signature-parameterized reader for arbitrary finite lists of flat,
alias-free definitions. Proved its definition-list soundness/completeness,
accepted-document soundness, exact compatibility with the previous escape reader
on every JSON value, and actual selected-alias evaluation without ambient capture.
This is standalone research tooling; canonical library and native files remain
unchanged, and no CSS feature coverage is added.

## Closed results

| Result | Scope |
| --- | --- |
| `exactFields_spec`, `exact_keys_spec` | The existing field checks reflect an independent key-list permutation relation when expected names are distinct. |
| `definition_spec`, `definition_list_spec`, `definitions_spec` | Iffs between executable admission and an independent alias-free JSON/typed-expression relation, including arbitrary finite profiles and duplicate-signature rejection. |
| `definition_names`, `admitted_alias_names` | Alias names preserve signature order and uniqueness. |
| `document_sound` | Every accepted document has exact outer keys, admitted definitions, the actual program JSON schema, and exact normalized typed erasure. |
| `escape_wrapper_equivalent` | The generic escape-profile wrapper equals the old fixed reader for all JSON values, including failures. |
| `definition_data_normalized` | Actual `readDefinition` acceptance supplies the normalized-data premise of the earlier alias prototype. |
| `selected_alias_semantics` | Actual admitted definitions and first-match lookup determine the declared singleton meaning under every ambient context tail. |
| `escape_fixture_relation` | The accepted escape document still corresponds to the existing CSS escape relation for every scalar input. |

The relations do not call high-level reader or checker functions. `Field` retains
`Json.getObjVal?` as a shared primitive. Enumeration and ordered-map lookup are
kept distinct: a case with correct cached sizes but misplaced keys passes exact
key enumeration while a named lookup fails.

`selected_alias_semantics` covers actual decoding of canonical
`nodeJson "use" [name]`, universally over admitted definitions and all ambient
tail types/values. It is not a whole-program alias-evaluation theorem or a theorem
over every raw-object layout of a use node. Fold binders retain their accumulator
and scalar bindings. Matching head type alone is not assumed to prevent capture;
the singleton definition check remains essential.

No converse of `DocumentSchema` is claimed for arbitrary alias-using programs.
Normalized erasure discards scope guards needed for that converse. Definitions,
in contrast, have a full admission iff because their bodies are alias-free.
JSON text parsing, duplicate text-key collapse, numeric spelling, source-map
meaning, and CSS prose interpretation remain outside these proofs. Source maps
are only required to be objects and are inert during execution.

## Verification

Fresh source-only replay passed in `verification-2/report.json`:

- 156 exact theorem audits: 108 canonical, seven prior prototype laws, and 41 new
  declarations (21 laws/bridges plus 20 boundary cases).
- 25 actual-file execution rows across five files and four caller profiles:
  escape, arbitrary-name successor, empty definitions, and fold-based alias.
  The fifth file distinguishes executable-looking source-map data from program.
- Eight malformed actual documents refused for the intended diagnostic.
- Four type-correct semantic mutants: missing duplicate-signature guard, ignored
  declared result type, swapped definition name, and executed source-map field.
  Each implementation compiles; an unchanged theorem fails; the baseline witness
  passes and the mutated witness is rejected as exactly false.
- Three preserved-input drift controls reject reader, prototype, and fixture edits.

The CLI imports only `DocumentModel`, reads the real file, calls
`readDocumentWith`, and executes the returned program. Its import closure contains
no generated escape reference. Runtime results are finite observations of the
text parser and executable route, separately from the universal value theorems.

An initial duplicate-guard mutant spelled as `if True` produced an additional
kernel diagnostic, so the strict checker refused to accept it as a clean semantic
control. The final mutant removes the guard structurally and produces only the
expected false-witness diagnostic. `INITIAL-CONTROL.log` retains the initial
observation; no theorem or acceptance criterion was weakened.

## Reproduction and provenance

```sh
python3 -B replay.py --lean /path/to/lean/bin/lean --out /new/report/path
```

The 45 inputs in `SOURCE-ONLY.json` are sufficient; the replay copies only that
roster and builds in a fresh temporary directory. Owned compiled output and
intermediate build directories were removed. The source manifest SHA-256 is
`f1edabfc7536fcd774189f89fd18fd9972b672296465a2a0e976bd2740071029`.

`ORIGINS.json` directly authenticates 21 Lean modules and three data/provenance
files against standalone library commit
`898fb45815c115362093116d81c09715ba94fcab`, and two prior prototype modules against
Firefox artifact commit `713bb6d320ece5371c107794b10180b91a82fef8`.
`PRESERVED.json` is enforced by the checker. `MAPPING.md` records the semantic and
primitive boundaries; inherited `CLAUSES.json` preserves the escape-spec excerpts.
No new normative CSS interpretation or canonical integration is part of this change.
