# Registered-value token boundaries

## Defect and repair

Registered `<length-percentage>` values can serialize as a dimension, percentage,
or function. The old metadata always reported Percentage. Lists also reused the
first component's pair for both endpoints. Substitution trusted these classes,
so it could merge distinct tokens: `font:var(--lp)serif` with 20px became invalid,
`margin:var(--list)auto` with a percentage/length list lost its declaration, and
a separately substituted @ delimiter merged with a following calc function.

The repair serializes the typed value once and scans its actual token classes.
It preserves whitespace, omits comments, accounts for skipped block closers and
uses the final sibling for the last class. Universal values keep their existing
path. The parser is dropped before transferring ownership of the CSS string.
The extra tokenizer pass is linear and may use a nesting stack; no quantitative
page-performance claim is made.

## Evidence

- Original 20-case diagnostic: 14 PASS / 6 FAIL.
- Expanded-v1: the five leading-at cases were invalid because @var was an
  at-keyword. Their failed controls rejected the fixture. Logs are preserved.
- Corrected 37-case baseline: 27 PASS / 10 FAIL. Provider, declaration-admission,
  raw/literal and explicit-separator controls pass.
- Candidate build: success. The initial compile failure and existing build
  monitor traceback are retained, not counted as a passing build.
- Candidate browser run: 308 PASS / 18 harness OK; ten intended improvements
  and 298 unchanged passing comparison cases. No new test skips or metadata.
- Native format and dedicated WPT lint pass. General strict lint reports only
  the configured ESLint exclusion of WPT HTML.
- Independent native/spec/WPT review and root checker replay agree.
- Exact two-file patch applies and reverses on both the branch base and upstream
  976279. Isolated upstream build/browser execution was not performed.

## Formal contribution and limits

The lead came from source inspection while extending verification, followed by
spec analysis and browser reproduction. Lean did not independently discover it.
The proof companion now establishes the scan's boundary-summary invariant and
finite-list composition against endpoints of an independently flattened token
sequence. Root fresh replay passes 22 audits, 24 actual-parser fixtures and four
compiled semantic mutants. Independent formal review is a separate acceptance
gate; see FORMAL-ACCEPTANCE.json when present.

Valid balanced typed serialization, the parser-to-event correspondence, native
representation/compiler and token-separator correctness remain assumptions or
separate work. This is not full CSS serialization verification. Actual font,
margin and CSSOM observations come from the separate spec/browser evidence.

## Packaging

The landable change contains only value.rs and registered-token-boundaries.html.
Evidence and tooling belong in a preceding companion commit. Do not count this
as a committed fix until the signed native commit and ledger entry exist.
