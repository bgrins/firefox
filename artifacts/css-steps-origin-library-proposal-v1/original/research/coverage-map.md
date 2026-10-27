# Accepted CSS coverage map

Current bounded ordinary-import/raw-scope composition: main, independent clean-source fresh and producer-bound native gates accepted at **11,564 named declarations, 12,172 ordered executable observations and 2,099 source hashes**, with both proof rejection controls. Its committed archive gate remains pending at this documentation freeze. Owner-derived checkpoint `7657c7a8a117132b327c528153d822d0dfb86c1d` is the preceding fully archived source. Current finite native evidence is **20/20**, 240 metadata readbacks and 15 controls on the cloned signed-zero local build; prior discrepancy outcomes remain unchanged. [ARTIFACT.md](../ARTIFACT.md) is the reproduction entry point. Counts are artifact inventories, not specification requirements or a percentage of CSS; historical families overlap and must not be summed.

The [current specification inventory](current-spec-inventory.md) supplies the
primary-source landscape. [coverage.json](../coverage.json) maps individual
checked fragments to modules, theorem names and exact limits. The sections below
summarize current capabilities rather than repeating historical exclusions.

## What the evidence establishes

| Evidence | Established claim | Remaining boundary |
| --- | --- | --- |
| Independent declarative relations and executable correspondence | All inputs satisfying the stated model/profile obey the checked relation; termination/progress and source boundaries are explicit | The mapping from normative prose to the relation is manually reviewed, not mechanically proved |
| Semantic laws, refinement and canonical construction | Universal matching/weight/provenance properties; older accepted parses keep exact outputs; canonical sources roundtrip within explicit domains | Semantic equivalence does not imply identical raw source, diagnostics, CSSOM serialization or complete host behavior |
| Kernel-checked finite examples | Exact listed model results, including rejection/diagnostic distinctions | Examples do not prove requirements beyond their stated input set |
| Same-source Firefox comparisons and negative controls | The report records exact agreement and disagreement for the supplied sources, snapshots and host profiles; harness perturbations expose selected mistakes | No general Firefox/Stylo refinement, WPT conformance claim or all-engine guarantee |
| Fresh source-only and committed-archive reproduction | The accepted source/declaration/case/control vectors reproduce independently | Reproduction does not repair an incorrect interpretation of the specification |

## Current algorithm and semantics families

