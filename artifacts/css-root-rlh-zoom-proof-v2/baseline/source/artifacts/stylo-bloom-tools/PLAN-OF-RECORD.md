# CSS and Stylo verification plan

Updated 18 October 2026. Work stays local; the user owns pushing.

## Accepted checkpoints

- Original Bloom milestones 1–6 are complete within their declared selector,
  provider and native interpretation boundaries. The original source gate remains
  immutable. Historical replay and a separate review of the current cache delta
  are recorded in `CONTINUATION-20261017.md`.
- Sixteen independent Firefox bugfix commits are listed in `BUGFIX-COMMITS.md`.
  The latest is `11482ee213bf63c749b6d205c2c7591d783bdaa8`.
- Twenty-four further repairs have completed their native/WPT and scoped formal
  reviews and await configured signing. The latest is the text-overflow line-state
  repair; its six-file fix and preceding source package are recorded in
  `css-text-overflow-line-state-fix-v1/verification-final-v1.json`.
- Standalone CSS model `251269ad1a3b769828efc3321c41464bec50a18a`:
  ordinary imports composed with explicit scopes, extending stylesheet acquisition,
  scope resolution, cascade and computed visibility.
  Main, fresh and committed source archive checks agree; finite native comparison
  passed 20/20 with 240 metadata readbacks and 15 controls. This does not prove
  complete CSS conformance or a general refinement of Gecko.

## In progress

1. **Broader spec/implementation audits.** Both reports are complete:
   `artifacts/css-breadth-audit-values-v1/REPORT.md` and
   `artifacts/css-breadth-audit-queries-animation-v1/REPORT.md`.
   Signed-zero Round fix `708b914901ee` has 64 passing regression cases and
   seven independently replayed bounded Lean laws, with exact source drift
   checks but no full native refinement. A follow-up literal-negative-zero
   probe exposes a conflict between current prose and existing upstream WPT;
   CSSWG issue9750 later supports literal negative zero. Preserve parsing and
   existing WPT; record the prose conflict without calling it another Gecko bug.
   Container-name invalidation is committed as `238710ff9db7`: 12 baseline
   failures become 12 passes; all 26 selected subtests pass.
   Animation now has 12 failures in 52 tests: finite identity, true-infinity
   direction, terminal parity and iteration events. Fix `0a81e1f36ab0` separates API/event indices from saturated accumulation
   counts. All 52 new tests pass; 246 selected subtests pass with five existing
   expected failures; build and native lint pass. The separate bounded Lean v2 contract passed independent replay (six audits,
   four compiled mutations, fourteen record corruptions and ten source controls).
   Double representability, timing arithmetic and event semantics remain outside
   its claim.
   These targeted audits do not survey all CSS.

   Completed scope-dependent nth sharing fix: `f4b34bf7fef1`, production guard
   plus 20-case WPT. Baseline ten failures become zero; 103 selected subtests,
   two reftests and 78 static comparisons pass. All 960 mutation comparisons also
   agree, but 30 fresh-reference vectors changed as the baseline fresh render
   shared the bug. Explicit WPT/ordinal oracles are the correctness evidence.
   The small Lean finite-mask contract passes five audits, three mutations and
   thirteen gate corruptions, independently replayed. Safe-entry fidelity remains
   an explicit assumption; no native visitor refinement is claimed.

   Completed filtered-nth relative invalidation fix: `b1b1bacb9406`, production
   fix plus ten-case WPT only. All 70 selected subtests, two reftests and 130
   independent mutation comparisons pass. Prior failed candidates are retained.

   Previous completed slice: **scope-limit invalidation proof**. The production fix and WPT are committed
   as `64ac54569f1cc202172ded92ee23ba749cd3284e`. Baseline 32/40 failures become
   40/40 passes; 131 selected WPT subtests pass. All 1,020 original mutation
   comparisons and 138 independent comparisons agree. The small handwritten
   dependency projection proof passes five audits and three negative controls;
   independent proof/gate review is accepted (11 additional gate corruptions
   rejected). This completed slice remains a bounded graph contract.
2. **Ordinary imports composed with explicit scopes.** Extend actual resource
   acquisition through raw scope parsing, instance identity, layer registration,
   scope assignments and source-to-computed provenance. Check repeated imports,
   conditions, proximity and rollback against finite HTTP browser fixtures.
   Keep imported omitted roots and `@import scope(...)` explicitly unavailable.
   Main model gate and final browser comparison passed: 11,564 audits, 12,172
   cases, 2,099 source fingerprints; 20/20 native comparisons, 240 metadata
   readbacks and 15 controls. Independent fresh rebuild also passed; standalone commit
   `251269ad1a3b769828efc3321c41464bec50a18a` contains the reviewed extension.
   Original archive session68227 lost its terminal record. Documented continuation
   54955 passed after source reauthentication; the committed archive and capsule
   are accepted, with details below.

## Next, in priority order

1. Validate ranked breadth-audit leads with spec-derived observable oracles;
   fix confirmed bugs individually with WPT before expanding the model.
2. Extend the invalidation model around the concrete bug, proving the relevant
   dependency projection preserves the enclosing rule subject. Clearly separate
   a handwritten graph contract from extracted native implementation claims.
3. Use import/scope counterexamples and unsupported-domain reports to choose the
   next semantic extension. Prefer observable browser discrepancies and connected
   source-to-computed proofs over adding isolated wrapper laws.

## Working rules

- Each bugfix commit contains its necessary production change and WPT/metadata.
  Tooling, proofs and research records remain separate.
- Record full commit hashes, pre/post test results and material limits in the
  bugfix index. Commit accepted standalone model checkpoints separately.
- Preserve failed runs and distinguish unsupported syntax, setup errors and
  actual semantic discrepancies. A fresh-DOM comparison alone is not a spec proof.
- Retain explicit unavailable results for unmodeled semantics. Historical proof
  replay does not certify changed native code.
- No pushes, Try jobs or external submissions.

## Next breadth target

Registered numeric property computation has a reproduced non-cyclic context
discrepancy: under parent30px/child10px, a registered number containing 1em
computes30 and produces width30px, while its absolute10px control computes10.
Both registration inheritance modes reproduce. This overlaps known tentative
WPT failures and is not counted as a newly discovered bug. Source/WPT and primary
spec/history agents are defining a focused fix boundary. Evidence:
`artifacts/css-custom-property-next-probe-v1/baseline-v1.json`. Dormant fallback
em/lh dependencies also differ from direct values, but their normative oracle
is unresolved; keep those observations separate.

### Registered numeric candidate

The exact sign-based WPT covers76cases over number/integer/percentage/angle/time/
resolution:24directem/lh cases fail,52absolute/substitution/length controls pass.
One-file candidate adds length-operand capability for the six numeric result
types. Build89036 passed; patched run25443 exited1: all76new cases pass, with
48changed existing tentative outcomes (18expected failures now pass and
30parent-font-context assertions now fail). Exact transitions are retained in
artifacts/css-registered-numeric-fix-v1/existing-outcome-changes.json.
No existing test expectations or metadata have been changed. Baseline existing tests37524 exited0 with69PASS/55expectedFAIL.
Some tentative registered font-consumer tests use an unsettled parent-context
oracle; any changed result must be individually recorded and reviewed before
commit, not silently treated as a regression fix. Structural dependency proof
work uses explicit lexical-flag and scheduler assumptions, excluding cycles.


## Second static breadth audit — 2026-10-18

Three agents completed color, logical/shorthand and relative-unit audits.
Synthesis: `artifacts/css-breadth-audit-round2-v1/REPORT.md`.
Root independently reproduced shorthand cache provenance and two color issue
families; literal/same-space/numeric controls pass. These are pending individual
fixes, not newly proved native correctness or committed patches. Next execution
order: shorthand provenance, missing color masks, then zero-prefix color folds.
Each needs focused WPT plus a standalone native fix, with proof/tooling separate.
Root metric orientation stays static-only: the shipped font probe passed; the
initial40px inference was incorrect and was withdrawn.

The current numeric candidate remains uncommitted pending disputed tentative
font-consumer expectation review. Its bounded dependency proof passed independent
root replay77357 and96-pin reauthentication; lexical flag accuracy and scheduler
readiness remain assumptions. Accepted proof record:
`artifacts/css-registered-numeric-proof-v1/ROOT-REVIEW-v1.json`.

The original model archive process68227 lost its handle and ended without a
terminal record or report. No success is inferred. A documented continuation54955
uses the same independently extracted archive and its own retained build outputs,
after reauthenticating all2099sources; reviewer retains ownership through terminal.


### Import/scope archive accepted

Documented continuation54955 completedexit 0. Commit
251269ad1a3b769828efc3321c41464bec50a18a is now the accepted source-archive
checkpoint:11564audits,12172cases,2099source hashes, all seven vectors exact.
Root reauthenticated capsule file identities; reviewer retained full terminal,
source, archive and native bindings. Original68227exit remains unknown and is
not counted as success. Capsule .lake/import-scope/capsule-v1.json and root
CSS-IMPORT-SCOPE-ROOT-ACCEPTANCE-v1.json preserve the precise claim.


### Shorthand cache provenance completed

Fix `11482ee213bf63c749b6d205c2c7591d783bdaa8` contains four native files and28-case WPT only.
Proof/tooling companion `f32fc6f2831ebe0987c9f0e9003b4597e3bce019` precedes it. Baseline20failures
become28passes;74selected subtests and2reftests pass,4existing expected
failures unchanged. Build/format pass; lint0errors with ignoredHTMLwarning.
Both original branch base and immediate pre-companion base accept the isolated
patch. Eight bounded Lean audits passed independent replay, with3compiled
mutations,14validator corruptions and7source guards. Fixed environment, stable
identity and supplied cascade eligibility remain explicit premises.

Next: missing color components through conversion, then zero-weight mixing
prefixes, each with independent WPT and source/proof review. Numeric-property
candidate remains separate and uncommitted pending tentative-cycle oracle work.

### RGB missing-component fix verified; commits pending

The one-line RGB/XYZ missing-mask repair passes all132new WPT cases;81failed
before the fix. Exactly42existing expected failures now pass. Final selected
gate45659 exited0 with1374passes,412unchanged expected failures and4OK harnesses.
The separately reviewed bounded mask proof passed independent replay. This is
an independent static rediscovery of a known expected-WPT-failure family, not a
defect discovered by Lean. Evidence: `artifacts/css-color-missing-fix-v1/verification.json`.
The proof companion alone is staged. Two configured 1Password signing attempts
failed; no commit was created and no signing configuration was changed.

### Zero-prefix color fold prepared

Baseline55074 exited1:12failures and4passing controls in16new WPT cases;
existing color-mix tests retain906passes and67expected failures. The native loop
is unchanged. A prepared rational stack/fold model passes17audits and4semantic
mutation controls, with9malformed-record checks. Native source binding and root
proof acceptance remain pending. Its claims exclude floating-point behavior and
full color interpolation. See `artifacts/css-color-zero-prefix-proof-v1/README.md`.

### Third breadth audit completed

At the user's request, three agents compared current specs with implementation
and tests for CSS math, transforms, and discrete Grid placement. Root reviewed
the reports; synthesis: `artifacts/css-breadth-audit-round3-v1/REPORT.md`.
First runtime targets are deferred percentage-transform composition and math
exceptional-value preservation. Longer proof targets are recursive partial
evaluation, numeric-type representation, and discrete Grid line lookup/placement.
The subsequent root probes reproduced deferred transform composition and three
math families. Evidence: `artifacts/css-breadth-probes-round3-v1/RESULTS-v1.json`.
Known pow failures and ambiguous boundary-only subgrid overlap remain separate.

### Deferred transform conversion repaired and tested

The generic matrix converter now rejects its two deferred operation variants,
allowing existing callers to retain them for context-aware evaluation. New WPT
baseline99584 has9failures/4passes; patched86643 exits0 with all13new and193existing
subtests passing,5OK harnesses. Distance/SMIL baseline41791 and patched7951 each
pass676checks with10expectedTODOs and no unexpected results. Build44203 exits0.
Lint57081 reports0errors/1ignoredHTMLwarning; format92422 passes, with unrelated
frozen proof-source formatting restored. The native/WPT-only patch applies to
both immediate and original bases. Final independent source/browser review is
accepted. Root proof replay39351 exits0 with22audits,8compiled mutations and8source
integrity controls;80capsule pins reauthenticated. The successful-conversion
theorem covers arbitrary finite trees/lists under explicit primitive/matrix
operator premises; IEEE, singular fallback and compositor correctness are
excluded. Evidence: `artifacts/css-transform-deferred-fix-v1/verification.json`.

