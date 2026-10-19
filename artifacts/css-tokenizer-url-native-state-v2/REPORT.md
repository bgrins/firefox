# URL native state: corrected ordered trace validation

## Reason for v2

The independent review found a concrete flaw in v1's finite checker: it accepted missing/duplicate/reordered helpers, unknown events and extra fields. The five exact reviewer traces and v1 acceptances are preserved in `validator-history/reviewer`. V1 is unchanged and is not treated as accepted native correspondence evidence.

V2 changes validation, not URL semantics. All 51 Lean modules, 388 theorem reports, native Rust source/instrumentation, binding inventories and 59 inputs are byte-identical to v1. `V1-TRANSFER.json` checks every unchanged predecessor input and lists the limited changed files.

## Correction

`native/check_states.py` independently generates the complete event sequence from each original input: initial name/URL-call eligibility; leading whitespace scan and quote rollback; bulk assignment; borrowed/owned body and allocation handoff; escapes; end/recovery loops; raw slices; seam exit; final token and caller bits. It computes metadata from original source scalar prefixes. It never reads actual event state, payload or counts to generate expectations.

Exact list comparison enforces case order and each observation's presence, order, multiplicity, arguments and state continuity. Unknown tags and wrong field arities fail separately. Hardcoded fixed-corpus totals remain only a drift check; they cannot substitute for this input-derived sequence.

The unchanged corpus generates 503 events: 56 URL calls, 230 helper transitions, 56 slices, 46 bulk observations and 59 final tokens. All three native build modes must match the full reference and each other; the uninstrumented build must preserve final tokens. The unchanged Lean driver separately checks 112 entry/exit observations.

Trace corruptions cover every event deletion, duplication, unknown tag and field-count change, every adjacent swap, whole-class deletion, events moved after publication, entire-seam deletion and annotation Option changes. Historical accepted examples and the reviewer's five exact traces must be rejected. Four native semantic mutants and four Lean semantic mutants remain required.

## Scope and replay

The mathematical helper → loop → leading/capture bridges are unchanged: 17 modules/107 reports added by v1 over the accepted predecessor, 51 modules/388 reports total. This v2 adds no theorem claims. The complete input-only Python control reference is a finite source-correspondence checker, not a verified translator. All arithmetic/headroom/codec/normal-return/allocation/compiler/public-history boundaries remain in `SOURCE-ADMISSION.md`.

No browser defect or production change is proposed. Use `README.md` for fresh source-only replay; independent review and root acceptance are separate gates. Source and replay receipts are separately sealed.