| Family | Universally checked fragment | Browser evidence | Major remaining work |
| --- | --- | --- | --- |
| Ordinary imports with raw scopes | Actual root/resource parsing, per-sheet placement, rich registration views, exact selected-instance source and ownerless child provenance; all-assignment specificity/proximity, origin-specific registry identity and exact source/cascade histories. | [Import-scope evidence](import-scope-browser-evidence.json): 20/20, 240 metadata observations, 15 controls; saved native inputs are distinct from universal model laws. | Imported/ownerless omitted scopes, scoped-import modifiers, nested imports, general Fetch/lifecycle and dynamic invalidation. No-import compatibility is source parsing only, not whole-host equivalence. |
| Static inline owner-derived implicit scope | Actual HTML style inventory in document preorder; same-context text/parent acquisition; complete omitted-start source; all-assignment availability and source/candidate/rollback histories. Incompatible owner/outer configurations are explicitly unavailable, including empty blocks. | [Owner-scope evidence](owner-scope-browser-evidence.json): 20/20, 240 metadata readbacks, 15 controls; generic model laws are separate from these finite observations. | Ambiguous above-outer interpretation; imports, shadow/tree-root fallback, linked/adopted sheets, dynamic owner changes, full HTML/CSP lifecycle and general browser refinement. Explicit-rule compatibility requires its exact-image premise. |
| CSS scalar input and tokenization | Preprocessing, dated name classes, escapes, hash flags, ident/function/URL dispatch, string and bad-URL recovery, comments, numeric/percentage/dimension tokens, guarded Unicode ranges, complete priority dispatch, finite token stream and exact original scalar/token provenance | Later selector-source suites exercise selected paths indirectly; tokenizer-only checkpoints did not claim native comparison | Byte/encoding input; full token serialization; browser numeric precision/range equivalence |
| Component syntax | Recursive block/function grouping, public component lists, single-component and comma-list entries; exact suffix/EOF/error policies, totality, canonical token construction, component-invocation source intervals and body-closure provenance | Source-selector suites exercise grouping; no independent general CSS parser refinement | Stylesheet objects/public single-rule seam, concrete property grammar dispatch and contextual rule instances |
| Declaration and recursive rule consumption | Prefix/recovery/priority and partial ordinary/list entries; independent recursive at-rule/qualified-rule/block relations, executable correspondence, proved input-derived fuel, NoEOF totality, mark/restore, exact emitted structure and explicit terminal-flush policies; generic stylesheet exhaustion and emitted-history contexts | No native claim; exact token/source cases and synthetic context-interface checks | Stylesheet objects/public single-rule seam; broader property/context/source instances beyond strict visibility; sibling-sensitive block context; declaration original-value intervals |
| DOM observations and normalized selectors | Finite coherent ordered forest; four combinators; logic; attributes; ranks/An+B; typed sibling filters; root/versioned-empty; relative paths; caller scope and ordered queries | Explicit fixed DOM snapshots, matches/closest/query ordering, detached and fragment examples | General DOM/shadow adapters, dynamic UI/language states, pseudo-elements, column/table semantics, multiple-ID host models |
| Full-component selector source | Decoded token adapters; atomic attributes; four indexed families; recursive not/of/is/where/has; retained-tree nesting restrictions; exact specificity and old-success preservation | Latest recursive recovery suites compare exact raw selectors, including recovery and named SyntaxErrors | Full selector validity; unsupported valid pseudo-classes; namespace environments; general forgiving recovery |
| Forgiving recovery | Global recursive any-value gate; exact direct-comma partition; independently certified empty, numeric and six additional forbidden-head families; all retained branches completely parsed | [Forbidden recovery](forbidden-recovery-browser-evidence.json): 46 selectors, six styles and 46 regression cases | Unknown inputs remain unsupported; nesting ampersands are preserved as unknown; broader invalidity/CSSOM preservation requires separate contracts |
| Document-language type semantics | Independent four-form any/null namespace type heads; HTML-in-HTML selector-name folding, foreign/null/XML original-name comparison; source and canonical roundtrips | [Explicit type heads](explicit-type-head-browser-evidence.json): 46 HTML + 46 XML cases, plus 46 prior all-HTML regressions | Named/default namespace environments and real host acquisition; preserved-name mixed-host recursive profiles now have separate explicit checked entry points |
| Host-aware compounds | Complete nonempty type/universal + unqualified-attribute and concrete DOM ID/class source grammar, exact document/mode/subject semantics, actual stored-name acquisition/provenance and qualified old-profile compatibility | [Host compound evidence](host-compound-browser-evidence.json): 45 HTML + 45 XML cases and five controls each | Namespace environments, real DOM/topology authentication and the inherited comment-separated operator interpretation gap; limited quirks remains model-only |
| Cascade/defaulting/inheritance | Closed precedence selection/defaulting/inheritance; matching-branch specificity; named custom cascade and source-derived author stylesheet/attached layer rollback with exact ordered winner histories; resolved scope regions, parent-hop proximity, nested applicability, weak ordering and exact unscoped embeddings | [Scope comparison](scope-cascade-browser-evidence.json): 29 queries/22 raw stylesheets plus 42 ordinary regressions; prior rendered visibility suites | Raw scope resolution/selector interpretation, shadow/encapsulation; general origin/context rollback; broader element-sensitive conditions, import/Fetch/dynamic-sheet composition and substituted rollback; animations/transitions; shorthands/aliases; presentation hints |
| Custom properties and substitution | Variables1 static cycles, rank-based solver and inherited environments; separately versioned Variables2/Values5 fresh-root guarded substitution; keyword completion and selected style composition | Versioned visibility/custom/layer suites; source values use a narrow separately checked keyword/var grammar | General component-token var substitution/serialization; registrations, taint, generated rollback cycles, general property grammars and other draft functions |
| Values and property computation | Exact symbolic decimal numbers with separate rational denotation; seven-dimensional type arithmetic, hint/context matching and tri-state addition; recursive calculation typing and production admission with context invariants; grouped calc source parsing, whitespace/precedence and explicit unit classification; exact finite rational signed-zero arithmetic, 18 fixed unit factors and normalized typed evaluation with subtree provenance; magnitude-preserving grouped source and exact type/evaluation correspondence with retained diagnostics; exceptional arithmetic/source evaluation preserving prior finite successes and actual subtree origins; supplied production/bounds/stage finalization and bounded number-only opacity; conditional ready percentage/unit environments preserving old successes and diagnostics; numeric-leaf/Sum residual simplification, independent ordered collection and same-environment normal forms; ready normalized comparison calls and recursive grouped function sources with exact argument grammar, preserved function boundaries, per-function numeric-category admission and conditional old semantic compatibility; local Product/Invert structural phases and canonical factor readiness; concrete typed child transport, faithful eligibility on coherent prepared inputs and guarded stable-child source admission; recursive typed child normalization with exact completed type/hint retention, totality and actual boundary provenance; bounded group-preserving source construction with direct-run shape proofs, explicit nested/outer normalization calls and actual entered-call boundary provenance; local residual Min/Max/Clamp phases with canonical readiness, exact type/hint transport and opaque-child retention; bounded visibility keyword/CSS-wide/var pipeline | Rendered visibility outcomes; 26 exact opacity calculations with declaration-admission/source-wrapper controls, plus 29 scoped visibility regressions; no general precision equivalence | Broader math functions and substitution; irrational conversion, broader residual operators/source history and concrete property/font/viewport acquisition beyond opacity; numeric color conversion and full color evaluation; layout/font/text/animation families |
| Supplied finite Round scalars | Four traditional strategies, exact multiples and signed zeros, adjacent rational bounds and general toward-zero absolute selection | Seven supplied finite observer cases plus one separate infinite-step control; no browser refinement | line-width, omitted defaults, units/types, parser, nonfinite Round and machine precision remain excluded |
| Relative-color component observations | Supplied conversion and original missing-channel carry; distinct bare-keyword and calculation substitution; component-level deferred acquisition and a generic math-environment bridge | Six synthetic executable controls; no native or browser refinement claim | Numeric conversion, IEEE/threshold behavior, full color validity/readiness, concrete origin acquisition, CSS expression integration, parsing and serialization |
| Whole source-to-style composition | Strict whole source, preserved-name host selectors and visibility inheritance on one forest; actual nested/dotted named and anonymous layer identities, complete-source IDs and document-global media/support activation, final ranks and source/candidate/winner histories; bounded source-derived import graphs, load/condition distinctions and actual instance identity; direct source rollback, ordered static inline author roots with shared identity/registry/order, actual owner-bound attribute source/direct candidates and same-forest mixed-attachment trace/defaulting; source-derived container-name metadata and name-only ancestor guards with subject-independent registration; accepted-domain engine simulation under appendPending | [Global condition evidence](global-condition-browser-evidence.json) binds raw sheets, recursive effective CSSOM/condition truth, actual screen medium, mixed-namespace snapshots and finite computed results | General contextual recovery, broader properties/mixed-property irrelevance, conditional metadata/container features, general conditions, full import placement/Fetch/dynamic or external top-level sheet acquisition, broader rollback and raw scope |

The current scalar/component tokenizer is broader than the older closed value
parser. Its existence does **not** mean `var()` accepts arbitrary component tokens
in the property pipeline. The normalized scope package now supplies applicability/proximity separately
from DOM `:scope` matching, but accepts already-resolved records and interpreted
selectors; it does not provide a general raw `@scope` source pipeline. Direct author `revert-layer` is **not**
a combined general origin/layer/generated rollback model.

