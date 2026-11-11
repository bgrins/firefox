# Frozen CSS grammar transfer benchmark

Eight properties from four CSS modules were selected before their current source grammars were acquired or inspected. The original extractor was then run unchanged, preserving every refusal. A separate, reviewed source-span selector passes selected Value fields and one production to the byte-identical original Parser. No grammar-language operator was added.

The baseline extractor refuses all eight at source-selection or metadata boundaries. After selector adaptation, the unchanged grammar parser admits four inputs. These are observations of this small selected corpus, not a percentage of CSS coverage or whole-property conformance. The selector was written after inspecting the sources; its results are not an unseen general-extraction accuracy measurement.

| Property | Module | Original extractor | Reviewed selector + unchanged Parser |
| --- | --- | --- | --- |
| text-align | CSS Text 3 | Missing property: shorthand class not selected | Admits eight keyword alternatives |
| text-transform | CSS Text 3 | No reviewed anchor | Refuses unsupported `||` |
| resize | CSS UI 4 | Property metadata continuation refused | Admits six keyword alternatives; independently checked below |
| outline-style | CSS UI 4 | Property metadata continuation refused | Refuses prose-defined reference |
| display | CSS Display 3 | No reviewed anchor | Refuses unsupported `||` |
| visibility | CSS Display 3 | No reviewed anchor | Admits three keyword alternatives |
| box-sizing | CSS Sizing 3 | No reviewed anchor | Admits two keyword alternatives |
| width | CSS Sizing 3 | Grouped/unquoted property definition not selected | Resolves box-size, then refuses its typed/ranged primitive |

`PROTOCOL.json` and its original hash record the selection and pre-acquisition resize oracle. `ORIGINAL-RESULTS.json` retains the eight literal baseline outcomes. `CONTEXTS.json` records the reviewed property blocks, heading anchors, Value spans and one structured production. `observed/` contains data programs, instruction/source maps and outcomes; these generated files are not needed for reproduction.

## Reproduce

```
python3 -I benchmark.py --out /new/generated-output
python3 -I check.py --lean /absolute/path/to/lean --out /new/check-output
python3 -I replay.py --lean /absolute/path/to/lean --out /new/source-only-output
```

Use the hash-pinned Lean 4.35.0-rc4 binary. The replay copies only SOURCE-ONLY.json inputs into a fresh directory, runs the checker and removes temporary sources/compiled objects. No earlier artifact, network, browser, native build or canonical library is needed. Preserved inputs are source-only and hash-authenticated.

## What transferred

The original extraction code itself is preserved byte-for-byte. Baseline replay calls its original `extract` function on every selected full source document, without extending its anchor registry or metadata handling. The adapted route uses that exact module’s `Parser` and data quotation function. Its semantic grammar still consists only of lowercase keyword terminals, named references, grouping, ordered juxtaposition, alternatives and optionality.

The source selector adaptation is deliberately distinct. Reviewed byte spans handle quoted/unquoted propdef containers, a shorthand class, grouped property names and metadata continuation lines without interpreting those fields. Every span is bound to an exact source digest and checked against its retained text. This is a sidecar of reviewed contexts, not a complete Bikeshed preprocessor or automatic normative/informative classifier. It does not infer missing primitive semantics or translate prose exceptions.

The outline-style refusal is substantive: its outline-line-style is defined in prose by referring to another module’s line-style while excluding `hidden`. Blindly importing that referenced grammar would lose the exception. The width refusal reaches a structured box-size production but cannot interpret a length-percentage primitive and its nonnegative range. The experiment keeps both boundaries unresolved.

Only resize gets a new independent formal fixture/reference. Its six-keyword oracle (`none`, `both`, `horizontal`, `vertical`, `block`, `inline`) was recorded in PROTOCOL before acquisition and was not changed after seeing the source. Lean checks the quoted JSON data decoding, exact finite language, and acceptance equivalence for every finite list of normalized keyword tokens, reusing the already proved generic matching and postfix laws. The actual-file runner imports only the data decoder/interpreter and reads the generated JSON; it does not substitute the reference fixture.

Kernel checking is over the quoted Json value and formal token grammar. Python source selection, notation parsing/quotation, raw JSON text parsing and semantic correspondence with the specification remain reviewed boundaries. The other three admitted property grammars have source-linked generated data only; no new property-specific theorem or browser result is claimed for them.

## Context and implicit extensions

Inputs are already decoded, ASCII-case-folded keyword token spellings. A rejected `INLINE` or CSS escape in this token API is not a claim that the equivalent raw CSS declaration is invalid. CSS-wide keyword admission, variable substitution, comments/whitespace tokenization and invalid-at-computed-value behavior are outside the enumerated property grammars.

Property context remains outside this experiment: text-align shorthand assignment, inherited/writing-mode behavior; text-transform’s text processing; resize’s scroll-container/replaced-element applicability and interaction/axis behavior; outline painting and the referenced prose exception; display’s box construction; visibility’s painting/hit-testing/table-collapse behavior; box-sizing’s sizing calculations; and width’s numeric, intrinsic and percentage semantics. Ignored metadata or a supported Value field never establishes the whole property.

## Source versions

SOURCES.json records the latest file-specific source commits returned by CSSWG’s primary repository API at acquisition time (2026-11-10 Pacific / 2026-11-11 UTC), with immutable raw-source URLs and SHA-256 hashes. “Current” refers to that observation, not a claim that the sources never change. The selected anchors and exact source contexts are in CONTEXTS.json.

No Firefox, Stylo, canonical Lean library, Git/index, application or previous artifact was changed. The practical next step is to review the source-context sidecar format and keep extraction failures separate from grammar failures. Extending unordered combinations or prose-exception semantics needs its own reviewed formal contracts; this benchmark does not add them.

| Module | Source revision | Last file change (UTC) |
| --- | --- | --- |
| css-text-3 | [e2a76bde01e7](https://raw.githubusercontent.com/w3c/csswg-drafts/e2a76bde01e77f714a8f22e9866d8c636b482a6f/css-text-3/Overview.bs) | 2026-08-14T15:44:50Z |
| css-ui-4 | [247bc6b2f2fb](https://raw.githubusercontent.com/w3c/csswg-drafts/247bc6b2f2fb8098aa27654316e2a2e968ee74bb/css-ui-4/Overview.bs) | 2026-10-15T17:21:27Z |
| css-display-3 | [3019d346a431](https://raw.githubusercontent.com/w3c/csswg-drafts/3019d346a43137ea579beaee8b30a4966032f68a/css-display-3/Overview.bs) | 2026-06-05T06:11:42Z |
| css-sizing-3 | [32ab981cb029](https://raw.githubusercontent.com/w3c/csswg-drafts/32ab981cb0297e83a866558eb658ee7ec6d9052f/css-sizing-3/Overview.bs) | 2026-10-08T19:04:45Z |
