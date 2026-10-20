# Attribute range producer audit

## Result

Found a release-reachable content-process crash in the raw typed-attribute constructor. `data-x=" var(--v)"` records reference positions before trimming the stored leading space. The resulting `[1,9)` reference is applied to eight bytes `var(--v)`. Root reproduced on the shared build and installed Firefox158, including the script-free minimal fixture. Retained release minidump metadata identifies the exact bounds panic. This is not evidence of memory corruption or unknown-data exfiltration.

Root owns runtime and repair. The exact candidate source review approves normalizing the constructor origin before recording references, with comment-preserving lookahead/reset. Parent reports26newPASS and343prior outcomes unchanged in its375-subtest matrix; the matrix remains root-owned and is not copied here as independently reviewed evidence. The retained root baseline/release receipts establish the original failure.

## Deliverables

- HYPOTHESIS.md: independent expected result and full failing path.
- CALLERS.md: constructor entry inventory and repair choices.
- SOURCE-MAP.md: substitution/serialization ranges to URL/string consumers, bounded negative findings.
- CANDIDATE-REVIEW.md: exact source review, cache/observer and pending-parser admission.
- attr-substitution-leading-whitespace.html:26-case proposed WPT, UTF-8/comment/whitespace/fallback controls; SHA858cd1e7077775790cfb40315816d5c0a450a373ca7e03d52b4abadf3a9bbdc4.
- FORMAL-SCOPE-PROPOSAL.md: parent-approved follow-on constructor/range proof; implementation belongs in css-variable-origin-proof-v1.
- TRAILING-ORACLE.md and trailing-metadata-probe.html: separate seven-case source hypothesis about end trimming retaining WhiteSpace token metadata. No runtime result or repair claim here.

## Limits

Source-based discovery plus root browser evidence, not theorem-based bug discovery. No native changes, builds, Git operations or browser processes were performed by this audit. Complete inspected source snapshots are retained; source-to-model translation and uninspected provider histories remain open. The earlier attr fallback and link-parameter seams are explicitly not counted as bugs.

The provenance security objective is spec-defined tainted URL rejection and metadata-preserving transformations. It is not global network noninterference: permitted CSS features can intentionally select clean URLs based on numeric layout/style data.