Next math order is infinite-divisor mod/rem, NaN-preserving clamp rewrites, then
nested progress. Independent spec/history review accepts their simple oracles.
A separate clamp probe97437 exits 1: the deferred-NaN upper argument is discarded
and yields75px instead of0px, while direct-NaN and finite controls pass. Preserve
unresolved potentially-NaN operands in the eventual simplification proof.

### Infinite-divisor mod/rem repaired and tested

The helper preserves finite dividends for valid infinite divisors, after mod's
opposite-sign exception. Baseline23961 has12failures/36passes in48new cases;
patched79350 exits0 with48new and267existing passes,3OK harnesses. All12changed
cases are independently reviewed;303other subtests retain their passing results.
Build18130 and format79224 exit 0. Lint10350 has0errors/4warnings:3existing unrelated
Rust formatting warnings and1ignoredWPT warning. Native/WPT-only patch applies
to both immediate and original bases. Root proof54388 exits0 with12audits,
4compiled mutations and13record guards;10source controls independently pass,
120candidate-capsule files reauthenticated. Finite arithmetic and formula
exception behavior remain explicit premises. Verification:
`artifacts/css-mod-rem-infinity-fix-v1/verification.json`.

RGB, transform and mod/rem patches are verified but uncommitted. The configured
1Password signer failed twice. A read-only check of the existing SSH agent found
no public identities, so the standard signer cannot currently provide an
alternative. Signing remains enabled and no Git configuration was changed.
The pending unlock/unsigned-commit choice remains with the user; research is
not otherwise blocked. Only the RGB proof companion is staged.

### Zero-prefix color repair verified

The normalized fold now evaluates zero-weight prefixes at half progress. Raw
interpolation behavior is preserved. Fresh baseline70624 has12failures/4passes;
patched27617 exits0 with16new passes,1118existing passes and67unchanged expected
failures. Root compared all1201subtest identities: exactly12failures become
passes,1189outcomes unchanged. Build93291 and format38724 pass; lint3838 reports
0errors/1ignoredHTMLwarning. Native/WPT-only patch applies to both bases.
Root proof replay23393 exits0:17audits,4semantic mutations,9record guards,
15source controls;69capsule pins reauthenticated. Rational compatible
interpolation remains a premise; IEEE, full premultiplication and all-zero-total
conformance are excluded. Verification: `artifacts/css-color-zero-prefix-fix-v1/verification.json`.
Commits remain pending the existing signing blocker.

### Fourth breadth audit dispatched

The user requested broader static spec/implementation analysis. Custom-property
dependency/substitution, logical-property mapping, and counters/generated-content
audits are running. Scope and deliverables: `artifacts/css-breadth-audit-round4-v1/PLAN.md`.
These are research leads, not new confirmed bugs.

### Fourth breadth audit completed and probed

Root reviewed all three reports. Browser session94365 reproduced numeric attr
parsing, attr fallback-cycle, and equal-size animation shorthand discrepancies:
35of61cases disagree, all202parse/support checks pass,12inputs unchanged.
Independent attr normative review is in progress. Counter sentinel/grouping
leads remain static. Prioritized synthesis: `artifacts/css-breadth-audit-round4-v1/REPORT.md`.

Clamp candidatev1 fixes literalNaNs but exposed separate early length conversion
censoring. Clamp-free probe8468 reproduces10px/.5 instead of0px/0; two finite
controls pass. Preserve this as its own fix, not a hidden prerequisite for clamp.
The final clamp WPT instead generates deferredNaN using finite-leaf sqrt and
adds five relative-infinity serialization controls. Fresh pre-clamp rebuild11098
passes; final94case baseline78919 has49FAIL45PASS. Candidatev2 preserves safe
nonfinite unit folds; final build/browser/proof review remains pending.

Attr numeric and fallback-cycle conformance findings are independently accepted;
root separately accepted equal-size animation precedence. Numeric attr is next:
45caseWPT baseline76319 has16FAIL29PASS;247existing subtests pass,4OK harnesses,
9inputs unchanged. Independent model/lexical source bridge work is underway.

Configured signing retry72303 exited128 with the same 1Password buffer error.
HEAD remains11482ee213bf63c749b6d205c2c7591d783bdaa8; only the RGB proof companion
is staged. No signing setting changed and no commit was created.

### Clamp simplification repaired and accepted

Final94case WPT baseline78919 has49FAIL45PASS; patched8023 exits0 with94new
and406existing passes,2unchanged expected failures and16OK harnesses.
Independent terminal review matched all502subtest identities: exactly49
improvements, all other outcomes and metadata unchanged. Native/WPT-only patch
applies to original32226andimmediate11482bases. Final build58284 and format40971
pass; lint3860 reports0errors/4warnings (3unrelated pre-existing Rust formatting
items retained,1ignoredHTML).

Root full candidate proof replay44342 exits0:47audits,15compiled mutations,
24record guards,13source controls,35capsule pins reauthenticated. Arbitrary-tree
preservation includes relative folds and all mixed-unit winner branches. Native
type/conversion/comparison certificates remain manually reviewed premises;
canonical and common-unit rational instances discharge their obligations.
IEEE arithmetic and the distinct early length-conversion defect are excluded.
Evidence: `artifacts/css-clamp-nan-fix-v1/verification.json`.

The pending verified native fixes are RGB missing masks, deferred transforms,
infinite-divisor mod/rem, zero-prefix color mixing, and clamp. Each has an
isolated native/WPT patch and separate replayable proof companion. All await
the existing signing blocker; no unsigned commits or pushes were made.

Next: complete numeric attr parsing/construction with its45case regression
test and independent lexical model, then equal-size animation shorthand
precedence, active attr fallback cycles, exceptional calc leaf conversion,
and remaining progress NaN work. Counter sentinel/grouping probes remain
queued as the next deliberate expansion into layout.

### Numeric attr repair accepted; fifth breadth audit underway

Numeric attr parsing now copies the exact numeric lexeme, validates exhaustion,
and appends the unit. The expanded 53-case WPT moves from 22 failures to all
passes. Patched session 15296 exited 0 with 300 passes and four OK harnesses;
all 247 existing cases remain passing and all nine inputs stayed unchanged.
Build 69078 passed after correcting the first candidate's Rust string type.
The isolated native/WPT patch applies to both original and immediate bases.
Evidence: `artifacts/css-attr-numeric-fix-v1/verification.json`.

Root proof replay 26277 exited 0: 14 audits, five Lean mutation controls,
13 diagnostic guards, 2,450 Rust bridge cases over all 49 units, four Rust
mutations, and three unit-inventory controls. Independent review also passed.
The token-list theorem is universal within its model; tokenization, cursor
semantics, numeric conversion and native recursive fallback remain explicit
boundaries. V1's hidden string-type mismatch and omitted seconds unit are
retained in the corrected V2 documentation. Commits await the existing signer
blocker; the staged RGB companion remains separate.

At the user's request, three new agents are surveying Grid, Flexbox and CSS
Text, extending beyond prior Stylo-focused work. Scope and report locations:
`artifacts/css-breadth-audit-round5-v1/PLAN.md`. Static leads require normative
review and browser confirmation before entering the confirmed-bug index.
The animation shorthand WPT baseline is running while these audits proceed.

Animation shorthand baseline 13267 exited 1 with exactly 12 new failures and
seven passing controls. Existing selected tests retain 23 passes and two
expected failures; all inputs stayed unchanged. Native repair remains next.
Evidence: `artifacts/css-logical-shorthand-tests-v1/BASELINE-v1.json`.

### Fifth breadth audit completed

Grid, Flexbox and CSS Text reports are complete and root-reviewed:
`artifacts/css-breadth-audit-round5-v1/REPORT.md`. The next cheap probes are
subgrid abspos endpoint invalidation, Greek/Lithuanian casing context, and
whitespace partition invariance. Flexbox finite-weight overflow follows after
reviewing supported numeric limits. None is a newly confirmed bug yet.

The strongest larger model extension is the finite Flexbox allocation/freeze
loop, followed by Grid repetition/compaction and reusable text-context scanners.
Each begins with independently specified behavior and explicit native bridge
obligations. These areas expand into Gecko layout beyond Stylo. Existing
Turkic WPT failures and prior Grid hypotheses remain separately identified.

### Fifth breadth browser probes and shorthand repair

Round-five probes completed: corrected run 91043 exited 1 for 20 semantic
mismatches across 18 of 110 cases; all 92 parser/support checks passed and nine
inputs stayed unchanged. Root recounted the 384 comparisons. Grid has four
failed cases; casing has three sigma and four Lithuanian discrepancies plus
one known Turkish failure; whitespace has six partition-dependent width
differences. V1 coordinate-rounding artifacts were corrected by measuring at
the same origin, with both runs preserved. Independent normative review is
underway; these are not yet additional accepted bugfix entries. Evidence:
`artifacts/css-breadth-probes-round5-v1/ROOT-RECOUNT-v1.json`.

The animation shorthand native patch adds physical-before-logical ordering
after component count and before IDL order. Build 90716 passed; patched WPT
97577 exited 0: all 19 new cases pass, existing 23 passes and two expected
failures unchanged. Exactly 12 failures improved. The isolated patch applies
to both bases. Generated shorthand classification was independently reviewed;
source-bound winner-model proof and terminal review are in progress.

Signed commit retry 62291 exited 128 with the same 1Password buffer failure.
No commit was created, signing remains enabled, and only the RGB proof
companion remains staged.

### Animation shorthand precedence accepted

Root proof replay 32298 and independent replay 20000 both exited 0: 14 Lean
audits, six Lean and five Rust semantic mutations, nine diagnostic guards,
nine source guards and four inventory guards. The exact extracted comparator
agrees on 277,729 ordered pairs of generated/mock property adapters. Root
reauthenticated 20 companion files and 27 replay inputs. The finite-list
winner theorem assumes a sorted permutation and correct expansion; value
agreement requires unique winner values. Runtime property filtering, aliases,
custom-property prepass and native sort correctness remain explicit boundaries.
Native/WPT and proof are accepted; commits await the existing signer failure.
Evidence: `artifacts/css-logical-shorthand-fix-v1/verification.json`.

Next Grid baseline 6308 exited 1: four out-of-range subgrid abspos failures,
34 new controls pass, existing abs-pos-001 passes and abs-pos-002 retains its
expected failure. Independent review accepts all 38 new WPT oracles. Full
helper-bound analysis is underway before a native repair; span and named-line
paths must be covered rather than skipping only the final clamping step.
Evidence: `artifacts/css-grid-abspos-tests-v1/BASELINE-v1.json`.

Independent normative review accepts four round-five families: Grid abspos
endpoints, sigma innerText, Lithuanian innerText, and whitespace partition
geometry. Root authenticated 55 evidence pins. Excluding known Turkish
calibration, 17 cases / 19 comparisons expose accepted discrepancies. All
18 casing expected strings were independently reconstructed from Unicode 17
data. Casing pixel evidence remains a separate gate. Recommended repair order
is Grid, sigma, Lithuanian, then the larger whitespace flow change.

Grid design must retain subgrid name-lookup bounds while separating numeric
clamping for abspos resolution. Equal explicit endpoints appear to expose a
distinct old abspos bug even in ordinary grids; preserve a separate candidate
and commit boundary instead of silently folding it into the subgrid repair.

### Sixth breadth audit dispatched

At the user's request, two new static scouts are inspecting sizing/aspect-ratio
constraint transfer and fragmentation/multicolumn break handling. Their scope,
evidence requirements and ownership are recorded in
`artifacts/css-breadth-audit-round6-v1/PLAN.md`. The active Grid proof continues
alongside them. Reports must distinguish candidates from confirmed defects and
record negative findings as well as opportunities for independent spec models.

Grid expanded baseline 55383 exited 1: 164 new passes and 32 new failures,
all in subgrid abspos cases; 16 existing subtests and four reftests pass, and
abs-pos-002 retains its expected failure. All 17 input hashes stayed stable.
The candidate passes explicit numerical bounds into the helper and finalizer,
preserving normal-flow map bounds exactly and choosing UA bounds for abspos.
Name lookup bounds remain unchanged. Two earlier design approaches were
rejected for a sentinel collision and an unproved bounds-containment premise.
Formatted candidate build and source-bound proof validation are underway.

### Sixth breadth audit completed

Both static reports are complete and root-reviewed; synthesis:
`artifacts/css-breadth-audit-round6-v1/REPORT.md`. Root authenticated 39 distinct
local source/test files and 13 retained remote snapshots. The first probes are
max-content replaced Grid self-stretch and page-only breaks in screen columns.
Border-box ratio min/max behavior is a useful existing WPT failure family.
None of these new scout witnesses has been run in a browser yet.

