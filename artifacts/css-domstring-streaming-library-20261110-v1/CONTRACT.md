# Chunked DOMString interpretation and CSS preprocessing

`Streaming.pipeline Streaming.utf16 Streaming.css` consumes arbitrary finite
lists of finite chunks of already-acquired `DomString.CodeUnit` values. It
preserves the high-surrogate carry and CR carry across chunk boundaries,
including empty chunks. At EOF it feeds the flushed UTF-16 carry through CSS
preprocessing before flushing the CR carry. An empty chunk does not signal EOF;
the complete adapter invokes EOF flushing once.

The generic adjacent-pair machine requires `Machine.unheld`: an input emitted
immediately cannot combine with a later input. Continuation laws lift this
obligation over input items, feeds and arbitrary partitions. UTF-16 and CSS
specializations connect to the independently stated `DomString.Decoded` and
`CodePointInput.Preprocess` relations. Pipeline factorization establishes
`domstring_prepared_iff`, normalized output, nonexpansion and reachable carry
domains. These universal results do not follow from the example vectors.

The seven `CssStreaming*` modules register 27 laws and the kernel-checked
`StreamingExamples.checks_pass` theorem for 32 executable observations. Examples
include split/minimum/maximum pairs, empty chunks, unmatched/reversed/overlapping
surrogates, split CRLF, both carries, EOF and rejected numeric input. Checking
the intermediate decoded points matters: early surrogate replacement is wrong
there even when final CSS filtering conceals it.

## Source contract

The source contract and immutable revisions are the existing
[DOMString input mapping](domstring-input.md) and `coverage.json` entries:
WebIDL DOMString and Infra strings supply already-acquired code units;
ECMAScript String Type, CodePointAt and StringToCodePoints define whole-input
interpretation; CSS Syntax input preprocessing defines filtering. CSSOMString
choice qualifies callers. This carry strategy is an implementation choice
proved equivalent to those reviewed whole-input relations. It is not required
by the specification and is not mechanically derived from prose. The integration
adds an algorithmic refinement of existing coverage, not another CSS feature.

The proof originated in Firefox artifact commit `d34a26d38d78`,
`artifacts/css-domstring-streaming-20261110-v1`. Its root replay authenticated nine
normative excerpts against pinned complete snapshots and four reference modules
against library revision `0127c4f42c620cdaba4f9b92cca93ca95df2d913`. The standalone
integration changes import paths and namespaces, prefixes example labels and
adds the aggregate example theorem. The external artifact retains six rejected
semantic mutants and three source/library drift controls; those historical
receipts are not rerun by this library's standard checker.

## Domain and exclusions

Input is `List (List (Fin 0x10000))`. `Streaming.admittedChunks` checks every
natural-number input before running the typed adapter. Values above 0xFFFF are
rejected rather than wrapped; direct `Fin` numerals can wrap. A supplementary
code-point number is not one code unit. Numeric admission does not enforce
ECMAScript's string-length limit; the mathematical domain is a superset of
finite JavaScript strings. These wrappers are whole-input admission helpers,
not incremental validation APIs.

Successful CSSOM coercion and DOMString type choice are caller premises. No
CSSOM guards, exceptions, side effects, DOM acquisition, byte decoder,
endianness, encoding/BOM policy, UTF-16 re-encoding, Unicode normalization,
arbitrary-index CodePointAt wrapper or IsUnpairedSurrogate return field is
proved. No tokenizer, Firefox adapter, native memory safety or general browser
behavior is proved. Finite-list semantics establish no infinite-stream
productivity, allocation, stack or performance bound.

## Validation scope

The standard checker registers these modules, axioms and ordered observations.
Integration validation builds the clean affected dependency closure, audits
its exact named theorem set, runs the new examples and existing input-layer
controls, and runs global `check.py --coverage-only`. That coverage-only command
checks static registration and does not run Lean. Neither check refreshes the
historical full-library or browser gate.