The supplied-environment evaluator operates on the original parsed tree. It does
not establish equivalence to CSS eager simplification followed by later stage
resolution. Its paired percentage-ratio cases expose a zero-basis history boundary;
missing measurements produce unavailable results rather than symbolic computed
values. No new native evidence accompanies that conditional model. The additive residual
profile separately preserves unavailable units and percentages, simplifies children
before parent collection, and proves valid normal forms and same-environment
idempotence. Structural validity is not CSS typing. Different-environment history
and general binary-source conversion remain explicit boundaries. The local
Product/Invert package separately checks structural phases and a canonical-only
readiness domain. The typed residual package adds actual child inference,
flatten/collection/distribution type transport and a faithful complete eligibility
instance on its coherent prepared domain, preserving original types and hints.
Reached unavailable conversion remains an interpretation boundary. Public source
admission checks already-stable children; pending Sum/Product simplification and
noncanonical unit normalization are excluded. Binary-AST lowering does not
reconstruct source grouping and flat operator-run history. The separate recursive
typed normalizer now completes children before mixed Sum/Invert/Product phases,
retains actual type/hint metadata and stops at reached child interpretation
boundaries. Distribution returns directly without a normalization restart.
This normalized-tree algorithm does not extend the source profile or prove
general fixed points or direct-evaluator value equivalence.

## Modules without a semantic implementation

Current primary versions must be selected from the inventory before each new
package. No broad claim is made for these areas:

- Conditional rules, supports/media/container evaluation and query environments.
- Raw scoped-rule root/limit resolution and selector interpretation; nesting
  normalization; shadow/featureless element matching and pseudo-elements.
- General Values4/5 source math and exact source history and real property/unit environment acquisition; registered custom properties and the
  associated typed value/cycle/animation interactions.
- Layout, intrinsic sizing, flex/grid/table algorithms, fragmentation, text
  shaping/fonts, painting/compositing, numeric color conversion and full color
  evaluation, transforms and animation timing. The limited relative-color
  component observation model above does not implement those broader areas.
- Selectors5 draft additions, including class-prefix matching, except research.
- CSSOM object construction/serialization and general browser implementation
  refinement.

## Preserved discrepancies and domain exclusions

Comment-separated attribute operators remain a visible cross-engine/spec
interpretation discrepancy, with failing same-source evidence retained separately
in [the attribute bundle](component-attribute-browser-evidence.json). They are not
silently counted as passing required browser cases. Draft empty-element behavior
and unsupported forgiving constructs are separately labeled observations.

Scalar input excludes unpaired UTF-16 surrogate/code-unit behavior. Mathematical
numbers retain exact values and sign/type identity without asserting native
floating-point/clamping equivalence. Complete finite-domain and sibling-coherence
assumptions remain part of the DOM model. Stylesheet fixtures use closed selector
preludes and explicit separated fields; broad EOF recovery does not erase that
input boundary.

## Prioritization criteria

The next package should add a substantial algorithm or semantics family, reuse
existing verified inputs, and close an important composition boundary. Further
small selector rejection families are deferred unless a concrete dependency
requires them. Compare candidates by:

1. An independently reviewable normative algorithm and a precise input/output
   contract, including errors and unsupported contexts.
2. Universal properties beyond a larger fixture corpus.
3. A useful connection to the existing tokenizer, cascade or value pipeline.
4. Versioned primary-source stability and explicit unresolved CSSWG decisions.
5. Distinguishing native evidence where meaningful, without equating samples
   with formal coverage.

The next-package decision is recorded in the refreshed [ROADMAP](../ROADMAP.md):
recursive typed child normalization and a bounded group-preserving source
constructor now compose the local phases with actual nested and outer calls.
Group-preserving comparison source construction and changing-environment stage/history
transport remain next substantive boundaries; the earlier binary AST still does not encode this
source history. Canonical readiness does not settle unresolved unit
conversion; Negate, broader comparison readiness and concrete property/layout acquisition
remain independent duties. Isolated host-attribute prerequisites are not accepted
coverage.

## Local comparison phase boundary

Canonical full selection and partial Min/Max grouping preserve actual original
type/hint folds and opaque-child order; Clamp has no partial rewrite. Unknown
noncanonical numeric readiness yields an explicit interpretation boundary. The
local Call interface assumes earlier child completion rather than proving it;
15 finite caller controls supply completed arithmetic-source constructions. This
does not extend recursive comparison normalization or comparison-source grammar.
The 79 new audit names and 86 cases measure this artifact, not specification
coverage. No browser evidence or future-environment value equivalence is added.


## Recursive comparison normalization

The separate enriched Tree now retains comparison calls under arithmetic and
normalizes actual children before local phases. Checked reconstruction preserves
comparison arity and optional endpoint positions. Supported coherent inputs keep
their exact type and hint or stop at an explicit Product/comparison interpretation
boundary; provenance distinguishes original subtree paths from completed child
payloads. Exact arbitrary-old-tree refinement preserves the previous normalizer's
entire optional outcome. The local phase's caller duty is discharged by this
recursive invocation relation, without extending source construction. The 287
additional audits and 74 cases measure artifacts, not specification requirements.
No new browser, general fixed-point or future-environment equivalence claim is made.


## Group-preserving comparison construction

Comparison source Plans now preserve direct arithmetic runs, group/calc boundaries,
complete argument chunks and optional clamp endpoints. Independent construction
relations record actual nested argument calls and the named-root/enclosing
normalizer schedule. Completion retains original type/hints; call-path and source
origin proofs identify the actual selected Plan, local assembled tree and decoded
literal descendants. Exact arithmetic-only syntax and constructor outcome
refinement preserve the earlier profile. Environment stage faithfulness and
changing-stage history remain external; this is no general future-value,
subtraction/Negate or native equivalence claim. The invocation trace counts
constructor-initiated calls only, not all recursive normalization calls.


## Staged retained-tree continuation

The source facade now seeds only actual completed construction and retains its
complete attempted source and invocation evidence. A checked request chain uses
actual prior residual trees, preserves original type/hints and already successful
environment resolutions, and stops before later requests on order, knowledge or
interpretation boundaries. Exact prefixes and local residual-subtree provenance
are proved. Pending resolution can change; arbitrary restyling is not increasing
knowledge. The terminal observer is stage-neutral, canonical, production-checked
and pre-censorship. Source controls distinguish continuation from reconstruction
with later information. Stage/environment faithfulness and concrete property
finalization remain separate, with no new native evidence.


## Finalization of actual staged results

Accepted after main and independent clean reproduction: 11 modules / 46 laws /
72 cases, aggregate 5,507 / 7,986 / 918. Committed archive reproduction precedes
next implementation.