Recommended new model boundaries are replaced sizing decisions/constraint
coordinates, typed break propagation, phase-aware multicolumn progress,
continuation conservation, and percentage-basis cache refinement. The prior
Flexbox allocation model remains a strong larger milestone. Spec ambiguity,
unsupported break keywords, existing failures and rejected hypotheses are
recorded rather than counted as newly found bugs.

Grid build 80976 and patched WPT 69862 exited 0. All 196 new cases pass, with
exactly 32 improvements; 16 existing subtests and four reftests pass, and the
one expected reftest failure is unchanged. All 17 run inputs stayed stable.
The native/WPT-only patch applies to both comparison bases. Producer proof
60584 passed; root replay and independent candidate/proof review are underway.

### Grid abspos repair accepted

Root proof replay 97340 and independent replay 71146 exited 0. Both accept
26 theorem audits, seven Lean mutations, eight C++ semantic mutations,
11 source controls and nine record guards. The extracted finite C++ adapter
checks 567,000 normal-flow cases, 542,080 abspos cases, and 344,120 bounded
distinct-endpoint projections. All 23 proof pins were reauthenticated; the
companion inventory contains 20 source files.

The theorem connects endpoint policy to independently specified interval
projection for distinct resolved endpoints within UA bounds. Native name
resolution, complete machine arithmetic, equal endpoints and beyond-UA
clamping remain explicit boundaries. Finite projection checks begin with
helper outputs; Lean absorption plus manual branch correspondence supplies
the raw-endpoint connection. Independent review also recounted all 219 WPT
statuses: exactly 32 improvements and 187 unchanged. Evidence:
`artifacts/css-grid-abspos-fix-v1/verification.json`. Commits await the existing
signing blocker; no signing settings or staged-companion ownership changed.

### Sixth breadth probes accepted; sizing repair underway

Run 61891 exited 1: 61 cases, 496 comparisons, 16 failing cases and 55
mismatches. All 74 syntax/support checks passed and 17 inputs stayed stable.
Independent review accepts max-content replaced Grid stretch, the known
border-box ratio family, and page-only requests affecting screen columns.
A failed ordinary-block modern-always positive control is a separate accepted
candidate. Root reauthenticated 101 review identities. Evidence:
`artifacts/css-breadth-probes-round6-v1/REPORT.md`.

The next native repair guards initial inline self-stretch with an auto preferred
size. It preserves later clamp bookkeeping and block sizing. Expanded sizing
baseline 88507 exited 1: 24 new FAIL / 24 PASS; three selected reftests pass and
four WPT042 expected failures remain. The WPT covers aligned writing modes,
directions, images/canvases, natural/explicit ratios, minimum/maximum constraints
and dynamic inline sizes. Baseline dynamic cases fail at the first assertion;
only a full patched pass can validate their subsequent states. Candidate build
80493 and a source-bound finite initial-selection proof are underway.

Sigma repair design proceeds separately: original-input Unicode context scans
avoid pending-output interactions with language-specific expansions. Text-run
boundaries and rendered-glyph evidence remain explicit gates before a repair.

Signed RGB companion retry 12142 exited 128 with the existing 1Password buffer
failure. No commit was created; signing remains enabled and only that companion
is staged. Research and local repair validation continue.

### Replaced Grid max-content repair accepted

Build 80493 and patched WPT 80851 exited 0. All 48 new cases pass: exactly
24 failures improved, and 33 other status records stayed unchanged. Three
existing reftests pass and the four known WPT042 failures remain separate.
All 12 run inputs stayed stable. Each of the four dynamic tests now reaches
all three states. The native/WPT-only patch applies to both comparison bases.

Root proof replay 83538 and independent replay 74474 exited 0. The accepted
companion contains 18 source files: 12 Lean audits over 960 finite contexts,
4,800 extracted C++ branch cases, three Lean and five C++ mutations, five
source controls and nine diagnostic controls. All 25 replay inputs were
authenticated. The theorem covers initial inline stretch selection and
preservation of clamp handling, not final sizing or later stretch promotion.
Native caller/predicate correspondence and geometry remain explicit bridges.
Evidence: `artifacts/css-sizing-stretch-fix-v1/verification.json`.

The next active work is sigma fixture construction and independent design
review. The original-input context proposal must stop at masked context in
partially revealed passwords; a raw full-run scan would change the existing
policy. UTF-16 masking granularity, extraction offsets and available-run context
are being reviewed before native integration. The 43-case literal oracle set
and deterministic font plan are ready; no sigma production edit has been made.

### Seventh breadth audit dispatched

At the user's request, a new static survey targets gradients, container queries
and animation timing. The gradient scout starts immediately. The two active
sigma agents will hand off their masking-fixture and independent proof work
before taking the other areas, preserving the three-worker limit. Sigma native
integration remains with root. Scope and evidence requirements:
`artifacts/css-breadth-audit-round7-v1/PLAN.md`.

Reports must distinguish static leads from confirmed defects, retain negative
findings, and rank small browser probes separately from useful formal models.
No production edits or new confirmed bugs are claimed by this dispatch.

### Sigma browser repair verified; proof and independent review underway

The mask-aware original-context helper is integrated and build 54622 exited 0.
Baseline WPT 35711 had 19 primary and 48 partition failures; patched 18945
exited 0 with all 111 subtests passing and the fixed-font rendering comparison
passing. The baseline rendering differed by 1,369 pixels. Root matched all 129
status identities: 68 improvements and 61 unchanged, including the two existing
expected locale failures. All 46 input pins stayed stable within each run.

Patched compatibility runner 14371 exited 0. All 105 isolated password-rendering
assertions, 287 existing password API assertions, five casing reftests and
19 text-security reftests retain their baseline results. The isolated probe
includes strict sigma/final-sigma calibration and surrogate-boundary widening.
The initial compatibility log parser expected JSON from the legacy reftest
logger and failed after the test process ended; that run is retained. Corrected
baseline runner 90472 records actual child exits and passed all selected gates.

Format 72974 passed; 12 unrelated formatting changes were restored from exact
snapshots. Lint 16857 reports zero errors and four ignored-WPT warnings. The
native/WPT-only patch applies independently to both original and immediate
bases. Evidence: `artifacts/css-sigma-fix-v1/verification.json`.

Independent source/WPT review and the final source-bound proof replay remain
pending. Prepared proof work includes arbitrary finite property-list and masked
projection theorems, plus finite testing of the exact helper against the actual
compiled ICU property backend; preparation is not final proof acceptance.
Cross-native-run context remains outside this repair's established boundary.
The configured signing blocker remains unchanged; no unsigned commits or
pushes were made.

### Sigma repair accepted

Root proof replay 45649 and independent replay 33599 both exited 0, producing
the exact producer receipt. The 14-file companion authenticates 22 inputs and
passes 16 Lean audits, eight Lean mutations, six diagnostic guards, seven native
mutations, five preservation guards and eight source-identity guards. The exact
helper runs 18,523,178 finite decisions against a scalar oracle; all 1,114,112
compiled ICU backend property answers match the pinned Unicode data.

Independent source/WPT and raw browser-result review is accepted. The theorem
is about arbitrary finite property lists; native UTF-16 execution is finite
evidence with transparent string/style adapters. Correct caller offsets and
frame/skip-map context supply remain explicit premises. This does not establish
casing across separate native text runs or a whole-pipeline formal proof.
Final evidence: `artifacts/css-sigma-fix-v1/verification-final-v1.json`.

### Seventh breadth audit completed

All three reports are complete and root-read; 90 retained source/test/spec/report
identities were authenticated. Synthesis:
`artifacts/css-breadth-audit-round7-v1/REPORT.md`. First probes are wrapped query
attribute dependencies, displaced gradient hints with explicit color spaces,
constant-border-box query invalidation, deferred size-query selection, and
animation extrapolation/offset narrowing. The conditions matrix is being prepared.

Useful model extensions are query-AST dependency completeness, query cache
soundness, gradient stop fixup and interpolation-parameter preservation, and
animation interval/segment refinement. Known failures, compatibility policies,
spec editorial gaps and negative findings remain separate. These static leads
are not added to the confirmed bug index before browser and normative review.

Configured signing retry 39949 exited 128 with the same 1Password buffer error.
HEAD remains 11482ee213bf63c749b6d205c2c7591d783bdaa8; no commit was created and
only the 12-file RGB proof companion is staged. Signing remains enabled.

### Seventh breadth conditions probes completed

Root session 78579 exited 0 after 42 cases and 102 states; this research runner
returns zero on completed probes even when observations differ. Literal-oracle
comparisons have 36 mismatches, fresh-document oracles 20, and incremental/fresh
comparisons 16. All recorded support checks passed, all 44 run inputs stayed
stable, and no experimental feature preferences were overridden. Evidence:
`artifacts/css-breadth-probes-round7-v1/conditions/RESULTS-v1.md`.

Observed families are wrapped attribute dependencies, deferred container
selection, changed threshold invalidation, constant-border-box content changes,
and registered boolean/unset values. Four known unknown-OR failures were also
reproduced. Independent normative/native review is underway; these are not yet
new accepted bug-index entries. Gradient and animation probe packages are being
prepared while this review proceeds.


## Eighth breadth audit dispatched (18 October 2026)

At the user's request, three agents are statically mapping current specifications,
native algorithms and WPT coverage in syntax/serialization, overflow/scroll snapping,
and tables. These expand the search beyond the earlier import/scope concentration.
The preceding conditions review and gradient/animation probe handoffs are preserved.
Assignments and evidence gates: [round-eight plan](../css-breadth-audit-round8-v1/PLAN.md).
No new defects are accepted by dispatching this survey.


### Conditions accepted; outer-wrapper repair under verification

The independent conditions review is complete: six bounded defect families
accepted, four unknown-OR calibration failures excluded. Root authenticated all
six review files and updated BUGFIX-COMMITS.md with separate pending entries.

An isolated 84-case WPT exercises direct/inner controls and outer parentheses,
not/and/or/nested combinations, every initial Boolean assignment, both mutation
directions, unique attributes, and named containers with intervening descendants.
Baseline runner 64418 exited 1: 76 new FAIL / 8 PASS and 139 existing PASS.
All pinned inputs were stable. The collector now uses the existing recursive
visitor. Format 2787 exited 0; 12 unrelated formatting changes were restored.
Build 14093 exited 0 (known export-monitor diagnostic retained). The identical
patched browser matrix and scoped structural proof/review are underway.
Evidence and gate plan: `artifacts/css-query-attribute-wrappers-fix-v1/PLAN.md`.


### Wrapper browser gate and independent patch review passed

Patched runner 17786 exited 0: 84 new and 139 existing subtests pass. Raw identity
comparison finds 76 improvements and 153 unchanged results, including harness
outcomes. The 35 run inputs stayed stable; only condition.rs, Firefox and XUL
changed between baseline and candidate. Lint 98221 exited 1 with zero errors and
one ignored-WPT warning. The two-file native/WPT patch applies independently at
both the original project base and current HEAD. Independent review accepted the
native change and test isolation/coverage, including 328 operand mutations.
Formal companion implementation and review remain pending; no commit made yet.

### Eighth breadth audit completed

All three reports are complete and root-read; 174 retained evidence files were
authenticated. Synthesis: `artifacts/css-breadth-audit-round8-v1/REPORT.md`.
First probes: off-axis oversized snap validity, table span/spacing minimum,
zero-area re-snap identity, table residual-space conservation. Three are small
geometry/state or integer arithmetic contracts; parser boundary/recovery and
border-edge order provide additional formal targets even without novel defects.
The exact CDC separator omission is already upstream rust-cssparser issue 434.
Current single-axis overflow is known standards catch-up with six expected WPT
failures. None of these new static suspects has yet been browser-reproduced.

### Animation and gradient runtime probes completed

Animation session 92202 exited 1 after all 19 cases: 267 support checks pass,
10 control cases pass, six of 19 value oracles differ. Large steps saturate
extrapolated values; four narrow-offset samples jump early. The steps fallback
has explicit prior art in bug 1706157. Precision/implementation-limit review is
still required before accepting the two families as repair targets.

Gradient session 4176 exited 0 (completed-measurement semantics): 40 cases,
six displaced-hint linear-sRGB color differences, zero support failures, and
all four solid controls passing. This run exercises drawSnapshot software paint;
the compositor gate remains open. Neither macOS readback nor a release claim is
implied. Both runs used the successful build 14093; all recorded source/binary
inputs remained stable. Receipts: per-package ROOT-RESULTS-v1.json under
`artifacts/css-breadth-probes-round7-v1/`. Independent runtime review is underway.


### Outer-wrapper repair fully accepted

