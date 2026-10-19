# URL provider scope

Full task remains open until the following are joined and independently reviewed. Components may be sealed separately; no finite corpus alone closes an obligation.

1. Pin complete current `consume_ident_like`, `consume_unquoted_url` (including internal/end/bad routines), tokenizer dispatch, escape/name/string providers and parser state/UTF-16 metadata helpers. Retain the committed bad-URL repair as baseline.
2. Model leading whitespace lookahead, quote delegation with no native advance, empty URL/EOF/close, and all newline forms. Spec consumes all but one leading whitespace before a quoted Function; retain the intermediate-cursor counterexample and prove combined whitespace/string equivalence instead.
3. Model borrowed→owned unquoted scan, NUL replacement, escapes, invalid characters, whitespace-end acceptance/rejection and actual bad-URL raw source span. Establish exact bounds and semantic payload projection.
4. Independently model CSS Syntax bad-URL remnants with full escapes; prove the native shortcut (only special-casing escaped close/backslash) reaches the same recovery boundary on admitted UTF-8 input. Do not assume this equivalence as a provider oracle.
5. Compose accepted escape/name/string results with explicit native codec/source-unit premises; derive return UTF-8 boundaries and output byte validity, including partial-copy rejoining.
6. Track line/UTF-16 column/source offset effects, including CRLF/CR/FF and quoted delegation. Frame source-map/sourceURL observers; URL contents are not comment tokens. Full cached public histories remain a separate task.
7. Retain independent spec reference, full-source native replay, source-to-model observations, meaningful mutants and bounded direct/refusal/EOF/Unicode controls. No new browser bug is claimed without a concrete consumer and independent oracle.
8. Close source-only checker/inventory, strict standard-axiom audit, relocated replay and tamper check. Explicitly retain compiler/heap/usize/metadata headroom and any failed/unproved premises.

Initial sources: tokenizer SHA5319a01e (includes earlier numeric/bad-URL work), parser SHA2ac2c7f8 (depth-recovery candidate). Their full bytes are retained. String predecessor authenticated before copying; its standard-library/codec/public-history boundaries carry forward.