A ready-context adapter now observes the actual canonical terminal leaf without
changing source, construction or stage history. Successful results retain coherent
source type/hints, actual computed/used readiness, checked environment extension,
production admission and outer censorship/clipping/rounding evidence. A concrete
number-opacity instance proves its actual computed frame and [0,1] result.
Canonical computed-to-used stability requires a successful guarded transition.
This does not add percentage opacity, source reconstruction, arbitrary restyling,
serialization, declaration admission or new browser equivalence evidence.

## Accepted strict visibility source bridge

Independent source/corpus review and main/clean-source reproduction passed for
24 modules, 106 laws and 96 cases. Committed-archive reproduction remains the gate
before next implementation. Actual qualified-prelude/declaration consumers feed decoded
selector/value admission, exact author declaration order and important flags,
maximal matching specificity, cascade/defaulting and inheritance. Every reached
accepted decision agrees with the generic engine under explicit appendPending.
Unsupported content retains the actual attempt and prevents a computed result;
there is no general recovery or mixed-property irrelevance theorem. Display4
force-hidden, rollback/custom properties, at-rules/nesting, raw scope/layers,
mixed-namespace host integration and layout/paint semantics remain outside this
profile. No native evidence is added.

## Host-aware compound acceptance

Main and independent source-only gates passed at 5,695 audits / 8,262 cases /
957 hashes. Firefox 160.0a1 build 20261016094257 agreed on 45 HTML and 45 XML
same-source cases, with all five snapshot/host controls in each suite. Exact
reports and source bindings are retained in
[the native evidence](host-compound-browser-evidence.json).
Committed-archive reproduction remains required before the next implementation.

The inherited comment-separated attribute-operator model/browser discrepancy is
an explicit admitted-source gap, excluded from the required native profile and
retained as a model-only case. No demonstrated regression, browser-defect verdict
or external CSSWG adjudication is asserted. See the [current disposition](attribute-operator-comment-disposition-20261017.md).
Recursive host-aware selectors, DOM identity acquisition, quirks ID/class behavior
and namespace environments remain separate duties. The next selected slice is
concrete DOM ID/class acquisition and explicit document modes, after archive
acceptance; future research is kept separate from this checkpoint.

## DOM identity compound accepted checkpoint

The isolated reviewed package adds actual DOM ID/class acquisition, explicit
standards/limited/quirks mode semantics, decoded compound source admission and
checked context outcomes: 16 modules, 111 laws and 196 cases. The accepted
vector is 5,806 audits / 8,458 cases / 974 hashes; main and independent clean
gates passed with both controls. Firefox Nightly passed 96 new cases and 45 shared
harness regression cases with all controls; committed archive f536c2b was
independently reproduced with exact source and result vectors.
ValidHost is not DOM authentication; limited quirks is model-only. Recursive host
selector/style composition and namespace environments remain separate priorities.

## Host selector chain accepted checkpoint

The isolated reviewed package adds preserved-name chains and lists, four
combinators, actual per-subject identity/source witnesses and conditional old HTML
refinement: 17 modules, 114 laws and 217 cases. Accepted full vector:
5,920 audits / 8,675 cases / 992 source hashes. Main and independent source-only
clean gates passed with both controls. Firefox Nightly passed all 123 cases across
HTML standards, HTML quirks and XML, with all six controls in each suite. Exact
reports and bindings are retained in the host-selector-chain browser evidence.
The committed archive gate remains pending.
Functional recursion and structural/scope semantics remain separate next work;
list-global specificity is not a matched-rule adapter. Limited quirks stays
model-only and the inherited comment/operator discrepancy remains explicit.

## Host logical recursion accepted checkpoint

The `host-logical-recursion-v1` checkpoint adds 23 modules, 190 named laws
and 220 kernel cases. Main and independent clean gates passed at
6,110 audits / 8,895 cases / 1,016 source hashes with both rejection controls.
All 123 native results and six controls per suite passed and were independently
bound to the exact producer. Committed-archive reproduction remains pending.

Actual preserved-name is/where/not nodes now compose with host chains, exact
node-specific identity acquisition and source component provenance. Independent
matching/specificity, old successful source lifting and positive-subject/negative
argument evidence cover the nonempty supported-all-branches domain. Unknown
branches stay unavailable, even under not. Function argument maximum specificity
is distinct from outer matching-list specificity. Complete-context checks precede
negation without authenticating the supplied DOM.

Empty functions, forgiving validity/recovery, structural/relative/scope semantics,
shadow and namespace environments, and whole mixed-host style remain separate.
Limited quirks remains model-only, and the inherited comment-separated attribute
operator source discrepancy is explicitly excluded from required native fixtures.
Three native suites each passed 41 source cases on the existing mixed-namespace
tree. Exact reports and producer bindings are retained in
`research/host-logical-browser-evidence.json`.


## Mixed-host whole-style checkpoint

The isolated host-visibility package adds actual ordinary stylesheet consumers,
preserved-name logical selectors, maximum matching outer-branch specificity and
same-forest cascade/defaulting/inheritance. Complete accepted-domain simulation
retains every reached decision under appendPending; late stops prevent partial
computation. Its 23 modules / 100 laws / 108 controls produce 6,210 / 9,003 / 1,040
integrated inventories. Main, independent fresh and native checks passed;
committed-archive reproduction remains pending. Native fixtures separately verify
CSSOM effective declarations, actual standards HTML document identity and mixed
namespace snapshots before 37 computed comparisons across 26 whole stylesheets.
Duplicate authored declaration provenance is not CSSOM serialization fidelity.
The fixed one-author-sheet/no-other-contributing-declarations premise, source and
host profile exclusions, and inherited operator-comment discrepancy remain explicit.


## Host structural source/style checkpoint

The package is independently reviewed at 53 modules / 355 laws / 418
cases. Main, independent fresh and native checks passed at 6,565 audits / 9,421
cases / 1,095 source hashes; committed-archive reproduction passed at `86d8eec`. Actual
root/ranks, supported recursive filters, all-argument specificity, successful old
source lifting and whole-source style simulation close the structural family on
the host-aware path. Exact-name same-type interpretation, topology faithfulness,
empty/forgiving/relative/scope boundaries and the inherited comment/operator gap
remain explicit. Native checks passed all 207 Boolean observations and 40 computed
queries, with document, snapshot, admission and perturbation controls.