Root replay 69655 and independent replay 63831 exited 0 and exactly match the
producer's receipt. The companion has 11 audited Lean theorems, 1,074 exact
extraction fixtures, 557 old-collector counterexamples, seven Lean mutations,
six diagnostic guards, six native mutations, 12 source-identity guards and four
whole-file preservation controls. The native bridge uses explicit payload/set
adapters; parser, leaf dependency correctness, opaque-leaf stability and real
restyle integration remain premises. Final evidence:
`artifacts/css-query-attribute-wrappers-fix-v1/verification-final-v1.json`.

Configured signing retry 18459 exited 128 with the same 1Password buffer error.
HEAD remains 11482ee213bf63c749b6d205c2c7591d783bdaa8. Only the original 12 RGB
companion files remain staged; signing was not disabled and no commit was made.

### Content-size cache repair in progress

Expanded baseline 25143 exited 1: 72 border-box cases fail and 72 content-box
controls pass, across three writing modes, supported containment axes, padding
and border changes, and both initial states. All 92 existing/wrapper controls
pass. The candidate changes only QueryContainerState size capture from frame
border size to GetContentRectRelativeToSelf().Size(), matching the query getter.
Format 45443 exited 0 (12 unrelated restorations); build 6873 exited 0; lint
81184 exited 1 with zero errors and one ignored-WPT warning. Paired WPT 68131
is running. Proof scope preserves type-eligible observables with explicit fixed
writing-mode/type/availability premises; it must not claim unrestricted equality
of the raw getter's extra contained axes. Native/proof review is underway.

### Runtime classification and new scroll probes

Animation/gradient review is complete. Gradient displaced linear-sRGB hints are
confirmed software-snapshot color errors, with compositor verification open.
Large steps are an observable known-fallback consequence, with bug 1706157 crash
safeguards to retain. Narrow keyframe offsets show precision loss, but conformance
remains unresolved because applicable numeric precision requirements need further
standards/owner review. Gradient fixture authorship is disclosed; the review's
separate decoder/oracle is computational cross-checking, not independent fixture
creation. Root authenticated the frozen review and retained its qualifications.

Round-eight scroll probe 50808 exited 0 after 24 cases/44 states: six differences
in 64 correctness comparisons, zero differences in 840 geometry checks, and no
support, semantic-control, target-setup or settling failures. Off-axis oversized
areas admit offset 400 on both axes; zero-area targets move 500→550 then remain
stale at 550 when their actual position becomes 800. One-jump and nonzero-area
controls pass. Raw-result/normative review is underway; no native fix yet.
Table probe preparation is frozen: 50 cases/150 states plus fresh comparisons,
awaiting the next free browser slot. All work remains local.

### Content-size cache repair fully accepted

Patched WPT 68131 exits 1 with all 144 new and 92 existing subtests passing.
Four existing unexpected passes are identical to baseline and account for the
nonzero harness result. The 240-record comparison finds exactly 72 improvements
and 168 unchanged records, including expected-status fields. No unrelated
expectations changed.

Root proof replay 65410 and independent replay 15896 exit 0, byte-identical to
the producer receipt. The 25-file companion authenticates 33 inputs, audits
11 Lean statements, checks 17,384 native pairs and 400 consumer masks, and
rejects the documented semantic/diagnostic/identity/preservation mutations.
The contract preserves type-eligible dimensional inputs under fixed type,
writing orientation, availability and consumer context; current geometry and
selection/scheduling remain premises. Both independent reviews are accepted.
Final evidence: `artifacts/css-query-content-box-fix-v1/verification-final-v1.json`.
The standalone native/WPT patch is ready; signing remains blocked.

### Ninth breadth audit dispatched

Three agents now examine Shapes/float exclusions, image and background sizing,
and transform geometry/reference boxes. This expands coverage beyond the
completed rounds; no new defect is implied by dispatch. Report requirements
and ownership: `artifacts/css-breadth-audit-round9-v1/PLAN.md`.

### Eighth breadth runtime review accepted

Scroll review accepts off-axis oversized snap validity and zero-area target
retention as separate bounded bugs. Table probe 69093 completed with exit 0 and
measurement semantics: 50 cases/150 states, 102 oracle differences in two
sizing families, no support failures, and 15,558 fresh/mutated comparisons
agreeing. Independent table review reproduced all geometry and authenticated
input identities. Root accepts span/spacing minimum and residual-allocation
defects; no invalidation finding or release/novelty claim. The next repair
addresses negative definite spanning-cell contributions to table minimum size.

### Table span-spacing repair baseline

Expanded WPT baseline 21445 exits 1 with 30 failures and 60 passes in the 90 new
cases. Existing fixed/colspan redistribution controls have 61 passes and 11
expected failures, with unchanged expectations. All 23 inputs stay stable. The candidate clamps the definite span
contribution in GetMinISize, matching final allocation. Percentage and residual
allocation code is unchanged. Format 37724 passes with 12 unrelated restorations;
lint 53962 exits 1 with zero errors and one ignored-WPT warning. Build 82398 and
paired validation are next; proof/source review is pending.

### Table span-spacing browser gate passed

Build 82398 and paired WPT 29618 exit 0. All 90 new cases pass, with exactly
30 improved results; the other 136 status records are unchanged, including
61 existing passes and 11 expected failures. All 23 inputs remain stable within
each run; only the native file and browser binaries differ between runs. The
standalone two-file patch applies to the original base and current HEAD.
Formal companion and independent patch review remain pending. Evidence:
`artifacts/css-table-span-spacing-fix-v1/verification.json`.

### Ninth breadth audit completed

All three reports are frozen and root-read, with retained evidence authenticated.
Synthesis: `artifacts/css-breadth-audit-round9-v1/REPORT.md`. Priority probes are
polygon arithmetic, HTML stroke-box reference dimensions, perspective content
offsets, missing-ratio object-fit sizing and overflow:clip flattening. Elliptical
shape-box margins are another geometric candidate. Background rounding leads
retain precision/prior-art qualifications; known sharp-corner failures and the
open inset specification conflict are excluded from new findings.

The transform agent is preparing browser probes. Other agents have handed off
their static reports and now handle the table span-spacing proof companion and
independent repair review. No round-nine defect has been browser-confirmed yet.
New formal targets include interval exclusions, optional intrinsic sizing data,
affine positioning, reference-box aliases and explicit flattening policies.

### Ninth breadth probes reproduced geometry defects

Polygon session 53306 completed with exit 0 (measurement semantics): 32 cases,
96 states, 276 active and fresh differences, zero support failures and 6,912
active/fresh comparisons agreeing. Independent review accepts the bounded
clipped-polygon exclusion defect. WPT baseline 69328 exits 1 with 16 failures
and 16 passes; two existing clipping reftests pass. A separate arithmetic
design review is checking coordinate differences and truncation preservation
before native integration.

Transform session 8770 completed with exit 0: 27 cases, 81 states, 56 differing
rectangle components; all support and semantic controls pass. Fresh geometry
agrees throughout. Stroke-box, perspective-origin and clip-flattening families
are undergoing independent normative/native/runtime review, so are not yet
confirmed-bug index entries.

Table proof producer and root replay 55682 pass with identical receipts: 13 Lean
audits, 19,146 finite C++ cases and the documented negative controls. Native/WPT
review is accepted; independent proof review is pending. The scalar clamp also
applies to existing min-content/max-content branches; WPT covers definite lengths.

### Table span-spacing repair fully accepted

Independent proof replay 27568 exits 0 and matches producer and root receipts.
The independent checker rederives all 19,146 native outputs and seven mutant
counts. The 17-file companion audits 13 Lean statements and keeps same-input,
nonnegative-contribution and representable-arithmetic premises explicit. Both
patch/runtime and formal reviews are accepted. The fix remains native source
plus one WPT; companion tooling is separate. Final evidence:
`artifacts/css-table-span-spacing-fix-v1/verification-final-v1.json`.
Local commits still await the configured signing service.

### Transform review accepted; polygon repair building

Independent review accepts all three transform families after reconstructing
81 states from physical rectangles and deriving corner/origin/grouping math.
All 47 semantic-control states pass; no fresh/mutated discrepancy occurs.
Stroke-box is the first subsequent repair, then perspective displacement.
Clip flattening additionally needs clipping/rendering review.

Polygon arithmetic design and WPT baseline reviews are accepted. The native
return now uses NSCoordMulDiv, preserving x1 plus truncated delta. Defined
upstream preprocessing and bounded coordinate differences remain explicit
premises. Format 84186 passes with 12 unrelated restorations. Build 94918,
paired testing and the formal companion are underway. An agent is separately
preparing missing-ratio object-fit paint probes.

Configured signing retry 43623 exits 128 with the same 1Password buffer error.
HEAD remains 11482ee213bf63c749b6d205c2c7591d783bdaa8, only the original RGB
companion is staged, and signing remains enabled.

### Polygon browser gate passed; positioning audit dispatched

Build 94918 and paired WPT 38467 exit 0. All 32 new cases and two existing
clipping reftests pass. Exact comparison finds 16 improvements and 19 unchanged
status records; all 18 inputs stay stable within each run. Only native source
and browser binaries differ between runs. The two-file patch applies at the
original project base and current HEAD. Lint has zero errors and one ignored-WPT
warning. Formal companion and final independent review remain pending.

A new artifact-only scout is auditing positioned layout: absolute/fixed containing
blocks, automatic margins, inset equations, writing modes and overconstraint rules.
It excludes already covered Grid endpoint and transform geometry cases.

### Polygon repair fully accepted

Root replay 83706 and independent replay 35100 exit 0, matching producer 93692
byte for byte. The companion audits 15 Lean statements and checks 29,615 native
cases plus 15,137 original-defined compatibility cases. Independent Fraction
oracles agree. Difference bounds, finite resolution and defined upstream
preprocessing remain explicit premises. Native/WPT and formal reviews are
accepted; final evidence is css-polygon-intercept-fix-v1/verification-final-v1.json.
The isolated fix and preceding proof companion await configured signing.

The next repair addresses CSS-layout stroke-box reference dimensions. Baseline
51522 has 72 FAIL / 144 PASS plus four existing CSS/SVG reftest passes. Candidate
removes the early return so stroke-box shares existing border-box handling.
Format 84859 passes, with 12 unrelated restorations; proof companion is underway.

### Stroke-box browser gate passed; tenth static audit complete

Build 56906 and paired WPT 2641 exit 0. All 216 new alias/percentage cases
and four existing CSS/SVG reftests pass. Exact status comparison finds 72
improvements and 149 unchanged records; 20 run inputs stay stable and only
native source/browser binaries differ. Scoped companion and independent review
remain pending. No unrelated expectations changed.

The positioning audit is root-read and authenticated. Its first probes target
one-auto-margin signed residuals and explicit-inset alignment through differently
oriented static wrappers. These remain static suspects, not confirmed bugs.
Synthesis: artifacts/css-breadth-audit-round10-v1/REPORT.md.

Object-fit probe v3 session 41423 completes with exit 0: 26 cases, 78 primary
and 78 fresh states, 30 paint differences per mode. All setup, support, reference,
semantic-control and fresh-consistency gates pass; independent review is underway.
V1 failed before measurement due to top-level data navigation; v2 had two stale
image-source metadata observations. Both are preserved. V3 explicitly waits for
the requested current source before decode/settling. Rendering evidence is
software drawSnapshot, with no compositor/release claim.

### Object-fit runtime review accepted

Independent review reconstructs all V3 sizing oracles from SVG XML and rational
arithmetic, then decodes retained pixels through ImageIO independently of the
producer's PNG code. Root replay 58417 exits 0 and matches independent 76451;
368 frozen evidence identities authenticate. All 30 candidate states per mode
paint a full constraint box instead of preserving the one natural dimension;
all 48 control states per mode pass. V3 is accepted and indexed as software-paint
evidence. Native/WPT repair, formal sizing companion and compositor/release
investigation are separate future gates.

### Stroke-box repair fully accepted

Root replay 60600 and independent replay 21345 exit 0, matching producer 47166.
The companion audits 14 Lean statements and checks 850 extracted-function
fixtures, each invoked twice. Independent oracles reproduce all values/provider
counters and the 42 old-contract disagreements. Seven Lean and nine native
mutations are rejected. Arbitrary-payload alias equality and fixed-input cache
behavior are proved; real frame/SVG/zoom geometry and invalidation remain premises.
Both native/WPT and scoped formal reviews are accepted. Final evidence:
artifacts/css-stroke-reference-box-fix-v1/verification-final-v1.json.

The standalone fix contains native source plus WPT; its 15-file companion is
separate. Configured signing still blocks commits, with HEAD unchanged and the
original 12 RGB companion files staged byte-for-byte. Positioning browser probe
preparation continues; the accepted image-sizing defect awaits its own repair.

### Partial image sizing repair baseline; positioning runtime completed

