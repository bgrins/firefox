# VariableValue constructor origin and range safety

Status: submitted for independent review after source-only replay; see external replay receipts. This capsule binds the leading-whitespace repair only. The later trailing-token and escaped-whitespace repairs are separate.

## Result and scope

The common-coordinate theorem constructs positions from a recursive UTF-8 component syntax and an absolute parser origin. Consuming the initial maximal CSS whitespace token before recording that origin gives the independently constructed relative layout. Legacy late trimming has a concrete out-of-bounds witness. Bounds are derived from characters and component construction; they are not supplied as arbitrary valid-offset premises.

The consumer connection derives outer reference order and disjointness, proves each clean-prefix/reference/final-suffix byte slice, identifies each nested fallback's exact text ending at `reference.end - 1`, proves the fallback scan both locally and in original-source coordinates, and composes successful source reads with replacement output and taint ranges. Nonempty tainted replacements cover their serialized output bytes after any inserted separator. Empty tainted strings retain aggregate provenance. The direct-return shortcut can record an empty interval; this has no claimed URL overlap. General allocation/size failure execution and complete token-class serialization equivalence are outside the universal correspondence.

There are 13 Lean modules and 88 named kernel audit results, including supporting lemmas and witnesses. This count is not a coverage measure. `constructor_consumer_safety`, `constructed_substitution_output`, `constructed_fallback_occurrence`, and `recursive_fallback_scan` state the main connected results. `ReplacementReading` characterizes replacement against actual source decompositions; `scanPieces` uses byte offsets. Both rely on a supplied replacement provider. There is no universal native translation proof.

## Native evidence

The harness compiles the complete retained cssparser crate and exact original/candidate constructor, recursive value scanners, chunk substitution, top-level substitution entry, `VariableValue::push`, and taint range constructors/collector. It extracts 22 complete items per variant plus one explicitly partial external-provider function: the signature and complete fallback tail of `substitute_one_reference`. `SOURCE-BINDING.json` records each extraction anchor and body hash (two records describe the one partial function); replay recomputes and compares the complete records.

The independent restricted-grammar oracle derives stored text, nested reference offsets, replacement text, serialized output ranges and aggregate taint from the input cases. It does not accept native output as expected input. It checks 49 cases in each of six variants: original, candidate, and four compiled semantic mutants. Cases include arbitrary-origin representatives, CRLF, comments, 2/3/4-byte UTF-8, fallback nesting/empty fallback, EOF quote repairs, missing-provider failure, and same-epoch cached first tokens. The generic value parser retains VT/NBSP; rejection by the outer typed-attribute grammar is covered by the separately root-run browser tests, not asserted here.

The candidate agrees on all 49 cases. Original and late-origin mutation have 28 out-of-bounds panics. Other mutation witnesses are concrete observable mismatches: omitting reset loses `var(`, comment-skipping loses retained comments, and character counts use offset 7 instead of byte offset 13. Kernel witnesses describe these modeled failures; these are not claims that four edited Lean implementations failed compilation.

The whole native corpus is bounded. It does not implement namespaces, registered value lookup, DOM attributes, all CSS substitution functions, dynamic cascade scheduling, or the URL policy. The replacement facade supplies `present → known` and `tainted → é中𐐀`, with all missing names using the exact native fallback tail. The actual URL-data and registry providers remain external.

## Exact source and independent browser evidence

Original custom_properties.rs: `18b61124b705887b6a103c015bfedec7bfdea63873248e067701c6097c90e56f`.
Candidate: `e3c5f24c1478ea9b1232748814b971939bf8b4895344b0717fdb3622ee7f3a20`.
The source file now live in the checkout has later repairs and must not replace this snapshot.

`admission/` copies authenticated full caller/provider sources and the separate source audit. Its transfer records the frozen source-audit FILES digest. The crashing raw-attribute path has no leading-whitespace skip before construction, while the ordinary declaration caller does. Fresh and cached-first-token native cases exercise the relevant parser-state distinction under a fixed observation epoch. General cache histories are not proved.

Root independently reproduced the content-process panic in release 158, including a script-free case, and reported the leading repair's 26 new browser assertions passing with 343 prior outcomes unchanged and six additional controls. Those browser receipts remain a separate root-owned gate; this capsule's replay does not launch Firefox. No exploitability claim follows from this proof.

## Admissions and limitations

Read `SOURCE-ADMISSIONS.md`. Most significantly, actual tokenization must correspond to the finite component tree, parser entry has no pending unconsumed block, and completed EOF repair must supply the appropriate delimiters and endpoint relation. `Repair.lean` proves prefix normalization commutes with the admitted append/delete operation, not complete quoted-token recovery. The predecessor endpoint capsule was authenticated for extraction infrastructure; its finite evidence is not silently promoted to the needed universal tokenizer contract.

The component's clean text is arbitrary UTF-8; comment retention and exact CSS whitespace normalization are modeled. Reference syntax, fallback header parsing/skipping, final trailing trim compatibility, token metadata decisions, limits, allocation and Rust/machine execution remain explicit bridges. This is a constructor/range-safety component, not a complete CSS grammar, URL security theorem, or proof that the unmodified trailing trim preserves token semantics.

## Replay

Externally authenticate FREEZE.json, MANIFEST.json and check.py using the handed-off hashes. Copy exactly the manifest files plus the two seals to an otherwise empty directory. Run:

```
python3 -I -S /absolute/capsule/check.py --output /absolute/new/external-output
```

The checker authenticates before importing local executable helpers, rejects unexpected files/directories, nonregular entries, duplicate JSON keys and internal output, kernel-checks the modules and axiom roster, rebuilds native variants from source, executes the independent row oracle, checks source extraction records, and reauthenticates after execution. Rust/Lean tools are externally installed and hash-bound; compiler, standard library and operating-system execution remain trusted. Generated binaries are outside the capsule.