## Host forgiving source/style checkpoint

The reviewed package has 62 modules / 440 public laws / 348 kernel cases.
Integrated main/fresh/native gates passed at inventories
7,005 / 9,769 / 1,159. Committed-archive reproduction passed at `71e7192`. Empty is/where, certified sufficient invalid-start discard,
whole-body validity and retained-only recovery-decision provenance compose through
actual strict source-to-style admission. Unknown unsupported branches remain
unavailable; not, nth-of and outer lists stay strict. Exact old successful-source
lifting preserves source objects and semantics without old-failure equality.
Native fixtures and CSSOM admission are separate finite evidence. All prior host,
forest, author-sheet and operator-comment boundaries remain explicit.


## Host relational source/style candidate

The isolated reviewed package has 63 modules / 441 public laws / 359 kernel cases. Relative selectors now retain actual initial-axis source evidence, anchored ordered paths and visited compound/subject origins. Nested logical tests use the full context rather than an implicit anchor-subtree restriction. Strict has argument admission, no retained nested has, old-success preservation and exact whole-style accepted-domain simulation are explicit. Main, independent fresh and native gates passed at 7,446 / 10,128 / 1,224; committed archive `912e0f0` passed. The finite native evidence covers 150 matching cases and 36 computed queries, with actual CSSOM admission and all controls. [Bound reports](host-relational-browser-evidence.json) retain the exact producer and fixture identities. Raw cascade layers and scope, versioned :empty, complete forgiving validity and dynamic/layout correspondence remain substantial gaps.


## Accepted raw named-layer source/style checkpoint

The isolated reviewed 43-module / 240-law / 136-case package connects actual named layer statements, flat blocks, reopening and empty registration to source-derived ranks, actual declarations and normal/important winner selection. It retains full reader/restore and assignment history and rejects whole-source unsupported tails before computation. Independent main/fresh/native gates passed at 7,686 / 10,264 / 1,268; committed archive passed at `4259dfb`. The native export has 33 sheets / 42 queries with recursive CSSOM admission. Six CSS-wide layer-name exclusions have separately retained finite browser disagreement; no new bug finding or universal native equivalence is claimed. Nested/dotted/anonymous grouping, import/conditional ordering, rollback and scope remain explicit gaps.


## Accepted nested named-layer checkpoint

The independently reviewed package adds 50 modules / 270 laws / 152 cases for actual nested/dotted source, stable segment identities, source-preorder registration snapshots and final hierarchy rank resolution. Parent direct slots follow descendants; later child registration may shift numeric indices while preserving old path order. Exact flat successful-source style compatibility and recursive accepted-domain engine simulation are checked. Main, independent fresh and native gates passed at 7,956 / 10,416 / 1,319. The finite native suite passed 44 queries across 36 sheets and all nine controls; committed archive fba53c4 passed on retry after preserving the disk-full failure. Exact reports and producer binding are retained in research/nested-layer-browser-evidence.json. Anonymous/import/conditional/rollback expansion, raw scope and broader host/property/recovery duties remain open.

## Accepted anonymous-layer checkpoint

The isolated reviewed package adds 55 modules, 316 named laws and 136 kernel
controls for tagged anonymous block occurrence identities through actual whole
source, pure assignment, final ranks and visibility cascade/inheritance. Empty
blocks allocate once, named registration does not advance the counter, and
actual node uniqueness is distinct from repeated ancestor path references.
Old accepted named sources retain mapped histories and exact compiled decisions.
Main, independent fresh and native gates passed at 8,272 / 10,552 / 1,375.
The finite native suite passed 42 queries across 34 sheets and all nine controls.
Committed archive `e2ee3de` passed; exact evidence is retained in
research/anonymous-layer-browser-evidence.json.
Conditional ordering, imports/instances and rollback remain subsequent gaps.

## Accepted document-global condition source package

The independently reviewed package adds 55 modules, 277 named laws and
172 kernel controls for bounded media/support conditions through complete source,
medium-independent anonymous occurrence annotation, active layer registration and
visibility cascade/inheritance. False groups retain source/annotation while active
registrations and declarations require all enclosing conditions. Active IDs can
have source-occurrence gaps; dense declaration order preserves positional sublists.
Main and independent clean-source reproduction passed at 8,549 / 10,724 / 1,431.
Native evidence binds 38 sheets and 45 screen queries with all 12 controls, plus
42 anonymous-layer regression queries with all 9 controls. Actual conditional
CSSOM/truth readback and distinct admission/value controls passed. Print remains
model-only. Commit `13c41ee` and its independent source-only archive are accepted.
General media/support, element-sensitive conditions, imports/instances, rollback
and raw scope remain substantial separate gaps.

## Accepted import instance source package

Independent isolated review accepted 68 modules / 352 laws / 139 exact cases,
including actual-run anonymous registry uniqueness without a caller freshness
premise. The source-to-style path now has a bounded import candidate with actual
placement, supplied resolution/load outcomes, repeated-instance identity,
conditional active registration and retained source/candidate/winner history.
Integrated main and independent clean source passed at 8,901 / 10,863 / 1,504.
The final producer-bound HTTP bundle was independently authenticated; commit
`b818a9a` and its independent source-only archive are accepted.
Research HTTP observations agree on 32 of 34 queries across 31 sheets; two
false-support import-layer order disagreements remain explicit and are never
counted as model matches. Seven protocol controls passed. See
[the normative trace](import-false-supports-order-trace-20261017.md).

## Accepted source rollback package

The independently reviewed package adds 63 modules, 274 public laws and 131 exact
cases. Actual direct author/unattached `revert-layer` declarations feed ordered
candidate histories, exact executable winner steps, independently characterized
normal/important intervals, final-rank/source provenance and per-subject traces
before same-forest visibility defaulting. Successful old literal sources refine
under explicit prepared-catalog alignment; no old failure equivalence is claimed.
Main and independent clean-source gates passed at 9,175 / 10,994 / 1,569. The final
producer-bound HTTP bundle was independently authenticated: 62 sheets, 69 queries,
67 agreements and the same two explicit false-support import disagreements. All
35 added rollback queries agree in this finite run, and all eight controls pass,
including an admitted rollback-boundary mutation. Committed source-only archive
`0f1f56b` passed with all seven producer vectors and committed native evidence bound. See `research/rollback-layer-browser-evidence.json`
(root-relative path) for the exact source/report/binary binding.
Multiple ordered top-level sheets, other origins and attached styles,
element-sensitive conditions, variables/substituted rollback, broader Fetch/query
semantics, raw scope and other properties remain separate obligations.