Object-fit baseline 30989 exits 1: both new paint reftests fail with exactly
48,000 differing pixels each; six existing SVG None reftests pass. The tests
cover 24 tiles each, with initial and post-TestRendered fit assignment. Literal
CSS rectangles are the shared reference. Large partial objects are clipped paint
controls, not measurements of their full unpainted dimensions.

The native candidate removes the missing-ratio early return; existing default-
sizing and constraint helpers already handle that case. Format 65569 exits 0
with 12 unrelated restorations. Build 6827 exits 0; lint 60034 has zero errors
and four ignored-WPT warnings. Paired reftests and scoped optional-dimension
proof/review are underway. The isolated five-file native/WPT patch applies at
both original base and current HEAD.

Positioning runtime 11302 completes exit 0: 40 cases, 120 states, 74 oracle
component differences per active/fresh mode and zero fresh/mutated differences.
All support, literal reference/calibration and semantic controls pass. All 145
run inputs remain stable. Independent review is separating geometric changes
from used-margin-only differences before accepting either candidate family.

### Eleventh breadth audit dispatched

At the user’s request, three artifact-only static surveys expand into block-flow
margin collapsing, clipping/masking and border radii, and fonts/line metrics.
Each must connect current normative rules to concrete implementation branches,
check existing WPT expectations/prior art, and propose bounded browser probes
and formal contracts. Static suspects are not confirmed bugs. Assignments and
evidence gates: artifacts/css-breadth-audit-round11-v1/PLAN.md.
The object-fit formal review and positioning repair handoffs remain pending.

### Object-fit root proof replay and positioning acceptance

Object-fit root replay 4154 exits 0 and exactly matches producer 26797. Fifteen
Lean audits and 2,355 extracted-helper fixtures pass; 380 old partial-size
counterexamples plus two None/both-dimension cases are distinguished from two
ScaleDown boundary changes excluded from normative claims. Positive-ratio
preservation has 720 finite controls; actual ratio arithmetic remains opaque.
Paired native/WPT review and its separate authorship correction are root-read
and authenticated. Independent formal review remains pending.

The positioning independent checker also replays with exit 0 and matching bytes.
Root accepts and indexes two separate bounded defect families: one-auto-margin
signed residuals and explicit-inset alignment through static wrappers. Negative
IMCB policy is not settled by the positive-IMCB margin evidence. Both repairs
and their WPT/proof companions remain to be developed.

### Positioning margin baseline and standards correction

New WPT baseline 97192 exits 1: 144 new FAIL / 288 PASS, 70 existing
subtests and two reftests PASS, eight pre-existing negative-IMCB expected
failures unchanged. Inputs remain stable. Two preflight failures (author-link
resource classification and nonexistent source path) were corrected before
browser execution; both logs are retained.

Issue 11478’s complete primary discussion corrects the earlier unresolved-policy
characterization: CSSWG resolved to floor IMCB size at zero and reaffirmed this
in November 2025; the issue is still labelled Needs Edits. Root design therefore
floors IMCB before subtracting fixed margins, retaining signed residuals.
Expanded negative-IMCB baseline and independent design review are next.
Evidence: artifacts/css-abspos-auto-margin-fix-v1/DESIGN-v1.md.

### Object-fit repair fully accepted

Independent formal replay 48038 exits 0 and matches producer 26797 and root 4154.
The reviewer independently reconstructs all 2,355 fixture results, 15 theorem
scopes and seven native mutation counts; root read and authenticated 118 review
files. Native/WPT and formal gates are complete within the recorded optional-size
and dispatch boundaries. Final evidence is
artifacts/css-object-fit-partial-fix-v1/verification-final-v1.json.
Standalone commits still await the configured signer.

Auto-margin candidate build 62245 succeeds, but independent design review finds
a required additional gate: automatic insets may be numerically resolved before
margin allocation. A sentinel-only check does not preserve their provenance when
moving the clamp. Add negative-fixed-margin automatic-inset controls and revise
the guard before accepting this repair. No paired success is claimed yet.

### Eleventh breadth audit complete

All three agent reports are root-read and authenticated. First new probes are
non-monotone padding/size zero classification in margin collapsing, transparent
mask-layer omission under intersect/subtract, and inherited from-font factors
from zero-size parents. A metric-axis probe requires a discriminating font;
the retained Noto font is explicitly insufficient. No new defect is confirmed
by these static reports. Synthesis: artifacts/css-breadth-audit-round11-v1/REPORT.md.

### Auto-margin browser gate passed after provenance correction

First candidate run 3420 exits 1 with 72 new automatic-inset regressions; those
were found by independent source review and confirmed by expanded WPT. Original
source build 59352 and baseline 98226 preserve all 216 automatic-inset controls.
The revised patch reuses anchor-resolved automatic-inset flags and avoids unused
residual arithmetic when neither margin is auto.

Revised build 1527 and patched WPT 5547 exit 0. All 792 new subtests pass;
70 existing subtests, two reftests and eight expected failures are unchanged.
Exact comparison finds 240 improvements and 637 unchanged records across 877
identities. All 25 run pins are stable; only native C++, its necessary header,
Firefox and XUL change between baseline and candidate. Format 25427 passes,
with 12 unrelated restorations; lint 85184 has zero errors and one ignored-WPT
warning. Three-file patch applies at original base and current HEAD. Scoped
proof and independent final patch review remain pending. Evidence:
artifacts/css-abspos-auto-margin-fix-v1/verification.json.

Configured signing retry 80922 exits 128 with the same 1Password buffer error.
HEAD remains 11482ee213bf63c749b6d205c2c7591d783bdaa8 and the original 12 RGB
companion files remain staged. Signing was not disabled and no commit was made.

The first round-eleven block-flow probe is now running against build 1527.

### Block-flow endpoint probe reproduced the predicted offsets

Root probe 75132 completes with exit 0 against build 1527: 30 cases, 90 active
and 90 fresh states, 18 parent-offset differences per mode. All support,
calibration and semantic controls pass; no state is inapplicable. All 270
active/fresh geometry comparisons agree. Preparation/external inputs and
metadata remain unchanged. Exit 0 means completed measurement, not passing
oracles. Independent normative/native/raw-geometry review is underway before
adding any confirmed bug entry. Evidence:
artifacts/css-breadth-probes-round11-v1/block-flow/ROOT-RESULTS-v1.json.

### Auto-margin independent native acceptance

Independent final native/WPT review is accepted. Root replay of verify_final.py
exits 0 and matches the independent receipt; root read the final report and
authenticated its freeze. Candidate v1’s rejection and the issue-resolution
correction remain preserved. Current verification.json is frozen preacceptance
evidence; final acceptance will be written separately after the proof gate.
Evidence: artifacts/css-abspos-auto-margin-fix-v1/ROOT-NATIVE-REVIEW-v1.json.

Formal producer has a source-bound caller/helper capsule and Lean model in
development, with mutation and independent-review gates still open. The new
block-flow runtime is under separate independent review. Masking paint-probe
preparation is running artifact-only. No browser/build session remains active
at this checkpoint; the latest local build contains the revised margin patch.

### Twelfth breadth audit dispatched

At the user’s request, three artifact-only surveys expand into CSS transitions,
CSSOM stylesheet mutation, and containment/content visibility. These add state
and lifecycle contracts alongside earlier numeric and geometry work. Each scout
must trace current normative rules to source and existing WPT, retain provenance,
and propose bounded browser and formal gates. Dispatch is not a bug finding.
Assignments: artifacts/css-breadth-audit-round12-v1/PLAN.md.

### Block-flow runtime review accepted

Root read the independent report, replayed its checker with exit 0 and identical
output, and authenticated all 146 frozen review files. Both positive preferred
height and bottom-padding paths produce 18 wrong parent offsets per mode; all
controls pass, including expression bases that genuinely resolve to zero. This
is indexed as one collapse-classification family pending repair design, not an
invalidation defect. A ReflowInput-based guard is under investigation; global
zero predicates have broader callers and are not being replaced without review.

The auto-margin producer froze 21 Lean audits and 2,124 native fixtures; root
replay is running. Masking preparation validation passed. Its first execution
failed at localhost socket binding before browser launch; the retained second
attempt runs with local browser permissions.

### Auto-margin root proof replay and masking measurements

Auto-margin root replay 19838 exits 0 and matches the producer receipt exactly:
21 theorem audits, 2,124 original/candidate native cases and all required
mutation/diagnostic/source-preservation controls pass. Root read the Lean model,
extractor, adapters, fixture oracle and checker. Independent formal review is
still required; anchor providers and arithmetic representability remain premises.

Masking run 17388 exits 0 with 208 software snapshots. Eight candidate states
per mode differ by 10,000 pixels each; all setup/support/calibration/reference,
96 semantic-control states per mode and active/fresh equality gates pass. All
201 input pins remain stable. Independent normative/native/pixel review is next;
no compositor or release result is claimed. The earlier sandbox-bind failure is
retained as preflight evidence. ROOT-RESULTS-v1.json records terminal status.

The block-flow WPT baseline now covers 90 subtests, including a minimum-height
extension, and five existing collapse reftests. Native code remains unchanged
while the resolved-size guard design is checked. Package:
artifacts/css-block-flow-collapse-fix-v1/DESIGN-v1.md.

### Twelfth breadth surveys complete

All three reports are root-read; 309 frozen package files authenticate and all
root integrity replays pass. First proposed gates are duplicate adopted sheets
with named layers, remembered size under CSS zoom, and cross-property discrete
transition cancellation. Identical-text asynchronous replacement and negative-
playback event ordering follow. No new defect is accepted from static reports.
Synthesis: artifacts/css-breadth-audit-round12-v1/REPORT.md.

### Block-flow candidate browser gate passed

Build 46955 exits 0; paired WPT 19771 exits 0 with all 90 new subtests and five
existing reftests passing. Exact comparison finds 36 improvements and 60
unchanged records. All 26 inputs stay stable within each run; only the native
file and browser binaries change between runs. Format 84318 passes with 12
unrelated restorations; lint 8122 has zero errors and one ignored-WPT warning.
The two-file patch applies to original base and HEAD. Independent design/native/
WPT review is running, with min/max, fragmentation and hidden-content boundaries
explicit; a formal companion remains to be developed.

Independent auto-margin formal replay also passed; its report is being frozen.
Masking has a separate independent normative/source/pixel reviewer. Configured
signing retry is running for the unchanged original staged RGB companion.

### Auto-margin repair fully accepted

Independent formal replay 88977 exits 0 and matches producer 65360 and root
19838. Its independent oracle regenerates all 2,124 fixtures, 4,248 original/
candidate rows and all nine native mutation outputs. Root read the report and
checker, replayed the checker with identical bytes, and authenticated 154 frozen
files plus both toolchain binaries. All 21 Lean audits and native/WPT gates are
accepted within the recorded provider, zero-initial-auto and representability
premises. Final evidence: css-abspos-auto-margin-fix-v1/verification-final-v1.json.
The three-file native/header/WPT patch and preceding 23-file tooling companion
await signing. This is the seventeenth fully accepted pending repair.

Configured signing retry 44462 exits 128 with the same 1Password buffer error.
HEAD and the original 12 staged RGB companion files remain unchanged; signing
was not disabled. No commit or push occurred.

Independent block-flow review found no immediate native defect but requires
focused provider controls: max/min bounds, indefinite bases, real border-box
adjustment, hidden-parent behavior and fragmented expression/literal equivalence.
An artifact-only agent is preparing those probes before final design acceptance.

### Masking runtime review accepted

Root read the independent normative/native/pixel report, replayed the separate
ImageIO checker as 27773 (exit 0, identical receipt), and authenticated 438 frozen
files. The two native sites are indexed separately: empty SVG region handling
and zero-size CSS image handling. Each requires an independent native/WPT fix;
shared alpha algebra can precede both. All 96 controls per mode pass. No
compositor or release-browser claim is added.

### Block-flow boundary baseline amendment required

Original-source build 91588 succeeds. Boundary run 79090 completes with stable
142 pins, zero support/fresh differences and five normative parent-offset
differences per mode. It also reveals 84 invalid fragmented-size calibrations:
CSSOM height is a fragment size, and a min-height block can grow to its child.
The 28-case raw result is retained as unaccepted v1. Author and reviewer are
preparing a v2 calibration using complete fragment geometry; no native change
is warranted by those harness assumptions. Current live block-flow source and
binary are original for the upcoming baseline, with candidate bytes preserved.

### Block-flow boundary gates passed

The v2 amendment preserves the original measurements and corrects only invalid
fragment calibration assumptions. Original run 72058 and candidate run 67362
both exit 0, with 152 inputs stable in each. Candidate rebuild 49337 exits 0.
Ten wrong offsets become zero, and 80 expression/literal fragment component
differences become zero. No literal-control geometry changes; no support,
calibration, or active/fresh failures. Only native source and browser binaries
differ between runs. Root replay of the independent fragment calibrator passes.
Candidate source and binary are restored. Final native review and the planned
formal companion remain open; this is not an arbitrary-fragmentation proof.
Evidence: css-block-flow-collapse-fix-v1/ROOT-BOUNDARY-REVIEW-v2.json.

### Duplicate adopted sheets measured

Round 12 CSSOM probe 46456 exits 0: 80 cases and 240 states per active/fresh mode.
Each mode has 48 named-layer discrepancies, 12 exploratory anonymous-important
differences, and 180 passing semantic controls. All support/reference gates pass;
all active/fresh colors agree. Root checker replay passes with stable inputs.
Independent normative/native review is pending; anonymous-layer identity stays
unresolved. Evidence: css-breadth-probes-round12-v1/cssom-duplicates/ROOT-RESULTS-v1.json.

### Thirteenth breadth audit dispatched

Three artifact-only agents survey background/border geometry, Flexbox/Grid
alignment, and CSS tokenization/recovery/serialization. Each must distinguish
static hypotheses, prior known failures, and useful proof contracts, and retain
spec/source/WPT evidence. Dispatch and preliminary leads are not accepted bugs.
Assignments: css-breadth-audit-round13-v1/PLAN.md.

### Thirteenth breadth surveys reviewed

Root read all three reports and replayed their verifiers: 278 frozen files across
backgrounds/borders, alignment and syntax. Priorities are bad-URL suffix recovery,
Grid baseline fallback safety, fractional border-image slices, and reversed
Flexbox safe alignment. Conflicting standards/test expectations remain explicit;
the apparent accelerated-gradient bug was rejected by its caller guard.
Synthesis: css-breadth-audit-round13-v1/REPORT.md.

### Block-flow final native review accepted

Root read and replayed the independent final native checker with byte-identical
output, authenticating all 258 frozen review files. Exactly 22 expected expression
observations improve; 146 others, including all 84 literal observations, remain
unchanged. The two-file native/WPT patch is accepted subject to its formal gate.
The full-function native capsule and ordinary-tree Lean companion are now under
development. Evidence: css-block-flow-collapse-fix-v1/ROOT-FINAL-NATIVE-REVIEW-v1.json.

### Bad-URL recovery repaired and paired WPT passed

The syntax scout found premature cursor advancement after unquoted URL whitespace.
Root standalone run 25725 exits 0 with 14 wrong results and 18 controls passing.
The new WPT extends coverage to borrowed/owned URL buffers: baseline 55244 has
28 FAIL and 36 PASS. Candidate run 79528 exits 0 with all 64 PASS; five nearby
passes and three expected failures remain unchanged (76 identities, 28 improve).

Initial incremental build and forced Cargo invocation reused the vendored crate;
the ineffective paired run is preserved. Targeted cssparser cache clearing and
forced build 9783 explicitly recompiled it, and relink 99606 succeeds. Format
73240 succeeds with 12 unrelated restorations; lint 57206 exits 1 with zero errors
and one ignored-WPT warning. The native/checksum/WPT patch applies independently
to original base and HEAD. Native/runtime independent review and a source-bound
suffix proof remain gates. Evidence: css-bad-url-recovery-fix-v1/ROOT-WPT-REVIEW-v1.json.

### Independent native/runtime reviews accepted

Root read and replayed the bad-URL independent checker, matching its paired
receipt and authenticating 87 review files. Native/checksum/WPT are accepted;
the scalar-suffix theorem and exact-tokenizer capsule are under development.
The independent finite scanner audit covers 271,464 inputs; it is explicitly
not a universal Rust proof. Final native acceptance:
css-bad-url-recovery-fix-v1/ROOT-NATIVE-REVIEW-v1.json.

Root also read and replayed the independent CSSOM duplicate checker, matching
its receipt and authenticating 174 files. One named-layer ordering family is
accepted. A separate artifact design compares full occurrence representation
with ordered layer-introduction metadata; no live CSSOM repair is made yet.
Anonymous-important stays exploratory. Root acceptance:
css-breadth-probes-round12-v1/cssom-duplicates/ROOT-REVIEW-v1.json.

Configured signing retry 97197 exits 128 with the same 1Password buffer error.
HEAD and all original 12 staged RGB companion inputs are unchanged; signing was
not disabled. Evidence: css-bad-url-recovery-fix-v1/SIGNING-RESULT-v1.json.
Proof work and repair design continue; signing is not a whole-goal blocker.

### Fourteenth breadth audit dispatched

At the user’s request, selectors/nesting static analysis starts immediately;
text-decoration and image-selection surveys are queued behind the CSSOM design
and bad-URL proof respectively. Each must retain an explicit inspected-coverage
ledger, rejected hypotheses, normative/source/WPT evidence and useful formal
contracts. The queue preserves existing deliverables and the three-worker limit.
Assignments and acceptance gates: css-breadth-audit-round14-v1/PLAN.md.
No finding is accepted from dispatch.

Block-flow’s producer reports a frozen companion with 34 Lean audits, 2,180
native fixtures and 2,532 model evaluations; root replay and independent formal
review remain pending. SVG mask WPT baseline session 68777 exits 1: both new
static/mutation reftests fail and all four existing compositing controls pass.
The runner reports stable inputs. Native SVG sources remain unchanged; pixel
inspection and repair design remain open.

### Block-flow root proof replay and SVG paired gate passed

Block-flow replay 22432 exits 0 and exactly matches producer 9753: 34 Lean
audits, 2,180 native fixtures and 2,532 executable model comparisons. Root read
the model, full-function bridge, adapters, oracle and checker and authenticated
27 frozen files. Independent formal review is assigned to the text-decoration
scout after its survey handoff. Provider and arbitrary-fragmentation exclusions
remain explicit: css-block-flow-collapse-proof-v1/ROOT-PROOF-REVIEW-v1.json.

SVG mask build 60460 and paired WPT 36533 exit 0: both new static/mutation
reftests improve FAIL→PASS and four existing references remain PASS. All 26
pins stay stable per run; only three native files and the binaries differ.
Baseline pixel decoding validates all 1.92 million test/reference pixels against
the independent eight-wrong-cell oracle. Empty-region classification is explicit;
other null-surface handling is preserved. Format35599 passes; lint83493 has
zero errors and four ignored-WPT warnings. The seven-file native/header/WPT
patch applies independently at original base and HEAD. Independent review and
the scoped alpha/native companion remain open. Evidence:
css-svg-empty-mask-fix-v1/ROOT-WPT-REVIEW-v1.json.

CSSOM repair design is root-read and its integrity/finite checker replay passes:
35 frozen files and 20 live inputs. Unique ownership plus complete ordered
applications is accepted as a prototype architecture; anonymous-important layer
identity and complete synchronization hooks remain unresolved landing gates.
No native CSSOM patch is accepted. Evidence:
cssom-duplicate-layers-design-v1/ROOT-DESIGN-REVIEW-v1.json.

### Bad-URL root proof replay and new nesting measurements

Bad-URL replay24730 exits0 and exactly matches producer18271:25Lean audits,
7,132 native fixtures in both actual macro configurations,8,268 model cases,
375 original-source mismatches and zero candidate mismatches. Root read the
model/oracle/capsule/exporter/checker and authenticated273freeze files plus
209source origins against current bytes. Independent formal review follows the
block-flow review: css-bad-url-recovery-proof-v1/ROOT-PROOF-REVIEW-v1.json.

Round14 selectors and text-decoration reports are root-read and their integrity
checkers pass (61 and106files respectively). Selectors discovery run18310 exits0
with7predicted failures and5control passes;36inputs remain stable and all support,
target and CSSOM gates hold. Five failures concern packed specificity arithmetic;
two concern invalid pseudo-element parent arms retaining prefix specificity.
These remain preliminary runtime findings awaiting independent normative/source
review and expanded controls, not new accepted bug entries. Evidence:
css-breadth-probes-round14-v1/selectors-baseline-v1/ROOT-RESULTS-v1.json.

SVG independent review requests one extra three-layer boundary gate. New16cell
reference with partial alpha, transform and clip passes as64540;13pinsstable.
The ten-file candidate applies at originalbase+HEAD; boundarylint has0errors
and3ignoredwarnings. Final native review and shared alpha/native proof are
underway: css-svg-empty-mask-fix-v1/ROOT-WPT-REVIEW-v2.json.

### Block-flow repair fully accepted; SVG native review accepted

Root read and replayed the independent block-flow formal checker with exit 0,
authenticating 156 files. Its independent stack-machine oracle matches all
4,360 native records and 2,532 model outputs; producer/root/independent proof
receipts agree. Native/WPT and formal gates are complete within the recorded
provider and normal-tree boundaries. Final acceptance and packaging are in
css-block-flow-collapse-fix-v1/verification-final-v1.json. This is the eighteenth
fully accepted pending repair; configured signing remains unresolved.

Root also read and replayed the independent SVG native/WPT checker with identical
bytes, authenticating 121 files and matching all ten current patch files. Native
and browser acceptance is recorded in css-svg-empty-mask-fix-v1/ROOT-NATIVE-REVIEW-v1.json.
Its shared rational-alpha and exact-native companion has an accepted scope plan
and is being implemented. CSS image mask repair remains separate.

Bad-URL independent formal review is running. The image-selection scout is
finishing its report, then will independently review the preliminary nesting
findings. No shared build or browser process remains active at this checkpoint.

### Fifteenth breadth audit dispatched

Two artifact-only scouts start ruby annotation layout and scroll anchoring. A
third survey of bidirectional inline integration is queued after the active SVG
mask proof freezes. These target gaps beyond the earlier targeted surveys and
require explicit coverage, rejected hypotheses, normative/source/WPT traces,
bounded witnesses and formal contracts. Existing repairs retain priority and
static leads are not accepted bugs. Assignments and gates:
artifacts/css-breadth-audit-round 15-v1/PLAN.md.

### Bad-URL formal review accepted

Root read the independent report and oracle, replayed the verifier with exit 0,
and authenticated 428 frozen files. Producer, root and independent proof receipts
match. All native/WPT and scoped formal gates are complete; universal UTF-8/native
state correspondence remains an explicit unproved premise. This is the nineteenth
fully accepted pending repair. The configured signing blocker remains separate
from ongoing research and fixes. Final evidence:
css-bad-url-recovery-fix-v1/verification-final-v1.json.

### CSS image empty-fill mask repair passed paired WPT

Baseline 27268 has three new failures and four existing passes; outside-clip
baseline 19121 also fails. The latter extends the same skipped-empty-fill defect
to prepared nonzero images positioned outside the mask painting area. A ten-line
nsCSSRendering.cpp repair handles successful preparation and empty fill for
IN/OUT while preserving background and resource-failure behavior.

Build 38979 succeeds. Paired runs 85821 and 65485 exit 0: all four new reftests
pass and four existing passes are unchanged. All run inputs remain stable; only
the native file and Firefox/XUL differ. The eleven-file native/WPT patch applies
at original base and HEAD. Format 51558 passes with twelve unrelated restorations;
lint 66449 has zero errors and ten ignored-WPT warnings. Independent native/WPT
review is active; a separate CSS image formal bridge remains required. Evidence:
css-image-zero-mask-fix-v1/ROOT-WPT-REVIEW-v1.json.

SVG proof replay 14069 exits 0 and matches producer 15453: 36 Lean theorems,
4,320 native cases per variant and 4,320 executable model comparisons. Root read
the model, full-function extractor, adapters, oracle and checker, authenticated
218 frozen files and seven source mappings. Independent formal review remains
pending; its native connection covers SVG only. Evidence:
css-empty-mask-composition-proof-v1/ROOT-PROOF-REVIEW-v1.json.

### SVG formal capsule lifetime defect found in independent review

The independent reviewer found that the callee fixture constructs MaskParams
with a temporary Matrix even though its extracted constructor stores a const
reference. The temporary expires before the subsequent native call. Prior green
v1 native replays are therefore insufficient for acceptance; root review is
superseded by ROOT-PROOF-REVIEW-AMENDMENT-v2.json. Pure Lean results and separate
Gecko/WPT evidence remain distinct. The producer is preserving v1 and preparing
a v2 capsule with a named live matrix and fresh full replays. Formal acceptance
remains withheld pending independent correction review.

### Fourteenth survey synthesis and nesting defect acceptance

Root read and authenticated the image-selection report; its checker passes with
99 files, 59 live origins and 224,694 finite model cases. A registered SVG MIME
parameter is the leading new probe; embedded resolution was rejected after the
CSSWG resolution check. All three round-fourteen reports are now synthesized in
css-breadth-audit-round14-v1/REPORT.md.