## Accepted ordered inline author sheets package

The independently reviewed package adds 34 modules, 149 public laws and 96 exact
cases. Ordered static enabled inline roots retain separate source/import histories
and source occurrence identities, share one final layer hierarchy and global
declaration order, and feed the existing exact rollback/defaulting pipeline.
Actual anonymous registry uniqueness, root-specific source/candidate provenance,
per-root activation history and successful singleton rule equality are checked.
Main and independent clean-source verification passed at 9,324 / 11,090 / 1,608.
The producer-bound HTTP bundle was independently authenticated: 41 three-root
scenarios, 46 queries, 44 agreements and the same two explicit false-support
import disagreements. All eleven controls passed, including actual owner-order,
owner-media, shared layer ordering and rollback mutations. Each actual owner and
associated sheet is checked against the modeled forest and static eligibility
profile; delayed loading does not supply source order. Committed source-only archive
`ee116c8` passed with all seven producer vectors and exact committed evidence. See `research/author-sheets-browser-evidence.json` (root-relative
path) for exact input/report/binary binding. Attached styles, other origins,
dynamic/external sheet acquisition, element-sensitive conditions, substituted
rollback, broader Fetch/query semantics, raw scope and other properties remain
separate obligations.

## Accepted owner-bound author style attributes package

The independently reviewed package adds 30 modules, 175 public laws and 128 exact
checks. Actual owner-bound null-namespace style sources use the complete
consume(false) declaration-list entry, with strict whole-input refusal and
accepted-domain event simulation. Direct attached candidates preserve duplicate
source positions without synthetic selectors. The mixed attachment rollback
interval preserves author-important stylesheet declarations for important attached
rollback; every actual ordered step and terminal literal retains its source.
Defaulting evaluates each ancestor's own attachment on the same forest. Actual
complete acquisition rules out fallback absence and unresolved result sentinels.
Absent or admitted empty attachments preserve old successful computations.

Main and independent clean-source verification passed at 9,499 / 11,218 / 1,643.
The producer-bound HTTP evidence was independently authenticated: 72 scenarios,
80 queries, 78 agreements and the same two inherited false-support import-order
disagreements. All 14 controls passed, including invalid attribute admission and
an admitted important-attached rollback mutation. All 720 owner raw/interface/
effective-CSSOM records are separate from authored duplicate history. See
`research/attached-style-browser-evidence.json` (root-relative path). Committed
archive `7f23946c7effc9ddedf4f89facd5a6aed3d35251` was independently accepted.

Other origins, presentation attributes, animations/transitions, blocking CSP
semantics, element-sensitive groups, dynamic/external sheet acquisition,
substitutions, raw scope, other properties and broader recovery remain open.
Faithful supported host interface and no-other-contributor premises remain
explicit; namespace membership alone is not a browser-host equivalence theorem.

## Source-derived named containers: main, fresh and native accepted

The independently reviewed package adds 123 modules, 630 public laws and 437
ordered checks. Actual container-name metadata uses the shared author-sheet and
owner-attribute cascade, rollback and same-forest defaulting. Name-only guards
select nearest strict ancestors from that computed metadata; missing ancestors
remain unknown. Complete-source scope excludes metadata beneath container groups,
even under false globals. Container layer registration is subject-independent.

Rich source, annotation and positional restoration witnesses distinguish actual
headers from the synthetic registration view. Actual runs prove enrichment,
complete mixed-property lowering and anonymous uniqueness. Ordered projections
retain source positions before subject filtering; metadata guards are proved
empty. Both properties retain raw root/resource/owner, selector, guard, rollback
and defaulting provenance. Old successful attached computations refine exactly.

Main and independent source-only verification passed at 10,129 audits / 11,655
ordered cases / 1,771 source hashes, with both rejection controls. Final HTTP
protocol evidence is independently authenticated: 105 scenarios, 115 visibility
queries, 1,050 metadata readbacks and all 17 controls. Agreement is 113/115; the
two inherited false-support import-order disagreements remain explicit failures
of model agreement. See `research/named-container-browser-evidence.json`.
Commit `7ef9eceaed237cba5ba978f542fdff82e10e354c` and its independent
source-only archive verification are accepted. The archive reproduces all seven
producer vectors and all 1,771 committed, extracted and current source hashes;
its report SHA-256 is `899447178e55cfc3b5ef07154aa45baddf24b0a5b7a618a4f8c0b548c737eee6`.

Size/style/scroll features, conditional metadata, container shorthand/type,
other origins and origin rollback, broader sheet acquisition, substitutions,
layout and general recovery remain outside this fragment. Counts describe the
artifact, not a percentage of CSS or a browser/spec refinement theorem.

## Resolved baseline-group fragment

BaselineAlignment models exact rational coordinates for a finite same-flow group
with supplied baselines, resolved margins and a fitting envelope. The checked
algorithm/refinement, origin-representation invariance and recomputed relative
error law do not cover baseline-provider selection, fonts, mixed writing modes,
overflow fallback, sizing or browser implementation refinement. See the
resolved-baseline-sharing-group entry in coverage.json and the README usage note.

## Fixed-provider CSSOM hit observations

`HitObservation` models the viewport and fallback rules of CSSOM View §5
(Editor’s Draft8October2026). `ActualResult` is relational: `actualOutcomes`
enumerates admissible results, not a deterministic API response. The separate
`elementsFromPoint` observer preserves supplied paint order, literal repeated
associations and the root-tail rule. Actual-target and overlap-ignoring
eligibility are distinct fixed-state inputs. Their independent pruning
certificates preserve each observer; geometry equality alone is insufficient.

Finite rational coordinates, supplied boxes/viewport/root and faithful eligibility
are explicit assumptions. This does not define hit testing, acquire DOM/paint
providers, prove native culling, or close extreme-coordinate behavior. Seven
existing proofs (including three support lemmas) are audited once; thirteen
executable checks distinguish bounds, fallback, repetitions and lost eligibility.
See the `fixed-provider-cssom-hit-observations` entry in coverage.json.

## Preselected counter element operations

`CounterGrouping` formalizes the CSS Lists 3 element-operation fragment from
sections 4.2 and 4.4.2 (Editor's Draft 28 April 2026; checked 24 October 2026).
Repeated increments sum within an element, the last set wins, a zero net
increment preserves the remembered nonzero increment, and automatic reversed
initialization stops at the first setting element. Normalizing each element
preserves the exact-integer scan. `CounterGroupingExamples` separately houses
the deliberately faulty flattened scan and its finite counterexamples.

Inputs already select one counter identity and scope, participating boxed
elements/pseudo-elements, computed operations and their correct order. The
model does not resolve names, inheritance, containment, display:contents,
box participation, parsing, implicit list-item events or layout invalidation.
Integers are unbounded; correspondence to a finite implementation requires
its actual intermediate range and clamping policy to preserve these operations.
It is not a native implementation or prose-translation refinement theorem.

`ImplementationSupport.CounterInitializerBounds` is a separate conditional
machine-arithmetic companion: supplied contribution/count bounds imply signed 64-bit
sum/negation bounds; checked final clamping matches exact final clamping. Its
signed 32/64-bit widths and node cap are implementation assumptions, not CSS rules.
It does not prove list ownership/count agreement, contribution attribution,
source casts, sentinel safety, or an end-to-end bridge to `CounterGrouping`.
The 24 existing results are audited once; six executable grouping witnesses do
not measure whole-CSS coverage. The four machine-bound results are
not listed as CSS features in coverage.json. These modules remain independent of any native
patch's acceptance or browser campaign.

## Relative color component observations

`RelativeColorChannels` models original missing-channel carry followed by
component substitution, with source preparation/conversion and a math evaluator
supplied. It distinguishes bare missing keywords from numeric-zero math operands,
retains remaining analogous sets, and distinguishes unresolved origin acquisition
from unavailable conversion. Literal or math component progress does not establish
full relative-color validity or readiness. The generic math environment is not an
integration with the CSS expression evaluator. Numeric color conversion, IEEE
rounding, epsilon classification, parsing, serialization and native correspondence
remain outside this partial Color4/5 fragment. Synthetic faulty providers belong
to `RelativeColorChannelsExamples`, not the core semantics.

## Counter representation provenance support

`ImplementationSupport.CounterProvenance` separates authored inline integers,
resolved boxed math, omitted defaults and raw computed-value inverse lifts.
Its five existing laws characterize explicit minimum normalization, preservation
of other signed32 values, parser-domain marker exclusion, raw numeric roundtrip
and the marker observation used by serialization. Raw mapped values can still
contain the reserved minimum; numeric roundtrip neither authenticates parser
provenance nor reconstructs an expression tree.

This is implementation-specific machine/representation support, not additional
normative CSS coverage. It does not evaluate CSS math, authenticate all producers,
repair mapped-reset aliases or prove the native counter pipeline. It is separate
from `CounterGrouping` element semantics and `CounterInitializerBounds` range
premises. The five reviewed results are registered once; six executable controls
in `CounterProvenanceExamples` distinguish these source domains and a deliberately
incorrect blanket-clamp adapter. No CSS feature or spec-coverage entry is added.

## Conditional numeric implementation support

`ImplementationSupport.IntegerRoundingDyadic` retains six reviewed support laws
for the integer conversion that widens before adding one half: exact rational
encodings, bounded dyadic coefficient capacity, and floor-cell preservation
under an explicit error bound. `ImplementationSupport.RoundRemainder` retains
six reviewed laws for positive-step directed rounding: a supplied truncating
remainder yields adjacent multiples, directed extrema, global nearest selection
with upper ties, toward-zero selection and exact rational comparison transfer.
The separate Examples modules retain the original proof witnesses and add six
executable controls per module. These 12 existing results are registered once;
registration adds no research theorem credit or normative CSS feature coverage.

This is conditional implementation support, not a complete IEEE or CSS round()
model. Native bit reinterpretation, binary64 correct rounding/error bounds, exact native
remainder, final binary32 projection, signed zero, special values, signed 32-bit
saturation and compiler/source refinement remain explicit external obligations.
The small-value theorem requires a strict error-versus-boundary margin; it does
not claim every promoted addition is exact. The remainder contract supplies an
unbounded integer quotient witness, not the potentially rounded native quotient.
The separate all-finite SMT result is not promoted to a Lean certificate.

Source correspondence as reviewed on 2026-10-24: the dyadic module supports the
promote-before-add expressions in `Integer::resolve` and
`Integer::to_computed_value` in `values/specified/number.rs`; the remainder module
supports finite nonzero-remainder bound reconstruction and strategy selection in
`values/generics/calc.rs`. These links identify conditional obligations, not proof
that native execution satisfies them. Existing `CssIntegerRounding` unit-step
semantics remain distinct. `coverage.json` is unchanged.

## Supplied subgrid line-list fragment

`SubgridLinePrefix`, `SubgridSequencePrefix` and `SubgridWholeAutofill` provide
bounded-prefix correspondence for fixed repetition sequences and one auto-fill,
whole-pattern maximality, and trailing unnamed-group padding. Inputs are supplied
line-name groups and line capacity; an unnamed group is one element, while an
empty pattern is not an admitted CSS repeat. The closed-form nonexhausted result
requires positive fixed counts and nonempty patterns. Twenty literal WPT oracles
exercise this fragment; they do not establish native or full Grid refinement.

The mapping follows the retained Grid Level 2 source plus CSSWG's 2025-08-13
resolution of issue8493. The visible draft's auto-repeat paragraph had a remainder
ambiguity; this model does not claim that prose was already amended. Parsing,
name scope, box participation, placement, line-capacity acquisition and coordinates
remain external. Only the narrow supplied-list fragment is mapped in coverage.json.

`ImplementationSupport.SubgridCountTransport` and `SubgridGuardedConsumer` are
separate arithmetic support: capped products and sums preserve remaining capacity,
and full-width guarded subtraction bounds the narrowed result even for negative
native caps. These laws do not prove a layout capacity is valid. Cached-observer
correspondence requires capacity <= signedMax <= storageCap; machine arithmetic,
FFI layout, allocation behavior and compiler refinement remain unproved. The
old narrowing functions are explicit countermodels and not CSS definitions.

Nineteen already reviewed public results are registered exactly once, with 28
executable checks (20 WPT oracles, four support controls, four false claims).
This adds no new research theorem credit or overall CSS coverage percentage.

### Counter descriptor representation support (2026-10-24)

The range/additive representation modules are ImplementationSupport, with eight plus
three previously reviewed results registered once. Inclusive semantic membership and
strict descending reference functions are separated from implementation admission,
resolution and export. This adds no feature to coverage.json. Supplied nonnegative
resolved weights, stable resolution, complete publication invariants and native
correspondence remain premises; unresolved descriptor rejection is not a CSS validity
theorem. Historical inline-only/partial-admission definitions are countermodels.

## Finite Round scalars and separate magnitude support

`CssFiniteRound` models the four traditional strategies on supplied exact rational
scalars with an explicit finite nonzero step. It proves adjacent-multiple bounds,
exact-input and zero-sign preservation, nearest upper ties, and general toward-zero
equivalence to minimum absolute bound selection. It reuses finite signed scalars,
extended reciprocal and clamp. This is partial Round coverage: line-width and
device-pixel snapping, omitted number-step defaults, units/types, parser admission,
nonfinite Round and native precision/refinement remain outside scope. None at zero
step marks exclusion. The infinite-step probe supplies a separate specified zero;
only seven of the eight observer cases execute this finite core.

`ImplementationSupport.RoundRemainderCapacity` and `Binary32Magnitude` separately
prove exact truncating-remainder magnitude capacity and a constructive finite
BitVec32 decoder equivalence on the common 2^-149 grid. Sign bits are deliberately
ignored by the magnitude decoder; exponent255 is excluded. Mathematical signed
tmod is distinct from Euclidean remainder and SMT fp.rem. Rust fmod/% correctness,
native bit reinterpretation, signed remainder-zero policy, f64 reconstruction,
final f32 projection and compiler/browser correspondence remain external.

Twenty-one existing declarations are registered once: capacity3, decoder7 and
finite Round11. The decoder imports the same capacity module, without duplicate
credit. Thirty-seven original anonymous examples are retained; twenty executable
controls include five expected-false observations. Integration adds zero research
theorem credit and no overall CSS coverage percentage. Only supplied finite Round
gets a narrow coverage entry; the machine-support modules add no CSS feature.


- `ImplementationSupport.RoundSpecialKnowledge`: four transferred class-algebra support laws, eight controls; no additional normative coverage. Finite-finite Round, scalar classification, AST knowledge/reachability and native correspondence are external. Existing finite-Round special-value exclusions remain. Installed descriptor source mapping is appended in README; all eleven existing descriptor declarations and nonnegative/representation premises are unchanged.


- `ImplementationSupport.FiniteModRemWitness` and `FiniteModRemContract`: 28 transferred implementation-support audits, including wrappers and spacing lemmas; 24 executable controls and 14 proof examples. No new research theorem credit or normative CSS feature. The old-formula witness retains nearest-rounding/source correspondence assumptions; replacement sign adjustment and closed projection retain native remainder/addition and operand-sign premises. The nearest divisor endpoint certificate permits ties and does not prove native tie-to-even behavior. Existing normative coverage remains unchanged.


### Animation context and endpoint implementation support

Four support modules transfer the reviewed exact-rational common-context, finite-DAG cache/schedule and typed endpoint-history obligations. Canonical VariableExpr.substitute_congr and VariableProperty.compute/defaulting are reused rather than duplicated. Numeric initial/default metadata is distinct from missing var fallback: present empty and multi-token wrong types do not use that fallback. The single-token research fragment correspondence is separately proved in css-keyframe-token-list-adapter-v1.

Ranks, complete dependencies, winning operations, current provider context, registration profile and coherent sample remain supplied; no CSS-cycle/SCC, native arithmetic, scheduler, taint/URL, parser or whole-animation refinement is claimed. All are ImplementationSupport; normative coverage is unchanged. Copying proofs adds zero research theorem credit. Source mappings and deduplicated registrations are recorded in css-keyframe-animation-library-proposal-v1. Earlier negative-control reduction failures are distinguished from the newly decisive replay; actual canonical totals require a full check.

CommitStyles prefix refresh support (`ImplementationSupport.CommitRefresh`) transfers the already-reviewed covering-refresh theorem and its bridge to `KeyframeSchedule`. It preserves ordered per-property composition while refreshing every contributing effect against a supplied current provider context. Six audit declarations and nine executable cases (three deliberately false) are transferred research support, not new proof-discovery or normative coverage. Native context freshness, complete prefix selection, endpoint semantics, scheduling delivery and source refinement remain assumptions.


Endpoint source indices (`ImplementationSupport.KeyframeEndpointIndices`) transfer the reviewed finite-block prefix/recovery and conditional machine-bound model. Empty input blocks retain slots, and skipped outputs do not shift source declaration indices. Fourteen existing audits (eight primary lemmas, three helpers and three refutations) and eight executable cases (three deliberately false) are implementation support only, with zero new proof-discovery credit or normative CSS coverage. Stable prioritized traversal, immutable declarations, successful bounded storage and source correspondence are premises; input-block count has a separate machine bound from declaration count. The archived descriptor-v2 mapping and transfer accounting are recorded in `css-keyframe-endpoint-index-library-proposal-v1`; allocator behavior, native publication/lifetime, provider correctness and CSS semantics are not proved.


Computed property-name support (`GuardedNames`, `GuardedNamesExamples`) preserves the old guarded solver through a full value/state embedding. Its name parser remains a supplied normalized-token adapter, with no raw CSS/native correspondence claim. The 25 transferred audits and 15 executable controls add no proof-discovery or numeric normative coverage credit. Full assumptions and exclusions are recorded in ARTIFACT.md; exact transfer/preimages are in `css-variables-computed-name-library-proposal-v2`. Existing fixed-name profile claims remain unchanged.