Root also read/replayed the independent nesting review. Two reproduced families
are accepted for repair as separate fixes: packed-specificity arithmetic and
invalid-parent-arm prefixes. Seven initial failures and five passing controls
are authenticated; expanded mutation/fresh controls are running before repair.
No selector production change has been made.

Round-fifteen ruby and scroll-anchoring reports are root-read and their checkers
pass. Leads remain static; bidi is preserved while its agent corrects the SVG
capsule lifetime defect. Partial synthesis is recorded in
css-breadth-audit-round 15-v1/ROOT-REVIEW-partial-v1.json.

The reviewer-requested eight-cell rounded mask clip reference passes as 88055.
The v2 mask patch has 14 standalone paths. Boundary lint 77790 reports zero
errors and three ignored-WPT warnings. Independent native review is finishing.

### CSS image native review accepted; nesting expansion completed

Root read the native report and independent pixel/receipt/patch checkers, then
replayed them as 37369 with exit 0. All 156 current origins, five receipt phases,
fourteen patch paths and 3.84 million baseline pixels authenticate. The bounded
native/WPT repair is accepted; exact image-path formal production is starting
under PROOF-PLAN-v1.md. No universal raster proof or release result is claimed.
Evidence: css-image-zero-mask-fix-v1/ROOT-NATIVE-REVIEW-v1.json.

Expanded nesting run 34330 exits 0: 22 cases and 88 observations, with 36
candidate discrepancies and 52 expected passes. All ten control cases and all
22 reset states pass; every mutated/restored result agrees with its fresh
equivalent. All 38 run pins stay stable. This supports the two existing defect
families and the prespecified repair controls, with no selector source edits.
Evidence: css-breadth-probes-round14-v1/selectors-baseline-v2/ROOT-RESULTS-v1.json.

SVG v2 also corrects a mutation-quality defect: the missing-initialization mutant
must use initialized direct-callee fixtures, avoiding undefined behavior from an
uninitialized caller flag. ASan fails to start even for a trivial executable in
this environment; retained timeouts are inconclusive, not passing sanitizer
evidence. Named-matrix ownership and a compiler lifetime diagnostic are being
reviewed alongside fresh ordinary/UBSan replays.

### Corrected SVG formal acceptance and completed round 15 survey

SVG v2 root replay 50197 and independent replay 68596 both exit 0 and match
the producer receipt. The 36 rational theorems, 4,320 native cases per variant,
4,320 Lean evaluations and mutation/diagnostic controls pass. Root authenticated
143 frozen entries and seven live source mappings. Named matrix ownership and
the initialized direct-callee mutation corpus resolve both review findings;
v1 remains rejected. Final verification is recorded in
`css-svg-empty-mask-fix-v1/verification-final-v1.json`. Twenty repairs are fully
accepted and await configured signing.

All round 15 static surveys are reviewed: ruby, scroll anchoring and bidi.
`css-breadth-audit-round 15-v1/REPORT.md` ranks next browser gates and records
known-issue/specification limits. Bidi browser session 9086 exits 0: all four
candidates fail as predicted and all eight controls pass, with 49 stable inputs.
This is a reproduced discrepancy awaiting independent defect review.

Signing retry 18973 exits 128 with the same 1Password buffer error. HEAD and
the original twelve staged RGB companion files are unchanged; signing remains
enabled. `css-image-zero-mask-fix-v1/SIGNING-RESULT-v1.json` records the outcome.
CSS image formal implementation and independent review continue, alongside an
independent nesting specificity repair design.

### Round 15 first browser gates complete

Ruby v2 session 77589 exits 0 with 15 candidate failures and 21 passing controls,
across spanning collapse and sole preserved whitespace. All 69 inputs are
stable; computed pre is recorded after strengthening the preliminary v1 probe.
Scroll session 5505 exits 0 with two candidate failures and eleven passing
controls, with 158 stable inputs. Immediate and settled scroll offsets agree.
Together with bidi, five discrepancy families are queued for independent
defect review. No production source changed for these probes. Evidence and
limits: `css-breadth-probes-round 15-v1/REPORT-v1.md`.

Next work: complete CSS image formal acceptance; review the nesting specificity
design and implement its independent repair/WPT; adjudicate round 15 findings
before adding their small native models and separate fixes. Keep known plaintext
alignment and the display:contents standards gate outside this new-defect list.

Bidi independent review is root-read and its live checker exits 0, confirming
the separate UAX9 ordering derivation and all 49 runtime pins. The loaded inline
image defect is accepted for repair, with neutral-complement and mutation WPT
gates required. Ruby and scroll reviews remain queued after active proof/design
work. See `css-breadth-probes-round 15-v1/ROOT-BIDI-REVIEW-v1.json`.

### CSS image formal acceptance and nesting arithmetic repair gates

CSS image producer 74384, root 93632 and independent 80474 all exit 0 with identical
summary b8367a98. There are 9,184 bounded native cases per variant, 9,184 Lean
evaluations, 36 shared plus 17 image theorem declarations, ten full-corpus native
mutations and two specific state-assertion controls. Root read the model, exact
extractor, adapters, checker and independent oracle/report, then replayed the
independent verifier with 19 live origins. Full raster/clip/decoding and universal
C++ refinement remain outside scope. ASan runtime is unavailable, explicitly.
The source-only packaging closure is repaired in a versioned addendum without
changing frozen evidence. Final verification is recorded; 21 accepted repairs
now await configured signing.

Nesting A baseline 77601 has 22 FAIL/16 PASS; build 67333 and paired 7608 exit 0 with
38 new PASS, 11 existing PASS and 3 existing reftestPASS. Boundary 46603 exits0: eight A
cases improve, four B cases remain wrong, all controls/reset/fresh-mutation
checks pass. The three-file patch applies independently to original base and
HEAD. Lint 59113 exits 1 with zero errors and one ignored-WPT ESLint warning.
The initial baseline 71951 was a test-setup error (missing body), retained and
rejected; revised baseline 35624 established 18 failures, then ID-level shadow
competitors extended the final baseline to 22.

Performance is a required gate, not optional cleanup: actual-crate benchmark
25142 finds 35.06x at P=1,000/A=100 for direct ampersands, from 1.137us to 39.851us.
The first recomputation algorithm is rejected for landing despite correctness
gates. Preserve fresh counting but cache direct-parent contributions, avoiding
repeated scans of identical parent lists. The producer is testing an artifact
revision before root applies it. Do not start broader Lean expansion until this
regression is resolved.

Ruby and scroll independent defect reviews are root-accepted, completing all
five round 15 adjudications. Two separate scroll repair designs are underway;
endpoint suppression must handle own versus ancestor ownership safely, while
fixed-child exclusion must preserve legitimate local absolute candidates.

### Sixteenth breadth survey dispatched

The user requested further static spec/implementation analysis. Motion paths
start immediately after the completed scroll repair design handoff. Display box
generation follows the nesting v2 static/performance review; text overflow and
ellipsis follow its formal companion. Three worker slots are respected, and
current verification deliverables retain priority. Each survey must retain an
explicit coverage ledger, negative findings, normative/native/WPT evidence and
ranked browser/proof targets. Assignment details and acceptance gates:
`css-breadth-audit-round16-v1/PLAN.md`. No new defect is established by dispatch.

### Optimized nesting integration and fixed-anchor repair

Root read/replayed producer and independent v2 source/performance gates. The
formatted candidate matches the frozen optimized source exactly. Format64767
exits0; twelve unrelated changes were restored before build26044 (exit0). Paired
WPT86724 exits0:38newPASS,11existingPASS,3reftestPASS,22improvements versus the
original. Boundary87668 exits0:22cases88observations exactly match the earlier
correctness-passing candidate, including the four separate B failures. The
three-file patch applies at original base and HEAD. Formal companion and final
independent native binding remain open.

Root also read/replayed both scroll designs (19files,sixorigins). The fixed-child
WPT baseline94273 has one expectedFAIL,four newcontrolPASS and three existingPASS.
The isolated native exclusion is applied; formatting/build/paired gates follow.
Own-scroller endpoint suppression remains a separate pending repair.

### Nesting root formal replay and fixed-anchor paired gates

Optimized nesting final independent native/WPT review is root-read/replayed and
accepted. Producer87069/root91589 formal replays exit0 with identical receipt:29
Lean theorems,133typed model/native comparisons,145actual native cases per variant,
10native and6Lean semantic mutants. All18complete native source bindings match.
Independent formal review follows the display survey; source-only packaging
closure is being made explicit in a versioned addendum. Native integer/provider
premises and separate defect B remain outside the acceptance claim.

Fixed-anchor build17708/paired41566 exit0:5new+3existing subtests pass. Original
13-case probe rerun25742 exits0 with159stablepins;only fixed-transformed changes,
all11controls and the separate suppression failure retain exact observations.
Two-file patch applies at originalbase/HEAD. Format76021exit0;lint12686exit1 with
zeroerrors/oneignoredwarning. Root read/replayed the complete traversal formal
scope; implementation is assigned, independent native review queued.

Round16 motion-path report is root-read and its live checker passes (114frozen
files,93liveorigins). First probe:literalpolygon with zero-area reference box.
Second:contained square/cardinal ray percentage-basis ordering. Boundary-origin
sides rays remain behind an explicit spec/WPT conflict;open shape wrapping is
also deferred for conflicting clauses. No browser finding accepted from survey.

### Round16 first runtime lead and source packaging

Root read/replayed the display survey (64files,45origin snapshots), prioritizing
generated-grid literal whitespace for a browser gate. Motion-reference run54822
exits0:72cases288observations,18candidate cases show wrong polygon displacement,
54controls pass;99pinsstable. Reference-size/support/initial/restored/fresh gates
pass across three writing modes and both directions. Independent normative/native
review is required before adding this as an accepted defect. Partial synthesis:
css-breadth-audit-round16-v1/REPORT-partial-v1.md.

Nesting source-only package closure passes:41paths include all39replay inputs,
the replay manifest and a dedicated entrypoint, with all18native source bindings.
Historical proof/performance evidence stays separate. Independent formal review
is active; fixed-anchor formal production is active and native review queued.

Configured signing retry36232 exits128 with the same1Password buffer error. HEAD
and all12staged companion files are unchanged;signing remains enabled. No commit
or push occurred. Evidence:css-scroll-fixed-anchor-fix-v1/SIGNING-RESULT-v1.json.

### Optimized nesting repair fully accepted

Root read and replayed the final independent formal review:160frozen files and
18live source bindings authenticate. Producer87069,root91589 and independent96570
exit0 with byte-identical receipt7863647d. The29producer Lean theorems,133typed
comparisons,145native cases per variant and10native/6Lean semantic controls pass.
Root also replayed the independent bounded packed/lexicographic maximum lemma
as63951exit0. Provider/representability premises and defectB remain explicit.

Native/WPT/performance and scoped formal gates are complete. Final packaging has
three fix files and43preceding tooling/guidance files; allfix hashes match paired
WPT inputs. This is the twenty-second fully accepted repair pending configured
signing. Final evidence:css-nesting-specificity-fix-v1/verification-final-v1.json.

Next priorities:finish fixed-anchor native review and formal companion; complete
text-overflow survey review; independently adjudicate the motion-path runtime
finding and run the generated-grid whitespace gate. NestingB,scroll endpoint,
ruby and bidi repairs remain separate queued work.

### Round16 surveys complete and runtime gates expanded

All three static reports are root-read and integrity-replayed. Full synthesis:
`css-breadth-audit-round16-v1/REPORT-v1.md`. Independent motion review is
root-accepted: 72 cases/288 observations confirm the literal polygon discrepancy
for zero-area reference boxes, with 54 passing controls. Main/compositor absent
reference transport remains an explicit repair gate.

Generated-grid run61512 exits0 with 12 failing candidates, 36 passing controls,
192 observations and 45 stable pins. Deferred counter/quote initialization must
remain valid in any normalization repair; independent review is active.

Text-overflow run22747 exits0 with two 13-row captures: three defect families
reproduce in four candidate rows; eight pre-control-reflow and nine final
controls pass. All reference pixels match exactly. Test glyph-edge mixtures use
a bounded neighboring-color rule; no pixels are omitted. The earlier strict
run59089 is retained as rejected control evidence. Independent raw-image review
is active. Native/WPT source has not changed for these new leads.

Fixed-anchor native/WPT independent review passes root replay. Its producer
formal preflight covers 4,929 cases and 48 theorems; final semantic mutation
evidence, root replay and independent review remain required. Root requested
executable counterexamples for six Lean mutations, separately from their proof
compilation failures. Do not count diagnostic assertions as semantic passes.

Next: finish fixed-anchor acceptance, then text-overflow line-state repair and
its extracted transition model. Keep vertical clipping and float-cache fixes
independent; motion and generated-grid repairs retain their provider/lifecycle
gates. Original Bloom milestones remain complete within their stated bounds.

### Round16 reviews accepted; next static target active

Generated-grid and all three text-overflow discrepancies now pass independent
defect review and root replay. Together with motion-path geometry, round16 has
five accepted defect families, still requiring separate native/WPT repairs and
proof companions. Final synthesis: css-breadth-audit-round16-v1/REPORT-v2.md.
Text-overflow line-state repair design is assigned in
css-text-overflow-line-state-design-v1/native-proposal-v1/. Root scope avoids
changing retry-time Reset behavior and explicitly audits clamp boundary paths.

Fixed-anchor root69253 full replay matches producer67512 byte-for-byte. Its
48 theorems, 4,929 native/model cases, 12 native mutants and six executable Lean
mutation witnesses pass; independent formal review is active. Root record:
css-scroll-fixed-anchor-fix-v1/ROOT-FORMAL-REPLAY-v1.json.

One freed worker continues breadth analysis of CSS Fonts face selection by
width/style/oblique angle/weight, including variable ranges. This is separate
from font metrics and shaping. Static scalar-score priority inversions are an
early lead only; no browser defect is accepted. Scope and ownership:
css-breadth-audit-round17-v1/PLAN.md. The other two workers handle fixed-anchor
formal review and text-overflow repair design.


### Eighteenth breadth survey scheduled

The user requested additional static specification/implementation scouts.
Whitespace/segment-break partition behavior starts after the current WPT review;
scroll/view timeline geometry follows fixed-anchor v2 production; anchor
positioning follows text-overflow line-state proof production. Each must report
negative coverage, supported-feature boundaries, concrete browser gates and
separate formal contracts. Assignments: css-breadth-audit-round18-v1/PLAN.md.
The three-worker limit is respected; existing proof work is preserved.

Fixed-anchor v1 remains partial: its original scope requires an independent
native-shaped Lean traversal and universal rich-trace agreement. The v2
extension is active; v1 bounded replay is not final acceptance. Revised
text-overflow WPT baseline40359 exits1: static/growth/restoration fail, shrink
passes, and ten existing outcomes are unchanged. Independent pixel review finds
3600 differing pixels on each failing page, including true start-side cases.
Native line-state candidate application and paired build/WPT remain pending.


### Text-overflow line-state candidate passes paired WPT

The exact two-assignment candidate is applied. Format26636 exits0; twelve
unrelated formatter changes were restored before build98859 (exit0). Paired
WPT99160 exits0: static/growth/restoration improve FAIL→PASS, shrink remains
PASS, and all ten existing outcomes are unchanged. Forty-one pins stay stable
per run; only TextOverflow.cpp and the two binaries change between runs.
The six-file Gecko/WPT patch applies at original base and HEAD. Lint12590 has
zero errors and five ignored-WPT warnings. Root record:
css-text-overflow-line-state-fix-v1/ROOT-WPT-REVIEW-v1.json.

Boundary31743 exits0 with61stablepins. Only the A test crops change; all24other
crops and all26references retain identical pixels. The original400wrong pixels
become one rejected corner pixel plus40allowed edge mixtures. This is NOT a
full rectangle-oracle pass. Strict same-glyph WPT references pass without fuzzy
metadata; independent native review must adjudicate the remaining corner pixel.
ROOT-BOUNDARY-REVIEW-v1.json preserves the limitation. The ordinary-line formal
producer is active; no final repair acceptance yet.

### Font-selection runtime leads reproduced

Round17 report is root-read and integrity-replayed (112files,54origins).
Browser4139 exits0:28cases,16predicted candidate discrepancies,12passingcontrols,
112loadedfaces,80/40calibrations,matchingfreshwidths and55stablepins. Root checker
also validates every parsed descriptor, declaration order and computed request.
This supports two preliminary families: scalar score priority inversion and
oblique search threshold. Independent defect review remains required; no native
font change or new accepted bug count. Evidence:
css-breadth-probes-round17-v1/ROOT-FONT-RESULTS-v1.json.

Configured signing retry41015 exits128 with the same1Password buffer error.
HEAD and all12staged RGB companion paths remain unchanged; signing stays enabled.
The accepted pending repair count remains22. This does not block further local
verification work. No shared root build/browser process remains active.


### Round18 runtime evidence and formal replay checkpoint

Three static assignments are active or delivered: whitespace and segment breaks,
scroll/view timeline geometry, and anchor positioning. Whitespace is frozen and
root-reviewed. Timeline and anchor scouts are checking current spec resolutions,
implementation and existing WPT before proposing browser gates. The timeline
scout rejected the no-overflow ViewTimeline lead after checking CSSWG issue 13988;
orthogonal pseudo-element scroller axes remain an unexecuted hypothesis.

Whitespace browser run27156 collected all141 observations and exited1 because two
ASCII pre-line partition controls unexpectedly failed. Preserve those failures.
The tab subgroup has18 zero-size intrinsic discrepancies, two zero-font exact-stop
discrepancies, four tiny-tab policy-sensitive observations and15 passing controls.
The tiny-tab interpretation remains unsettled; partition extensions overlap the
previously accepted whitespace family. No new defect is accepted from this run.
Evidence: css-breadth-probes-round18-v1/ROOT-WHITESPACE-RESULTS-v1.json.

Fixed-anchor v2 root replay23530 exits0 with a byte-identical producer summary:
48 inherited and37 new theorem audits,4170 classifier rows and766 traversal
rows per native variant. Only the766 graph rows exercise four independent
spec/native traversal outcomes; classifier rows must not be counted as additional
traversal comparisons. A clean source-only copy verifies. Independent review is
active; v1 remains historical partial evidence.

Text-overflow explicit glyph reference v2 matches all4000 pixels in both phases
(run47927 exit0). It independently reproduces the corner mixture rejected by the
older rectangle oracle; that older result remains recorded. Native/WPT independent
review and the484-file pre-import closure replay3658 pass. Formal root replay2756
exits0 and matches producer receipt f2af5871:138 cases,776 rows per native variant,
1552 Lean rows,20 theorem audits, seven native semantic mutants and four executed
Lean mutation counterexamples. The finite-sequence theorem is definitional
normalization with the same seeded cache, not universal native refinement.
Independent formal review and final source packaging remain required.

There are still16 committed fixes and22 fully accepted repairs pending signing.
No native changes, builds, commits or signing retries were made in this checkpoint.
Next: finish the two independent formal gates, adjudicate the font/tab leads,
and run the timeline scout's concrete browser witness after its handoff.


### Fixed-anchor repair fully accepted

Independent v2 formal replay91017 and root checker both pass, matching producer
and root full replay summary0471241f. Root read the complete independent report,
raw-wire oracle and verifiers. The required independent interpreter milestone is
satisfied:37 new and48 inherited theorem audits,766 traversal graphs and4170
separate classifier inputs, with complete semantic trace comparison. Frame
construction, geometry, ownership and stable provider assumptions remain explicit;
this is not universal C++ refinement.

Final acceptance: css-scroll-fixed-anchor-fix-v1/verification-final-v2.json.
The39-file source-only companion precedes the standalone two-file native/WPT
patch. All current patch bytes still match the paired browser inputs. This is
the twenty-third fully accepted repair awaiting configured signing; no new
commit hash exists. Text-overflow formal independent review is now active.


### Text-overflow ordinary line-state repair fully accepted

Independent formal replay47771, root2756 and a fresh source-only replay16102 all
exit0 with identical receipt f2af5871. Root read and replayed the independent
raw-input oracle and verifier. The20 theorem audits and bounded native/model
comparison are accepted within the explicitly limited entry/cache scope; the
finite sequence theorem is definitional normalization, not C++ refinement.

Final acceptance: css-text-overflow-line-state-fix-v1/verification-final-v1.json.
The21-file source-only companion precedes the six-file native/WPT patch. This is
the twenty-fourth fully accepted repair pending configured signing. The original
rectangle residual remains documented alongside exact same-glyph references.

Round18 timeline run12247 reproduces two logical-axis errors on an orthogonal
pseudo scroller, with all six controls passing and39 stable inputs. Independent
review is queued after the anchor scout. Zero-tab WPT baseline56364 has126 FAIL
and18 PASS across144 subtests; thirteen existing reftests pass and one expected
failure remains. The zero-tab candidate is not yet applied. Independent tab
review is active. Signing retry86680 fails with the same1Password buffer error;
HEAD and twelve staged companion files are unchanged.


## Round 19 static expansion — 18 October 2026

At the user's request, two new scouts are active:

- `css_filter_effects_static`: filter lists, SVG primitives, color-space and
  backend boundaries; exclude the accepted empty-mask composition repairs.
- `css_scroll_into_view_static`: logical alignment and coordinate conversion
  through nested scrollers; distinguish existing snap/anchoring/timeline leads.

Assignment and evidence requirements are in
`artifacts/css-breadth-audit-round19-v1/ASSIGNMENTS.md`. Each scout must rank
concrete testable hypotheses and useful proof contracts, identify existing WPT
and known issues, and record negative findings. Neither audit is a conformance
claim. The third worker continues the zero-tab intrinsic caller proof.

The zero-tab candidate has passed its paired 144-subtest WPT and the original
141-observation boundary replay: exactly 20 intended row changes, with the two
existing ASCII partition failed controls preserved. Root authenticated the
54 stable boundary inputs in `css-tab-zero-intrinsic-fix-v1/ROOT-BOUNDARY-REVIEW-v1.json`.
Independent native/WPT review is delivered but awaits root replay; formal work
is still running, so the accepted pending-repair count remains 24.

Font repair designs and timeline independent review are delivered for root
review. The anchor probe completed all 30 observations but exited 1: 12
selection-candidate discrepancies and four unexpected changed-phase controls.
`css-breadth-probes-round18-v1/ROOT-ANCHOR-RESULTS-v1.json` preserves that failure;
timing versus invalidation remains unresolved.


### Round19 execution checkpoint

Both static scouts completed and passed root live replay. The scrolling scout's
first 22-observation local browser probe reproduced eight center/margin/padding
discrepancies, with14 controls and33 stable inputs. This remains a preliminary
finding pending independent normative/native review and known-bug adjudication:
`css-breadth-probes-round19-v1/ROOT-SCROLL-CENTER-RESULTS-v1.json`.
The filter discrete-transfer boundary hypothesis is still unexecuted; it needs
separate software and compositor observations. Root read both complete reports.

The pseudo-timeline axis repair is now a three-file standalone patch that applies
at original base and HEAD. Its exact40case WPT paired cycle78913 passed:
16FAIL becomePASS;24existing subtests and1reftest pass, and1existing expectedFAIL
is unchanged. Both builds exit0; formatting is complete and lint has0errors with
one ignored-WPTwarning. Root receipt: `css-timeline-pseudo-axis-fix-v1/ROOT-WPT-REVIEW-v2.json`.
The four recreation-opacity failures remain in a separate executable44case
diagnostic. They are not bundled into this repair. Orthogonal-root provider
controls, independent native review and formal acceptance remain required.
The viewport oracle must account for HTML body's used-writing-mode propagation;
`ROOT-BOUNDARY-PLAN-v1.md` records that prerequisite.

Root accepted both separate font implementation designs after full read and
replay. Worker assignments now are zero-tab full caller proof, timeline
source-resolution/cache proof under the approved complete plan, and font
threshold proof plus reusable complete font consumer extraction. Producer
progress is not final proof acceptance. No font candidate is applied live.

Signing retry46762 exits128 with the same1Password buffer error. HEAD and the
original12 staged RGB companion files remain unchanged. Sixteen commits and
24fully accepted pending repairs remain the authoritative counts. There is no
whole-project blocker: browser, proof and repair work continues.


### Round20 static expansion dispatched

At the user’s request, CSS zoom and DOM geometry has a new active scout.
Multicolumn spanner construction/updates and list marker boxes/updates are
assigned to follow the complete timeline and font proof handoffs respectively.
This targets gaps in earlier surveys while preserving current proof scopes and
the three-worker limit. Assignments and evidence requirements:
`css-breadth-audit-round20-v1/PLAN.md`. No new bug is claimed by dispatch.

Timeline root boundary v2 run80574 exits0: eight genuine standards/quirks
fixtures and128time observations pass. Original/candidate root pairing remains
required; v1’s srcdoc setup failure is retained. Zero-tab independent formal
replay matches the producer, but review requires four corrections: pre-import
authentication, negative intrinsic inputs, defined saturation branch inputs,
and explicit formal applicability premises. V1 is not formally accepted.
Sixteen committed fixes and24fully accepted pending repairs remain unchanged.
