# CSS semantics in Lean: research prototype

This independent Lean library models explicitly scoped CSS selector, cascade, and
closed property semantics. It has no Stylo, Gecko, Aeneas, or Bloom filter dependency.
It is an initial research artifact, not a complete CSS formalization or a
mechanically verified translation of specification prose.

Start with [ARTIFACT.md](ARTIFACT.md) for reproduction, representative proofs,
browser comparisons and trust boundaries. The sections below retain the detailed
development history; historical counts and exclusions belong to their checkpoints.

For current algorithm families, finite browser evidence and remaining CSS modules,
see the [accepted coverage map](research/coverage-map.md) and
[primary-spec inventory](research/current-spec-inventory.md). Audit/case counts
are not a percentage of CSS specification coverage. Historical checkpoint sections
retain their original profile exclusions.

## Current checked pipeline

Normalized selectors → matching and list specificity → applicable stylesheet
rules → closed Cascade 5 winner → closed literal defaulting/inheritance.
The variable-aware branch adds inherited custom-property computation,
substitution, and a closed ordinary-property decoder after winner selection.
`Style.compute_sound` connects these stages to a declarative relation. It is a
soundness result for the stated profile, not full CSS conformance or a browser
refinement. Equal complete cascade keys can admit multiple declarative winners.

[coverage.json](coverage.json) records supported fragments, explicit unsupported
features, source revisions/maturity, theorem links, and queued packages in a
machine-readable form. `check.py` validates its links and includes it in the
source fingerprint. [The expansion review](research/extension-review.md)
records independent semantic and fresh-archive checks at each checkpoint.

## Resolved baseline groups

`BaselineAlignment.solve` accepts a finite same-context/flow/preference group with
supplied optional first/last baselines, exact rational lengths and resolved margins.
It returns border-start positions only when the nonnegative container fits the
group envelope. `placement_iff` connects the algorithm to independent baseline
alignment and margin-edge contact constraints. `solve_reencode` preserves the
whole result under storage-origin changes chosen by input value;
`solve_occurrences` additionally permits independent choices for equal duplicate
input occurrences through the ordered `Reencoded` relation;
`recomputed_relative_preserved_iff_constant` characterizes when baseline errors
preserve pairwise placement after recomputing the group.

This is the limited CSS Align 3 / Flexbox 1 profile recorded in `coverage.json`.
It supplies neither baseline donors/fonts nor layout sizing, overflow fallback,
scroll rules or a Gecko refinement. Missing providers are unavailable, not zero.

## Raw scope source profile

The separate raw `@scope` facade connects explicit scope syntax to nested root
assignments, per-assignment selector specificity, proximity and computed
`visibility`. It supports the documented origin, layer, attached-style,
container-metadata and rollback subset. It excludes imports, omitted scope
starts, shadow trees and dynamic mutation; other unsupported syntax returns
unavailable. See [the scope profile and acceptance requirements](ARTIFACT.md#raw-scope-source-extension),
[coverage.json](coverage.json), and the [review history](research/extension-review.md).
Generic kernel proofs, finite kernel examples, and browser comparisons provide
different evidence; none establishes all-CSS conformance or Gecko refinement.

## Specification and scope

The initial reference is the [22 January 2026 Selectors Level 4 Working
Draft](https://www.w3.org/TR/2026/WD-selectors-4-20260122/). Research notes and
the section mapping live in [research](research/).

The original base fragment accepts normalized selector syntax: compounds containing namespace,
type, ID, and class constraints, combined using child and descendant
combinators. Every compound has an explicit resolved namespace constraint,
including compounds without a type name. An empty constraint compound means
the universal selector in its resolved namespace. Repeated ID and class
constraints are conjunctions; distinct nodes may have duplicate IDs. Each element
has at most one ID in this profile; document languages with multiple IDs per
element require a broader adapter/model.

This is a case-sensitive profile. Namespace URI, local name, ID, and class
comparisons use exact Lean string equality. The model distinguishes a null
namespace from an unrestricted namespace. The original fragment leaves parsing, escape decoding, namespace
prefix/default resolution, class tokenization, and document-language name
normalization to adapters. The bounded raw HTML selector extension below
adds an explicit interpretation of type-name folding; quirks-mode ID/class matching is unsupported.

The input is an abstract element parent forest with a natural-number depth
that strictly decreases towards each parent. This allows arbitrarily large
trees while excluding cycles and infinite ancestor paths. It does not require
global finiteness, unique IDs, a single root, or a depth bound chosen by the
verifier. The ordered extension adds sibling groups, and `FiniteForest` supplies a complete
finite element domain for forward relative-selector search.

Later modules below add structural/relational selectors, specificity, cascade,
and closed computed values, explicit element scope, and bounded raw parsers.
Shadow DOM, featureless elements, pseudo-elements, general parsing recovery,
layout, and dynamic mutation remain unsupported.

## Checked results

`CssSemantics/Dom.lean` defines the forest and strict ancestor relation, and
proves that ancestors have smaller depth and a node is never its own ancestor.

`CssSemantics/Selectors.lean` defines matching independently of an implementation
and proves:

- A matched selector's subject compound matches its subject element.
- A child-combinator match implies the corresponding descendant match.
- Every compound in `Selector.ancestorCompounds` has a matching strict ancestor
  whenever the complete selector matches.

The last theorem is a necessary condition only. It deliberately forgets child
distance, ancestor ordering between the listed compounds, and their joint
witnesses. Its converse would be false. A future optimization proof could use
this condition after separately proving a browser adapter and hash/filter
contracts; no such connection is claimed here.

`CssSemantics/Examples.lean` checks a successful descendant match, rejection of
a skipped child, rejection of self descent, same-element class conjunction,
duplicate IDs, null-versus-any namespaces, case sensitivity, namespace
constraints on class-only compounds, and mixed-combinator adjacency. These are
Lean examples, not browser conformance tests.

`CssSemantics/Executable.lean` adds an executable Boolean matcher and proves
`Selector.matchesBool_iff`: it returns true exactly when the existing
declarative `Selector.Matches` holds. The declaration is unchanged. The proof
covers both soundness and completeness for this scoped model, including
mixed child/descendant chains.

Ancestor search follows parent links until it reaches a root. Its termination
proof uses the supplied parent-depth law, with no arbitrary search cutoff and
no equality requirement on node identifiers. To run the matcher, the caller
must provide executable element and parent functions, together with the
forest's depth function and proof. Termination does not imply that the
reference algorithm is fast: nested descendant combinators can repeat ancestor
searches. No production performance claim is made.

`CssSemantics/ExecutableExamples.lean` contains 12 named example cases. Their
aggregate expected result is proved in Lean using ordinary simplification of
the recursion equations. `tests/RunExamples.lean` also executes the cases and
fails if any result differs. Neither the equivalence proof nor the example
proof uses `native_decide` or trusts execution results as proof terms.

## Reproduce

Requirements: Lean **4.35.0-rc4** and Python 3. No additional Lean packages or
network access are required once the pinned Lean toolchain is installed.

```sh
python3 check.py
```

For an existing unpacked toolchain:

```sh
python3 check.py --lake /absolute/path/to/lean-toolchain/bin/lake
```

`check.py` builds the library, checks the pinned version, audits the axioms of
the public theorem inventory, runs the ordered executable cases, and requires
Lean to reject deliberately invalid child and adjacent-sibling proofs. Current
counts are recorded in `.lake/verification/report.json`. It writes logs and
source hashes under `.lake/verification/`, records command return codes and log hashes, rejects
duplicate audit declarations/results, checks that every public theorem in the
source is audited, and checks that source hashes have not
changed during verification. A failed run removes any previous acceptance report.
The intentionally invalid file `tests/RejectDescendantAsChild.lean` is excluded
from the normal library build.

There are no `sorry` declarations or custom axioms. Some proofs use Lean's
standard `propext`, `Quot.sound`, and `Classical.choice` foundations; the audit
records the exact dependencies per theorem. The forest's parent-depth law is
an explicit input obligation, not an axiom. Trust in the prose-to-model
interpretation and a future DOM adapter remains separate from kernel checking.

## Provider observations

Import `CssSemantics.ProviderObservation` (also exported by `CssSemantics`) to
read an observation from the state returned by an optional forcing operation.
`successful_state` and `successful_observation` retain both parts of a successful
query. The query, step and history erasure laws change observations and logs
while preserving the world and success/failure. Mutation, admission and forcing
are independent of the log. These are generic provider-interface results;
they do not prove CSS rectangle rules, native layout correctness or target
lifetime. All five proofs are included in the standard axiom audit.

## Evolving with the specification

Changes should identify the dated specification revision and affected
sections, review the semantic interpretation, add examples that distinguish
the old and new behavior, and rerun the proofs. Browser/WPT differential checks
should become another validation layer when an executable adapter exists.
They will provide evidence about the interpretation, not replace it.

An [independent preliminary semantic review](research/semantic-review.md)
checked the current fragment against the cited sections and reproduced a
clean copied-package build. This scoped review does not establish full CSS
conformance. Before treating this as a reusable package, we still need a
well-defined supported-input adapter, broader conformance examples, further
external review, and release/versioning policy. The first downstream target is a narrow Stylo
ancestor-filter theorem, while the library's definitions stay independent of
that implementation.

## Logical matching extension

`CssSemantics/Logical.lean` provides `MatchExpr`, a semantic intermediate
representation with conjunction, disjunction, negation, and child/descendant
composition at any expression position. Its executable matcher is proved
sound and complete for its declarative semantics. The original `Selector`
embeds with a proved matching equivalence. `SelectorList` matches when any
member matches; the empty internal list matches nothing.

This represents the matching behavior needed by normalized selector lists,
`:is()`, `:where()`, and `:not()`, including complex arguments and logical
constraints on ancestors. It is not a CSS grammar: arbitrary expression trees
may lack CSS spellings. Raw empty `:not()` remains invalid; an empty list left
by forgiving `:is()`/`:where()` parsing matches nothing. Parsing and validity
are not implemented. `:is()` and `:where()` have equal matching behavior but
different specificity, which this representation intentionally does not encode.

Namespace constraints must already be resolved for their syntactic context.
In particular, default namespaces do not constrain an argument subject compound
inside these logical pseudo-classes unless it has an explicit type/universal
selector. The generic semantic representation cannot recover that distinction.
`LogicalExamples.lean` adds eight executed/proved positive and negative cases,
plus empty-list and second-list-member kernel checks. There is no browser
adapter or mechanically proved prose translation.

See [ROADMAP.md](ROADMAP.md) for the continuation plan and coverage matrix.

## Ordered sibling extension

`Siblings.lean` adds coherent, finite, duplicate-free element sibling groups,
with each node's exact position. Membership preserves the optional element
parent; children of the same element parent must share a group. Separate groups
can have no element parent, distinguishing detached roots from elements inside
a document or fragment. An adapter must establish that these explicit groups
are exactly the concrete parent's element children in document order, excluding
text/comments; the abstract model does not itself identify non-element parents.

`TreeExpr` composes all four combinators with logical expressions at arbitrary
positions. Its Boolean matcher is proved equivalent to declarative matching.
Adjacency is exactly one position before the subject; subsequent-sibling
matching permits any strictly earlier position. Proofs establish that earlier
siblings are distinct, have the same element parent, and have the stated unique
position. Searches enumerate actual sibling-list lengths, without an arbitrary
cutoff. The reference adjacency algorithm scans the finite group; it makes no
production-performance claim.

Nine executed and kernel-checked cases distinguish skipped adjacency, directed
order, self exclusion, fragment groups, isolated roots, mixed child/sibling
chains, and negation. A separate deliberately invalid proof must be rejected
when it tries to use strict precedence as immediate adjacency.

## Attribute extension

`Attributes.lean` covers presence and `=`, `~=`, `|=`, `^=`, `$=`, `*=` against
normalized attribute lists. It distinguishes missing attributes from empty
values and gives the substring operators their required nonempty-operand guard.
The dash operator intentionally accepts an empty operand for an empty value or
one beginning with `-`. Token matching uses exactly CSS's five ASCII whitespace
characters; nonbreaking space is not a separator.

Attribute names and namespace constraints must already be normalized. The
default attribute namespace is null, and explicit wildcard/exact namespaces
are represented. Value comparison is explicit sensitive or ASCII-insensitive;
no Unicode case folding occurs. An adapter must resolve language-dependent
default sensitivity and the `i`/`s` flags, parsing, name normalization, and
attribute uniqueness. `TreeExpr.attributeTest` composes these tests at any
combinator position using an attributed ordered forest.

The operator and attribute-list Boolean matchers have declarative equivalence
proofs. Prefix/suffix operations use Lean's proved list relations; substring
uses the standard decidable infix relation. The kernel checks all 25 edge cases,
and the runner executes them independently. An additional kernel check combines
an ancestor attribute test with a child combinator.

## Structural position extension

`AnB.lean` checks exact signed `An+B` arithmetic for positive one-based positions,
with arbitrary integer coefficients and nonnegative integer witnesses. Its
quotient-based executable decision procedure is proved equivalent for zero,
positive, and negative steps and offsets, without bounded witness search.

`Structural.lean` provides filtered forward/reverse sibling positions for
`nth-child`/`nth-last-child`. A match requires that the subject itself satisfy
the filter; rank is one plus the number of matching strictly earlier/later
element siblings. The executable rank is proved equal to the declarative
count, and matching is equivalent. This is not a separate proof against a
parser or a filtered-list-index implementation.

The `all` constructor supplies the unrestricted namespace wildcard needed when
`of S` is omitted. `ofType` builds a filter from a supplied subject's namespace
and local name; it must be evaluated for that same subject to represent
`nth-of-type`. First/last positions are the `0n+1` cases; only-child/type can be
expressed by conjunction of forward and reverse first positions. These tests
are currently a separate `NthSelector` layer whose filter can be any `TreeExpr`;
structural tests cannot yet occur recursively inside that filter or at arbitrary
`TreeExpr` positions. The original nth filter excludes `:root` and `:empty`;
these now have separate explicit content-context semantics below.

Twelve arithmetic and sixteen structural examples include excluded filtered
subjects, fragment/detached roots, reversed order, signed formulas, and two
same-name/different-namespace type distinctions. All are executed and checked
by the kernel. The abstract natural-number indices have no machine overflow.

## Anchored relative matching extension

`Relative.lean` adds a finite complete node domain. The adapter must provide an
exhaustive duplicate-free list containing every node in its abstract type;
finite sibling groups alone do not guarantee finite descendants. The reference
algorithm searches that actual domain for each relative step. There is no
arbitrary depth or node cutoff, and no performance claim.

A relative path starts with its anchor as the left endpoint of the first axis.
Each subsequent step starts at the previous witness. Omitted CSS relative
combinators must normalize to strict descendant; explicit child/next/subsequent
axes use their existing orientation. `RelativeSelector` is nonempty, and
`HasSelector` is existential matching over a list of relative selectors.
Both Boolean matchers are proved equivalent to declarative anchored paths.

Step predicates are the existing `TreeExpr` semantic IR. They can contain
logical predicates and normalized complex tests; this does not establish that
an arbitrary IR expression has a valid CSS spelling. Raw invalid or nested
`:has()` and pseudo-elements are not accepted or parsed. An empty internal
has-list rejects, without claiming raw empty `:has()` is valid. This is a
separate evaluation layer; `:has()` cannot yet occur inside general TreeExpr
syntax. Negation placement is tested explicitly.

Fifteen executed/kernel-checked cases distinguish a following sibling outside
the anchor subtree, skipped adjacency, linked versus unrelated witnesses,
strict descent, list branches, fragments, detached roots, and
`:not(:has(p))` versus `:has(:not(p))`.

## Syntax-preserving specificity extension

`Specificity.lean` uses unbounded natural-number triples, lexicographic order,
componentwise addition, and maxima. Its proofs establish total order properties,
maximum bounds/provenance, and associativity of addition. It does not model a
browser's finite component representation or clamping.

`Syntax.lean` preserves universal/type/ID/class/attribute syntax, conjunction,
combinators, and distinct `:is()`/`:where()`/`:not()` constructors. An explicit
zero-specificity `namespaceGuard` represents an implicit resolved namespace
restriction separately from an explicit universal. Namespace prefix/default
resolution still belongs to an adapter. `alternatives` represents pseudo-class
argument grouping; top-level lists use `SyntaxList` instead.

This normalized representation is syntax-preserving, not syntax-validating:
constructors permit trees that are not legal CSS grammar, such as alternatives
or compound conjunctions in arbitrary positions. Inputs require independent
validation and context-aware namespace normalization. No raw parser, forgiving
recovery, or grammar-validity theorem is provided.

Lowering to `TreeExpr` is proved to preserve declarative matching, and the
lowered executable matcher is sound and complete. Specificity follows the
interpreted syntax rules: logical argument maxima, zero for `:where()`, and
sums across compounds/combinators. The prose-to-rule interpretation is reviewed,
not mechanically translated from W3C prose. Structural and relational syntax
are not yet part of this representation.

For top-level lists, only matching branches contribute. A selected specificity
is proved to belong to a matching branch and dominate all matching branches;
`none` is equivalent to no branch matching. `some (0,0,0)` remains distinct
from no match. Sixteen exact-result cases distinguish top-level filtering from
`:is()` maxima, duplicate atoms, `:where()`, unmatched/zero cases, namespace
context, and summation. The runner verifies complete optional triples before
reporting whether each case matches.

## Combined structural and relational syntax

`AdvancedSyntax.lean` preserves explicit/omitted nth filters and relative-step
syntax. Lowering to the earlier structural/path layers is proved to preserve
filter matching, rank, and anchored witnesses. Nth specificity adds one class
component to the maximum explicit filter specificity; `:has()` uses the maximum
relative-branch sum, including branches that did not match.

`Combined.lean` composes these tests with core selectors, logical pseudo-classes,
and combinators, with another executable/declarative equivalence theorem.
Fourteen exact matching-and-specificity cases cover static argument maxima,
relative-step sums, `:where()`, negation, and nth tests on a combinator's left.
The shared style pipeline below supplies dynamic top-level list selection for
the combined representation as well.

This original representation keeps nth filters and relative-step tests limited
to core syntax. The recursive representation below covers nested nth filters,
nth tests inside `:has()`, and `:has()` inside nth filters. Its nesting check is separate
from CSS's prohibition on nesting `:has()` inside `:has()`. Neither pseudo-element
selection nor parsing/validation is supplied. The earlier standalone-layer
limitations describe their original APIs; `CombinedSyntax` supplies outer
composition while retaining these inner-argument limits.

## Closed cascade and inheritance extension

`Cascade.lean` models applicable declarations for one property in one
encapsulation context, using the stable Cascade 5 ordering. The key compares
origin/importance, element-attached status, resolved layer rank, specificity,
and source order. Important origins and layers reverse their normal order.
Unlayered precedence has an explicit flag; signed layer ranks avoid subtraction
saturation or a guessed maximum layer count. Winner selection is proved to
return an input declaration at least as strong as every candidate, and `none`
occurs exactly for an empty candidate list.

Inputs must already have passed selector, media/supports and property-validity
filtering. Attached entries represent applicable element-attached declarations;
layer indices represent fully resolved layer order. This does not model layer
registration/nesting, presentation hints, shadow-context precedence,
animations/transitions, `@scope`, rollback (`revert`/`revert-layer`), or general
shorthand/variable resolution. Source order must be correctly assigned; equal
complete keys choose the later list member, so no arbitrary-enumeration
invariance claim is made for tied keys. Seventeen exact-result cases exercise
precedence reversals and competing ordering dimensions.

`Defaulting.lean` models a closed property/value profile with a constant initial
value, an inherited flag, and identity computation for literal values. Missing
values and `unset` use normal defaulting; explicit `initial` and `inherit`
override the inherited flag. Inheritance uses the parent's computed result,
falling back to initial at a root. Resolution has a declarative equivalence
and uniqueness theorem. Recursive computation over the parent forest is also
proved equivalent and unique, terminating by the forest's depth law without a
fixed bound.

Eighteen exact-result cases cover missing/explicit values and multilevel
inheritance, including an intermediate initial reset and a noninherited parent
whose initial result must be inherited instead of skipping to a grandparent.
This is not general CSS value computation: relative units, environment-dependent
initial values, flattened shadow inheritance, custom properties, and cycles
need separate models. The cascade winner and defaulting APIs are currently
independent; a fully checked selector-to-property adapter is still pending.

## Selector-to-property bridge

`Style.lean` now connects combined selector matching, dynamic top-level list
specificity, cascade ordering, and defaulting. The selected weight is
characterized by a matching branch and an upper bound over every matching
branch. A candidate entry exists exactly when its source rule has that
matching weight. Winner soundness establishes both source-rule provenance and
maximal priority, so an unmatched important rule cannot enter the cascade.

`StyleDeclaration` intentionally represents stylesheet declarations only: it
has no attached-style or supplied-specificity field. Instantiation sets
`attached = false` and computes specificity from the matching selector list.
The bridge remains one property and one declaration per rule, with conditions
and property validity already filtered. Layer ranks and declaration source
positions remain adapter inputs. Inline targeting requires its own explicit
applicability path and is not part of this bridge.

`Style.compute_sound` carries the selected cascade result through recursive
parent computation into a separate declarative `Style.Computed` relation.
The relation permits any maximal candidate when complete keys tie; the
algorithm's deterministic tie policy is sound, but no inverse equivalence or
uniqueness theorem is claimed for the combined relation.

Eleven exact winner cases and a four-node inheritance chain check this
connection, including unmatched high-ID top-list branches versus `:is()`,
`:where()`, nth/has maxima, unmatched important rules, layer/source precedence,
missing-child inheritance, and an initial reset inherited by its child.

## Browser fixture comparison

`CssSemantics.BrowserFixtures` pairs 31 CSS strings with normalized model selectors
and a seven-element forest. The exporter evaluates the proved matcher, checks
its kernel-checked expectations, and exports the exact namespace, attribute,
class, parent, and sibling observations. The standalone page reconstructs this
forest using detached elements and document fragments, checks the observations
back against the export, then calls `Element.matches`.

Run the proof check first, then an isolated Firefox instance:

```
python3 check.py --lake /path/to/lake
python3 browser_check.py --lake /path/to/lake --firefox /path/to/firefox
```

The runner creates its own headless profile and Marionette connection; it does
not attach to an existing browser. Reports and logs are in `.lake/browser-check`.
Its source hashes must agree with the successful proof report before and after
export/browser execution. It checks the exact result pairs and runs deliberately
inconsistent DOM and flipped-expectation controls. For manual use, open
`browser/index.html` and load the generated `fixtures.json`.

This is finite differential evidence for these reviewed CSS/AST pairs, not a
parser proof, general DOM adapter proof, or browser refinement theorem. It does
not cover querySelectorAll enumeration, :scope, computed style, or layout; later
sections describe separate suites for some of those interfaces.

## Document-root and direct-content selectors

`ContentContext` adds an explicit optional document element and complete ordered
child-content observations. Its element projection must agree with the forest's
parent and sibling relations. `:root` uses the document element observation;
detached and fragment roots do not become document elements merely because they
have no element parent. `:empty` rejects any element child and checks direct text,
while comments and processing instructions do not affect matching.

Two profiles preserve the spec boundary: `strictText` permits only empty text;
`documentWhitespace` accepts an explicitly supplied host-normalized text
predicate. The fixture predicate permits space, tab, and LF; its CR rejection
means unnormalized input is outside that fixture profile, and form feed is not
silently treated as document whitespace. Completeness of non-element content and
host text normalization remain adapter obligations. Generated pseudo content is
not a DOM child and is outside this input model.

`ContextSyntax` composes these tests with the prior selectors under logical
operators and combinators, with an executable/declarative equivalence theorem
and syntax-sensitive specificity. The earlier context representation retains core-only nth filters and has steps;
the recursive representation below removes that restriction. Contextual selectors use the shared `GenericStyleRule` pipeline described below. The original browser evidence predates this content extension; the newer content suite below covers these observations.

## Shared selector-to-property interpretation

`SelectorModel` supplies a parent forest, declarative matching, and static
specificity. `ExecutableSelectorModel` additionally supplies the executable
matcher and its equivalence proof. The Combined and contextual instances use the
existing proved semantics; the contextual instance fixes one empty-content
profile. A single `GenericStyle` implementation handles matching-list weights,
rule applicability, cascade selection, and parent-computed inheritance.

`GenericStyle.compute_sound` relates this pipeline to its declarative result.
Matching and inheritance share the model's forest projection. The original
Combined APIs remain specializations, with `Style.compute_eq_generic` proving
identity of the computed result. An arbitrary future instance must justify its
matcher law and spec interpretation; the generic theorem does not establish
that an arbitrary supplied predicate or specificity function follows CSS.

Contextual examples check root/empty applicability, static pseudo argument max
versus dynamic top-level lists, specificity suppression, importance/layers,
and profile-dependent cascade/defaulting. The closed value, single-context,
prevalidated stylesheet, no-inline-targeting and tied-key limits still apply.

## Recursive inner selectors

`RecursiveSyntax` and nonempty `RecursivePath` allow structural, content, logical,
and relational tests inside nth filters and relative paths. This covers nested
nth filters, nth inside has, has inside nth, and root/empty within those tests.
Mutual executable/declarative equivalence is proved by syntax/path size;
forward matching searches the complete finite domain without a depth cutoff.
`GenericNth` supplies predicate-based filtered ranks and proves exact
specialization to the original `NthSelector`. The recursive interpretation feeds
the same generic cascade/defaulting pipeline.

The normalized representation is broader than valid raw CSS. `noNestedHas` is a
separate structural check, proved equivalent to maximum has nesting depth at
most one; independent has branches are accepted. The raw matcher does not
silently reject syntax that fails this check. CSS-facing input still requires
normalization, the nesting invariant, and other grammar checks; forgiving
`:is`/`:where` recovery happens before this representation and is not proved.
Specificity preserves pseudo argument max, nth's class increment, path sums,
and where suppression. The content browser suite below compares selected recursive compositions;
the earlier 31-case report is retained as a historical checkpoint.

## Recursive/content browser fixtures

A second suite exports the explicit document element and all direct element,
text, comment, and processing-instruction observations. The runner reconstructs
and reads them back before comparing 25 strict-text recursive/root/empty cases:

```
python3 browser_check.py --lake /path/to/lake --firefox /path/to/firefox --fixture-suite content
```

Evidence goes to `.lake/browser-check/content`. Three additional observations
compare the draft whitespace profile's predictions with actual browser results;
they are labeled separately and do not count as strict-profile agreements.
Their case identities, model expectations, and observed Boolean/error fields
are still validated. Both suites check corrupted-snapshot and flipped-expectation
controls. These remain finite, manually reviewed CSS/AST correspondences, with
no general parser, DOM-adapter, or browser-refinement theorem.

The local Nightly 160.0a1 run on 16 October 2026 agreed with all 25 required
content cases and all 31 original cases. All three draft-whitespace observations
predicted true in that named model profile and returned false in the browser,
without parse errors. These observations document the profile difference; they
do not establish a general conformance verdict. The content suite also rejects
a deliberately corrupted child order while preserving the exported sibling order.

## Closed visibility computed-style comparison

`ComputedBrowserFixtures` interprets the Display 3 `visibility` profile:
visible/hidden/collapse, inherited by default, initial visible, identity keyword
computation. It excludes Display 4's additional force-hidden value and all box,
rendering, animation, transition, inline-style, non-author-origin and shadow
behavior. Nineteen manually paired stylesheet/model scenarios make 42 exact
computed-keyword predictions, checked by the kernel and the executable pipeline.
They exercise selector specificity, layers, importance, source order, and
initial/inherit/unset through several ancestors.

```
python3 browser_check.py --lake /path/to/lake --firefox /path/to/firefox --fixture-suite computed
```

This separate suite creates an attached, rendered, offscreen iframe in standards
mode. The complete eight-element snapshot includes the stylesheet element.
It verifies the element domain, installs the paired author stylesheet, and reads
`getComputedStyle(...).visibility`; results and stylesheet observations are
checked against the exact exported case identities. Reports are written to
`.lake/browser-check/computed`. A wrong DOM observation and a flipped expected
keyword must both be detected. The manual stylesheet/normalized-rule mapping
and browser adapter remain unproved, so finite agreement is differential evidence.

The 16 October 2026 local Nightly 160.0a1 run agreed with all 42 computed-keyword
predictions and detected both deliberate failures. This establishes finite
pipeline evidence for the named profile; it does not verify CSS parsing,
all cascade contexts, or layout behavior.

## Variables 1 dependency and substitution fragment

`Variables.lean` represents prevalidated literal token sequences, concatenation,
and references with or without fallback. `references_iff` proves complete static
reference extraction, including nested fallback syntax. Literal tokens must not
hide further substitution functions. Exact property names are case-sensitive;
parsing and serialization are external.

Substitution takes an **already-computed** reference environment. Its executable
result is equivalent to the independent inductive `Substitutes` relation and is
unique. Agreement on the expression's references implies equal results. `none`
denotes an invalid or missing referenced value; `some []` is valid and bypasses
fallback. This stage does not solve a recursive environment or parse the result
against an ordinary property's grammar.

`FiniteGraph.lean` proves positive reachability and cycle detection using finite
pivot closure. Every edge destination must be enumerated; no fixed depth or
node-count limit is assumed. Duplicate pivots are harmless, and no reflexive
path is inserted. The reference implementation may recompute subrelations and
makes no performance claim.

`VariablesGraph.lean` supplies this graph from unique, already-cascaded bindings.
Its `names` list is destination support, not an inventory of every declared
property. Static edges include all fallback references, as required by the
[Variables 1 snapshot](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/#cycles).
Cycle membership differs from merely depending on a cycle. Equivalent edge
relations have equal cycle results regardless of binding enumeration.

The 31 executed examples cover substitution, valid empty values, case-sensitive
names, both cycle members, a noncyclic consumer, transitive dependencies, and an
unused fallback self-cycle. The next layer connects graph invalidation and substitution to a recursive
custom-property solver.

[The version trace](research/variables-substitution-trace.md) separately follows
current Variables 2 / Values 5 guarded substitution. Its lazy fallback and cycle
marking rules are not implemented by this snapshot graph. The original browser reports concern earlier selector/visibility checkpoints.
The variable-aware suite below has its own source-bound evidence record.

### Recursive snapshot computation

`VariablesRank.lean` counts distinct reachable reference names. Following a
reference to a noncyclic target strictly lowers that count: the target is a
new reachable witness, and everything it reaches is already reachable from
the owner. This proves termination without a guessed fuel limit.

`VariablesSolver.lean` invalidates cycle members before any substitution,
resolves missing names as invalid, and computes other bindings recursively.
`compute_iff` proves equivalence to the independent inductive `Computed`
relation; results are unique. `compute_congr` proves equal computation whenever
two unique binding lists contain the same entries, so enumeration and rank
representation do not determine the result.

Seventeen kernel-checked and executed cases include fallback recovery by a
consumer outside a cycle, fallback failing to rescue a cycle member, an unused
fallback self-cycle, empty valid values, repeated shared dependencies, exact
case matching, and reversed binding order. This solver covers a single element's
already-cascaded declarations; the following layer adds inherited computed values. The
latest draft's guarded lazy cycle profile is implemented separately below.

### Inherited custom-property environments

`VariablesBase.lean` generalizes the solver over a supplied computed environment.
Only names without a local binding use that environment. Local cycles and failed
expressions remain invalid even if the supplied environment contains a valid
value for the same name. The original solver specializes the base to all-invalid;
`compute_eq_base` proves that specialization directly.

`VariablesInheritance.lean` recursively supplies the parent element's computed
environment, using the forest depth law. The resulting function is equivalent
to an independent relation with an existential parent environment and per-name
computation judgments. It is unique. Missing local names inherit; missing root
names and local cycle members are invalid. The parent forest is an explicit
inheritance-parent contract; shadow/registered-property policies are not derived.

The first profile accepts local normalized expressions or absence. It excludes
CSS-wide custom-property keyword handling, including keywords produced **after
substitution** by a fallback or concatenation. Merely dropping a declaration of
`initial` would wrongly turn invalidation into inheritance. No such normalization
is performed here. Closed token profiles must also exclude hidden substitutions,
registration, animation taint, and unsupported value functions.

Sixteen checked three-generation cases distinguish parent-computed aliases from
re-evaluated expressions, child overrides, inherited empty values, and failures
that block a valid parent value. The following sections add ordinary-property decoding and a separate browser
fixture boundary for these custom-property operations.

## Substitution into ordinary properties

`ClosedValues.lean` supplies an interpreted token domain with a single literal,
`initial`, `inherit`, or `unset` as accepted values. The executable decoder is
equivalent to an independent singleton grammar; empty and multiple-token
sequences are rejected. `KeywordToken.invalid` is a **present** token rejected by
that ordinary-property grammar, not the invalid custom-property result `none`.
Raw CSS tokenization, whitespace normalization, and the interpretation of the
closed literal domain remain adapter obligations.

`VariableProperty.lean` prepares an already-selected declaration. It substitutes
against computed custom properties, then decodes the result. Substitution or
grammar failure becomes `unset`; neither triggers selection of an earlier
losing declaration. Executable preparation/defaulting is equivalent to explicit
relations using the substitution proof and the supplied decoder.

`VariableStyle.compute_sound` connects existing selector/cascade provenance,
computed custom-property environments, preparation, and ordinary-property
inheritance through the same forest. The final theorem is soundness only because
cascade ties can admit multiple relation winners. Custom-property declarations
are still supplied as unique already-cascaded per-node bindings; this theorem
does not derive those bindings from stylesheet rules.

The 24 decoder/defaulting cases distinguish missing from empty, present tokens
rejected by the consuming grammar, unused fallbacks, concatenation, and CSS-wide
keywords produced for the consuming ordinary property. This does not add
CSS-wide keyword interpretation for custom-property computation itself. The
following browser fixtures test the connected variable-aware branch; observed
results are recorded separately from these proofs.

### Variable-aware browser fixtures

The `variables` suite pairs 15 raw stylesheets with normalized declarations and
19 computed visibility queries on the same complete eight-element document as
the earlier computed suite. The cases cover parse-time rejection versus
computed-time failure, present invalid and empty custom values, consuming
CSS-wide keywords, cycle recovery, the snapshot unused-fallback cycle, and
inherited computed aliases. Parse-invalid declarations are manually omitted
from the normalized model; this is not a parser proof.

```sh
python3 browser_check.py --fixture-suite variables --lake /path/to/lake --firefox /path/to/firefox
```

Expectations are exported by evaluating `VariableStyle.compute`, checked against
the kernel fixtures, and bound to the successful full proof report. The runner
uses fresh rendered standards-mode iframes, exact DOM and stylesheet readback,
independent result checks, and the existing negative controls. Its profile is
Variables 1 plus the closed Display 3 visibility grammar. The unused-fallback
cycle scenario must not be silently reinterpreted as the latest draft algorithm.
Results are recorded separately from kernel proofs; no general browser
refinement follows from finite comparison.

The local Nightly 160.0a1 comparison agreed on 18 of 19 queries, with both
negative controls passing. The retained disagreement is
`--b:visible; --a:var(--b,var(--a)); visibility:var(--a,collapse)`: the
pinned Variables 1 graph predicts `collapse`, while Nightly computes `visible`.
This is consistent with the source-traced lazy Variables 2/Values 5 algorithm.
The strict browser command exits unsuccessfully and preserves the full report;
the expectation is not changed. This is a versioned semantic disagreement, not
a Gecko bug verdict or a proof of the draft algorithm. See
[the evidence](research/variables-browser-evidence.json) and
[the algorithm trace](research/variables-substitution-trace.md).

## Current-draft guarded substitution

`GuardedSolver` is a separate interpreted Variables 2 / Values 5 profile for
fresh requests over normalized `var()` expressions. It records active property
owners and marks exactly the repeated interval. Marks survive fallback recovery
and all remaining substitutions; concatenation evaluates both sides even when
the first value is invalid. A marked owner returns invalid after its expression
finishes. Returning removes its own mark while preserving callers' marks.

The executable resolver is equivalent to mutually inductive name/expression
relations using the original bindings. Each fresh owner removes its declaration
from the recursion support; a proved lookup invariant preserves all nonactive
names. State laws prove caller-mark preservation, active-frame containment, and
an empty mark state after every fresh request. The result is unique for fixed
inputs. There is no arbitrary recursion limit. `GuardedNormalization.expand`
requires a proof that its budget covers remaining declarations and is proved
equal to the resolver for the full value/state pair; fixtures use the exact
declaration count solely to enable kernel reduction.

Twenty-two computation cases and three state cases exercise failure sequencing,
cycle participants versus outside consumers, unused fallbacks, inherited inputs,
and shared dependencies. `snapshot_draft_difference` proves the normalized
unused-fallback witness returns invalid in the snapshot model and `[1]` in the
guarded model. This theorem formalizes our interpreted profiles; it does not
mechanize the specification prose or establish browser conformance.

The supplied inherited environment must already contain computed tokens. This
module has no cross-request cache, custom-property cascade, or CSS-wide
custom-property result handling. Parent-tree integration is provided below. Registration, animation
taint, spread, arbitrary substitution functions, tokenization and serialization
remain outside this closed draft profile.

### Shared versioned property pipeline

`VariableModel` keeps a per-name computation relation separate from its
executable implementation and equivalence law. Snapshot and guarded factories
retain their respective independent relations. `GenericVariableEnvironment`
constructs inherited environments by parent recursion; its executable and
declarative environments are equivalent and unique. The original snapshot API
is an exact specialization.

`GenericVariableStyle.compute_sound` connects either solver to selector
applicability, cascade selection, ordinary-property preparation and inheritance
using the same forest. Pure preparation over computed values is consistent with
the stateful expression evaluator when its resolver preserves state, as proved
by `GuardedExpr.evaluate_pure`. Each guarded per-name result uses a fresh request;
this is not a theorem about persistent browser caches or evaluation order.

The separate `guarded` browser suite has 21 scenarios and 25 kernel-checked
visibility predictions. It reuses the earlier 15 CSS/model inputs under explicit
draft names, changes only the unused-fallback prediction, and adds six cases
that exercise later substitutions after failure or cycle marking. The snapshot
suite and its retained disagreement remain available.

```sh
python3 browser_check.py --fixture-suite guarded --lake /path/to/lake --firefox /path/to/firefox
```

The local Nightly 160.0a1 run agrees on all 25 draft-profile queries and passes
both rejection controls. [Source-bound evidence](research/guarded-browser-evidence.json)
records that finite comparison. It includes the unused-fallback result that
disagrees with the preserved Variables 1 snapshot expectation; neither report
establishes general browser conformance or a persistent-cache theorem.

## Custom-property keyword completion

`KeywordCompletion` adds an interpreted unregistered-property profile for
`initial`, `inherit` and `unset`. It recognizes a lone keyword after substitution
as well as a direct typed declaration. `initial` becomes guaranteed-invalid;
`inherit` and `unset` read the same property's parent-computed value, or invalid
at the root. Empty token sequences and multiple-token values remain present.

Both solvers now have a completion hook at each local property's return, before
its dependent consumers read it. Cycle invalidation bypasses the hook; absent
local declarations return the inherited value directly. Independent computation
relations and full equivalence proofs include this placement. The old APIs are
identity specializations, retaining their previous results. An arbitrary hook
is not automatically valid CSS: the closed keyword finalizer has its own
relation equivalence and invalid-value preservation theorem.

`ExecutableVariableModel.snapshotKeywords` and `.guardedKeywords` connect the
closed completion policy to the existing shared inheritance/style pipeline.
This normalized API leaves tokenization and identifier normalization external;
the closed raw-value adapter described below supplies a bounded parser. Rollback keywords (`revert`, `revert-layer`, `revert-rule`) require
cascade context absent from the unique-winning-binding input and are excluded.
The [source trace](research/custom-property-keyword-trace.md) records the
algorithm interpretation and version boundaries.

Nine additional browser scenarios supply ten kernel-checked visibility queries:
completion before dependent reads, root inheritance, failed/cyclic local values,
multiple tokens, and concatenation that produces a lone keyword.

```sh
python3 browser_check.py --fixture-suite keywords --lake /path/to/lake --firefox /path/to/firefox
```

The keyword profile has 23 shared computation fixtures checked under both
solvers, plus controls proving an arbitrary completion hook cannot rescue a
cycle owner. Closure theorems establish that parent-recursive environments
contain no lone CSS-wide keywords: that property is proved from the root, rather
than assumed for each constructed parent environment.

Fresh Nightly 160.0a1 comparison matches all ten keyword queries, with both
rejection controls passing. [Source-bound evidence](research/keyword-browser-evidence.json)
records the finite comparison; raw parsing, rollback and general browser
refinement remain outside this result.

## Named custom declarations and the cascade

`CustomCascade` selects custom declarations by exact normalized name using the
same selector applicability, specificity and cascade machinery as ordinary
properties. It constructs unique bindings from finite source-name support and
proves every lookup equals its per-name cascade result, including absent names.
Winner provenance and selected-expression dependency correspondence exclude
references in losing declarations from the custom-property graph.

`CustomStyle.compute_sound` connects that selection to completed custom values,
ordinary declaration selection, substitution, decoding and inherited computed
values. Cascade ties retain the existing soundness-only contract. Both keyword
solver profiles are proved lookup-extensional; a generic parent theorem then
shows that changing only losing declarations preserves computed environments
and consuming values, even if binding enumeration changes.

Thirteen paired stylesheet cases cover losing/winning cycles, inheritance,
case-sensitive names, selector-list specificity, layer and importance order,
winning initial/empty values and non-propagation of custom importance to its
consumer. A general fixture theorem proves removal of a losing self-reference
preserves computed values at every node.

```sh
python3 browser_check.py --fixture-suite custom --lake /path/to/lake --firefox /path/to/firefox
```

The model still takes parsed, normalized rules with condition applicability and
layer order supplied externally. Raw declaration syntax, inline targeting,
registration, rollback and additional substitution functions remain outside
this profile. Exact name identity is preserved; Unicode normalization is not
applied to names. Fresh Nightly comparison matches all 13 queries and passes
both rejection controls. [Source-bound evidence](research/custom-browser-evidence.json)
records the finite result; it is not a general browser refinement theorem.

## Direct layer rollback

`LayerRollback` models direct `revert-layer` while retaining applicable candidates.
At each maximal rollback declaration, it removes the current layer and all later
layers in normal order, across both importance strata. Unlayered declarations
form the final layer. This interval cut can expose an earlier normal declaration
beneath a later important declaration. The [source trace](research/revert-layer-trace.md)
records the pinned/current specification interpretation and its exclusions.

The evaluator terminates by strict candidate-count decrease and is sound against
an independent repeated-maximal-selection relation. Terminal literal provenance,
profile preservation and compatibility with ordinary cascade selection when no
rollback exists are proved. Exact length-bounded normalization agrees with the
unbounded evaluator; it is a proof reduction aid, not a retry cutoff.

`LayerStyleRule` admits only one author context without inline attachment; its
candidate generator proves that restriction. Selector applicability feeds the
rollback relation and then the same property defaulting/inheritance model.
Tied cascade keys retain the soundness-only boundary. Twelve paired stylesheets
provide thirteen kernel-checked visibility predictions, including important
intervals, unlayered rollback, repeated rollback, inherited defaults and initial.

```sh
python3 browser_check.py --fixture-suite layers --lake /path/to/lake --firefox /path/to/firefox
```

Fresh Nightly comparison matches all thirteen queries and passes both rejection
controls; [source-bound evidence](research/layer-browser-evidence.json) records
that finite result. Generated rollback after substitution, custom
rollback before binding construction, other origins, inline exceptions, nested
layer normalization, shorthands/aliases, animation and registration remain
outside this direct ordinary-property profile.

## Direct custom-property layer rollback

`LayerCustomCascade` resolves direct typed rollback before building unique
custom-property bindings. Every lookup equals its retained-candidate result;
terminal expression provenance includes the original matching named rule.
Dependency edges therefore come from expressions selected after rollback.
Exhaustion can occur despite applicable declarations, so it is not identified
with absence of matching rules.

`LayerCustomStyle.compute_sound` connects that declarative selection to completed
custom environments and consuming ordinary-property values. Both keyword models
prove an explicit missing-inheritance law. Thus exhausted custom declarations
inherit their parent's computed value, while selected initial, cycles or invalid
expressions keep their existing behavior. Equality of selected raw expressions
at all nodes/names preserves the computed pipeline.

Eleven paired stylesheets cover discarded and newly exposed cycles, inherited
exhaustion, selected initial and empty values, exact names, important intervals,
and keyword completion before dependent reads.

```sh
python3 browser_check.py --fixture-suite layer-custom --lake /path/to/lake --firefox /path/to/firefox
```

Fresh Nightly comparison matches all eleven queries and passes both rejection
controls; [source-bound evidence](research/layer-custom-browser-evidence.json)
records the finite result. This bridge permits direct rollback in custom
declarations; its ordinary-property rule path is the existing nonrollback
pipeline. Generated rollback remains excluded, particularly its interaction
with active custom-property cycles; see the open design boundary in the
[source trace](research/revert-layer-trace.md). Other origins, inline exceptions,
registration and raw parsing are also outside this profile.

## Closed raw values through computed styles

`RawTokens` and `ValueSyntax` parse a deliberately small raw character language:
`visible`, `hidden`, `collapse`, `initial`, `inherit`, `unset` (ASCII case variants
included), exact custom names matching `--[A-Za-z]+`, balanced `var()` calls
(with ASCII-insensitive function recognition), CSS whitespace and token sequences.
Maximal identifier scanning prevents keyword-prefix splitting. Omitted and empty
fallbacks remain distinct; adjacent functions and closed comments at token
boundaries are accepted. Escapes, non-ASCII identifiers, general tokens, computed
variable names, comma literals and EOF recovery remain unsupported. A rejected string may still be valid CSS.

The executable lexer and parser are proved equivalent to independent inductive
grammars. Canonical serialization parses back to every valid sequence AST; this
is not CSSOM serialization. Lexer recursion decreases remaining character length.
The parser's input-length budget is proved sufficient for every grammar derivation,
so it introduces no arbitrary nesting cutoff. Lowering preserves the full value
and state of guarded evaluation, including traversal after a failed first reference.

`ParsedDeclaration` retains custom token sequences, including empty values.
Ordinary values without references are decoded before entering the cascade;
accepted values with references enter as pending expressions. Failure after
substitution defaults without reviving an earlier declaration. No-reference
substitution independence justifies static decoding under an empty environment.
The fixture builder separately rejects unsupported raw parsing before it can
omit a supported direct value that fails the closed property grammar.

`ParsedBrowserFixtures` stores each raw value once: the verified parser supplies
its model expression, and a fixed rule template inserts the same string into the
browser stylesheet. The initial checkpoint has thirteen scenarios and fourteen
queries, including the
difference between direct `visible hidden` rejection and deferred invalidity after
`var()`. Selector templates, property metadata, declaration construction and the
DOM adapter remain outside the raw-value proof; this is not a stylesheet parser.
Primary interpretation and limits are recorded in
[the parser design](research/value-parser-design.md).

```sh
python3 browser_check.py --fixture-suite parsed-values --lake /path/to/lake --firefox /path/to/firefox
```

At that checkpoint, local Nightly agrees with all fourteen queries, and both
rejection controls pass.
[The source-bound evidence](research/parsed-values-browser-evidence.json) records
this finite comparison separately from the grammar and evaluator proofs.


### Closed comments at token boundaries

`CommentScan` stops at the first closing delimiter, with success equivalent to
an independent relation that forbids skipping that delimiter. Its strict suffix
length theorem supports lexer termination. `RawTokens` resumes tokenization
after a closed comment; it never removes comments from the raw string first.
Thus `visible/**/hidden` remains two identifiers and `var/**/(` never becomes a
function token. Comment contents do not nest and contribute no value token.
Canonical serialization still emits spaces and does not preserve comments.

Unterminated comments remain unsupported. Inserting such a raw value into a
stylesheet could consume the template's semicolon, brace and subsequent rules;
value-only EOF recovery would not justify that surrounding adapter. The source
trace and this scope choice are recorded in
[the comment tokenizer design](research/comment-tokenizer-design.md).

Eight additional generated stylesheet scenarios bring the current suite to
21 scenarios and 22 queries. They exercise empty custom values, direct versus
pending property-grammar failure, completed keywords, and comment-contained
rule punctuation. Local Nightly agrees with all 22 queries, and both rejection
controls pass. [The comment-extension evidence](research/comment-values-browser-evidence.json)
binds the results to this checked source; the earlier fourteen-query record remains
available for its historical checkpoint. Comment bodies are opaque and may
contain characters outside the restricted atom/name alphabet.


### ASCII recognition and exact custom names

`AsciiCase` folds only ASCII A through Z. Keyword and function recognition use
that operation; identifier tokens and sequence atoms retain their original
strings. Custom names are never folded: `--A` and `--a` select different bindings.
Function casing is canonicalized by the existing `varOpen` token, so serialization
preserves stored atom/name spelling and emits canonical `var(`. Source bytes and
original function casing are not promised to roundtrip.

The visibility adapter classifies mixed-case atoms into its closed typed keyword
domain. This supports computed visibility comparisons, not serialization or
inspection of arbitrary computed custom-property token text. Digits, underscores,
non-ASCII names, escapes and broader token types remain outside the accepted
language. See [the ASCII case design](research/ascii-case-design.md).

Nine additional generated scenarios bring the current suite to 30 stylesheets
and 31 queries. They distinguish exact name identity, missing differently cased
references, function recognition, and generated mixed-case CSS-wide keywords.
Local Nightly agrees with all 31 queries and both rejection controls pass.
[The case-extension evidence](research/ascii-values-browser-evidence.json) retains
the exact profile and source hashes. General adapter theorems establish raw
grammar acceptance and preservation of custom declaration names.


### Explicit element scope and DOM lookup

`GenericRecursiveSyntax` parameterizes recursive matching by observation atoms.
The previous recursive API is its exact empty-atom specialization; generic
embedding laws preserve matching, specificity and the nesting restriction.
`ScopedSyntax` supplies explicit element-root membership with class specificity.
The same roots reach logical arguments, nth filters and relative paths while a
`:has()` path's anchor changes independently. Empty root sets have no implicit
fallback. Arbitrary root lists are abstract observations, not claims that every
list is a valid DOM query input.

`ScopedElement.elementMatches` sets the receiver as subject and sole scope root.
`closest` retains that receiver while traversing inclusive ancestors; its
independent first-match relation and executable iff forbid skipping an earlier
match. Termination follows parent depth without a cutoff. Query membership is
strict-descendant eligibility plus matching against the full forest with fixed
receiver scope. The receiver can participate as a selector ancestor while being
excluded from final query candidates. This membership module makes no ordering claim; the ordered extension below
derives querySelector first results and querySelectorAll lists from child order.

The same-forest selector model instance connects explicit scope to the generic
style pipeline, without claiming browser stylesheet-scope behavior. Virtual
Document/DocumentFragment/ShadowRoot contexts, implicit scope fallback, shadow
featurelessness and @scope rules/proximity remain excluded. The raw parser below
covers a smaller selector language.
Element receivers living in fragments are distinct from Fragment API receivers.
See [the scope interface trace](research/scope-context-design.md).

The dedicated `scope` browser suite checks 15 Element.matches calls, eight
closest results and eight querySelectorAll membership observations against the
model. All 31 agree with local Nightly. Four controls reject an inconsistent DOM
snapshot, swapped child order, a flipped expected result, and a changed query
receiver. [The scoped lookup evidence](research/scope-browser-evidence.json)
retains exact sources and outcomes; this finite comparison is not general DOM
or selector refinement. Run it with `browser_check.py --fixture-suite scope`.


### Ordered element queries

`ContentPreorder` derives a depth-first element preorder from the complete ordered
child lists. A maximum depth derived from the finite domain justifies downward
recursion; it is not a search cutoff. An independent `Traversal` relation proves
the exact visit/child-concatenation order, alongside completeness and no duplicates.
Equal child lists give equal traversals even if node enumeration or depth witnesses
differ. The concrete fixture deliberately reverses its finite node enumeration.

`OrderedQueries` filters strict descendant preorder with fixed receiver scope.
Independent `Selected` and `FirstMatch` relations describe stable filtering and
the first successful candidate, including every skipped failure. Their composition
with `Traversal` characterizes both APIs without assuming the executable traversal
is already correct. General membership, order-preserving sublist, no-duplicates,
first-result absence and uniqueness laws are checked.

This is an element-only, no-shadow interpretation of DOM preorder. The supplied
direct child order must correspond to the DOM; omitted text/comment/processing
instruction nodes are leaves with no element descendants. There is no universal
DOM projection theorem. Virtual roots, shadow-including traversal, pseudo-element
results, mutation timing and WebIDL NodeList allocation remain outside the model.
The next module connects a bounded raw selector language to these ordered APIs. See [the ordered query design](research/ordered-query-design.md).

Seventeen deeper-tree cases compare exact querySelectorAll sequences and
querySelector first results: all 34 observations agree with local Nightly. Cases
include ancestors above the receiver, duplicate/unsorted selector branches and
fixed scope inside nested filters. Five controls cover snapshots, child order,
changed receiver, a reversed expected sequence and irrelevant domain-enumeration
reversal. [The ordered query evidence](research/ordered-query-browser-evidence.json)
records the checked sources. Run `browser_check.py --fixture-suite ordered-queries`.
The earlier scope suite remains a separately versioned membership/closest profile.

### Closed raw HTML selector queries

`SelectorTokens` preserves identifier spelling, whitespace tokens and contiguous
hash tokens. Closed comments are skipped between tokens: `div/**/.a` remains one
compound, while `div/**/ .a` has a descendant combinator. A canonical serializer
uses comment boundaries to preserve every valid token sequence; it is not a
bytewise source inverse. Lexical matching uses actual remaining input length.

`SelectorText` parses a nonempty list of compound/combinator chains. Its executable
parser is equivalent to independent state-transition and finish relations, which
share structural AST helpers. `SelectorValidity` proves accepted raw input has
valid, nonempty compounds. `SelectorLowering` connects independent compound/chain
matching and specificity to the existing scoped semantics. Top-level branches
remain separate; the query disjunction is not a cascade specificity calculation.
These are interpreted grammar proofs, not an extracted W3C grammar theorem.

The accepted profile contains type/universal/ID/class/:scope selectors, the
attribute and eight structural pseudo forms described below, four combinators
and top-level lists.
Names use `[A-Za-z][A-Za-z0-9_-]*`. Type and pseudo recognition fold ASCII in the
HTML standards-mode profile; ID/class spelling and repeated constraints stay
exact. Namespaces, escapes, broader identifiers, logical/relative function parsing,
pseudo-elements and forgiving recovery are unsupported.
Parser rejection does not imply that the source is invalid CSS.

The `parsed-selectors` suite supplies the identical raw string to the verified
parser and native query APIs. It checks HTML content type, standards mode and
all element namespaces before comparison. Thirty-three sources produce 66
ordered-list/first-result observations; local Nightly agrees with all of them.
Six controls exercise snapshot fidelity, child order, expected outcomes, receiver
scope, irrelevant enumeration, and rejection of a foreign-namespace fixture.
[The selector parser evidence](research/parsed-selector-browser-evidence.json)
retains the versioned profile and source hashes. DOM construction and its element
projection remain adapter obligations; no general browser refinement is claimed.
See [the parser design](research/selector-parser-design.md).

### Parsed selector and value fields through computed style

`ParsedSelectors` accepts the closed selector grammar while rejecting every
parsed `:scope` occurrence. Comments containing that text remain harmless.
Accepted branches preserve their raw-chain matching and specificity, and their
matching and selected list weight are independent of supplied scope roots.
Top-level weights use only matching branches, including repeated constraints.

`ParsedStyle.RawRule` supplies selector text, a typed ordinary/custom property,
raw value text and typed importance. Both raw fields must parse. Outer failure
means unsupported input; accepted omission means a no-reference ordinary value
fails the closed property grammar before cascade. Pending `var()` values retain
their declaration until computed-value checking. Empty custom values remain
present. Rules preserve exact custom names and author/importance/source-order
metadata; omitted declarations still consume their original list position.

Independent rule-list processing and metadata/provenance laws connect acceptance
to `CustomStyle`'s declarative pipeline. The final result is soundness through
matching, custom cascade, guarded computation, keyword completion, inheritance
and ordinary-property defaulting. Tied cascade keys retain the existing
soundness-only boundary. The general theorem takes an explicit selector model;
the browser fixture supplies the scoped HTML interpretation with empty roots.

The `parsed-style` suite generates each stylesheet from the same raw selector
and value fields that the model parses. Twenty-four scenarios produce 25 visibility
queries, all agreeing with local Nightly. Snapshot, flipped-outcome and foreign-
namespace rejection controls pass. [Evidence](research/parsed-style-browser-evidence.json)
retains source hashes and the explicit HTML profile. Braces, property choice,
importance suffixes and rule ordering remain template/metadata inputs: this is
not a whole-stylesheet parser. Layers, inline declarations, other origins,
stylesheet scope, broader raw syntax and general browser refinement are excluded.
See [the interface design](research/parsed-style-design.md).


## Raw attribute selector extension

`QuotedString` proves an independent first-closing-delimiter relation equivalent
to the scanner, exact decomposition, suffix decrease, and serialization. Quoted
payloads preserve comment-like text and the opposite quote. This closed profile
requires a closing quote and printable ASCII, excluding backslash and the active
quote; escapes, newline errors, EOF recovery and general Unicode are unsupported.

`AttributeText` adds presence and all six value operators, identifier/quoted
values and explicit `i`/`s` flags to the existing raw selector pipeline. Operator
characters may be separated by comments but not whitespace. Transition grammar
and validity proofs preserve exact payloads, class-level specificity and explicit
scope behavior through lowering. Unprefixed attributes use the null namespace.
The HTML profile lowercases names and uses the pinned 46-name default-insensitivity
table; explicit flags override that default. XML/foreign-element and quirks-mode
interpretations remain separate adapter obligations.

Forty raw selectors yield 80 ordered-list/first-result comparisons against the
same DOM fixture with exact attribute readback. The 41 parser checks also cover
unsupported input, comment boundaries, repeated specificity and flag normalization.
See [the source/design trace](research/attribute-parser-design.md) and run
`browser_check.py --fixture-suite parsed-attributes` with the existing required
`--firefox` and `--lake` arguments. Browser agreement is reported separately from
kernel proof; no generic browser-parser refinement is claimed.

The comment-separated operator `[data-list~/**/=alpha]` is retained as a visible
specification/browser divergence: the model accepts separate delimiter tokens,
while Firefox 158/160 and Chrome 155 reject it. The current required browser gate
covers 78 observations; these remaining two observations keep their mismatches
and errors in the report. This is a cross-engine/spec discrepancy pending CSSWG
interpretation, not a claim of a Firefox defect. The standalone reproduction is
[attribute-operator-comments.html](research/attribute-operator-comments.html).


## Raw structural pseudo-classes

The raw parser recognizes `:root`, `:empty`, `:first-child`, `:last-child`,
`:only-child`, `:first-of-type`, `:last-of-type` and `:only-of-type`, including
ASCII case folding and comment boundaries after the colon. `StructuralPseudo`
interprets these through the existing document, content and sibling models.
Its boundary laws characterize first/last by absence of earlier/later qualifying
siblings, and only by absence of another qualifying sibling. Typed filters use
the subject's namespace and local name; the two only forms each carry one
pseudo-class of specificity.

The explicit `EmptyProfile` now flows through raw declarative matching, lowering,
matching-branch specificity and the stylesheet facade. This preserves the
separation between strict browser text handling and the draft document-whitespace
interpretation. Scope-root independence remains proved for accepted stylesheet
branches, while actual `:scope` continues to require an explicit query receiver.

Thirty-three normalized cases cover detached/fragment groups, repeated types and
same-local-name/different-namespace siblings. Thirty-five same-string browser
fixtures cover parsed forms, root matching, typed predicates on the left of a
combinator, attributes, case/comments and receiver scope. Two draft `:empty`
observations remain separate. The computed-style suite includes only-child and
only-of-type competing against their higher-weight first/last conjunctions.
Indexed functions are covered by the later package below. Escapes, namespace
syntax, logical/relative functions and forgiving recovery remain unsupported.

## Standalone An+B arguments

`AnBTokens` preserves integer-form number signs and magnitudes, maximal
identifier/dimension boundaries, whitespace and closed comments. Independent
lexical relations are equivalent to the scanners, with strict suffix-decrease
proofs. Decimal/exponent continuations are rejected explicitly; they cannot be
misread as integer dimensions. Escapes, broader identifiers, strings, blocks,
functions and EOF comment recovery remain outside this lexer.

`AnBText` implements the eighteen alternatives of Syntax 3's `<a-n-plus-b>` token
grammar within that profile. Its independent grammar distinguishes signed and
unsigned offsets, embedded negative suffixes, and the special no-whitespace rule
after an initial plus. Parsing is sound, complete and unique for that grammar;
raw matching composes with the existing positive-index arithmetic relation.
Canonical source rendering roundtrips every pair of mathematical integer
coefficients. It is not CSSOM serialization or a bytewise source inverse.

Forty token cases, six canonical cases and 98 raw cases cover the grammar and
boundary distinctions. Every required raw case separately proves lexical
support; twelve additional controls exercise unsupported lexical forms.
The `anb` browser suite inserts the identical argument into a fixed
`:nth-child(...)` template. Forty-nine accepted arguments at three sibling
positions and 49 expected `SyntaxError` rejections give 196 observations.
The harness verifies the DOM snapshot and named exception behavior, including
a control that replaces a rejected selector with a valid one.

This standalone checkpoint originally used a fixed function wrapper. The later
indexed package below adds whole-selector source parsing; the later optional
`of` package adds one level of closed selector lists. Browser numeric limits
and general parser/DOM refinement remain excluded. See [the design](research/anb-parser-design.md)
and [browser evidence](research/anb-browser-evidence.json).


## Raw indexed pseudo-classes

The raw parser now accepts `:nth-child()`, `:nth-last-child()`, `:nth-of-type()`
and `:nth-last-of-type()` without an `of` list. Function names must be contiguous
with their opening parenthesis. `FunctionBody` preserves exact argument bytes,
including comments and bounded quoted strings, while checking nested delimiters
and a mandatory closing delimiter. Its independent transition relation, exact
suffix law and serializer composition are kernel checked. Outer `url` names are
excluded because CSS tokenization gives them special handling.

This scanner proves a closed balanced-source fragment, not arbitrary CSS
component-value parsing. Nested bad-URL recovery can group source differently;
accepted An+B bodies cannot contain such nested functions. Escapes, broader
identifiers, EOF recovery and mismatched delimiter recovery are unsupported.
See [the source boundary review](research/function-source-profile-review.md).

`IndexedPseudo` reads each evaluated subject's namespace and type, including
subjects on the left of combinators. Each family has one pseudo-class weight.
General rank laws prove forward plus reverse rank equals the filtered sibling
count plus one, and each rank is bounded by that count when the subject is
included. These laws apply to arbitrary Boolean sibling filters, allowing later
recursive filters to reuse them.

`IndexedSelectorText` composes canonical An+B rendering, valid closed bodies,
selector token serialization and the raw grammar: every indexed family and
mathematical integer coefficient pair has a source string that parses back to
its selector. This is not CSSOM serialization or a browser numeric-limit claim.
Existing matching, specificity and stylesheet scope-independence proofs extend
through the new observation constructor.

The package adds 38 scanner cases, 16 exact function-token/roundtrip cases,
34 normalized indexed cases, 61 whole-selector browser fixtures, ten separate
unsupported-source controls and five specificity checks. The browser fixtures
include 47 Boolean outcomes and 14 explicitly invalid `SyntaxError` outcomes.
Valid optional `of` forms and EOF recovery are outside that required error gate.
Three added cascade scenarios distinguish implicit type weight, repeated pseudo
weight and unmatched high-specificity branches. Run `browser_check.py
--fixture-suite parsed-indexed` with the usual `--firefox` and `--lake` arguments.
No generic specification translation or browser refinement theorem is claimed.


## Bounded optional `of` selector lists

`OfSelectorText` extends the raw selector profile with `:nth-child(An+B of S)`
and `:nth-last-child(An+B of S)`. `S` is a nonempty, unforgiving list accepted
by the earlier selector parser: types, IDs, classes, attributes, combinators,
scope, structural pseudos and indexed functions without their own `of` list.
Nested `of`, logical functions, relative `:has()`, pseudo-elements, namespace
syntax, escapes and recovery remain unsupported. A rejected source is not
necessarily invalid CSS.

`OfPrefix` uses the bounded An+B lexer to stop at a separate case-folded `of`
identifier, with exact source-suffix preservation and mandatory progress. It
neither strips comments nor joins lexical units. `OfArgument` proves the formula
and prefix split together; suffix validity is deferred to the selector parser.
This keyword boundary is relative to the ASCII lexical profile. Non-ASCII or
escaped identifier continuations can appear in a rejected split suffix, but the
outer closed selector parser never accepts those continuations as a valid list.

The extended grammar records both the suffix's independent raw parse and its
lowered syntax. It evaluates the list before assigning sibling ranks, retains
fixed scope roots across all siblings, and adds one pseudo-class weight to the
maximum *syntactic* argument weight, including unmatched branches. A generic
state-runner theorem preserves transition/finish correspondence without imposing
a fixed nesting fuel. The nonrecursive suffix parser makes this profile's one
level of `of` explicit.

`ScopedScopeFree` checks syntactic absence of scope through every recursive
constructor and proves root independence. It is sufficient, not necessary:
contradictory scope-bearing syntax may be semantically independent. The stylesheet
facade uses this check, so a scope-bearing branch inside an `of` filter cannot
enter the implicit-root style profile. Scope independence does not establish
selector validity or nested-`:has()` admissibility.

`OfSelectorCanonical` gives a whole-source roundtrip for arbitrary mathematical
coefficients and directions, conditional on an accepted base suffix and an
explicit closed-body witness for that exact suffix. Arbitrary valid selector
token lists need not be balanced; token validity alone is not that witness.
Separate laws prove syntactic maximum weight and equivalence of universal `of`
filters to unfiltered child/reverse-child matching and specificity.

The package adds 34 exact prefix/formula/suffix cases, 15 recursive scope checks,
55 raw browser fixtures (41 Boolean outcomes and 14 explicitly invalid named
SyntaxErrors), eleven unsupported controls, seven specificity checks, six style
admission checks and three rendered cascade scenarios. The latter distinguish
unmatched argument-ID weight, a universal argument's zero weight and list maximum
versus sum. Run `browser_check.py --fixture-suite parsed-of` with the usual
browser/toolchain arguments. General CSS tokenization, prose translation,
DOM projection and native browser refinement remain separate obligations.

## Bounded raw negation and reusable parser extensions

`NegationSelectorText` adds unforgiving `:not()` arguments to the raw profile.
Arguments are complete, nonempty complex selector lists accepted by
`OfSelectorText`, so they may contain one-level optional `of` filters. Multiple
sibling `:not()` occurrences are supported. Nested `:not()`, negation inside an
`of` filter, nested `of`, forgiving `:is()`/`:where()`, and relative `:has()` remain
unsupported. Existing ASCII, namespace, closed-body and recovery exclusions
still apply. This staging is explicit; rejection does not establish CSS invalidity.

The independent argument grammar retains the entire raw-list parse. Matching
negates whether any argument branch matches the same subject under the same
scope roots. Specificity is the maximum syntactic argument weight, including
unmatched branches, with no added pseudo-class unit. The style facade checks
scope absence recursively through negation and its nested filters. It does not
implement stylesheet recovery for an invalid selector rule.

`SelectorExtension` proves extension-first transition, run, raw-parse, validity,
uniqueness and query-matching correspondence once for a supplied parser profile.
The prior optional-of executable equations remain unchanged and have checked
pointwise equalities to this generic instance. Negation supplies a second small
profile, using the optional-of parser both as its fallback and as its argument
parser. `FunctionPayloadBound` separately proves that every emitted function
body is strictly shorter than the containing source, a prerequisite for future
well-founded recursive parsing; arbitrary recursive raw syntax is not yet claimed.

`NegationSelectorCanonical` proves exact whole-source construction from an
accepted argument list and an explicit closed-body witness for that same text.
The package includes 30 argument-level cases, 44 same-text browser fixtures
(32 Boolean results and 12 named SyntaxErrors), eleven unsupported controls,
eight specificity checks and six style-admission checks. Three rendered cases
distinguish unmatched argument-ID weight, no additional pseudo-class unit, and
maximum rather than sum. Run `browser_check.py --fixture-suite parsed-negation`
with the usual browser/toolchain arguments. Specification interpretation and
DOM projection remain manual boundaries; browser comparisons are finite evidence.


## Recursive unforgiving selector functions

`RecursiveSelectorText` removes the earlier staging restriction for `:not()` and
optional `of` arguments. These functions may nest in any supported combination;
all four indexed families remain available. The parser terminates by strictly
decreasing source length, with an explicit guard discharged for every actual
function token and optional-of suffix. It uses no fixed nesting fuel. Native
browser depth, numeric and resource limits are not modeled.

An independent positive mutual grammar records raw lexical proofs, state runs,
function arguments and lowered syntax. Pseudo/function positions dispatch
exclusively to that grammar; other positions retain the base selector grammar.
The parser is proved equivalent to this grammar for every source. The An+B and
optional-of argument languages are proved disjoint, so executable priority cannot
silently discard a valid grammar production. General state-run correspondence
only needs callback equivalence for tokens actually present in the source.

Every successful base, optional-of and bounded-negation parse is proved to remain
successful with exactly the same chains. Raw matching, uniqueness, validity,
style scope-independence and canonical source construction carry through the
recursive grammar. Canonical `not` and `of` constructors still require an
accepted argument and an explicit closed-body witness for that exact text.

This remains the closed ASCII, standards-mode HTML profile. Forgiving `:is()` and
`:where()`, relative `:has()`, namespaces, pseudo-elements, escapes, non-ASCII names,
EOF recovery and general CSS component recovery are unsupported. The earlier
checkpoint-specific nesting exclusions remain true of their older parser APIs;
the current stylesheet facade uses the has extension described below.

The new corpus has 43 same-text cases (33 Boolean outcomes and ten named
SyntaxErrors), eight unsupported controls, seven specificity checks and seven
style-admission checks. Three more rendered cases distinguish double-negation
weight, unmatched IDs inside negated filters and nested indexed pseudo units.
Run `browser_check.py --fixture-suite parsed-recursive` with the usual arguments.
Proofs concern the explicitly defined grammar and tree model; finite browser
agreement does not establish full CSS or Stylo refinement.


## Supported logical lists and explicit empty arguments

`LogicalSelectorText` adds `:is()` and `:where()` with arbitrary supported nesting
through the recursive parser. This source profile requires every nonempty
argument branch to parse. A failing branch makes the source unsupported; it is
not discarded. Full forgiving parsing, including `:is(p,)`, unknown branches,
pseudo-element branches and valid unmodeled functions, remains outside the model.

An empty body has a separate `EmptySelectorSource.Empty` witness: successful
lexing and only whitespace tokens, with comments consumed by the lexer. It is
proved incompatible with a selector derivation for any function grammar. Thus
valid empty/comment-only arguments become an empty selector list without treating
an arbitrary parse failure as empty. Empty `is` and `where` match nothing. `is`
uses the greatest syntactic argument specificity, while `where` and its arguments
contribute zero. Both retain the same subject and scope roots. The style facade
still rejects scope hidden below zero-weight arguments.

The common `SelectorRecursion` engine proves length-decreasing parsing from
explicit grammar/callback obligations. The earlier recursive executable equations
remain unchanged, with arbitrary-input equality to the common engine. Every
successful old recursive parse also embeds into the logical grammar with exactly
the same chains. Canonical `is`/`where` construction preserves accepted arguments
or an explicit empty witness, plus the exact closed-body premise.

This package adds 15 lexical-empty cases, 39 required Boolean browser cases,
14 unsupported controls, eleven specificity checks, nine style-admission checks
and four rendered cascade distinctions. Four additional native-only observations
show browser behavior for unsupported forgiving forms. Their expected fields
are native probes, not model matching predictions: the kernel check establishes
that the model rejects those sources. They are separately labeled in reports.
Run `browser_check.py --fixture-suite parsed-logical` with the usual arguments.
In this logical parser API, relative `has` remains excluded; the current facade
uses the extension below. Namespaces, escapes, broader names, component recovery
and browser resource-limit equivalence remain excluded. No generic CSS/Stylo
refinement is claimed.


## Closed relative selectors and has

`HasSelectorText` accepts `:has()` over a nonempty, unforgiving list of relative
selectors. Each branch has an explicit initial child, adjacent or following axis,
or an implied descendant axis. Token partitioning has an independent separator
relation, exact reconstruction and no internal separator tokens. Quoted strings
and function bodies retain their commas as payload; every resulting branch must
parse completely as exactly one chain. This is not a general CSS component parser.

The argument parser uses the prior has-free logical profile and explicitly checks
that each lowered chain contains no has. Its grammar keeps that premise visible.
Outer has-enabled functions may occur inside not/is/where/of, but a has argument
cannot contain another has. A nested has under forgiving is/where can still be
valid native CSS after recovery; such inputs are unsupported here, not classified
as required syntax errors. No general has-free theorem for arbitrary future
logical-parser extensions is assumed.

Relative lowering has a declarative endpoint relation and a continuation proof
that preserves traversal order across chains. The relative anchor is the current
subject; caller scope roots stay fixed at every endpoint. Initial axes add no
specificity. Relative branches use their syntactic maximum, including unmatched
branches, with no extra has pseudo-class unit. The explicit no-has premise proves
admissibility of each constructed has expression. The style scope check traverses
the relative path, including zero-weight logical syntax.

The same recursion engine supplies full raw-parser correspondence; every prior
successful logical parse embeds with identical chains. Canonical has source
construction retains both exact relative-argument acceptance and a closed-body
witness. The internal empty alternative path is a normalized zero/no-match value;
the source parser still proves that every accepted relative list is nonempty.

Coverage includes 29 normalized cases, 61 required same-text browser outcomes
(47 Booleans and 14 named SyntaxErrors), eleven unsupported controls, ten weights,
eight style-admission checks and four rendered scenarios. Two separate native-only
observations cover unsupported nested-has recovery inside forgiving functions;
the model checks rejection, not their native matching predictions. Run
`browser_check.py --fixture-suite parsed-has` with the usual arguments. No native
browser refinement, resource-limit equivalence, arbitrary components or full
forgiving recovery is claimed.


## Full parsed-tree has admissibility

`SelectorInvariant` proves a reusable Simple-predicate invariant through every
base parser transition, from an explicit before-state witness. It covers current
compounds, pending chains and completed branches, including attribute transitions.
`HasSelectorAdmissibility` instantiates it and performs a five-motive induction
through the positive recursive grammar. Every accepted chain and query now has
`noNestedHas = true`, and therefore normalized `hasDepth <= 1`.

This bounds nesting of has expressions, not total logical-function nesting or
native browser stack/resource use. It strengthens the earlier per-function
witness without changing the parser, accepted source profile or executable case
corpus. The latest native evidence remains the separately source-bound has
checkpoint in research/has-browser-evidence.json; this proof-only extension does
not claim that those browser reports were rerun against its additional files.


## Scalar input preprocessing and standalone escapes

`CssInput` implements the dated Syntax 3 preprocessing rules over Lean scalar
characters: CRLF collapses, CR/FF become LF, and null becomes U+FFFD. Independent
relations characterize execution, normalized output, fixed points, idempotence
and nonincreasing length. The domain excludes surrogate code units because Lean
Char cannot represent them; this is not a complete DOMString or byte decoder.

`CssEscape` consumes after a backslash. Its declarative hex relation has an
independent decomposition/maximality characterization and a six-digit bound.
Exactly one following normalized whitespace character is consumed. Numeric zero,
surrogates and values above the Unicode maximum produce U+FFFD. A nonhex escaped
character is retained. EOF returns U+FFFD with an explicit local recovery flag;
that flag is not a general CSS invalidity verdict or string-token EOF behavior.
The valid-caller interface rejects a following LF and admits EOF.

A canonical six-hex-digit renderer roundtrips every nonzero scalar character with
an arbitrary exact suffix. `CssEscapeInput` composes preprocessing and consumption,
proves normalization of the rendered prefix, and preserves the processed suffix.
Input normalization happens once: decoded CR/FF are retained as identifier data.
The total low-level consumer is defined beyond its caller domain; CSS claims use
the valid-caller/preprocessed interfaces. Source spellings, decoded values and
local recovery flags remain distinct.

This adds 24 preprocessing and 47 escape/composition kernel cases. Existing
selector tokenizers and the closed function-body scanner are unchanged; they do
not yet gain Unicode or escaped names. No new native browser run is claimed for
these standalone lexical foundations. Current name ranges/start predicates and
name consumption are covered by the separate package below; token integration
remains subsequent work.

## Dated name classes and decoded name consumption

`CssNameClasses` follows the explicit non-ASCII identifier ranges in CSS Syntax
3 CRD 1 October 2026, together with identifier-start, continuation, valid-escape
and three-code-point start decisions. It does not use the older blanket
non-ASCII predicate. The 85 boundary/start cases make that version choice visible;
no native agreement with the new table is assumed.

`CssName` separately specifies one consumed name unit, a maximal run and an
identifier caller. The scanner terminates by strictly decreasing source length,
including an EOF escape's consumed backslash. Its independent relation proves
exact raw prefix/remainder decomposition, maximal stopping, uniqueness and
nonempty decoded output for accepted identifiers. Name consumption permits
leading digits; the identifier caller applies the separate start decision.
Escaped punctuation, whitespace and decoded CR/FF can be name data. An invalid
newline escape ends the consumed prefix and leaves the backslash unconsumed.
Comments end a name; they are not removed inside this scanner.

Canonical names escape every nonzero scalar with six hex digits and a terminator.
The roundtrip holds for arbitrary nonempty decoded values, without revalidating
them as literal identifier characters. An arbitrary suffix is preserved when it
is a proved name boundary. `CssNameInput` preprocesses once and proves the same
canonical identity; its spelling/remainder theorem concerns the **preprocessed**
source, not an original raw offset mapping. The low-level relation remains broad:
a raw unnormalized escaped NUL can produce NUL, while the input facade replaces
it before scanning. `CssNameValueLaws` proves every accepted input value is
nonempty and nonzero, hence always has a canonical identifier spelling. There
are 57 further exact scanner/spelling/canonical cases.

These are standalone lexical foundations. Existing selector-tokenizer integration
and its function-body scanner remain unchanged; standalone hash and URL dispatch
helpers are described below. No new
browser run or escaped-selector admission is claimed. Scalar-only input excludes
surrogate code units and byte decoding; current source profile exclusions still
apply. See [the name/escape contract](research/name-escape-contract.md).

## Standalone hash-token flags

`CssHash` specifies the name-consuming branch after a number sign. Admission is
an initial name code point or valid escape; the **raw** identifier-start decision
sets the id/unrestricted flag before decoding. `#1` and an escaped spelling of
that same value therefore have different flags. The explicit `afterHash` result
keeps the number-sign delimiter alternative and its complete unconsumed suffix;
`parseInput = none` means no hash token at this prefix, not invalid CSS.

An independent relation proves exact execution, source decomposition and
progress, nonempty names and normalized-source nonzero decoded values. An
unrestricted name must begin with a decoded digit or hyphen; that necessary
condition is not a complete flag-realizability characterization. Canonical
rendering covers id hashes for every nonempty nonzero decoded value. It does
not preserve unrestricted flags by escaping arbitrary values. The 43 kernel and
runtime cases cover paired flags, exact remainders, delimiter recovery,
preprocessing, local escape EOF recovery and canonical id values.

This module leaves selector tokenizers and browser admission unchanged. Standalone ident-like/decoded-URL dispatch is covered below. Full-token CDC
priority, unrestricted hash serialization and escaped component bodies remain
separate work; URL-body consumption is covered below. No new
native browser run is claimed; see [the hash contract](research/hash-token-contract.md).

## Ident-like dispatch and URL continuation

`CssIdentLike` composes accepted name consumption with the next raw character.
The decoded name controls ASCII-insensitive URL recognition; an escaped opening
parenthesis in that value remains data. Ordinary function dispatch consumes only
the immediate opening parenthesis and leaves the complete body remainder. It
does not require or consume a closing delimiter.

For decoded URL names, `CssUrlDispatch` consumes whitespace only while the next
two characters are whitespace, retaining the last one. Literal quote or
whitespace-plus-quote then selects the function opener branch. All other URL
prefixes produce an explicit `urlInput` continuation with its exact remainder;
URL value accumulation and bad-URL recovery are provided by the separate
completion module below. Comments
and escaped quotes do not satisfy the literal quote test.

Independent relations prove both algorithms, exact source-prefix decomposition,
strict input progress and nonempty/nonzero normalized names. Canonical escaped
name/call rendering works for arbitrary nonzero decoded names and arbitrary body
suffixes; input composition explicitly preprocesses the body. The 24 trim/quote
and 47 dispatch/canonical cases distinguish these boundaries and EOF handling.

This is a standalone subalgorithm with an identifier-start caller premise. It
is not a full tokenizer: raw CDC and number priorities still belong to outer
caller dispatch. Existing selector source profiles and browser admission are
unchanged. The old closed opaque function-body scanner has a different role;
no general component-value correspondence or new native run is claimed. See
[the ident-like/URL contract](research/ident-like-url-contract.md).

## Unquoted URL consumption and recovery

`CssUrlToken` consumes unquoted URL bodies, with independent one-step/run
relations and a scanner that terminates by source length. Leading whitespace,
trailing whitespace, raw/escaped closes, escaped values, forbidden characters,
EOF and recovery each have explicit productions. `CssBadUrl` consumes remnants
through a raw close or EOF, skipping valid escapes so an escaped close cannot
end recovery. This recovery does not balance nested parentheses or strip comments.
`CssWhitespace` independently specifies maximal normalized whitespace runs.

Results keep the URL/bad-URL token, exact remainder and `parseError`. That flag
records explicit local parse-error instructions, not overall CSS invalidity.
In particular, whitespace followed by more content emits a bad-URL token without
an explicit error instruction in this algorithm. Forbidden-character and invalid
escape branches set the flag; EOF returns a recoverable URL token with the flag.
Bad-remnants scanning emits no additional error. Higher-level parser treatment
of these tokens is outside this flag's meaning.

`CssIdentLikeComplete` resolves the earlier URL continuation using these rules,
while retaining identifier and function-opener outcomes. Preprocessing occurs
once at the input facade. Exact consumed-source/remainder and nonzero-value laws
hold for normalized input. Canonical body and whole URL-token rendering cover
arbitrary nonzero scalar lists, including empty values and escaped controls,
quotes and parentheses. They preserve arbitrary suffixes; the input theorem
normalizes only that following source, preserving decoded CR/FF values.

The checkpoint adds 41 recovery/whitespace and 73 URL/composition/canonical cases.
It adds no selector-source admission or native browser run. Full tokenizer
CDC/numeric priorities, general component parsing and byte/surrogate input
remain outside the profile; standalone string consumption is covered below. The low-level URL body consumer
assumes an unquoted caller; the complete ident-like entry chooses quoted URL
function openers before calling it. See [the reviewed contract](research/ident-like-url-contract.md).


## Standalone string token consumption

`CssStringQuote`, `CssStringToken` and `CssStringTokenLaws` model the two
quote-delimited branches of the dated Syntax 3 string-token algorithm. Independent
step/run relations agree with execution, preserve exact source remainders and
prove strict progress after the opening quote. The body consumer intentionally
allows a terminal raw LF to remain unconsumed.

`CssStringRecoveryLaws` proves that every bad-string result retains an LF-prefixed
remainder and an explicit local error. Backslash EOF is ignored before EOF
recovery; backslash LF continues the string without adding a character. Escaped
LF/CR/FF are decoded value data and are never normalized again. Comment-looking
text, other quotes and raw non-newline controls remain ordinary string data.

`CssStringCanonical` and `CssStringValueLaws` prove normalized nonzero values and
canonical body/whole-source roundtrips for either quote, arbitrary nonzero scalar
lists (including empty values) and arbitrary following source. Re-rendering an
accepted recovered string preserves its value and deliberately produces a closed
string with no local error; it does not preserve the original spelling or
recovery diagnostics. The input facade preprocesses source exactly once.

The 70 new cases include 49 quoted-source boundaries, five deliberately broad
low-level body cases and 16 canonical cases. This is a standalone lexical
foundation: existing selector admission and opaque function-body scanning remain
unchanged. No browser execution, full tokenizer/component parser, byte decoding
or surrogate-code-unit model is claimed. See
[the string contract](research/string-token-contract.md) for pinned source and
integration boundaries.


## Standalone comment consumption

`CssComments` extends the existing closed comment scanner with an independently
specified unterminated-body relation and explicit EOF recovery. The whole-input
consumer removes adjacent leading comments and stops before whitespace or other
non-comment text. Quotes, backslashes and nested openers are ordinary body data;
the first raw closing delimiter ends the comment.

Proofs cover execution correspondence, exact compatibility with closed
`CommentScan` results, consumed-prefix/remainder decomposition, length bounds,
strict progress after an opener, maximal stopping boundary and idempotence.
Every explicit comment error implies an empty remainder. The input facade
preprocesses once; low-level body results retain exact raw suffixes.

The 36 cases cover repeated comments, EOF, overlapping delimiters, ordinary
quote/escape-looking content and raw versus normalized following input. This
standalone foundation does not change existing selector admission or native
browser evidence. See [the primary-source contract](research/comment-consumption-contract.md).


## General numeric tokens and exact decimal meaning

`CssNumberParts`, `CssNumberSyntax`, `CssNumberLaws` and `CssNumberInput`
verify general decimal prefixes with optional sign, maximal integer digits,
optional fraction and optional exponent. Independent relations agree with the
executable scanner. Number admission is separate from the broad low-level
consumer; accepted prefixes have valid fields, exact consumed spelling and
strict source progress. Incomplete exponent/fraction prefixes remain untouched.

`CssNumberValue` preserves a signed integer significand and decimal scale,
with the original optional sign and integer/number type retained separately.
Its universal rational-denotation theorem agrees with an independently expressed
signed integer-plus-fraction value multiplied by the decimal exponent. Thus
`1`, `1.0` and `1e0` can have equal mathematical values while retaining distinct
syntax/type information; `-0` retains its minus sign. Parsing never evaluates
large powers. Exact rational meaning does not assert browser floating-point
range, rounding or a negative-zero numeric representation.

`CssNumericToken` composes numbers, percentages and dimensions. Identifier-start
admission precedes a literal percent sign, and dimension units use the complete
decoded-name consumer. Percentages carry value/sign without the number type
flag. The laws preserve exact suffix/progress and normalized nonempty/nonzero
units. Local escape-EOF diagnostics imply an empty remainder; these flags do not
classify overall CSS validity.

`CssNumberCanonical` and `CssNumberCanonicalInput` preserve every valid decimal
field when rendering with a mandatory following space and arbitrary suffix.
That explicit boundary prevents merging into further digits, an exponent or a
dimension. The input and full number-token bridges preserve the separator and
normalize only following source. This is not a general bare-prefix or dimension
unit serialization theorem.

The package adds 127 cases: 55 prefix boundaries, 50 composed tokens, 12 exact
semantic comparisons and 10 canonical boundaries. Existing bounded An+B and
selector lexers remain unchanged, and no native browser execution is added.
The tokenizer priorities and special Unicode-range mode are covered below;
general component parsing remains separate. See [the numeric contract](research/numeric-token-contract.md)
and [the next dispatch contract](research/tokenizer-dispatch-contract.md).


## Guarded Unicode-range token consumption

`CssUnicodeRange` models the raw U/u-plus prefix, bounded hexadecimal and
question-mark segments, and optional explicit second endpoint. Its independent
relations agree with execution; the laws preserve exact suffixes and prove
strict guarded progress. The first segment has at most six combined hex and
question-mark positions. Wildcards replace their positions with zero/F for the
endpoints and leave any following explicit range untouched.

This lexical consumer deliberately accepts reversed endpoints, surrogate values
and values above the Unicode scalar maximum. It adds no endpoint clamping,
ordering validation or local parse-error flag. Descriptor validity is separate,
and callers must explicitly enable the special Unicode-range tokenizer mode;
the normal tokenizer mode does not produce these tokens.

`CssUnicodeRangeCanonical` renders two six-hex endpoints and proves exact
roundtrip for arbitrary endpoints below `16^6` and arbitrary following source.
The fixed width prevents following hexadecimal text from being consumed. The
input facade preprocesses once; the canonical theorem itself preserves raw
suffix characters.

The 51 cases distinguish wildcard bounds, incomplete second endpoints, reversed
and non-scalar ranges, escaped-prefix rejection, preprocessing and exact
canonical suffixes. Existing selector admission and browser evidence remain
unchanged. See [the Unicode-range contract](research/unicode-range-token-contract.md).


## Scalar token dispatch and streams

`CssTokenizer` combines the checked lexical consumers with at-keyword admission,
punctuation, delimiters, CDO and CDC. Its independent relation records the
priority guards explicitly. Comments are consumed before each token; numeric
admission precedes CDC and identifier handling. Escaped names keep decoded URL
dispatch, while raw hash admission determines the hash flag.

The single-call consumer proves exact source/remainder decomposition, normalized
remainders and strict progress for every non-EOF result. Invalid backslash-LF
produces a delimiter with a local error; escaped EOF follows identifier recovery.
String recovery may leave LF for the next call. These diagnostics record local
algorithm instructions and do not classify overall CSS validity.

`CssTokenStream` proves a generic finite stream relation agrees with a
well-founded driver. `CssTokenization.tokenize` preprocesses scalar input once
and defaults to Unicode-range mode disabled. Its public list excludes the
conceptual EOF sentinel, retaining the terminal call's diagnostic separately in
`terminalError`. Per-token errors stay attached to their token. The concrete
proofs establish no emitted EOF, a source-length token bound and an empty
remainder at the terminal call. No preprocessing is repeated between calls.

The package adds 135 cases: 25 at-keyword boundaries, 64 direct dispatch cases
and 46 complete streams. Numeric values remain exact symbolic values, with no
claim about browser floating-point conversion or limits. Existing bounded
selector parsers are not switched to this lexer; component grouping is covered below; general token serialization and
forgiving-selector recovery remain separate. There is
no new native browser run. See the [dispatch contract](research/tokenizer-dispatch-contract.md)
and [stream contract](research/token-stream-contract.md).


## Recursive component grouping and public lists

`CssComponentParser` consumes nested parentheses, brackets, braces and functions
over token sequences. Independent mutual `One` and `Body` relations agree with
execution. Matching closing tokens are consumed; mismatched closing tokens stay
as ordinary components. EOF terminates unfinished groups. The pinned 2026
algorithms add no local parse error merely because a block or function ends at
EOF. The old opaque `FunctionBody` source scanner retains its narrower mandatory
closing-delimiter profile.

The implementation has explicit fuel sufficiency proofs: every derivable parse
completes within the public source-length bound. The consumer is total for
nonempty token sequences without EOF tokens, and body consumption also accepts
empty input. Exact suffix, strict component progress, uniqueness and structural
well-formedness are proved. The single-component API returns no component for
empty input; its callers stop at conceptual EOF.

`CssComponentList` implements the separate public list policy. An explicit stop
token or a right brace in nested mode is retained in the remainder. A top-level
unmatched right brace is consumed and retained as a component, with a list error.
That error policy is not applied inside block/function bodies.
`CssComponentSource` composes scalar preprocessing, tokenization and complete list
grouping, preserving all lexical observations separately from its grouping error.
It proves totality and complete consumption of the projected token sequence.

`CssComponentCanonical` renders token sequences, not CSS source strings.
Structural well-formedness permits closing-token leaves, so it alone cannot
guarantee roundtrip. The stronger `Renderable`/`ContextSafe` predicates prohibit
a group's own matching close as a direct leaf. Every parser-produced tree
satisfies these predicates and renders with an arbitrary exact suffix roundtrip,
including trees recovered at EOF.

The 103 cases cover 31 type/equality checks, 36 raw-source scenarios, 12 list
policies, 8 single-component boundaries and 16 canonical cases. Fabricated EOF
tokens are tested only as out-of-domain controls. Existing selector admission
and native browser evidence remain unchanged. The comma-separated entry point is covered below; stylesheet/declaration
grammar and forgiving-selector recovery remain separate.
See the [component contract](research/component-token-contract.md).


## Comma-separated component entry point

`CssCommaComponents` follows the entry-point loop over a token stream: while
input remains, consume a public component list with comma as its stop token,
append that group, and discard one separator. Its independent `Groups` relation
agrees with execution, including strict progress for empty groups and totality
on noEOF token sequences.

Empty input produces no groups. The universal comma-run law proves that `n`
comma tokens produce exactly `n` empty groups. A trailing comma does not create
an additional group, while trailing whitespace creates actual component content.
Nested functions and blocks shield their commas through the accepted grouping
model; string, URL and escaped-name content remains token data.

`CssCommaSource` preserves all lexical observations and each group's local
grouping error. Its 36 independently authored source cases cover empty/trailing
groups, delimiter shielding, recovery, normalization and explicit range mode.
This is the generic Syntax entry point, with no selector-grammar or general CSS
validity claim. Single-component trimming and exact-one acceptance are covered below; no new
native browser run is added.


## Single-component entry and canonical domain

`CssSingleComponent` follows the entry-point rule: discard leading whitespace
tokens, require input, consume one component, discard trailing whitespace tokens,
and require exhaustion. Its independent relation distinguishes the accepted
component from empty-input and extra-component syntax errors. Execution agrees
on noEOF token sequences. Escaped whitespace inside decoded name/string data is
not a whitespace token and is not trimmed.

`CssSingleComponentSource` always returns the complete lexical observations and
an optional component. Absence means this entry point's syntax error, proved
equivalent to its empty/extra witnesses. Lexical diagnostics remain separate.
A standalone comma or closing brace can be one component; a recovered bad-string
or bad-URL token can also be one component. None of those results establish
validity under a property or selector grammar. The public-list right-brace error
policy does not apply to this entry point.

`CssSingleCanonical` characterizes the canonical token domain: a `Renderable`
component whose head is not a whitespace token. Every accepted output meets this
condition and roundtrips with arbitrary surrounding token whitespace. A
whitespace leaf is structurally valid but is trimmed away by the entry point.

The 52 cases cover 36 scalar-source expectations, 6 token boundaries and 10
canonical cases. Fabricated EOF tokens remain explicit out-of-domain controls.
No existing selector facade is switched, no native run is added, and token
rendering is not a general CSS source serializer. The separate leaf component
adapter below supports decoded selector names and ID hashes.


## Decoded component selector adapter

`ComponentSelectorTokens` converts ten component-leaf kinds into the existing
selector token alphabet: decoded identifiers, ID-flagged hashes, whitespace and
the supported punctuation. Names remain exact values. An escaped comma, colon
or dot is name data; an escaped leading digit can form an ID, while an
unrestricted hash is not promoted to one. Blocks, functions and the remaining
token kinds stay outside this first adapter.

`ComponentSelectorText` composes scalar preprocessing, complete tokenization,
component grouping and the existing unqualified selector grammar. Independent
conversion, accepted-parse and unsupported-attempt relations agree with
execution. A source attempt retains full component/lexer diagnostics even when
its selector result is absent. Unsupported input is not a proof of invalid CSS
and is never silently discarded as a forgiving branch. Matching and syntactic
specificity provenance are proved with explicit content context, empty profile
and original scope roots.

`ComponentSelectorCompatibility` proves a partial inverse for the ten old token
kinds and preserves exact token-parser results. This is not raw-source lexer
equivalence. Existing `ParsedSelectors` and `HasSelectorText` source facades and
old source-validity predicates remain unchanged. Native comparisons use the
HTML standards-mode unqualified selector profile; namespace-declaration
resolution and quirks mode are separate.

`SelectorNameSource` and `ComponentSelectorCanonical` prove complete source
generation for any nonempty decoded type, ID or class name containing no NUL
characters. Six-digit escape rendering passes through preprocessing, full token
dispatch, grouping and selector parsing to the exact name-bearing AST. This
handles punctuation, digits, Unicode and decoded whitespace without rescanning
values. It is a named-subset source serializer, not a general selector serializer.

The 147 new cases comprise 35 conversion checks, 48 same-source matching cases,
12 unsupported controls, 8 specificity checks, 8 retained-diagnostic checks and
36 canonical-source checks. The browser exporter preserves original strings,
including escape terminators, preprocessing controls and EOF recovery. Run
`browser_check.py --fixture-suite component-selectors` with the usual arguments.
Finite browser evidence is recorded separately; it does not prove prose
translation, DOM projection or native parser refinement. Atomic attribute blocks are covered by the extension below;
component-based function arguments remain next work. See the
[adapter contract](research/component-selector-adapter-contract.md).


## Atomic attribute components

`ComponentAttributeTokens` expands a bracket component only after converting its
complete supported interior. Decoded identifiers, strings, whitespace and
attribute operators are retained as token values; nested components and other
token kinds are unsupported. Structural bracket delimiters are supplied from
the grouped component, including a bracket recovered at EOF. Interior conversion
cannot emit bracket or comma tokens. `AttributeTokenBoundary` and
`AttributeAtomicity` prove that successful parsing keeps the same prepared
selector frame through the interior, completes exactly one attribute at its
closing boundary, then resumes on the exact remaining suffix.

String tokens no longer carry their source quote style. The adapter uses an
internal double-quote tag. `AttributeQuoteErasure` proves step commutation,
simulation, image correspondence and unchanged lowering under this operation.
It explicitly proves that the old quoted-source validity predicate need not
survive quote erasure; that predicate is not weakened or assumed here.

`ComponentSelectorProfile` shares the source/grammar/diagnostic composition.
Exact compatibility laws preserve the previous leaf adapter's full source
result, raw parse and query. The attribute profile preserves every previously
successful leaf parse with the same chains. Existing stylesheet and recursive
opaque-source facades remain unchanged. Attribute matching uses the existing
HTML standards-mode unqualified, namespace-null, ASCII case and modifier rules.

`AttributeCanonicalSource` and `ComponentAttributeCanonical` prove whole-source
presence/equality roundtrips for arbitrary nonempty names and arbitrary string
values containing no NUL. Empty values are supported. Escaped names, quotes,
controls and bracket characters pass through preprocessing, complete
tokenization and grouping to the exact attribute AST. General selector source
serialization is not claimed.

The 142 new cases include 26 token/list conversion checks, 8 retained-diagnostic
cases, 54 same-source matching pairs, 12 unsupported controls, 2 written-spec
operator discrepancy checks, 8 specificity cases and 32 canonical-source cases.
The required native suite is `browser_check.py --fixture-suite component-attributes`.
The separate `component-attribute-discrepancies` suite preserves the two known
comment-separated operator mismatches alongside an ordinary passing control.
It is expected to return a failing differential report; that report is retained
separately from required native agreement. The existing
[operator trace](research/attribute-operator-comments-trace.md) still classifies
this as an unresolved written-spec/cross-engine compatibility question, without
a Firefox defect or CSSWG-intent verdict.

A missing closing bracket adds no component-body error in the pinned revision;
an unterminated string retains its lexical error. Either may still supply an
accepted attribute grammar. Unsupported results are never inferred to be
certified invalid CSS or silently discarded. Namespace declarations, quirks
mode, component-based function arguments and full forgiving recovery remain
outside this extension.


### Full-component An+B arguments

`ComponentAnBTokens` converts complete lists of whitespace, decoded identifiers,
plus/minus delimiters and integer number/dimension components into the existing
An+B token grammar. Decoded names and units are used directly; the old ASCII
lexer validity predicate is not asserted. `ComponentAnB` composes that grammar
with full scalar preprocessing, tokenization and grouping. Its independent
accepted/unsupported relation retains all lexical and grouping observations,
including when the argument is unsupported.

`CssIntegerTokenBridge` retains optional signs and signed zero, checks integer
type, scale zero and exact sign/value consistency, and rejects inconsistent
fabricated records. Source-derived integer admission is proved from the number
consumer. Generic recursive leaf-invariant laws propagate that guarantee through
numeric dispatch, comments, the complete token stream and nested component
bodies. At the actual argument entry, a number or dimension leaf passes this
bridge exactly when its type is integer. `2.0n` and `2e0n` therefore cannot become
integer dimensions merely because their mathematical values are integral.

`ComponentAnBCompatibility` embeds every old An+B token list into components and
preserves its exact parser result. This is token-level preservation, not a raw
source lexer equivalence. `ComponentAnBCanonical.render` provides a universal
full-source roundtrip for arbitrary integer coefficients: rendered numeric
boundaries, complete tokenization, grouping and parsed coefficients are proved.
Huge coefficients remain exact in the model; native integer range and precision
are outside this correspondence.

The package adds 84 audited declarations and 146 exact cases: 24 integer bridge
cases, 64 raw argument admissions/formulas, 8 retained diagnostic results,
42 matching observations and 8 canonical source cases. The browser exporter
places each unchanged argument inside an explicit indexed-family wrapper and
compares the existing normalized rank semantics. Four of those strings come
from the public canonical renderer. Terminal-comment recovery and huge values
are model-only cases. Matching/specificity provenance applies to a parsed
argument plus an explicit family; no whole-selector source parser theorem is
claimed for these wrappers.

The existing selector facades remain unchanged. Optional `of`, arbitrary nested
component arguments, namespaces, quirks mode and full forgiving recovery remain
outside this standalone entry. Unsupported admission is not a certified CSS
syntax error. The separate package below admits decoded indexed function components
directly into the selector state machine, preserving component boundaries and
previous attribute-profile results. See
[the dated component indexed contract](research/component-indexed-adapter-contract.md).

### Decoded indexed function selectors

`ComponentFunctionTokens` adds an intact function variant to the previous atomic
attribute token stream. Decoded function names and grouped child components are
preserved exactly. Conversion proves that emitted base tokens never contain the
old raw-body function variant; no component payload is serialized back into a
raw body for parsing. Unsupported nested attribute components remain unsupported.

`ComponentFunctionParser` handles function tokens only in the pseudo-class name
state and delegates base tokens to the established selector machine. A failed
function argument does not fall back to another token interpretation. Its
independent transition/run grammar agrees with execution, and embedding any old
token list preserves the exact old parser result. `ComponentIndexedFunction`
recognizes the four decoded indexed names under ASCII case folding and parses
their complete child list through the full-component An+B grammar.

The source-profile abstraction now parameterizes both token carrier and parser.
Existing leaf and attribute profiles instantiate their original implementations;
explicit component/source/raw/query equalities preserve old results and all
retained diagnostics. `ComponentIndexedSelector` extends successful attribute
sources with exactly the same chains, while generic source matching/specificity
provenance applies to the new profile.

EOF-recovered functions and unterminated comments are grouped before argument
admission, with lexical and grouping observations retained. Escaped function
names, escaped units, compound and combinator subjects, namespaces in normalized
typed sibling filtering, and fixed receiver scope are represented without
changing the existing stylesheet facade. The profile still excludes namespace
syntax, optional `of`, logical/relational component arguments and full forgiving
recovery; unsupported admission is not certified CSS invalidity.


Whole-source canonical construction now proves an unconditional exact indexed
AST roundtrip for all four families and arbitrary mathematical integer
coefficients. It renders escaped family names, tokenizes the complete selector,
groups a real function component and applies the indexed grammar. Source
normalization and closing boundaries are proved separately. This theorem does
not depend on native numeric range or precision behavior.

This package adds 50 audited declarations and 108 exact cases: 12 converter
cases, 52 supported whole-selector matching cases, 20 unsupported controls,
8 syntactic weights, 8 retained diagnostic results and 8 canonical AST cases.
Four native source strings are produced by the public canonical renderer.
The browser exporter retains exact source text and complete context snapshots;
large integer canonical examples stay in the model-only corpus. The previous
attribute suite is retained as a browser regression gate.


### Recursive component negation and filtered indexing

`RecursiveComponentSyntax` admits nested `:not()` and the optional `of` selector
list of `:nth-child()`/`:nth-last-child()` over actual grouped components. Its
positive mutual grammar requires complete arguments. `ComponentOfArgument`
splits at the first direct decoded `of` identifier and preserves the exact suffix;
identifiers inside functions or blocks are not separators. The accepted prefix
is disjoint from plain An+B, which justifies executable dispatch priority.

`ComponentTreeSize` provides a computable structural count. Function-origin and
suffix bounds justify well-founded recursion without a fixed nesting cutoff.
`ComponentSelectorRecursion` proves execution agrees with the grammar and
removes every runtime size guard from the correspondence result. The generic
transition bridge requires callback correctness only for actual converted
function tokens. Previous successful indexed component sources retain exactly
their chains and queries under `RecursiveComponentSelector`.

Negation uses the syntactic maximum argument weight with no extra pseudo-class
unit. Filtered indexing adds one unit and keeps the original scope roots while
evaluating every sibling. Provenance laws connect both forms to the complete
parsed branch list, including unmatched high-specificity branches. The source
facade retains lexical and grouping observations even for unsupported input.

Canonical single-function source construction requires an explicit closed-body
tokenization and grouping witness, plus normalized body input. It preserves
those observations and derives the exact selector AST. This avoids assuming
that appending a closing parenthesis preserves an arbitrary EOF-sensitive body.
The earlier unconditional indexed canonical theorem remains available.

The package adds 66 audited declarations and 125 exact cases: 30 optional-of
prefix/split cases, 55 supported matching cases, 17 unsupported controls,
8 syntactic weights, 9 diagnostic results and 6 rendered-source AST cases.
Four browser strings use the public canonical constructor. Cases distinguish
nested filters and negation, escaped names/markers/closers, fixed scope across
sibling subjects, complete unforgiving lists, and EOF recovery. A mistaken
unsupported expectation for `:not(p\))` was corrected after the kernel case
failed: its escaped closer is type-name data, so the negation is supported.

This remains a separate component profile. The stylesheet and older raw-source
facades are unchanged. Component `:is()`, `:where()`, `:has()`, namespaces,
pseudo-elements, relative selector arguments, quirks mode, native numeric range
and precision, and general forgiving recovery remain excluded. An unsupported
model result is not a claim that the source is invalid CSS. The prior indexed
suite serves as the native regression gate.

### All-supported logical component arguments

`LogicalComponentSyntax` adds `:is()` and `:where()` to the recursive component
profile. An independent `EmptyComponentList` relation recognizes only whitespace
leaves, including an empty list after comment removal; its generic transition
invariant proves that an empty argument cannot also parse as a nonempty selector.
An escaped whitespace or newline identifier remains name data.

Nonempty arguments require the complete recursive supported selector grammar.
The implementation does not discard failed branches. Unknown pseudo-classes,
unmodeled valid selectors, empty comma branches and unsupported components make
the whole model source unsupported. This is an explicit all-supported fragment
of forgiving CSS syntax, not an implementation of full forgiving recovery.
The browser-only observations retain valid native forgiving behavior separately
from model predictions.

The new positive mutual grammar reuses the existing structural recursion engine.
An exact mutual embedding preserves all earlier recursive not/of chains and
queries. Matching keeps the original caller scope through both new constructors;
`:is()` uses the syntactic maximum argument weight and `:where()` contributes
zero, including when nested around nonzero-weight selectors. Empty arguments
match nothing and have zero weight.

The source facade retains complete lexical and grouping diagnostics. The shared
canonical function constructor keeps explicit closed-tokenization/grouping
premises, without an arbitrary EOF-sensitive append assumption. The existing
stylesheet and older raw-source facades are unchanged. Component `:has()`,
namespaces, pseudo-elements, relative selector arguments, quirks mode, native
integer range/precision and full forgiving recovery remain excluded.

This package adds 43 audited declarations and 119 exact cases: 24 whitespace
emptiness boundaries, 52 supported matching cases, 11 unsupported controls,
11 syntactic weights, 9 retained diagnostic results, 8 canonical AST cases and
4 explicit model rejections associated with native-only forgiving observations.
Two required native strings use the public constructor. The previous recursive
not/of suite is retained as a native regression gate.

### Relative component arguments and has

`SeparatedParts` proves exact separator partitioning, including a final empty
branch after a trailing separator. `ComponentListParts` specializes it to direct
comma leaves; commas inside strings, attributes and functions remain opaque.
This differs from the generic CSS comma-component entry, whose consumed trailing
separator is not enough to enforce an unforgiving selector list.

`ComponentRelativePrefix` consumes leading whitespace and at most one direct
child, adjacent or following combinator; otherwise the first axis is descendant.
Escaped comma/axis/whitespace identifiers remain name data. Each branch must parse
as exactly one complete logical component chain with an explicit no-has guard.
`RelativeComponentSelector` retains the existing relative-chain path lowering,
fixed caller scope and syntactic maximum over all branches.

`HasComponentSyntax` adds this relative grammar to the positive recursive
component profile. Has is allowed under outer not/is/where/of; its own arguments
use the prior has-free logical profile. A full mutual embedding preserves earlier
logical chains and queries. A separate induction over every accepted parse proves
no nested has and bounds normalized has depth by one, including deeply nested
logical and filtered selectors.

The source facade retains lexical and grouping observations. Unknown branches
inside forgiving logical arguments stay unsupported by this profile, including
nested has that a native forgiving list can discard. Required native errors are
limited to independently reviewed invalid forms; the two forgiving nested-has
observations remain separate unsupported model sources.

Canonical construction retains actual closed-tokenization/grouping premises and
normalized body input. The existing stylesheet and older raw-source facades are
unchanged. Namespace syntax, pseudo-elements, unmodeled stateful pseudo-classes,
quirks mode, native integer range/precision and full forgiving recovery remain
outside this component profile.

This package adds 87 audited declarations and 147 exact cases: 36 partition/prefix
boundaries, 73 required native cases (59 matching Booleans and 14 independently
classified syntax errors), 8 unsupported controls, 10 syntactic weights,
10 retained diagnostic results, 8 canonical AST cases and 2 model rejections for
separate native-only forgiving observations. Three required strings use the public
canonical constructor. The prior logical component suite is the native regression
gate.

### Component selectors in the checked style pipeline

`SelectorAdmission` parameterizes selector source admission while preserving
complete top-level branches and rejecting scope-dependent branches. Exact lowering
laws connect this check to recursive scope independence. Matching specificity uses
only matching top-level branches; functional argument specificity retains its
syntactic maximum. Admitted source witnesses survive into ordinary and custom
rules, and changing caller roots leaves their candidate lists, winners, custom
cascade and custom lookup unchanged.

`ParsedStyleProfile` reuses the existing raw-rule, declaration admission and value
building definitions. Arbitrary-input equations preserve the old rule/list/compute
executables and their declarative relations. `ComponentStyleSelectors` and
`ComponentStyle` instantiate the new full-component has profile without replacing
the old facades. The existing bounded value grammar, custom-property handling,
invalid-direct-value omission and pending-value behavior are unchanged. The
end-to-end computation theorem composes admitted sources with the checked cascade
and variable model; it is not an implementation-refinement theorem.

Raw rules contain already-separated selector/property/value fields. This is not a
whole stylesheet parser or invalid-rule recovery model. Every rendered scenario
has a kernel-checked component partition: exact selector components, zero or one
joining whitespace leaf, and the exact following brace block. The optional joining
leaf accounts for hexadecimal escapes consuming a terminator space. Internal
whitespace is not erased. An independently recovered unclosed function is admitted
as a separated selector but fails the rendered boundary check because it captures
the rule block; paired exact grouping laws preserve that distinction.

Eighteen computed scenarios cover decoded names and attributes, matching-list and
functional specificity, where/has/not/of, custom inheritance and direct versus
pending invalid values. Eighteen boundary checks, fourteen admission controls and
two EOF boundary controls accompany them. Scope inside zero-specificity or nested
functions remains rejected. General forgiving recovery, arbitrary stylesheet
prelude recovery, namespace syntax, pseudo-elements, stateful pseudo-classes,
quirks mode and native numeric precision remain outside this profile.

This package adds 56 audited declarations and 52 exact cases.

### Certified empty branches in forgiving arguments

`ForgivingComponentArguments` partitions direct component commas and discards
only independently recognized whitespace-empty chunks. Every other chunk must
produce exactly one complete supported selector chain. Callback failure is
whole-input unsupported, even if an earlier branch matched. Independent grammar
relations and executable correspondence retain the ordered accepted branches;
provenance accounts for every input chunk and proves an empty output exactly when
all chunks are whitespace-empty. Leading and trailing component commas preserve
the result. Callback correspondence is restricted to actual chunks, whose explicit
component count is bounded by the original input.

`SelectorBranchInvariant` proves that comma-free converted components cannot
produce multiple chains: only a direct comma changes completed-chain history.
Atomic attribute expansion and opaque function children cannot inject that
transition. The standalone `ForgivingComponentEntry` uses the accepted has
profile for each retained branch, preserves prior comma-free accepted inputs,
and carries lexical/grouping diagnostics even for unsupported attempts.

This package models the certified empty-branch subset of forgiving is/where
arguments. It does not switch any whole-selector, relative-selector or style
facade, and does not add recursive empty-branch recovery inside existing functions.
Unknown or otherwise unsupported nonempty branches remain unsupported. The
recursive extension below proves ordered compatibility for complete previous
selector lists and preserves context-specific nested-has restrictions.

Thirty-four native wrapper cases have kernel-checked exact function grouping as
well as matching expectations. This checks that appending the wrapper close does
not change the modeled argument components; EOF-sensitive recovery examples are
model-only diagnostic cases. Is retains the syntactic maximum of accepted branch
weights; where gives zero, and both preserve caller roots. Ten unsupported mixed
lists, six specificity cases and eleven diagnostic cases accompany the wrappers.
This is finite browser evidence, not a browser or prose-translation refinement.

This package adds 47 audited declarations and 95 exact cases.


## Recursive certified empty-branch recovery

`ForgivingLogicalSyntax` and `ForgivingHasSyntax` integrate the preceding
standalone argument rule into complete selectors. Only independently certified
whitespace-empty branches of `:is()` and `:where()` are discarded. This works
recursively inside logical functions, `:not()`, filtered `:nth-child()` and
`:has()` relative arguments. A nonempty branch that the model cannot parse still
makes the bounded argument unsupported, including valid but unmodeled selectors
such as `:lang(en)`.

The grammar uses positive mutual relations and an explicit component-tree count
for recursive calls. A separate fixed has-free logical parser supplies relative
arguments, retaining the complete singleton branch and no-nested-has checks.
Original scope roots remain fixed through every sibling filter and relative path.
The parsed-tree admissibility proof covers every new constructor.

`SelectorBranchHistory` proves exact parser concatenation across a direct comma
for arbitrary function callbacks. `ComponentSelectorPartition` lifts this to an
ordered partition theorem: every previously accepted list keeps precisely the
same chains. The converse requires that no partition chunk is empty. Full mutual
compatibility then preserves all earlier logical and has selector results, rather
than only a finite regression corpus. Parameterized relative extraction also
retains exact old runtime and grammar equations.

The generic `ComponentFunctionSource` construction retains explicit normalized
body, closed token-stream and body-grouping premises. It makes no claim that
appending a close delimiter preserves arbitrary EOF-sensitive tokenization.
Provenance laws account for every retained or discarded branch, syntactic maximum
specificity, zero `:where()` weight and fixed-root matching.

This package adds 143 audited theorems and 90 executable cases: 48 complete
selector expectations (42 Boolean and six explicitly invalid forms), eight
unsupported controls, eight weight cases, eight diagnostic cases, six rendered
style scenarios, six exact rule-boundary checks and six scope controls. Four
selector cases use the canonical source renderer unchanged. The browser suites
are `forgiving-has` and `forgiving-has-style`.

`ParsedStyleRefinement` proves that an extending source parser preserves every
previously admitted selector list, emitted rule and computed result. The new
style scenarios instantiate that theorem over already-separated rule fields;
all rendered sources have checked selector-prelude/declaration-block boundaries.
They do not establish a stylesheet parser or invalid-rule recovery. Existing
source and style entry points remain unchanged alongside the new profile.

General forgiving recovery is still outside this profile. The separate prerequisite below supplies an independent grouped `<any-value>`
gate and a narrow invalid-branch classifier. Unsupported valid selectors must never be discarded merely because
this parser returns failure. No mechanical prose translation, full CSS
conformance or browser refinement is claimed.


## Grouped any-value and numeric-start certificates

`CssAnyValue` checks recursive grouped components against the structural
`<any-value>` exclusions. Bad string/URL tokens and unmatched closing leaves are
rejected at every depth; semicolons and exclamation delimiters remain allowed.
Fabricated EOF/opening-token leaves are excluded from this grouped domain.
Decoded token-value validity remains an upstream tokenizer responsibility.
`ValidList` admits optional empty content; `AnyValue` requires nonempty content.
The comma-partition theorem proves that the whole gate passes exactly when every
partition chunk passes, so an invalid chunk cannot be hidden by discarding it.

`SelectorPrefixGrammar` records a necessary grammar abstraction for the start of
a complex real selector: a type or subclass selector, including namespace
prefixes and opaque attribute/pseudo arguments, preceded by optional whitespace.
`NumericStart` proves the absence of such a prefix for number, percentage and
dimension tokens. The mapping from the CSS grammar to this abstraction is
manually reviewed, not a mechanized equivalence proof or complete validity parser.

`NumericSelectorBranch` returns three distinct outcomes. A complete singleton
selector parse is supported; a numeric-start certificate is invalid relative to
the necessary prefix grammar; other input is unknown. Failed parsing alone never
produces an invalid certificate. Escaped digit, whitespace and comma identifiers
remain name data. Numeric starts are proved impossible through the existing
converter and every recursive handler, preserving previously supported singleton
branches.

`NumericBranchSource` retains the original component and lexical observations.
Its `discardCandidate` checks only the supplied branch's structural gate and
numeric certificate. Discarding branches in a full argument additionally requires
the global gate; this checkpoint does not change any selector recovery entry.
Forty any-value source/domain cases and 34 classifier cases distinguish recovered
EOF strings from bad strings, local parse errors from structural exclusions,
unsupported valid selectors from invalid prefixes, and malformed remainders from
safe discard candidates. All 55 new laws are kernel audited. No new native
comparison or browser implementation refinement is claimed.


## Globally gated certified forgiving arguments

`CertifiedComponentEntry` extends standalone forgiving argument admission with
numeric-start recovery. The complete grouped argument must first satisfy the
recursive optional `<any-value>` gate. Bad strings, bad URLs or unmatched closing
leaves in any chunk reject the argument before recovery can hide them. Exact
comma partitions retain empty chunks. Only whitespace-empty or independently
certified number, percentage and dimension starts are discarded. Every retained
branch must completely parse to one chain in the earlier recursive empty-only
has profile.

`FilteredSelectorArguments` extracts a reusable discard engine, while
`ForgivingDiscardExtraction` preserves the old empty-only runtime and grammar on
arbitrary inputs. The engine proves correspondence and ordered provenance; a
concrete discard policy supplies its separate semantic certificate. Universal
any-value preservation for earlier logical, relative and has successes establishes
that the new outer gate does not remove those accepted inputs. Compatibility
retains exactly the earlier standalone and recursive argument chain lists.

Matching laws retain caller scope roots, the maximum specificity of retained
branches and zero `:where()` weight. `CertifiedArgumentCanonical.render` prepends
a signed numeric branch to any normalized accepted argument and preserves its
exact chains and lexical, terminal and grouping diagnostics. The construction
only prepends source, so it does not assume that adding a delimiter preserves
EOF-sensitive tokenization.

This package adds 92 audited laws and 104 executable cases: 36 same-source
wrapper predictions, 36 exact wrapper-grouping checks, 15 unsupported/global-gate
controls, six weights and 11 diagnostic cases. Four wrapper inputs use the
canonical renderer. The `certified-component` browser suite compares those 36
supported argument predictions in checked `:is()`/`:where()` wrappers.

This is a standalone argument entry. Existing whole-selector and style facades
remain separate. This entry does not admit nested numeric recovery; the recursive
profile below adds it. Unsupported
valid pseudos, namespaces, nesting `&`, pseudo-elements and other nonnumeric
unknown branches remain unsupported rather than being discarded. The necessary
prefix abstraction is manually justified, not a complete CSS validity grammar;
its negative result is used only for the proved numeric-start family. CSSOM
serialization, broader forgiving recovery, mechanical prose translation and
browser implementation refinement remain outside this checkpoint.

## Recursive certified numeric recovery

`ComponentRecoverySyntax` is a shared positive recursive grammar parameterized by
an argument gate/discard policy and an optional fixed relative-selector profile.
Its six mutually inductive relations keep recursive parsing positive. The
executable handler uses the existing decreasing component count; correctness of
callbacks is restricted to actual smaller argument chunks and suffixes. A
recognized `has` function with no relative profile fails directly.

The certified instance checks recursive optional `<any-value>` before discarding
whitespace-empty or numeric-start branches. A has-free logical instance supplies
the fixed relative parser, and a second instance enables `:has()`. Numeric
recovery now composes inside `:is()`, `:where()`, `:not()`, filtered indexed
selectors and relative has arguments. Unknown nonnumeric branches still reject
the bounded profile. The generic policy interface itself asserts no CSS validity
claim; the concrete policy retains its separately reviewed numeric certificate.

Full mutual compatibility preserves the exact earlier logical, relative and has
chain lists, raw-source parses and queries. Generic admission proofs ensure the
has-free instance produces no has predicates, and every optional-relative
instance produces no nested has predicates. These properties concern retained
selector trees; an invalid numeric branch can contain a discarded has spelling.

The source facade remains separate from earlier entries. Rendered style scenarios
use an explicit extending admission profile and checked selector-prelude/block
boundaries over already-separated rule fields. Conditional canonical whole-source
proofs retain normalized-body, closed-tokenization and body-grouping premises.
Neither arbitrary EOF-sensitive source concatenation nor whole stylesheet
parsing is assumed.

Nesting ampersands, valid unmodeled pseudo-classes, namespaces, pseudo-elements
and other unsupported nonnumeric branches remain unknown. General invalidity
classification, CSSOM serialization, mechanical specification translation and
browser implementation refinement are outside this checkpoint.

This package adds 70 audited laws and 96 executable cases: 46 complete selector
expectations (40 Boolean results and six independently invalid unforgiving forms),
13 unsupported/global-gate controls, eight specificity checks, 10 diagnostics,
six rendered style scenarios, six exact rule-boundary checks and seven scope
controls. Four selector inputs use canonical function source construction.
The browser suites are `certified-recovery` and `certified-recovery-style`.


## Recursive recovery for certified forbidden heads

`ForbiddenRecoverySelector` uses the shared recursive recovery grammar with a
larger, independently certified discard family: numeric tokens, unrestricted
hashes, ordinary strings, ordinary URLs, at-keywords, parenthesis blocks and
brace blocks. The necessary-prefix abstraction now explicitly admits nesting
ampersands. Only the enumerated forbidden families obtain a negative certificate;
unknown names, namespaces, ampersands, bare functions, malformed class/pseudo
starts and leading combinators remain unsupported. A quoted `url()` function is
kept distinct from an ordinary URL token.

Every forgiving argument must pass the recursive optional `<any-value>` gate
before any branch is removed. A bad token or unmatched closing leaf anywhere in
the argument cannot be hidden behind a forbidden start. The retained branches
parse completely. Unforgiving `:not()`, optional-of lists and relative has lists
continue to reject malformed branches.

`ComponentRecoveryRefinement` proves exact successful-parse preservation between
policies, including their fixed relative profiles. The new instance preserves
all earlier numeric-recovery chain lists, source/query results and admitted
style results. Generic fixed-root matching, retained syntactic maximum, zero
where weight and retained-tree no-nested-has laws apply unchanged.

`StringArgumentPrefixSource` and `ForbiddenArgumentCanonical` prepend a quoted
invalid branch and comma to an accepted normalized argument. Arbitrary nonzero
decoded payloads are supported, including empty strings. Exact lexical, terminal
and grouping diagnostics of the original body are preserved. This prefix-only
construction does not assume EOF-sensitive suffix concatenation; the separate
whole-function canonical laws still require closed tokenization/grouping.

This package adds 77 audited laws and 145 executable cases: 46 certificate/domain
checks, 46 whole-source expectations (40 Boolean results and six independently
invalid unforgiving forms), 15 unsupported/global-gate controls, eight weights,
11 diagnostics, six rendered style scenarios, six rule-boundary checks and seven
scope controls. Four native selector inputs use the quoted-prefix renderer.
The suites are `forbidden-recovery` and `forbidden-recovery-style`.

All raw/component selector matching and these native fixtures retain the host
boundary described in “Closed raw HTML selector queries”: an HTML standards-mode
document with every modeled element in the HTML namespace. Existing type and
attribute folding rely on that boundary. Explicit mixed-namespace type heads
require a separate host-aware semantic package; these profiles do not claim
correct foreign-element or XML matching. General CSS validity, broader unknown
branch recovery, CSSOM serialization, whole stylesheet parsing and browser
implementation refinement remain outside this checkpoint.


## Explicit namespace type heads

`ExplicitTypeHeadSource` is an independent, complete single-head entry for
`*|name`, `|name`, `*|*` and `|*`. Outer whitespace is allowed; internal whitespace
is not. Comments follow the existing tokenizer, and names retain their decoded
spelling. Unsupported attempts preserve lexical, terminal and grouping diagnostics.
A source such as `* |P` is outside this single-head grammar; rejection does not
claim that the complete selector is invalid.

`ExplicitTypeHead` makes document language an explicit semantic parameter. In an
HTML document, an HTML-namespace subject compares against the ASCII-lowercased
selector name. Foreign/null-namespace subjects and all XML-document subjects
compare the original decoded spelling. The subject's local name is never changed.
Any namespace includes null; the explicit null constraint excludes every non-null
namespace. Named heads contribute one type specificity unit and universal heads
contribute zero, independently of their namespace constraint.

`ExplicitTypeHeadCanonical.render` reconstructs each supported head through the
full source tokenizer, component grouping and head parser. Named values require
nonempty, nonzero decoded characters; punctuation, Unicode and decoded whitespace
are valid name data when escaped. Universal heads have no name-value premise.
The universal roundtrip also preserves exact clean diagnostics, matching and weight.

This package adds 50 audited laws and 156 executable cases: 36 semantic/weight
cases, 46 source expectations in each HTML and XML host, 10 unsupported controls,
10 diagnostics and eight canonical AST cases. Each native host suite has 40
Boolean expectations and six independently invalid shapes; four sources use the
canonical renderer. Mixed fixtures include HTML lower/uppercase local names, SVG
`linearGradient`/`lineargradient`, null `P`/`p`, and another non-null namespace.
The `type-head-html` and `type-head-xml` suites verify document content type,
compatibility mode, exact namespace/local-name snapshots and ordinary rejection
controls. Additional perturbations change document language and subject namespace
to ensure those inputs affect matching.

Existing recursive selector and style profiles remain unchanged and all-HTML.
This package does not generalize their attribute interpretation. Compound and
recursive integration first needs host-correct semantics for every admitted
construct. Named/default namespaces, attribute namespace syntax, full stylesheet
parsing, broader XML host behavior, CSSOM serialization and browser implementation
refinement remain separate work.


## Declaration consumption boundary

The Syntax expansion now includes bad-declaration remnants, declaration
name/colon/value consumption, priority extraction, and a context-parameterized
ordinary finalizer. The package adds 90 audited laws and 112 exact kernel cases.
These are algorithm and source-boundary checks; no browser wrapper evidence is
claimed for this checkpoint.

`CssBadDeclaration` preserves nested right braces and consumes a stopping
semicolon. Other input is discarded one complete component at a time. Its
independent relation proves suffix/terminal witnesses and totality for public
EOF-free token streams, with strict progress except at the specified empty or
nested-brace stops. No new local parse-error flag is invented by this subalgorithm.

`CssDeclarationSyntax` preserves the decoded property spelling and parses values
through the existing component consumer. Its initial identifier is mandatory;
leading whitespace belongs to the caller. Whitespace after the name and colon
is discarded. A successful candidate retains its stopping semicolon, whereas
malformed-header recovery consumes it. `CssDeclarationPriority` removes only the
final non-whitespace exclamation/important pair and trims trailing whitespace;
strings and groups stay opaque. Theorems establish exact output-prefix and generic
member-predicate preservation, not only listed examples.

`CssDeclarationContext` applies the ordinary top-level brace restriction and a
tri-state context profile. `CssDeclarationOrdinary` proves accepted results retain
candidate, context and structural witnesses with unchanged remainder/error fields.
The context profile must supply its own property/rule grammar interpretation;
constant profiles in the examples are synthetic interface tests. Names beginning
with two hyphens are conservatively unsupported before the brace check, and
unicode-range is unsupported after it. These source-dependent routes need
original text/trivia and retokenization, which token values alone cannot supply.

`CssDeclarationSource.consume` is the scalar-source adapter for the candidate
phase. It preserves the complete lexical result, including diagnostics in any
unconsumed suffix. It is not the public parse-declaration entry and does not imply
whole-source exhaustion. Canonical component-list/declaration construction works
at the token level with explicit safe heads, stopped suffix and post-colon
whitespace premises; it makes no arbitrary raw-source append claim.

The 112 cases comprise 28 priority cases, 24 recovery remainders, 34 source
candidates and 26 context-interface checks. The public single-declaration entry below adds exhaustion. Concrete property
grammar adapters, source spans, custom original text, unicode-range reconsumption
and whole rule/stylesheet contexts remain next steps. The existing
[CSSWG #11017](https://github.com/w3c/csswg-drafts/issues/11017) block-finalization
omission remains an explicit text dependency; this package inserts no silent fix.
See [the declaration contract](research/declaration-consumption-contract.md).


## Ordinary single-declaration entry

`CssDeclarationEntry` adds the public initial-whitespace and full-consumption
boundary over the ordinary declaration profile. Empty input is rejected; all
other input calls ordinary consumption with `nested=false`. A non-whitespace
remainder rejects the entry, including a retained semicolon. The independent
relations prove executable correspondence and totality for actual token streams.

Unknown context or source-dependent decisions remain unsupported at exhaustion.
A known extra remainder independently rejects any completion that preserves that
remainder; `Finished.extra_rejects_completion` states this premise explicitly.
Accepted results retain the structural, context and exhaustion witnesses.
Lexical and grouping diagnostics remain separate from the outcome. The complete
lexical record still includes unconsumed suffixes.

Canonical token construction terminates at EOF, supports arbitrary initial token
whitespace, and retains explicit safe-component and post-colon whitespace
premises. Its candidate is priority extraction of the supplied values. It makes
no raw-source serializer claim. The 21 added audits and 36 exact source cases use
synthetic context oracles; real property grammars, original custom text/trivia,
unicode-range reconsumption and declaration-list/rule contexts remain separate.
No new native browser evidence is claimed.


## Original scalar and token source traces

`CssInputTrace` associates every normalized scalar with its original one- or
two-scalar chunk. Original concatenation reproduces the input exactly; normalized
projection is the existing preprocessing result. Prefix, suffix and interval laws
map normalized ranges back to literal original substrings, including CRLF, FF
and NUL. All offsets count Unicode scalars, not bytes or UTF-16 code units.

`CssTokenTrace` retains each token's leading comment trivia and consumed spelling.
Whitespace remains its own token spelling. Independent comment/core witnesses
prove exact source partition and erasure to the existing lexical result. The
traced stream separately retains terminal EOF comments; EOF itself is not emitted
as a public token. Recovery text belongs to its consuming token, while bad-string
LF remains available to the next token. Full source reconstruction and erasure
preserve every existing token and diagnostic.

`CssSourceTrace` composes preprocessing with the traced stream. `rawSpelling`,
`rawTrivia` and `rawTerminal` recover exact original scalar substrings. Their
preprocessing gives the corresponding normalized spelling/comment trace; actual
token-position witnesses justify the token-specific laws. The package adds 71
audits and 81 exact cases, with no new browser or performance claim.

These ranges preserve lexical provenance. They do not yet select a declaration
value interval, especially for comment-only values or comments adjacent to removed
whitespace and priority tokens. The following component package adds invocation-level intervals and actual
closer versus EOF provenance. Custom original-text capture, unicode-range source
reconsumption and CSSOM serialization remain separate work. See the
[source boundary contract](research/declaration-source-contract.md).


## Component intervals and body closure

`CssComponentTrace` annotates each top-level component returned by an existing
component-list invocation with its exact consumed token prefix. It reuses the
checked parsers and proves that erasing annotations gives the existing result,
including remainder and grouping diagnostic. Exact token partition, nonempty
consumption and component-origin witnesses hold universally. Nested contents
remain inside their containing interval; this is not a recursive per-node map.

`CssComponentSourceTrace` composes those annotations with original scalar traces.
Its complete parse erases exactly to the existing component source entry. Every
actual component position maps to the exact contiguous lexical token records.
`rawComponent` returns the original lexical-step interval, including its first
token's leading comments and excluding pending next-token or terminal trivia.
Preprocessing this literal source substring gives the exact normalized interval.

`CssComponentClosure` separately records whether the current body invocation
ends at an actual matching closer or at EOF. It erases exactly to `consumeBody`;
an inner child's closer cannot stand in for the outer closer. Closed results have
an actual source-token witness, and unclosed results have empty remainder.
ContextSafe canonical body construction proves the same distinction without
inventing a closing token. The package adds 46 audits and 50 exact cases.

These invocation-level ranges do not select original declaration-value text.
In particular, comment-only values and comments attached to a pending semicolon
need a separate caller convention, and terminal comments stay independently
observable even after EOF grouping recovery. Custom capture, unicode-range
retokenization, property grammars and rule/stylesheet contexts remain separate.
No new native browser or performance claim is made.


## At-rule prelude and prefix boundary

`CssAtRulePrelude` proves exact consumption through four endpoints: EOF,
consumed semicolon, retained right brace in nested mode, and retained opening
brace for block delegation. A right brace outside nested mode remains prelude
data. Existing component consumption shields delimiters inside groups; this
algorithm adds no component-list diagnostic for a direct right brace.

`CssAtRulePrefix` requires an initial at-keyword token, preserves its decoded
name, and proves strict progress, exact remainder and terminal provenance.
Its source facade keeps the full lexical trace, including diagnostics in an
unconsumed suffix. Initial whitespace is the caller's responsibility; failure
outside this entry domain does not certify invalid CSS. Token canonical laws
preserve every endpoint under explicit safe-head and renderability premises.
The package adds 40 audited laws and 34 exact source cases.

An opening brace suspends this fragment before `consume-block`. It does not
substitute simple-block grouping for block contents or claim at-rule contextual
validity. The declaration-list algorithm reaches block parsing even when it
discards an at-rule's returned value. Full list composition and block/context
completion remain separate, including the documented terminal declaration
flush issue CSSWG #11017. No new native browser claim is made. See the
[at-rule and declaration-list contract](research/at-rule-declaration-list-contract.md).


## Declaration-list attempts and resolution

`CssDeclarationListAttempt` composes the public list loop with checked ordinary
consumption and at-rule prefix parsing. Independent step/run relations prove
executable correspondence, strict recursive progress and EOF-free totality.
The loop tests input exhaustion before removing whitespace, so a trailing
whitespace-only iteration retains its rejected ordinary EOF attempt.

Ordinary accepted, rejected and unsupported outcomes keep their exact remainder
and diagnostic. Semicolons are skipped; at-rules ending at semicolon or EOF are
recorded as discarded attempts. At-rule block parsing suspends with its exact
name, prelude and brace-prefixed remainder. Every event and terminal suspension
has an originating source-suffix witness. The source facade preserves all lexical
observations, including those beyond a suspension.

`CssDeclarationListResolved` permits an ordered candidate list only after input
exhaustion and when every ordinary outcome is known. Its failure theorem exposes
an unsupported ordinary event or a block suspension. Rejected and discarded
at-rule attempts are omitted; accepted candidates retain their ordinary-context
provenance and order. Canonical token prefixes preserve arbitrary continuations,
including unsupported outcomes and suspended blocks.

The package adds 40 audits and 58 cases. Context choices in the cases are
synthetic interface oracles, not real property grammars. This is an explicit
partial list interface, with guarded resolution relative to that context; it
adds no browser claim. Custom original text, unicode-range reconsumption,
at-rule validity and block completion are outside this partial interface. The
parameterized recursive engine below completes the control flow while keeping
semantic callback duties and CSSWG #11017 explicit.


## Parameterized recursive blocks and rules

`CssRuleGrammar` gives independent positive relations for at-rule consumption,
qualified-rule consumption, block consumption and block contents. `CssRuleEngine`
executes the mutually recursive algorithms. `CssRuleParser` supplies a proved
input-derived budget: four times the token count plus a phase constant. Soundness,
completeness and equality for every sufficient larger budget are checked. Separate
well-founded relational proofs establish totality on EOF-free tokens, with an
initial at-keyword required for at-rules and an opening brace required for blocks.
These are consumption entries; they may retain a suffix.

The engine preserves declaration mark/restore: a rejected declaration is retried
as a qualified rule from the original input. No-rule and invalid-rule outcomes
remain distinct because only the latter flushes pending declarations. At-rule
transitions flush before consuming the rule, even when its validator rejects it.
The recursive AST distinguishes no at-rule block from an empty block and preserves
initial declarations, child rules and later nested-declaration runs in order.
Suffix/progress, actual close-or-EOF consumption and validator provenance are
proved. Qualified preludes retain optional-stop precedence, nested closing-brace
behavior, custom-property-looking prefix recovery and exact direct-brace errors.

`CssRuleInterface.Profile` requires a total known declaration decision, its exact
consumption relation and suffix/progress contract, completed-rule validators,
and explicit child-context selection. These are semantic obligations of an
instance. The partial ordinary consumer's unsupported result is never silently
converted to rejection. A source-aware instance must additionally tie its context
and original-text spans to the exact token stream. This package does not supply
real property/at-rule grammars, custom original-value capture or that source-context
bridge. `CssRuleTestProfile` is a synthetic oracle for control-flow tests only.

The required `TerminalFlush` argument has no default. `literalDraft` follows the
inspected draft's terminal return without appending pending declarations;
`appendPending` separately models the proposed correction to open
[CSSWG #11017](https://github.com/w3c/csswg-drafts/issues/11017). Both are proved
against their explicitly parameterized relation, and distinguishing cases retain
their different outputs. This does not resolve the normative-text issue or assert
a browser defect.

`CssRuleSource` composes the consumers with the checked scalar token trace and
retains complete lexical diagnostics, including any unconsumed suffix. Grouping
and declaration/rule observations remain separate from lexical errors. Canonical
qualified-prelude token constructions preserve exact endpoints and errors under
explicit safe-head/renderability premises; no raw rule serializer is claimed.

The package adds 99 named audits and 75 exact cases: 12 structural distinctions
and 63 source/control-flow observations, including a paired parent/child-context
test. No new native comparison or complete stylesheet/source-to-style claim is
made. The stylesheet-contents entry below composes the outer loop; concrete
semantic/source instances remain open in that package. The strict visibility
instance below supplies a bounded concrete bridge; see the [block completion contract](research/block-completion-design.md).


## Parameterized stylesheet contents

`CssStylesheetContents` consumes a complete EOF-free token stream using the
accepted recursive rule engine. Independent step and sequence relations prove
executable correspondence, uniqueness and totality. Whitespace, CDO and CDC are
skipped at rule boundaries; a semicolon enters qualified-rule parsing. Only
returned rules extend the ordered output.

`ContextFor` selects each attempt's context from the initial context and the
already emitted rule list. Every output rule has an actual source-suffix witness
and validator approval at an exact preceding output prefix. `Advance` composes
actual finite transitions with their errors and retained suffix; it does not
assume arbitrary concatenation preserves EOF-sensitive parsing. Canonical skipped
token prefixes are proved separately.

Context sufficiency, declaration decisions, real rule validity and source/span
consistency remain instance obligations. Context is still fixed within each
recursive block invocation, so this outer interface does not supply sibling-aware
nested validation. The terminal-flush policy remains an explicit argument.
`CssStylesheetSource` retains the full lexical trace and separate parser errors.

This package adds 30 audits and 38 source cases using synthetic validators,
including cases distinguishing accepted, rejected and skipped prior attempts.
It adds no browser evidence or real property grammar. Stylesheet objects, byte
input, CSSOM and serialization remain outside the entry. Public single-rule
parsing is deferred because the pinned text has an unresolved absent-at-rule
result-domain seam; see the [entry contract](research/stylesheet-entry-contract.md).
The separate Values 4 dimensional-type package below supplies the next semantic slice.


## Numeric dimensional types and percentage hints

`CssNumericType` models the seven CSS dimensional exponents and an optional
percentage hint. Missing and explicit zero map entries share a representation;
ordered-map presence and Typed OM dictionary serialization are excluded. Frequency
and time remain distinct CSS base types. Independent relations characterize hint
application/alignment, multiplication and inversion. The proofs include
commutativity, associative Option composition, identity, inversion involution and
cancellation that retains the original percentage hint.

`CssNumericTypeAddition` separates supported types, specified incompatibility and
an undetermined helper-domain case. Its ordered provisional search tries each
non-percent base against the original operands and proves first-success behavior.
The search is interpreted only for null-hint inputs. The inspected Typed OM caller
can reach that search with preexisting hints even though its helper requires no
hint; the model preserves this gap rather than silently overwriting the hint or
reporting incompatibility. This is not a browser defect claim. The dated
[arithmetic contract](research/numeric-type-contract.md) records the exact trace.

`CssCalculationType` gives percentage-terminal types, production matching and
metadata-only consistency. Context distinguishes percentages disallowed, unresolved
or relative to numbers, and percentages relative to a dimension. Number and
dimension matching have different hint requirements. Terminal typing alone does
not admit a value into a property grammar, and dimensional cancellation does not
remove percentage provenance.

The package adds 57 audits and 69 exact cases. It adds no native evidence and does
not parse raw math expressions, classify every unit, evaluate magnitudes, model
IEEE-754 values, convert units, check ranges or implement property/CSSOM admission.
The normalized type-expression composition below preserves type failure,
undetermined arithmetic and final production mismatch as distinct outcomes.


## Normalized calculation type expressions

`CssCalculationTyping.Expr` is a type abstraction with number, six dimension and
percentage literals, negation, and binary arithmetic. Magnitudes and concrete
units are erased. Independent operation, propagation and typing relations prove
correspondence to structural inference, totality and uniqueness. A known type
failure dominates an undetermined sibling; without such a failure, unresolved
arithmetic propagates. Final production admission distinguishes type failure,
undetermined arithmetic and a supported type that does not match the production.

`CssNumericTypeContext` and `CssCalculationContextLaws` prove that every supported
subtree retains a null hint or the current context target. Unhinted results have
zero percentage power, and all supported results satisfy normalization. In a
context resolving percentages to a non-percent dimension, undetermined addition
is universally excluded. Number/unresolved contexts retain the inspected seam.

The package adds 31 audits and 46 exact tree/production cases. Negating or
subtracting equal dimensions does not erase their types, and cancellation retains
percentage hints. This is type inference, not numeric evaluation or property
validation. It supplies no native claim, raw math parser, unit classifier, numeric
limits, arbitrary math-function semantics or serializer. The source adapter below
validates precedence and required operator whitespace before type erasure;
see the [type-expression contract](research/calculation-typing-contract.md).


## Grouped calculation source and type admission

`CssCalcUnit` classifies 55 decoded unit spellings directly defined in the pinned
Values 4 draft and five numeric keywords, using ASCII case folding. Its independent
membership relation proves the exact table boundary. The `fr` unit belongs to the
separate Grid definition and remains unsupported, along with container units and
unknown unit names. Unsupported classification is not a CSS invalidity certificate.

`CssCalcSplit`, `CssCalcTrim`, `CssCalcView` and `CssCalcParser` compose full grouped
components into type-erased arithmetic trees. Independent positive relations
record outer trimming, the last eligible direct operator, absence of later
operators, and complete singleton terminals or groups. Sum splits precede product
splits, giving product precedence and left association. Binary plus/minus require
actual whitespace components on both sides; comments alone do not provide them.
Parentheses and decoded `calc` functions recurse without flattening their children.
Strict bounds in the computable component count establish termination, with no
fixed nesting cutoff, and the executable corresponds exactly to the grammar.

Signed numeric tokens are operands. The internal `negate` constructor does not
admit arbitrary source unary operators such as `-(1)`. Numeric magnitudes, signs
and concrete units are erased only after token classification; this tree records
types, not numeric values. EOF-recovered groups can be supported without claiming
an actual closing token or inventing a parse error.

`CssCalcSource` separates a complete calculation argument from a full single
`calc(...)` entry. Every source attempt retains the complete lexical/grouping
result, including when its expression is unsupported. Subsequent production
assessment preserves arithmetic type failure, undetermined hint behavior and
production mismatch as separate outcomes. Supplied contexts and productions do
not implement whole property grammars.

`CssCalcProvenance` proves actual nested component origins for all output literals
and excludes internal negation and flex types from every supported source tree.
The package adds 56 named audits and 185 exact cases. These cover the unit/keyword
table, source precedence and whitespace,
signed operands, escaped units/functions, EOF diagnostics and source-to-type
composition. No new native claim is added. Numeric evaluation, IEEE-754 values,
unit conversion, ranges, limits, other math functions, substitution, general
serialization and property admission remain outside this package; see the
[source contract](research/calculation-source-contract.md).

## Resolved scope applicability and weak proximity

`CssScopeDistance` counts actual parent edges, with an independent `Hops` relation.
The forest's depth field supplies a termination rank, not a distance. Resolved
`CssScopeRegion` records include a root and lower limits: applicability includes
the root and descendants, excluding each limit and its descendants. Root inclusion
requires the explicit validity premise that limits are proper descendants.

`CssScopeStack` receives nested regions innermost first. Every region must admit
the subject, while only the innermost root determines proximity. An absent
applicability result differs from an applicable unscoped result with infinite
proximity. The supplied region records and stack order require external provenance.

`CssScopedCascade` inserts finite/infinite proximity after the complete specificity
triple and before source order, preserving the existing origin, importance,
attachment and layer comparisons. This follows the current Cascade 6 sorting
algorithm and the CSSWG's 22 March 2023 weak-proximity resolution; the draft's stale
stronger scope-effects wording is recorded in the
[dated scope contract](research/scope-cascade-contract.md). Universal embedding
laws preserve the old unscoped ordering and winners exactly.

`CssScopeStyle` matches every resolved root instance before choosing a winner.
A nearer root whose selector fails cannot suppress a farther matching instance.
Its generic selector family receives the root; the concrete scoped family gives
`:scope` that singleton and preserves selector specificity. Selectors are already
interpreted for their scoped context. Passing a normalized selector is not a proof
of raw relative-selector interpretation, and no implicit scope-root prefix is
inserted. Only subjects are filtered by region applicability; selector ancestors
may lie outside the region.

`CssScopeStyleProvenance` identifies actual matching selectors, selected weights,
original declarations, all applicable regions and the innermost distance witness.
`CssScopeComputed` composes ordinary parent inheritance and proves exact old
unscoped computation under the stated same-forest premise. An excluded descendant
can still inherit a computed value from a styled ancestor.

The package adds 79 named audits and 77 exact cases: 22 region cases, 26 ordering
and stack cases, and 29 computed queries across 22 closed stylesheet scenarios.
The latter use explicit `:scope` anchors and manually supplied resolved records;
the browser comparison is finite evidence, not a parser or browser-refinement
proof. Cases distinguish weak ordering, layers, multiple roots, limits, nested
regions, selector weights and inheritance. Raw `@scope` parsing, root/limit
resolution, omitted roots, arbitrary nesting-selector interpretation, shadow and
encapsulation contexts, pseudo-elements, stylesheet integration, animations and
transitions remain outside this normalized profile. Existing HTML selector and
visibility-property assumptions remain in force.

## Finite numeric magnitudes and fixed unit conversion

`CssFiniteScalar` represents an exact rational value and a negative-zero bit.
Independent arithmetic relations characterize addition, direct subtraction,
multiplication and division with nonzero divisors. Every result satisfies the
zero-bit invariant. Symbolic source numbers map every zero spelling to positive
zero; operations can generate and retain negative zero. `reverseSign` is a
representation helper, not an implementation of the CSS internal `Negate` node.

`CssUnitFactor` supplies 18 exact positive rational conversions into px, deg, s,
hz and dppx, including the `x` resolution alias. Lookup corresponds to independent
ASCII-folded table membership and the existing unit classifier. `CssUnitScalar`
proves exact multiplication and preservation of computed zero signs. Radians,
contextual units and flex units remain unsupported, even for zero magnitudes.
The [dated evaluation contract](research/numeric-evaluation-contract.md) records
the primary unit ratios and signed-zero rules.

`CssFiniteCalculation` evaluates normalized magnitude trees with canonical-unit
literals and binary arithmetic. Its exact type erasure uses the existing type
checker; independent type and value relations characterize the combined result.
Type failure, undetermined type inference and unresolved percentage basis, flex
unit or zero divisor remain distinct. Checking types before value-domain errors
is this profile's outcome priority, not a claim about CSS diagnostic ordering.

`CssFiniteCalculationProvenance` proves successful, valid values for every actual
subtree, excludes percentage/flex leaves from supported evaluations and proves
every evaluated divisor nonzero. Multiplication by zero does not discard an
unresolved subtree or repair a type mismatch. `CssUnitCalculation` converts a
symbolic number and known unit into a dimension literal and proves its exact
typed rational result, including positive source-zero semantics.

The package adds 87 named audits and 148 kernel-checked cases: 36 scalar, 31
calculation, 59 fixed-unit, 12 scalar-conversion and 10 unit-to-calculation cases.
These certify an exact mathematical subset. No new browser comparison, binary
precision equivalence or numeric serialization claim is made. That normalized
package does not parse source magnitudes; the following source extension adds
that composition. The exceptional extension below adds nonfinite values.
Other remaining value domains include
irrational and contextual conversion, percentage environments, unary `Negate`,
other math functions, property admission, range/overflow behavior and top-level
censorship, rounding and clamping. Canonical normalized literals require caller
provenance; this evaluator does not yet produce computed property values.

## Grouped calculation magnitudes and source evaluation

`CssCalcMagnitudeTerminal` retains symbolic numeric values, integer/number flags,
optional source signs, decoded unit lists and keyword spelling. Parsing does not
evaluate decimal powers. The magnitude view and recursive parser reuse the
accepted trim/split rules, whitespace requirements, precedence and grouping.
Universal erasure and lifting laws preserve the old terminal, view and parser
results for arbitrary component lists. `CssCalcMagnitudeSource` extends that
identity through argument/full-call source entries, complete diagnostics and
production assessment.

`CssCalcMagnitudeProvenance` reconstructs every retained literal as an actual
nested decoded component, preserving its fields and unit/keyword admission.
This is decoded component provenance, not original escape spelling or raw source
intervals. Existing lexical and grouping observations remain attached to every
attempt, including unsupported inputs and EOF-recovered groups.

`CssCalcFiniteConversion` maps source numbers and the fixed rational unit table
to canonical magnitude trees. Unsupported known units and keywords retain named
conversion-domain reasons. Percentages retain the missing-value-basis boundary.
`CssCalcValueSource` distinguishes unsupported parsing, type failure,
undetermined type inference, conversion unavailability and finite-value domain
unavailability. Unsupported parsing is not a certified CSS syntax error. Type
checking precedes conversion, and leftmost conversion reasons follow the stated
model reporting policy.

`CssCalcValueLaws` proves exact conversion erasure for valid retained terminals,
then derives actual source-to-finite-evaluator correspondence, old-type-parser
provenance, scalar validity and nonzero evaluated divisors. Returned scalars are
**internal, before top-level censorship**: `calc(-2 * 0)` retains negative zero
here. These results are not final computed property values or serialized CSS.

The package adds 71 named audits and 117 kernel-checked cases: 20 terminal-field
controls, 16 source magnitude trees, 65 source value outcomes and 16 diagnostic
observations. All 18 fixed conversions, exact rational arithmetic, source and
generated zero signs, precedence, escaped names, whitespace/comments, symbolic
large exponents, EOF recovery and domain failures are covered. No new browser
numeric comparison is claimed. Nonfinite arithmetic is added in the extension
below. Irrational arithmetic, contextual
units and percentage environments, property finalization, censorship, rounding,
clamping, implementation range/precision, other math functions, substitution and
general serialization remain open. Explicit evaluation may compute large powers;
that work is separate from symbolic parsing.

## Exceptional calculation arithmetic and source evaluation

`CssExtendedScalar` adds signed infinities and NaN to the finite rational scalar.
Direct binary operations implement the traced NaN overrides, infinity signs,
zero-divisor outcomes and finite/infinity signed zeros. Independent operation
relations characterize each executable result and prove output validity.
Structural equality compares representations, including the NaN constructor;
it is not IEEE numeric comparison.

`CssExceptionalKeyword` admits decoded `infinity`, `-infinity` and `NaN` with
ASCII case folding. `CssExceptionalCalculation` evaluates the existing
magnitude tree, and `CssExceptionalSource` retains the existing type-first
source pipeline. Source zero spellings remain positive; generated negative
zero and exceptional results survive nested calculations. Known units without
a fixed factor, percentage bases and `e`/`pi` remain unavailable. An exceptional
operand does not discard an unavailable child in this bounded evaluator.

`CssExceptionalRefinement` preserves every successful finite result, including
its type, rational magnitude and zero sign. It also proves arbitrary-source
diagnostic projection equality and exact parser-failure equivalence. The new
arithmetic gains no parser coverage. Subtree provenance supplies valid evaluated
values throughout successful trees, and traces an exceptional result to an
actual exceptional keyword or evaluated zero-divisor subtree. Literal witnesses
retain the existing decoded component origins.

The package adds 79 named audits and 301 kernel-checked cases: 196 scalar
operation cells, 16 decoded keyword controls, 70 source outcomes and 19 diagnostic
observations. Independent source review and reproduction check these artifacts;
these counts are not percentages of specification coverage. The
[dated exceptional-arithmetic contract](research/exceptional-arithmetic-contract.md)
records the primary call chain and model boundaries.

Results remain **internal, before final censorship**. No concrete property
bounds, final admission, censorship, clipping, integer rounding, comparison,
`min`/`max`, internal unary `Negate`, transcendental functions, contextual unit or
percentage environment, general simplifier equivalence, substitution or numeric
serialization is implemented here. Exact rational arithmetic does not establish
browser precision or overflow behavior; this package adds no native comparison.
The following extension supplies explicit finalization contexts and a narrow
number-only opacity instance.

## Contextual numeric finalization and bounded opacity

`CssNumericClipping`, `CssNumericCensorship` and `CssNumericFinalization` finalize
an evaluated expression using explicit ordered bounds and a supplied production.
NaN becomes zero before clipping, infinities reach the supplied endpoints, and
negative zero loses its sign at this boundary. Integer targets round to nearest
with ties toward positive infinity. Independent interval relations characterize
rounding and clipping; integer endpoints ensure these operations commute.
Fractional bounds are permitted for real targets, with explicit counterexamples
to extending integer commutation to arbitrary fractional endpoints.

The caller supplies whether the context is available at computed or used value
time. This is a semantic interface obligation, not a theorem that a real property
or layout provides those bounds at that stage. Invalid supplied bounds, missing
context, production mismatch and upstream evaluation unavailability remain
separate outcomes. Reporting precedence is a model policy. The generic endpoint
operation does not implement angle representability overflow or the `round()`
function.

`CssFinalizedSource` retains the exact original parse, type, value and diagnostics.
Its proofs connect a final result to the actual supplied expression, admitted
production, ready context and bounded output. Nested subtree values remain
unchanged; only the full supplied expression is finalized. Argument mode does
not establish where a fragment occurred in a larger stylesheet.

`CssOpacityCalculation` fixes full `calc()` mode, number production, computed
stage and Color4 bounds `[0,1]`. It proves every accepted result lies within that
interval. The parser still permits its existing EOF recovery. The 26 native
fixtures separately check exact grouped declaration-wrapper boundaries before
exporting their unchanged closed source strings. Their expected displays are
limited to `0`, `0.25`, `0.5`, `0.75` and `1`; no general rational serialization
or browser precision equivalence follows. The browser harness verifies HTML
standards mode, exact DOM/style text, CSSOM opacity admission and computed value,
with rejected-declaration, property, snapshot and expectation controls. Prior
visibility fixtures exercise the same generalized property reader.

This package adds 74 named audits and 160 kernel-checked cases: 32 rounding
boundaries, 50 supplied-context source outcomes, 20 diagnostic observations,
26 opacity values, 26 wrapper boundaries and six exclusions. These are artifact
inventories, not specification coverage percentages. The
[dated finalization contract](research/numeric-finalization-contract.md)
records the primary Values4/Color4 chain and assumptions.

This finalization package leaves contextual unit/basis resolution to the supplied
environment extension below. Percentage opacity, ordinary literal opacity
admission, general property interpretation, cascade integration of numeric values,
color/compositing, representation precision, angle overflow, other math functions,
internal unary `Negate` and general numeric serialization remain open.

## Supplied percentage bases and relative unit factors

`CssNumericEnvironment` and `CssEnvironmentUnits` resolve reached numeric leaves
using an explicit environment. A percentage basis supplies a valid finite scalar
and a dimensional target matching the type context. Negative and signed-zero
bases are permitted. The independent `CssRelativeUnit` inventory contains 36
relative length names and is proved equivalent to the existing length classifier
minus the fixed-unit table. The 18 fixed factors always take priority; relative
factors are looked up using decoded ASCII-folded names and must be nonnegative
rationals, including zero. Unknown units gain no parser coverage, and radians,
`e` and `pi` remain unavailable.

`CssEnvironmentCalculation` and `CssEnvironmentSource` preserve the existing
type-first pipeline and source grammar. Independent leaf and tree relations
identify exact percentage and unit products. Only reached leaves validate their
supplied data: unused invalid entries cannot change an earlier successful result.
Number-relative percentages retain their existing percent type; this extension
does not turn percentage opacity into a number before type checking.

**This is conditional evaluation of the original parsed tree in a supplied ready
environment, not equivalence to the full CSS computed/used-value simplifier.**
Prior simplification history matters. The paired `calc(50%/25%)` cases produce
`2` with a nonzero basis and NaN with a zero basis after resolving the operands;
this evaluator does not cancel percentages first. This ready-tree profile leaves symbolic residual values to the bounded additive
extension below. Real font/viewport selection, property-specific basis acquisition
and a complete source-to-stage rewrite history remain separate obligations. The
[dated environment contract](research/numeric-environment-contract.md) records
this boundary and the primary resolution rules.

`CssEnvironmentRefinement` preserves every old successful type/value result for
arbitrary supplied environments and gives exact old behavior for the empty
environment. Parser failure and diagnostic projections remain unchanged.
`CssEnvironmentProvenance` recovers actual source literals and successful subtree
values, including the basis or factor witness and exact rational product.
`CssEnvironmentFinalization` composes the existing explicit bounds, production
and readiness interface and preserves previous finalized successes. Its
computed-to-used law uses the same supplied environment; it does not assert that
real layout data stays unchanged between stages.

The package adds 80 named audits and 146 kernel-checked model cases: 54 relative
unit controls, 60 source outcomes, 16 diagnostic observations and 16 supplied
context finalization outcomes. Zero factors, negative and signed-zero bases,
reached-only failures, type precedence, EOF recovery and exact prior-result
preservation are covered. No new browser comparison, property/layout acquisition,
general serialization or implementation precision claim is made. These counts
measure the artifact inventory, not specification coverage.

## Additive residual calculation trees

`CssResidualCalculation` represents numeric atoms and nonempty `Sum` trees.
Atoms retain their unit and extended scalar, including negative zero, infinities
and NaN. Dimension keys use decoded lowercase names admitted by the existing
unit classifier. `WellFormed` is a structural condition; it does not assert CSS
type compatibility or property admission. Original calculation types and percent
hints remain external metadata for any future source bridge.

`CssResidualResolution` converts available fixed or supplied factors and matching
percentage bases to supported canonical units. It retains unavailable relative
units, radians and percentages, including zero coefficients. A percentage basis
whose target lacks a supported canonical unit also remains unresolved. This
separate profile does not change the earlier ready-tree evaluator.

`CssResidualSimplification` simplifies children before collecting their results
at the parent. `CssNumericCollection` independently relates stable extraction,
coefficient addition and collection. Each group starts with its first actual
coefficient, preserving a singleton negative zero; canceled units remain present.
Groups occupy their first occurrence positions, an explicit model ordering
policy. A singleton result collapses to its numeric atom. Fabricated empty sums
stay empty and lie outside `WellFormed`.

The normal-form laws prove valid output, distinct unit keys, exact key support
relative to resolved child outputs, and idempotence under the same environment.
They do not claim that resolution preserves original unit names or that changing
environments commutes with simplification. Tests distinguish resolving a canceled
percentage later against a negative basis from resolving each operand first.
The [dated residual contract](research/calculation-residual-contract.md) records
this history boundary and the numeric-leaf, recursive-child and Sum algorithm
scope.

This package adds 78 audited laws and 70 kernel-checked cases: 32 collection
controls and 38 residual-tree outcomes. The complete named proof inventory
includes the mutual correspondence and normal-form proofs. These counts are
artifact inventories, not specification coverage percentages. No new browser
comparison or general source-lowering theorem is claimed. Binary subtraction to
`Negate` conversion, Product simplification, original type metadata composition,
property/stage acquisition and serialization remain open. The following package
adds ready comparison calls separately from residual simplification.

## Ready comparison calculations

`CssComparisonScalar` gives independent selection relations and executable
minimum, maximum and clamp operations. NaN absorbs; negative zero orders below
positive zero. Nonempty extrema start with the first actual value. Clamp retains
explicit absent endpoints and selects the lower endpoint when bounds are
reversed. Results come from actual inputs. Order, extrema bounds and algebra
carry the validity and non-NaN premises needed for representation-level laws.

`CssComparisonTyping` represents normalized calls over the existing magnitude
expression grammar. It combines original argument types and percent hints;
`CssComparisonCalculation` checks an explicit production before evaluating
arguments under the supplied environment. Missing conversion information stays
unavailable. Equal unresolved percentage units alone do not permit comparing
coefficients, since a later basis can reverse their order. Final property
censorship remains a separate outer operation.

`Call.Valid` requires each actual argument to have consistent decoded numeric
metadata. The executable correspondence also covers fabricated records; it does
not certify their CSS admission. The corpus construction proves validity when
building calls from separately parsed argument strings. Result provenance gives
an actual evaluated argument, and singleton calls refine the previous evaluator
with the explicit production check.

This normalized-call package adds 91 audited laws and 178 kernel cases: 134
scalar/list/clamp controls and 44 calls. Its source boundary is extended by the
recursive package below; neither package adds browser evidence. Exact rational precision,
supplied environment duties and the direct-tree simplification-history boundary
remain unchanged. Partial residual comparisons, general Product/Invert conversion,
Negate source lowering and general source equivalence remain open; the local
structural phase profile below has a separate conditional contract. See the
[dated comparison contract](research/calculation-comparison-contract.md).

## Recursive comparison-function sources

`CssMathExpression` retains every `calc`, `min`, `max` and `clamp` function
boundary. `CssMathView`, `CssMathArguments` and `CssMathParser` give independent
positive grammar relations and a parser terminating on explicit component-tree
counts. Each argument is fully consumed; direct commas retain empty chunks,
while commas inside grouped components stay opaque. Extrema require one or more
arguments. Clamp requires three positions and admits decoded, ASCII-folded
`none` only in its two endpoint positions. Existing operator-whitespace, unit
and keyword restrictions remain explicit. Unsupported input is not a certified
CSS syntax error.

`CssNumericCategory` and `CssMathTyping` require a numeric category at every
function node, retaining the original dimensional type and percentage hint.
Parenthesized binary intermediates may have compound dimensions. Thus
`calc((1px * 1px) / 1px)` is admitted as a length, while
`calc(calc(1px * 1px) / 1px)` fails the inner function-category check. The dated
[primary trace](research/comparison-source-contract.md) records this distinction
and its CSSWG clarification.

`CssMathCalculation` composes the existing ready environment and exceptional
arithmetic with recursive comparisons. Type and function checks, then the
explicit outer production, precede magnitude evaluation. Missing information
remains unavailable; the provisional hint-domain outcome remains undetermined.
Source facades preserve the complete grouped diagnostic result. Universal laws
recover actual decoded literal origins and supported types and valid values at
every actual subtree. Values remain internal and uncensored; this package does
not choose a property, stage, bounds or browser numeric precision.

Successful partial syntax erasure reproduces the earlier calc parser exactly,
including its grouped source diagnostics, and every old parse has a new syntactic
lift. Normalized old comparison calls preserve supported results. Semantic
source preservation is conditional on `AdmittedErasure`, whose independent
constructors require every retained calc boundary to have an admitted original
type, plus explicit outer production matching. This avoids asserting that the
earlier outer-only type profile already enforced every nested function boundary.

The package adds 125 audited laws and 157 kernel cases: 24 numeric-category
controls, 18 exact source ASTs, 34 unsupported inputs, 61 source evaluation
outcomes and 20 diagnostics. No new native evidence is claimed. Supplied
percentage/unit environments, ready-tree zero-basis ratios, partial residual
comparison readiness, general Product/Invert conversion and Negate source lowering
retain their separate contracts; the local phase package below does not supply
a full recursive simplifier. This is not a general equivalence with the
CSS simplification pipeline or full property parsing.

## Local Product and Invert phases

`CssProductStructure`, `CssProductFlatten`, `CssProductNumbers`,
`CssProductDistribution` and `CssInvertPhase` formalize the local steps after
child simplification. Product expands its direct Product children, combines
number coefficients and distributes an exact number-times-all-numeric-Sum
pair. Invert evaluates a number reciprocal, removes double inversion or retains
the node. Independent relations correspond to each executable phase. Number
collection starts with an actual coefficient and keeps the first number's
position; coefficient fold order is an explicit deterministic model policy.
Distribution returns its Sum without restarting singleton collapse or collection.

`CssProductReadiness` supplies a separate sufficient canonical domain. Each
factor is an already-canonical number/dimension atom or its reciprocal. Actual
scalar multiplication/division witnesses and unit-power addition must produce
the result, whose powers equal the unchanged original powers and whose target
unit is canonical. Empty factors, percentages and noncanonical dimensions are
outside this domain. In particular, `em/px`, `em/em` and even unnormalized
`in/in` do not acquire a canonical magnitude from projected type cancellation.
The [dated primary trace](research/product-invert-research-20261017.md) records
why unconditional step-9.4 magnitude interpretation remains unresolved.

`CssProductPhase` records the exact input, flattened and collected lists. Its
supplied eligibility profile is indexed by this history and the original type;
its Boolean corresponds to an independent predicate and implies numeric-category
admission. This implication does not prove faithful or complete CSS eligibility.
A concrete instance must separately justify child-type multiplication and its
transport through source and structural history. The false branch is therefore
a supplied-eligibility residual, interpreted as normative fallback only for such
an instance. Reached eligibility without canonical readiness instead produces
an explicit `interpretationBoundary`, not a claimed CSS result.

Product and Invert wrappers preserve original type, percent hint and external
history. Structural well-formedness ensures valid atoms and nonempty Sum/Product
lists; it does not certify original typing, child simplification or source
history. The package adds 94 audited laws and 86 kernel cases, including the
synthetic eligibility interface and a paired staged signed-zero distinction.
Distributing negative zero across unresolved `[1px,-1%]`, then resolving a 100px
basis, gives positive zero; resolving the Sum first and multiplying gives
negative zero. These are different model histories, not a browser comparison.

There is no recursive source simplifier or new native evidence here. Existing
source evaluators are unchanged. The typed package below discharges concrete
eligibility and type transport on its stated domain. General canonical conversion,
recursive source history, residual comparisons, Negate lowering and property-stage
acquisition remain separate obligations. No reassociation,
distribution or source-to-simplification equivalence is inferred from these local
phase proofs.

## Typed residual transport and guarded Product sources

`CssTypedResidual` retains the original numeric type and percentage hint at each
numeric leaf. Operator types are inferred from their actual children.
`CssContextualTypeAlgebra`, `CssProductTypes` and `CssSumTypes` prove supported
fold transport, including genuine type-addition/hint distribution. Internal leaf
coherence uses original powers and contextual hints; it does not impose final
production matching on internal values. A cancellation may retain a percent hint
while its powers become those of a number.

`CssTypedProductTransport`, the number-collection modules and the distribution
modules preserve actual supported types and hints through the corresponding
structural phases. Combined coefficients retain the product of their original
types. These are type equalities, not scalar distributivity or reassociation
claims. `CssTypedProductEligibility` supplies a concrete instance of the earlier
profile: it checks the exact prepared typed trace, its erased structural history
and the inferred original type, then the numeric category. On the explicit
coherent, well-typed, prepared domain, eligibility is equivalent to the category
of the actual post-structural children in both directions. A fabricated trace or
wrong annotation lies outside that domain. Canonical readiness still requires
independent magnitude evidence; an eligible normalized `em/px` tree reaches the
interpretation boundary rather than acquiring an invented conversion.

`CssTypedResidualLowering` translates the supported literal/add/multiply/divide/
calc fragment of the existing function-preserving binary AST. Conditional typing
proofs retain function admission and original leaf types. Subtraction, Negate and
comparisons are outside this translation. Since the existing parser makes
parentheses transparent and retains binary associations, this is not a
reconstruction of the CSS internal tree's flat operator runs and grouping
history. The unrestricted `CssTypedProductEntry.process` is a local root-phase
transformation; it does not establish recursive child simplification.

The public `CssTypedProductSource` entry therefore adds a checked child-normality
restriction. Original Product children must be canonical numeric atoms or
retained reciprocals of canonical dimensions. Every admitted atom resolves to
itself under arbitrary supplied environments, and an admitted reciprocal has an
actual retained-Invert witness. Pending Sum/Product children, numeric
reciprocals, percentages and noncanonical unit normalization are excluded.
For example, the local transformation can distribute `(1 + 2) * 3`, but the
public source entry excludes `calc((1 + 2) * 3)` because its Sum child needs
simplification first. This is a sufficient bounded admission rule, not a full
recursive source simplifier.

Universal provenance recovers actual decoded source components and unchanged
literal types from retained input leaves. Source attempts preserve the complete
grouped diagnostic object, including EOF recovery. Unsupported admission is not
a CSS syntax-error certificate. Results remain internal and uncensored.
The [typed transport contract](research/typed-residual-transport-20261017.md)
records source-history, child-order and conversion boundaries.

This package adds 198 named audits and 150 kernel cases: 48 contextual algebra
and fold controls, 42 structural/eligibility/lowering cases, 42 guarded sources
and 18 diagnostic observations. It adds no browser evidence. Recursive child
normalization and bounded group-preserving source construction are supplied separately below. General conversion,
residual comparisons, Negate lowering and real property-stage acquisition remain
separate work; no general source-to-simplification value equivalence is claimed.


## Recursive typed child normalization

`CssTypedNormalization` processes the nonempty normalized typed tree recursively.
Numeric leaves resolve using the supplied environment while retaining their
original types and hints. Sum children complete before direct Sum flattening and
same-unit numeric collection; opaque children and zero coefficients remain.
Collection starts with the first actual coefficient and keeps its first position.
`CssSumTypeTransport` proves supported grouping and permutation transport under
the common-context assumptions. It does not assert arbitrary associativity of
incompatible or undetermined type results.

Invert and Product phases also follow completed children. Product input typing
is checked before those child calls. Concrete eligibility checks the prepared
returned children, and canonical readiness supplies separate magnitude evidence.
Distribution returns its new Sum directly; this invocation does not normalize
that result again. Thus the normalized tree for `(1 + 2) * 3` completes its Sum
child first and returns `9`, while an explicit local distribution invocation on
unprocessed children returns `Sum[3,6]`. Both paths have distinct checked cases.

Independent `Normalized` and `ChildrenNormalized` relations describe the exact
recursion. Every well-typed coherent input produces either a completed tree or
an explicit interpretation boundary. A completed tree retains the original
inferred type and percentage hint. A reached child boundary stops the parent's
phase. Its path identifies an actual original Product subtree, and its trace
records that subtree's completed children, concrete eligibility and unavailable
canonical magnitude. Reporting the first encountered boundary is a deterministic
model policy. No `em/px` magnitude is inferred without conversion evidence.

This package accepts supplied typed trees. The existing guarded source facade
remains bounded to its earlier stable-child profile. The separate group-preserving
source constructor below retains operator runs, parentheses and nested
construction/simplification calls. The older binary AST translation does not
supply that history. No general fixed-point, scalar
reassociation, direct-evaluator equivalence, source simplification or final
property claim follows from this package. Negate, residual comparisons and real
property/layout environment acquisition remain separate work.

The [recursive normalization contract](research/recursive-typed-normalization-20261017.md)
records the manually reviewed algorithm boundary. The package adds 19 modules,
113 named audits and 76 kernel cases: 30 leaf-resolution/Sum-transport controls
and 46 recursive normalization/boundary observations. Fabricated mismatched
annotations are explicitly outside the well-typed guarantee, even when the
runtime returns a tree. Results remain internal and uncensored; there is no new
native evidence.

## Group-preserving calculation construction

`CssCalculationPlanParser` admits grouped component sources containing numeric
literals, addition, multiplication, division, parentheses and `calc()`. Its Plan
retains direct operator runs and explicit group/function boundaries. Independent
Shape proofs establish nonempty runs and atomic Product factors. For example,
`12 / 2 / 3` constructs one Product with two reciprocal factors, while
`12 / (2 / 3)` invokes construction for the grouped denominator first. Original
function-category admission is retained; parentheses can hold compound types
that a nested `calc()` cannot admit.

`CssCalculationConstruction` separates structural assembly from a complete
construction invocation. Only actual group/calc leaves recursively construct
and normalize their arguments during assembly. Synthetic operator runs assemble
their children without extra construction calls. Each completed invocation then
runs the recursive typed normalizer on its assembled root, including the actual
repeat visits to results returned by nested calls. Singleton Product/group roots
pass through; singleton literal/calc leaves receive a Sum wrapper. This does not
assume normalization is idempotent. Full call mode checks the outer `calc()` and
enters its argument; argument mode can retain `calc()` as a nested leaf.

Independent construction, assembly and child-list relations correspond exactly
to the executable recursion. Valid Plans with supported original typing and
available literal construction always produce either a completed tree or an
interpretation boundary. Completed results preserve the original type and hint.
The source facade retains the exact parsed Plan and grouped diagnostic object.
Its optional construction result does not classify every unavailable cause as a
CSS syntax or type failure. In particular, `e` and `pi` are parsed but exact
literal construction is unavailable. EOF group recovery remains admitted.

A boundary records the actual local assembly whose normalization stopped.
Its call path is relative to the selected entered Plan, separately from the
normalizer's path within that assembly. Provenance identifies the actual nested
construction invocation and local Product trace; it never fabricates a completed
enclosing tree when an earlier nested call stopped. Cases distinguish direct-run
outer normalization from a stopped parenthesized or nested `calc()` invocation.

The supplied environment must faithfully represent availability at the modeled
stage. Reconstructing the source later with a different ready environment is not
proved equivalent to preserving its earlier simplified history. Canonical
conversion boundaries remain explicit. Subtraction/Negate, comparison-function
construction, final property handling and real environment acquisition remain
separate. There is no general scalar reassociation, old evaluator equivalence,
raw source-span or browser-refinement claim.

The [grouped construction contract](research/grouped-calculation-construction-20261017.md)
records the focused manual primary-spec trace. This package adds 24 modules,
115 named audits and 103 kernel cases: 26 Plan observations, 35 source results,
24 assembly/call-boundary controls and 18 diagnostics. Results are internal and
uncensored; no native evidence is added.

## Local residual comparison phase

`CssResidualComparison.phase` handles a supplied `min`/`max` or `clamp` call
whose child trees have already been produced by its caller. The local relation
does not certify that earlier child-normalization history. It checks the actual
original type fold and numeric-category admission before magnitude readiness.
Canonical numeric leaves have exact supported units and valid extended scalars;
noncanonical numeric leaves produce an explicit interpretation boundary. Equal
unit spelling alone does not establish magnitude readiness.

With all canonical numeric children, independent scalar extrema/clamp relations
produce a canonical leaf retaining the original type and percentage hint. With
opaque nonnumeric children, `min`/`max` selects within each canonical same-unit
group and preserves the opaque children. Collection uses the first actual scalar
as its seed and replaces a group at its first position. Every removed operand's
original type contributes to the replacement, including hints from operands
whose magnitude was not selected. A singleton collapses. `clamp` has no partial
rewrite and retains an opaque-child call unchanged. A partial NaN group does not
discard an opaque sibling.

Independent readiness, collection and phase relations correspond to the runtime.
Coherent admitted calls always produce a completed tree, retained call or
interpretation boundary, preserving the original type and hint. Provenance gives
actual selected scalar/unit origins, the exact retained opaque subsequence, and
an actual unavailable numeric child for each boundary. Fabricated annotations
remain outside the coherence guarantees even if the total helper returns a value.

This package adds 14 modules, 79 named audits and 86 kernel cases: 32 readiness,
39 phase and 15 caller-composition controls. The latter use actual completed
arithmetic `calc()` construction results before an explicitly supplied local
comparison call. They do not add comparison-source parsing or a recursive
comparison simplifier. Existing opaque examples include completed mixed-unit
residual Sums. Supplied environment faithfulness, changing-stage history,
Negate lowering, broader readiness and concrete property handling remain separate.
Results are internal and uncensored, with no new native or general future-value
equivalence claim. The [dated local comparison contract](research/residual-comparison-simplification-20261017.md)
records the manual primary-spec trace and these caller duties.


## Recursive residual comparisons

`CssRecursiveResidual.Tree` retains actual `min`, `max`, and `clamp` nodes inside
Sum, Product and Invert. Each numeric leaf keeps its original type annotation.
Inference reads actual children; comparisons require a supported combined type
and numeric-category admission, while arithmetic intermediates can retain
compound powers. No synthetic arithmetic tree stands for a comparison.

The normalizer checks original Product/comparison typing before calling children,
completes children in order, and then applies the local phase. A rebuilt comparison
keeps the operator, exact arity and optional endpoint positions. Retained comparison
calls become actual recursive nodes. Scalar selection preserves original type and
hint contributions from every operand, including unselected operands. Mixed
canonical groups preserve opaque child payloads and their order; NaN cannot bypass
an unresolved operand or discard an opaque sibling. Distribution returns its new
Sum directly without restarting normalization.

Independent positive relations correspond to the runtime. Coherent, supported
inputs are total into a completed tree with the same original type and hint, or
an explicit interpretation boundary. The first reached child boundary stops the
parent. Product and comparison reasons have different data; path witnesses locate
the actual original subtree and separately record its completed local children.
Clamp indices follow present lower endpoint, center, then present upper endpoint.
Helper failure on fabricated unsupported annotations is not a CSS-invalidity claim.

Exact embedding/projection and type laws preserve the old arithmetic model.
The old normalizer's complete optional outcome is preserved for arbitrary old
trees under the same context/environment, including unavailable outcomes and exact
Product boundary paths, annotations, prepared children and factors. The frozen old
datatype and runtime remain available.

The package adds 43 modules, 287 named audits and 74 kernel cases: 24 embedding/type
controls, 12 shape-rebuild controls and 38 recursive outcomes/boundaries. It is a
normalized-tree algorithm; the existing group-preserving arithmetic source
constructor is separate. The following source package extends that boundary.
Changing-stage environment history, broader readiness and real property/font/viewport
acquisition remain open.
No general fixed-point, direct-evaluator or future-value equivalence is asserted.
Negate lowering and final censorship remain separate, and no browser evidence is
added. The [dated recursive comparison contract](research/recursive-residual-comparison-20261017.md)
records the model and manual primary-spec boundary.


## Group-preserving comparison source construction

The source Plan now retains `min`, `max` and `clamp` alongside direct arithmetic
runs, parentheses and `calc` calls. Complete component admission preserves comma
chunks and each optional clamp endpoint. The fixed literal/unit profile supports
addition, multiplication and division; subtraction, unary groups and other math
functions remain outside it. Parsed `e` and `pi` retain syntax but have no exact
literal constructor in this rational/exceptional domain.

Construction follows explicit nested calls. Direct operator runs assemble without
an extra calculation call. Actual grouped and function arguments construct in
order. A standalone comparison normalizes its named root; a full `calc` call enters
its argument. A nested comparison returns its representation before the enclosing
calculation normalizes it. The named-root eager call is a manually reviewed
specialization of the primary prose, recorded in the dated contract.

Independent positive relations correspond to all six runtime entries. Original
function category checks precede construction. Valid, supported inputs with
available exact leaf construction complete with the same original type and hint,
or stop at an interpretation boundary. The ordered log records each
constructor-initiated normalizer invocation, including its Plan, assembled tree
and actual normalization result. Recursive normalizer child calls remain in the
normalizer relation rather than being counted as separate constructor events.

Actual-subplan and boundary-path proofs identify the selected entry and stopped
local invocation, including named-root versus calculation wrapping. Source proofs
retain grouped diagnostics and actual decoded literal origins; they do not supply
raw offsets for each invocation. The result stores syntax separately from optional
construction. An absent construction does not classify a CSS syntax/type error.

Exact old parser projection and source-success embedding preserve the earlier
arithmetic profile. Its complete optional constructor outcomes are preserved for
arbitrary old Plans under the same environment, including boundary paths and
payloads. New invocation logs are additional evidence. Kernel cases inspect full
ordered invocation records, grouped versus direct arithmetic, optional endpoints,
retained comparisons, exceptional values and diagnostic distinctions.

Supplied environment availability must still correspond to the intended stage.
Reconstructing source with later layout data is not proved equivalent to retaining
its earlier simplified history. Negate lowering, broader conversion readiness,
concrete property acquisition and final censorship remain separate. No browser
or general direct-evaluator equivalence is claimed. See the
[dated source-construction contract](research/comparison-source-construction-20261017.md).


## Staged retained-calculation history

The stage runner continues an actual completed residual tree through supplied
specified, computed and used requests. It keeps each input frame, environment,
request and result, and passes the returned tree to the next request. Independent
relations certify execution, original type/hint preservation, completed-prefix
composition and the exact unprocessed suffix after a stop.

Checked environment extension preserves every already successful basis and unit
factor resolution. Its executable checker uses the independent finite inventory
of relative units and the checked basis resolver. New information may resolve
pending leaves. Invalid or irrelevant raw entries do not count as known
resolutions. Changing an already accepted factor stops this increasing-knowledge
model; general dynamic restyling is outside its scope.

The source facade preserves the entire construction attempt, diagnostics and
original invocation record. Only completed construction supplies a seed. An
initial interpretation boundary remains an initial boundary for every future
request list. Later order, knowledge and interpretation stops are distinct, and
no later request runs after them. Boundary provenance identifies an actual
subtree of the prior residual frame and its local unavailable reason.

A terminal observer requires an actual canonical numeric leaf and a supplied
production match. It returns the actual stage and unchanged original metadata.
This observation is stage-neutral and pre-censorship: a used-stage residual need
not be numeric, and negative zero, NaN and infinity remain observable. Property
clipping, integer conversion and serialization require separate finalization.

The source cases include a history distinction: constructing
`calc((-1 * 0) * (1px + -1%))` without a basis, then continuing with a positive
100px basis, produces positive zero. Constructing with that basis initially
produces negative zero in this uncensored model. Exact transition snapshots retain
the individual leaf hints and actual prior frames. Neither result establishes a
browser discrepancy or general source-reconstruction equivalence.

The caller must still justify each environment's availability at its stated
stage, including the initial source seed. This package does not infer property,
font or viewport data. It adds 93 named laws and 101 kernel cases across 18 modules;
these are artifact inventories, not counts of CSS requirements. See the
[dated staged-history contract](research/staged-calculation-history-20261017.md).


## Finalization of actual staged results

The finalization adapter reads the actual completed frame and canonical numeric
leaf from a retained stage history. It requires an actual computed or used stage,
a ready context, valid supplied bounds and an original-type production match.
Specified frames remain unavailable to this bounded adapter. Numeric, stage and
context unavailability, invalid bounds and production mismatch have separate
outcomes; their checking order is interface policy, not CSS error precedence.

The wrapper preserves the complete prior source attempt and Assessment, including
construction calls, stage inputs/results and stopped suffixes. It does not
reconstruct source, replace the retained tree or resume a stopped chain. Successful
source results carry the actual coherent leaf and original source type/hint,
checked environment extension, stage/readiness and outer Finished witness.

An actual successful continuation of a canonical computed result to used time
keeps the leaf and finalized value under the same context availability. The proof
requires that transition, so it cannot bypass an order or knowledge stop. This is
not a general normalization-idempotence or source-reconstruction claim.

The concrete number-opacity instance fixes empty initial information, one
computed request, number production and [0,1] bounds. Its theorem identifies the
actual computed frame and censorship of that frame's scalar. The current full-call
profile includes named comparisons and nested calc; percentages, bare values,
subtraction/Negate and unavailable constants/conversions remain outside it.
Kernel controls distinguish outer clipping from premature clipping of nested
intermediates and retain uncensored values in the original history.

This package adds 46 named laws and 72 kernel cases across 11 modules. It supplies
no new browser evidence or equivalence to the older direct-evaluator opacity
package. Environment acquisition, other concrete property contexts, implementation
precision, serialization and declaration admission remain separate. See the
[dated staged-finalization contract](research/staged-property-finalization-20261017.md).

## Strict ordinary stylesheet source to visibility

The strict source facade connects actual stylesheet token consumption to decoded
selector and declaration admission, author cascade, defaulting and inheritance.
It uses the existing qualified-prelude and declaration consumers directly. Every
accepted declaration retains its decoded components and important flag; lowering
assigns its actual global declaration index as source order. Selector-list weight
comes from the maximum matching branch. Whole accepted source computation is total
under the supplied document model, with actual source origins for candidates and
winners.

Admission is bounded to ordinary top-level rules, the current scope-free component
selector grammar, and visibility values visible/hidden/collapse plus
initial/inherit/unset. Unknown or unsupported content stops before rule/declaration
fallback. The result retains the lexical trace, accepted rule/body prefix and
actual stopping prelude or Candidate. No style is computed from a partial prefix.
A stop is not a certificate that the source is invalid CSS. Explicit brace endings,
EOF body recovery, token errors and terminal comment errors remain distinguishable.

Independent positive relations prove accepted-domain agreement with every reached
reader/validator call in the generic stylesheet engine under `appendPending`.
The total proof-target Profile is used only for this agreement; its off-domain
completion is not CSS recovery semantics. The current Syntax draft's terminal
pending-declaration omission remains an explicit CSSWG #11017 policy boundary.

The package adds 106 named laws and 96 kernel cases across 24 modules. Cases cover
selected selector-list specificity, duplicate declarations, important ordering,
inheritance/defaulting, decoded escapes, EOF diagnostics and late unsupported
content suppressing computation. These counts inventory the artifact, not CSS
coverage. No new browser comparison is claimed.

Display4 force-hidden, rollback keywords, other properties, custom properties,
var(), at-rules, nesting, layers and raw scope remain unsupported. The model
computes a visibility keyword; layout, painting, accessibility effects and CSSOM
serialization remain separate. Existing all-HTML selector and supplied-forest
premises still apply. See the [dated strict source contract](research/strict-visibility-stylesheet-20261017.md)
and [coverage priorities](research/coverage-priorities-20261017.md).

## Host-aware type and attribute compounds

The separate compound source profile accepts a type or universal head, unqualified
attribute blocks, or both. Heads may be unqualified, explicitly any namespace, or
explicitly null namespace. Admission requires a nonempty compound and complete
component consumption. Actual decoded names, ordered bracket components and the
full lexical/grouping diagnostics remain available.

Matching distinguishes HTML subjects in HTML documents from foreign subjects and
XML documents. Only the HTML-host case folds selector-side names and applies the
HTML default attribute-value case table. Explicit `i`/`s` flags affect values only.
Actual stored names are never rewritten, and unqualified attributes match only
actual null-namespace attributes. The profile assumes ordinary non-featureless
subjects and no declared default namespace.

Source and match provenance identifies actual parsed atoms and stored attributes.
Earlier successful explicit-head sources embed exactly. Compatibility with the
older HTML compound lowering requires an actual HTML host and an any-namespace
head; it does not expand that older profile to foreign or XML subjects.

The package adds 82 named laws and 180 kernel cases across 14 modules. Two browser
suite exporters provide 45 admitted same-source cases each for HTML and XML, with
exact document/namespace/name/attribute snapshots and five harness controls. Native
execution evidence is recorded separately. The known comment-separated attribute
operator boundary remains an explicit model-only case outside these suites.

IDs/classes, recursive selectors, lists/combinators/pseudos, named/default namespace
environments and attribute namespace syntax remain unsupported. Existing recursive
selector and strict visibility profiles retain their earlier host premises. No
whole mixed-host style computation or general browser equivalence is claimed.
See the [dated host compound contract](research/host-aware-compound-20261017.md).

## DOM identity and document-mode compounds

The separate DOM profile acquires its single concept ID and ordered class tokens
from actual null-namespace lowercase `id` and `class` attributes. Empty ID is
absent; class acquisition splits the five ASCII whitespace characters and removes
exact duplicate tokens in first-occurrence order. Cached Element identity fields
are ignored. Raw `getAttribute("id")` snapshots remain distinct from concept ID:
a prefix-free namespaced attribute can appear in the former but not the latter.

The source grammar adds ordered ID/hash and adjacent dot/identifier atoms to the
host-aware compound profile. It retains decoded spelling, actual component origins
and complete lexical diagnostics. Standards and limited-quirks ID/class matching
is exact; quirks matching folds ASCII values even on foreign subjects. Ordinary
`[id]` and `[class]` selectors retain their separate attribute case rules.

The checked evaluator distinguishes unsupported source, invalid supplied host
context and a Boolean match. `ValidHost` checks only language/mode compatibility
and unique namespace/localName attribute keys. It does not authenticate a real
DOM snapshot or owner-document membership. Source-first checking is interface
policy. Ordinary non-featureless subjects and no default namespace remain premises.

This package adds 111 named laws and 196 kernel cases across 16 modules. Three
browser exporters supply 32 same-source cases each for standards HTML, quirks HTML
and XML, with actual document construction/readback and six perturbation controls.
Limited quirks remains model-only; finite browser execution is recorded separately.
Attribute-only old host compounds embed exactly. No general XML schema identity,
dynamic mutation, recursive host selector or mixed-host style theorem follows.
Lists, combinators, pseudos and namespace environments remain outside this profile.
The inherited comment-separated attribute-operator admitted-source gap remains
explicit and is excluded from required native cases. See the
[dated DOM identity contract](research/dom-identity-compound-20261017.md).

## Preserved-name host selector chains and lists

The separate chain source profile extends DOM identity compounds with descendant,
child, adjacent and subsequent-sibling combinators and complete selector lists.
Its scanner retains actual component chunks, treats bracket contents atomically,
and distinguishes real whitespace from comments. Every branch must be supported;
a later unsupported branch suppresses evaluation of the entire list. The complete
lexical/grouping attempt remains available, and unsupported does not mean invalid CSS.

Lowering emits actual host observations, steps and alternatives, with no old
cached/HTML selector leaves. Each visited ancestor or sibling supplies its own
stored names and acquired ID/classes under one fixed document language and mode.
Independent witnesses retain the ordered compounds, actual related subjects,
selected identity attributes and corresponding source component chunks. The
machine preserves the exact ordered compound inventory without loss or duplication.

The checked facade validates mode compatibility and unique attribute keys at all
nodes before matching admitted syntax. This includes unused nodes by interface
policy; it is not a DOM-authentication or CSS-validity test. Static same-document
forest/snapshot faithfulness and ordinary non-featureless subjects remain premises.
Per-chain specificity stays separate from list disjunction. No global maximum
list weight is promoted to a matched rule's specificity. Old HTML compatibility
requires actual all-node HTML/cache agreement, nonquirks mode and any-namespace heads.

This package adds 114 named laws and 217 kernel cases across 17 modules. Three
native exporters each provide 41 source cases on a deeper mixed-namespace tree,
with the existing document/mode/topology controls; execution evidence is separate.
Limited quirks remains model-only. Functional pseudos, scope, structural filters,
shadow topology, namespace environments and whole mixed-host style are not admitted
by this slice. The inherited comment-separated attribute-operator discrepancy
remains explicit and is excluded from required native fixtures. See the
[dated host-chain contract](research/host-recursive-integration-20261017.md).

## Preserved-name host logical selectors

The separate logical source profile adds nested `:is()`, `:where()` and `:not()`
to actual host compounds and four-combinator chains. Every argument list is
nonempty and every branch must be supported. Unknown syntax makes the entire
bounded admission unavailable, including below negation. This does not classify
that syntax as invalid CSS or implement forgiving branch removal. Empty `:is()`,
`:where()` and valid selectors such as `:not(:is())` remain outside this profile.

The mutual syntax retains original decoded names, function boundaries and argument
order. Lowering starts from actual heads, atoms or function arguments and emits
dedicated host observations; it introduces no old cached selector leaves or
synthetic source identity atoms. Independent matching and specificity agree with
the generic recursive model. `:is()` and `:not()` use the maximum weight of all
arguments, including unmatched ones; `:where()` contributes zero. Outer selector
lists retain separate branch weights and are not yet a mixed-host cascade adapter.

Recursive parsing consumes actual smaller function bodies and preserves complete
lexical/grouping attempts. Exact old successful source admission lifts with the
same grouped object, matching and specificity. Positive subject witnesses locate
actual node-specific acquisition and source terminals. Negation instead requires
absence of matches for all arguments; its syntactic terminal inventory is retained
without claiming positive subjects or an exhaustive runtime visitation log.

The checked evaluator validates the entire supplied context before matching
admitted syntax. Invalid unused nodes therefore block negation by interface policy.
These checks establish mode compatibility and unique attribute keys, not DOM
authentication, topology faithfulness or CSS validity. The package adds 190 named
laws and 220 kernel cases across 23 modules. Three native exporters supply 41 cases
each under standards HTML, quirks HTML and XML; execution evidence is separate.

Forgiving recovery, empty functions, `:has()`, structural filters, scope, shadow
topology, namespace environments and whole mixed-host style remain separate.
Limited quirks is model-only. The inherited comment-separated attribute-operator
source discrepancy remains explicit and excluded from required native fixtures.
See the [dated logical contract](research/host-logical-recursion-20261017.md).

## Preserved-host whole-stylesheet visibility

The separate `CssHostVisibilityStylesheet.observe` entry now connects actual
whole ordinary source to preserved-name host selector matching, author cascade
and visibility defaulting/inheritance. Matching and inheritance share the exact
supplied forest. Rule specificity uses the greatest matching outer-list branch;
`:is()`/`:not()` argument maxima and `:where()` zero retain their own rules.
Independent source relations and accepted-domain generic-engine simulation cover
all reached declaration and qualified-rule decisions under explicit
`appendPending`. Actual source order, important flags, candidate/winner evidence,
matched subjects and parent computation are retained.

The checked entry first retains and admits the complete source, then validates
fixed host mode and unique attribute keys at all nodes. Unsupported trailing
content suppresses the whole computed result; it is not classified as invalid
CSS. Context validation does not authenticate actual DOM topology. The profile
models one applicable author unlayered sheet with no other contributing
UA/user/inline/presentation/animation/transition declarations. Values are
visible/hidden/collapse plus initial/inherit/unset. Current draft force-hidden,
other properties, variables, rollback, at-rules/nesting, raw scope/layers,
namespace environments and the logical source profile's remaining exclusions
stay unsupported. No rendering or accessibility result follows.

The package adds 23 modules, 100 named laws and 108 kernel observations. Its
native exporter supplies 26 whole stylesheet scenarios and 37 computed queries
on a standards HTML document containing HTML, SVG and null-namespace elements.
Opt-in CSSOM admission checks verify effective declarations before reading
computed values, with actual invalid-value and summary mutation controls;
CSSOM duplicate collapse is distinct from preserved authored declaration history.
XML/quirks computed results remain model-only. The inherited comment-separated
operator discrepancy remains excluded from required native cases. Full/fresh and
native execution are separately recorded in the research acceptance ledger.


## Host structural selectors through source and style

The separate `HostStructuralSource` / `HostStructuralEvaluation` and
`CssStructuralVisibilityStylesheet.observe` entries add root, first/last/only
child and of-type, four An+B families and supported nonempty nth-child/last-child
filters to the preserved-name host pipeline. Actual component consumers retain
An+B and `of` splits, nested filter source occurrences and diagnostics. Unknown
filter branches stay unavailable even under negation. Old successful logical
sources lift exactly with the same grouped source object, semantics and weight.

Root uses the actual supplied documentElement. Inclusive sibling rank requires
subject membership and retains the exact ordered matching subset. Same-type
ranking compares stored namespace/local-name pairs; it does not fold DOM names.
The equivalent host type-selector theorem requires an unchanged-name premise.
Script-created uppercase HTML names expose a distinct prose interpretation
boundary, documented with targeted Firefox observations. Fragment singleton
fixtures test absence of an element parent without claiming truly unparented
DOM nodes or deriving singleton siblings from parent=None alone.

Filtered nth adds one pseudo-class weight plus the maximum of all filter
arguments. Only-child/of-type contribute one weight, and outer rule lists retain
the maximum matching branch. Whole-source style uses the same forest for
matching and inheritance, explicit appendPending, strict complete-source
admission and actual candidate/winner provenance. This remains a single author
unlayered visibility profile with no other contributing declarations.

The package contains 53 modules, 355 named laws and 418 kernel cases. Its native
exports contain 69 matching cases per HTML standards/quirks/XML document and
24 whole stylesheets with 40 standards-HTML computed queries, with actual
CSSOM admission. Build and native execution acceptance is recorded separately.
`:empty`, empty/forgiving logical functions, relative/scope/shadow semantics,
namespace environments, dynamic invalidation and layout remain unsupported.
Limited quirks and XML/quirks computed results remain model-only. The inherited
comment-separated attribute-operator discrepancy remains excluded from native
cases. These results do not prove the CSS prose or general browser refinement.


## Host empty logical functions and certified forgiving source/style

`HostForgivingSource` and `HostForgivingEvaluation` add actual empty is/where
terminals, which match false with zero specificity. `not(is())` remains a real
nonempty negation; an nth filter whose only branch is an empty is function is admitted
but selects no siblings. Not, nth-of and outer rule lists remain unforgiving.

A whole-body AnyValue gate precedes exact comma partition and branch recovery.
Only independently certified empty or forbidden-start branches are discarded.
Unknown unsupported branches stop bounded admission, including under negation.
Retained order and duplicate branches are preserved. Is uses all retained
argument weights, where stays zero, and outer style uses matching branch weights.

`HostForgivingRecoveryView.inspect` retains the original source attempt and
extracts ordered recovery decisions with exact original chunks. Independent
relations prove source-preorder locations and actual recovery certificates,
following only retained branches. This view is evidence extraction, not a
runtime event trace. Old successful structural sources lift exactly through
proved AnyValue safety and direct-comma partitions, with unchanged matching and
weights; no old parse-failure equivalence is claimed.

`CssForgivingVisibilityStylesheet.observe` connects this source profile to the
same strict whole-sheet visibility pipeline, accepted-domain engine simulation,
appendPending policy and shared matching/inheritance forest. Unknown trailing
source suppresses computation. All-node host validation and one author unlayered
sheet with no other contributing declarations remain premises.

The package contains 62 modules, 440 named laws and 348 kernel cases. Native
exports contain 45 matching cases per HTML standards/quirks/XML document and
25 standards-HTML stylesheets with 32 computed queries, including effective
CSSOM admission of empty unmatched rules. Execution acceptance is recorded
separately. General invalidity/forgiving recovery, :empty version semantics,
relative/scope/shadow profiles, namespace environments, dynamic invalidation and
layout remain outside this profile. Limited quirks and XML/quirks computed results
remain model-only. The inherited comment-separated attribute-operator discrepancy
remains explicit and excluded from required native cases. This is neither a
mechanical translation of CSS prose nor general browser equivalence.

## Host anchored relative selectors through source and style

`HostRelationalSource` and `HostRelationalEvaluation` add nonempty `:has()`
arguments over actual preserved-name host chains. `HostRelative` gives direct
anchor-to-node reachability and exact generic path lowering. The first axis is
an actual omitted descendant or explicit child/adjacent/following combinator.
Ordered path witnesses retain the actual visited compounds and subject nodes.
Nested logical tests use the full context: `:has(:is(body .Selected))` can inspect
an ancestor outside the anchor subtree, unlike the direct relative path
`:has(body .Selected)` at an anchor below body.

The whole has body passes AnyValue, then every direct comma chunk must parse as
one actual chain. Has arguments remain unforgiving. Frozen argument chains
cannot retain nested has; the richer outer syntax permits has inside logical
and nth filters. Unknown unsupported syntax never becomes a discard certificate.
Empty is/where inside a relative branch remains false, while a negated empty
branch still needs an actual reached node. Has uses the maximum argument weight;
outer stylesheet lists continue to use the maximum matching branch weight.

Old successful sources lift with their actual grouped object and recovery
decisions, preserving matching and specificity. Source, selected branch and
visited-subject provenance remain distinct from exhaustive execution traces.
`CssRelationalVisibilityStylesheet.observe` uses the same complete-source
admission, appendPending policy, shared matching/inheritance forest and actual
candidate/winner evidence. Its scope remains one author unlayered visibility
sheet with no other contributing declarations.

The package contains 63 modules, 441 named laws and 359 kernel cases.
Native exports contain 50 matching cases per HTML standards/quirks/XML document
and 26 standards-HTML stylesheets with 36 computed queries and effective CSSOM
admission. Execution acceptance is recorded separately. Full validity, retained
nested has, empty has, versioned :empty, scope/shadow, namespace environments,
dynamic invalidation and layout remain outside the profile. Limited quirks and
XML/quirks computed results remain model-only. The inherited comment-separated
attribute-operator discrepancy stays explicit and excluded from native fixtures.
This is neither mechanical CSS prose translation nor general browser refinement.

## Raw named layers through whole-source visibility

The bounded layer profile now reads actual top-level `@layer a,b;` statements,
flat named blocks, reopened names and ordinary unlayered rules. It records every
registration event, including empty blocks and repeated names, before assigning
actual declarations their layer ranks. Declaration `sourceOrder` counts only
admitted declarations. Normal and important precedence, unlayered extremes,
actual matching-branch specificity and inheritance use the same context forest.
The checked evaluator retains source and assignment history; unsupported trailing
input produces no partial computed result. Existing accepted unlayered sources
retain their exact rules and values.

Layer rule lists and declaration bodies have distinct reader contexts. The
accepted-domain generic-engine proof includes actual declaration attempts,
forced-none results, restoration and nested qualified parsing, with explicit
`appendPending`. It preserves witnessed EOF/brace endings and diagnostics.
This does not establish general CSS recovery fidelity.

Names are single decoded identifiers with exact case-sensitive identity.
Escaped punctuation stays within that segment; dotted paths are deferred.
The selected draft excludes six CSS-wide names, including `revert-rule`, and
allows `default`. A [retained Firefox probe](research/raw-layer-name-probe-20261017.json)
accepted the six excluded names; this remains explicit candidate-discrepancy
evidence outside the model's admitted domain, with no new bug claim.
[CSSOM probing](research/raw-layer-serialization-probe-20261017.json) also separates
serialized API names from decoded registry identity.

The package contains 43 modules, 240 named laws and 136 kernel cases. Native expectations contain 33 standards-HTML sheets and 42
computed queries with recursive CSSOM rule/declaration admission. Layer-order
and winning-layer mutations distinguish admission from final-value comparison.
Exported expectations are separate from execution reports. The model assumes
one author sheet with no other contributing declarations and faithful supplied
host/topology data. Limited quirks and XML/quirks computed controls remain
model-only, as does the inherited comment-separated attribute-operator gap.

Nested/dotted/anonymous layers, imports, conditionals, rollback, scope, variables,
other properties, full validity/recovery and rendering remain explicit future
work. This initial layer subset is not full CSS conformance, a mechanized prose
translation or a general browser-refinement theorem.


## Nested and dotted named layers through whole-source visibility

The separate nested-layer source profile admits recursive named blocks and dotted
paths using actual identifier/dot components. Relative paths concatenate enclosing
segments; an escaped dot remains inside one segment. Every segment retains the
selected draft's keyword exclusions. Complete source admission precedes pure
assignment, and unsupported input prevents partial computed results.

Assignment retains immediate source-preorder hierarchy snapshots and declaration
paths. Final children-before-parent ordering places a parent's direct declarations
after all its descendants. Adding a child can change numeric ranks, so resolution
uses the complete final hierarchy. The proofs preserve existing path identities
and pairwise order, and connect final ranks to normal and important cascade
precedence. Only declarations advance sourceOrder. Exact source, candidate/winner,
host-subject and stored-history provenance is retained.

Independent recursive grammar and accepted-domain generic-engine simulation retain
actual reader contexts, restored attempts, nested flags, errors and explicit
appendPending. Old successful flat sources preserve exact compiled rules and
checked decisions; the richer event history is not asserted equal to the old one.

The package adds 50 modules, 270 named laws and 152 kernel cases. Native expectations
cover 36 standards-HTML sheets and 44 computed queries with recursive CSSOM
admission and order/winner mutation controls. Execution reports remain separate.
Dotted and nested authored grouping, serialized CSSOM names and decoded identities
are distinguished. The retained keyword disagreement and inherited attribute
operator/comment gap remain explicit, with no new browser-defect claim.

Anonymous layers, imports, conditionals, rollback, raw scope, other properties and
general recovery remain unsupported. The same one-author-sheet, no-other-contributor
and faithful host/topology premises apply. Limited quirks and XML/quirks computed
controls remain model-only. This is neither a mechanical CSS prose translation
nor general browser equivalence.

## Anonymous occurrence layers through whole-source visibility

The separate anonymous-layer profile adds unnamed blocks to the recursive named
and dotted source pipeline. An actual whitespace-only prelude denotes omission;
`@layer;` remains unavailable. Independent grammar and accepted-domain engine
simulation preserve reader contexts, restored attempts, nested flags, diagnostics
and appendPending. Whole source acceptance precedes pure assignment.

Tagged anonymous IDs are distinct from authored names. Each anonymous block,
including an empty one, allocates once in source preorder. Named registrations
and declarations do not advance the counter. The public single-sheet entry starts
with empty registry and zero counter. Proofs preserve hierarchy well-formedness,
ID bounds and uniqueness in the actual node inventory. Repeated anonymous ancestor
references in descendant paths do not create new nodes. Cross-sheet identity needs
a later stylesheet-instance model.

Named children reopen under the same anonymous parent and stay distinct under
different anonymous parents. Final hierarchy traversal can reverse allocation
order; IDs are not cascade ranks. Entries retain full tagged paths until final
children-before-parent resolution, with normal/important precedence and
unlayered extremes. Only declarations advance sourceOrder. Exact reached States,
source block occurrences, candidate/winner and stored computation provenance are
retained. Old accepted named sources preserve mapped histories, unchanged counter,
compiled rules and checked decisions.

The package adds 55 modules, 316 named laws and 136 kernel cases. Native
expectations contain 34 standards-HTML sheets and 42 computed queries with
recursive CSSOM admission and order/winner mutation controls. CSSOM's empty block
name is an observation, not the anonymous identity. Two anonymous parents with
equal child names and important declarations distinguish separate occurrences;
reopening within one parent is tested separately. Execution evidence remains
separate from these expectations.

The one-author-sheet/no-other-contributor and faithful host/topology premises
remain. Conditional ordering, imports/instances, rollback, raw scope, variables,
other properties and general recovery remain unsupported. Limited quirks and
XML/quirks computed controls remain model-only. Retained layer-keyword and
attribute-operator/comment disagreements remain explicit. This is neither full
CSS layer coverage, mechanical prose translation nor general browser equivalence.

## Document-global conditions through source-derived layers and visibility

The separate conditional profile adds actual media and supports groups to the
named/dotted/anonymous source pipeline. Media admission supports empty lists,
all/screen/print, not/only and complete comma branches. Supports admission retains
literal visibility values, numeric-singleton false certificates, actual optional
important extraction, parentheses, not and homogeneous and/or. Unknown syntax
remains unavailable even under negation or a Boolean shortcut. Fixed usable
visibility support and the supplied medium are explicit processor premises.

Complete source admission precedes both semantic passes and checks false bodies
too. Original groups, reader contexts/restored attempts, diagnostics, endings and
appendPending remain in the accepted-domain engine simulation. A bounded stop
is not a CSS-invalid verdict or a claim of full CSS error recovery.

Medium-independent annotation assigns anonymous occurrence IDs throughout the
complete source, including suppressed groups. Activation has no allocator: false
global groups retain their local condition event but omit descendant registration
and declarations. IDs therefore keep source identity across screen and print and
can have inactive gaps. Active hierarchy invariants and final path ranks remain
proved; IDs are not ranks. Dense active declaration sourceOrder preserves the
positional Sublist and relative order of complete marked declarations, including
duplicates, without asserting equal numeric positions across media.

Stored source, annotation, activation and final rule witnesses retain actual
condition/source provenance, candidate/winner priority and matching-branch
specificity, host observations and inheritance through the same supplied forest.
Old accepted anonymous sources preserve final registry/entries, compiled rules
and checked outcomes for either medium. Earlier failure behavior is not equated.

This package adds 55 modules, 277 named laws and 172 kernel cases.
Native expectations comprise 38 standards-HTML sheets and 45 screen queries.
The opt-in harness checks actual conditional CSSOM classes/text and false-body
children, native matchMedia and one-argument CSS.supports truth, and the queried
iframe's medium. Separate condition truth/source-admission and computed-winner
controls join the existing layer controls. Exported expectations are not execution
evidence; completed main/fresh/native/archive records remain separate.

The one-author-sheet/no-other-contributor and faithful host/topology premises
remain. Print and limited-quirks/XML computed controls remain model-only.
General media/support, element-sensitive conditions, imports/instances, rollback,
raw scope, variables, other properties and dynamic/layout effects remain open.
The admitted comment/operator browser gap and excluded layer-keyword mismatches
remain explicit. This is not full CSS coverage or a browser equivalence theorem.

## Imports, stylesheet instances, and source-derived layer visibility

The import profile reads complete raw stylesheets through the actual tokenizer,
component and rule consumers. An import header retains its decoded URL, optional
named or anonymous layer, optional direct-declaration or grouped supports
condition, and bounded media list. Actual semicolons and sheet-local placement
are required: layer statements leave the prelude open; admitted ordinary rules
and blocks close it. Nested imports, charset, named supports-condition rules and
other unsupported forms stop this bounded entry. These exclusions do not classify
all such syntax as invalid CSS or implement general CSS recovery. The accepted
source simulation preserves the same lexical object and generic rule tree under
explicit sheet/body/declaration contexts and `appendPending`.

A supplied resolver and finite resource catalog describe addresses and actual
available or failed resources. Preparation retains source parse attempts; it is
not proof of fetching or association. Expansion distinguishes false-support
suppression, permitted inactive-media skipping, failed loads, admitted loaded
instances, unresolved addresses, missing resources, ancestor cycles and
unavailable source syntax. Available inactive sheets still require complete
bounded admission. Inherited media eligibility is carried into child imports.
The inline root's base address is separate from an optional actual resource
address. Repeated sibling imports of the same URL remain separate instances;
cycle checks use resolved ancestor addresses. Recursion decreases an actual
remaining-catalog/input measure, without an arbitrary depth limit.

Root-local anonymous IDs preserve the complete root source interval, including
suppressed blocks. Other IDs encode separate wrapper and imported-local keys
using actual source item-index paths. A URL is not an instance identity, and an
encoded ID is neither an expansion ordinal nor a layer rank. Relocation retains
the original local annotation witness. The actual checked run proves unique
anonymous tree nodes in its stored active registry, using source occurrence
separation and fresh-key absence without assuming numeric encounter order.
Active registration records failed layered
imports when conditions hold and suppresses false conditions. Entries retain
full tagged paths until final hierarchy rank resolution; dense source order
counts active declarations. Readiness proves final rule lowering succeeds for
successful checked expansion. Source, catalog, import and host failures remain
distinct, with no computed prefix after an unavailable whole-source result.

Provenance connects actual stored expansion, activation and rules to reached
headers, resource source text, ancestor conditions, declaration tokens, final
layer rank, selected outer selector branch and same-forest inheritance. The old
successful conditional-source profile embeds with unchanged compiled rules when
the supplied catalog has unique addresses. No equality of old failure results is
claimed. URL/Fetch correctness, resource authenticity, usable support and actual
host/tree correspondence remain explicit premises; the model does not infer them
from a cache, raw record or non-null associated sheet.

The separate HTTP runner uses real same-origin document and stylesheet resources,
exact response status/MIME/body journals, authored import URLs and resolved
associated-sheet URLs, actual parent/owner links and distinct stylesheet objects.
It checks recursive CSSOM, support/media truth, load/error events and host
snapshots before comparing computed visibility. The report records the installed
Nightly executable path, unchanged pre/post SHA-256, runtime version and build ID;
this is not a repository objdir build. Direct import supports text is
grouped for the one-argument `CSS.supports` API. Unique uncached false-support
resources provide finite no-request observations. Failed loads and successful
empty stylesheets are distinguished independently of CSSOM association. Seven
controls include altered actual response bytes, URL resolution, header/support
summaries, source conditions, host snapshots and an admitted computed winner.

All normative expectations remain in the report. The current finite Nightly
observations agree on 32 of 34 queries. Two false-support layered-import order
cases disagree: null association and no request accompany the cascade order of a
registered layer. The current normative trace supports the existing model;
normal and important controls, including false-media and no-import baselines,
remain recorded. A separately fingerprinted discrepancy manifest requires exactly
these observations and never counts them as model matches. Protocol/control
acceptance is reported separately from computed agreement. This is neither a
universal browser refinement nor a new defect adjudication. See the retained
[trace](research/import-false-supports-order-trace-20261017.md) and
[evidence](research/import-false-supports-order-evidence-20261017.json).

Redirects, cross-origin/security/encoding/Fetch behavior, unavailable external
resource semantics, multiple top-level author/UA/user sheet ordering, general
media/supports, element-sensitive conditions, rollback/revert-layer/revert-rule,
raw scope, variables and other properties remain separate gaps. The inherited
comment-separated attribute-operator gap remains admitted model syntax with an
unresolved native discrepancy; reserved layer keywords remain excluded-profile
observations. This package does not replace those boundaries or claim completion
of CSS imports or the cascade.

## Source-derived author visibility with `revert-layer`

The rollback profile adds direct `visibility:revert-layer` to the bounded imported, conditional, nested/anonymous-layer source path. Its 63 modules and 274 public laws use distinct declaration/source admissions while reusing the actual source-position annotation, import expansion and active layer registration machinery. A new preparation relation establishes the same raw source/annotation objects without claiming that the older declaration profile accepted rollback. The checked run proves final rank readiness and unique anonymous tree-node identities for its same stored active registry.

Each subject has an ordered candidate list and an exact winner trace. A rollback step records the full list, the actual `Cascade.winner`, and the surviving ordered list. The independent interval relation removes the closed interval from the selected layer's normal position through its important position; surviving entries are in physically earlier layers. All actual candidates and trace lists are proved author and unattached. Equal-key ties follow the executable winner's list order; an arbitrary maximal declaration is not substituted. Literal terminal values then use visibility defaulting and inheritance over the same supplied host forest. The public observation retains the queried subject's trace; inherited computation can use additional ancestor traces.

Source proofs connect each selected rollback and terminal literal to its real declaration consumption, priority, final registered path/rank, active import/global-condition ancestry, and actual matching selector branch. Ordered snapshots preserve duplicates before filtering. Old successful source graphs retain their compiled rules under literal value embedding and compute the same values, even when an unreachable previously unavailable catalog sheet becomes newly admissible. No equivalence of old failure outcomes or arbitrary prepared catalogs is asserted.

The corpus contains 131 ordered checks, including exact trace snapshots and 62 HTTP sheets/69 computed queries. The HTTP corpus retains all 31 prior import sheets, including their two documented false-support layer-order disagreements, and adds 31 rollback sheets/35 queries. Actual recursive CSSOM, request/status/MIME/body data, URL bases, repeated instance objects, document/host snapshots and eight phase controls (including an admitted rollback-boundary mutation) remain checked. Browser protocol acceptance is separate from model agreement; final producer-bound evidence is recorded separately from exploratory runs.

This profile is limited to direct declarations in one author, unattached stylesheet graph with no other contributing declarations, a faithful supplied resolver/resource catalog, and the existing host/context premises. It does not add `revert`, `revert-rule`, attached style, other origins, variables or substituted rollback values, other properties, element-sensitive conditions, broader URL/Fetch behavior, or multiple top-level sheet composition. A supports test for `visibility:revert-layer` remains outside the existing bounded supports grammar. General selector recovery, raw scope and the rest of the coverage inventory remain open. The admitted comment-separated attribute-operator gap remains distinct from the excluded reserved layer-name browser observations and the retained false-support import disagreements.

## Ordered inline author stylesheet roots

The author-sheet profile accepts an ordered list of source strings sharing one document base, host forest, medium and resource environment. It prepares each source independently, retains the exact indexed root/import expansion, then activates all expanded roots into one layer hierarchy. Only after all roots register does it resolve final layer ranks and assign one global declaration order. The existing exact rollback candidate/step history and same-forest visibility defaulting consume that final rule list.

The 34 modules and 149 public laws preserve per-root boundaries through an independent sequential activation relation. Anonymous identities use the actual root index and import-occurrence path; repeated resource addresses do not merge instances. The same stored active registry is proved well formed with unique anonymous tree-node IDs. Selected declarations, layer registrations, terminal literals and rollback steps retain their actual root/source position, reached import and condition ancestry, selector match, priority and final rank. A successful older inline single-root computation compiles to exactly the same rules after injective identity renaming; numeric anonymous IDs need not agree, and no old failure equivalence is claimed.

The checked interface validates every root source before catalog validity and reached import expansion. It reports the earliest unsupported root or actual stopped import root index, and produces no computed prefix. This is a bounded diagnostic policy, not a browser parse/load chronology claim. An empty root list still validates the catalog and global host context. Unknown source syntax remains unavailable even in retained inactive bodies.

There are 96 ordered kernel checks, including 41 native scenarios/46 computed queries, 30 diagnostic/history checks and 20 identity/rank checks. Native scenarios use three actual modeled style-owner nodes in the same ten-node host forest, including empty root sources. The separate HTTP harness verifies actual document/style-sheet order, enabled/untitled/empty-media inline premises, every root's load outcome, recursive CSSOM and distinct imported sheet objects, resource status/MIME/bytes, resolved bases and condition truth. Delayed resource responses distinguish owner order from completion order. Eleven controls distinguish protocol/admission failures from admitted changes to root order, layer order and rollback boundaries. Research observations are 44/46, with the same two false-support import ordering disagreements retained explicitly; protocol acceptance does not imply computed agreement. Final producer-bound native and clean-source/archive gates are recorded separately.

After `check.py` succeeds, run `python3 author_sheets_browser_check.py --firefox "/Applications/Firefox Nightly.app/Contents/MacOS/firefox" --lake /path/to/lake` for the separate producer-bound suite. It writes `.lake/browser-check/author-sheets-visibility/report.json`; a zero exit status certifies the protocol and expected discrepancy set, not full model agreement.

This slice covers static enabled inline author roots with no other contributing declarations. External top-level sheets, alternate/disabled/adopted sheets, dynamic sheet order, other origins, attached styles, element-sensitive conditions, broader URL/Fetch behavior and general CSS recovery remain outside it. Root strings alone do not prove CSSOM order or actual owner topology; those are explicit host/native correspondence premises. The broader inventory remains open, including other properties, substitutions and rollback forms. The admitted comment-separated attribute-operator gap, excluded reserved layer-name observations and two false-support import disagreements remain distinct.

## Owner-bound author style attributes

The attached-style profile acquires each owner's actual null-namespace lowercase `style` attribute from the same host context used by selectors and inheritance. Supported host namespaces are HTML, SVG and MathML, subject to faithful inline-style interface correspondence, usable CSS and no blocking CSP. A present exact style key on another namespace returns `unsupportedOwner`; an absent exact key contributes no attached declarations. Differently cased or namespaced keys remain distinct.

The complete attribute parser calls the actual declaration consumer with `nested=false`. It preserves duplicate declarations, priority and consumed suffixes. Empty input, whitespace and semicolons complete; a closing brace never completes an accepted prefix. Unsupported properties/values, at-rules and recovery make the whole attribute unavailable. This is a bounded strict domain, not a claim that native CSS recovery rejects those inputs. Accepted inputs simulate the existing declaration-list engine with exact accepted-event order.

Existing ordered author-sheet/import preparation, registration and final layer ranks remain shared. Each subject's own direct attribute candidates follow its stylesheet candidates, with author origin, attached priority, no layer and exact local declaration order. No synthetic selector is created. Defaulting evaluates every ancestor's own attached candidates on the same forest. Source-first acquisition across finite context nodes is an interface diagnostic policy, not a document-order theorem. Root/import failures precede acquisition; complete acquisition precedes the global host guard; no computed prefix is exposed on failure.

The independent mixed attachment interval preserves author-important stylesheet rules when an important attached `revert-layer` wins. Normal attached rollback retains normal unattached entries; ordinary rollback retains physically earlier unattached entries and important attached entries outside its interval. Exact actual-winner traces retain ordered before/after lists and source origins. Actual lists satisfy the author/no-layer-for-attached premises. Old all-unattached traces agree exactly, and old successful computations are preserved when every owner has an absent or admitted empty attribute, including ancestor defaulting.

The isolated package contains 30 modules, 175 public laws and 128 ordered checks. Its HTTP browser suite has 72 scenarios and 80 queries, retaining the three modeled inline style owners and ten actual nodes in each scenario, including an explicit MathML namespace variant. Admission verifies actual raw attribute keys/values, host interfaces and effective CSSOM declarations separately; CSSOM duplicate collapse is not used as authored history. Fourteen controls distinguish source/admission failure from admitted cascade changes. The research run agrees on 78/80 queries and retains exactly the two inherited false-support import-order disagreements. Protocol success is distinct from complete model agreement. Main/fresh/final-native/committed-archive gates remain separate.

After `check.py` succeeds, run `python3 attached_style_browser_check.py --firefox "/Applications/Firefox Nightly.app/Contents/MacOS/firefox" --lake /path/to/lake`. Evidence is written to `.lake/browser-check/attached-style-visibility/report.json` and pins the executable before/after hash as well as the exact producer/source vector.

Other origins, presentation attributes, animations/transitions, actual blocking CSP algorithms, external/alternate/adopted/dynamic sheet acquisition, element-sensitive conditions, substitutions, other properties and general recovery remain outside this profile. The broader coverage inventory remains open. The admitted comment-separated attribute-operator gap, excluded reserved layer-name observations and two false-support import disagreements remain separately documented.

## Source-derived named container groups

This fragment follows [Conditional 5 container names](https://drafts.csswg.org/css-conditional-5/#container-name), [name-only queries](https://drafts.csswg.org/css-conditional-5/#container-rule), and [Cascade 5 layer ordering](https://drafts.csswg.org/css-cascade-5/#layer-order), with the bounded source domain below.

The named-container profile admits a single decoded custom identifier in `@container` and actual `container-name` declarations alongside visibility. Name lists preserve decoded spelling, order and duplicates; `none` supplies the empty list. Initial, inherit, unset and revert-layer use the existing cascade/defaulting machinery. Name admission excludes the six current CSS-wide keywords, default, none, and, not and or in ASCII case permutations. Identity remains case-sensitive. Layer-name admission remains a separate grammar.

Container metadata comes from actual stylesheet/import and same-owner style-attribute declarations, including specificity, importance, shared final layer ranks, attached priority and exact rollback histories. The property is non-inherited with an empty initial name list; explicit inherit uses the same forest. Metadata is computed first. Each name-only query then searches strict ancestors for the nearest matching decoded name. Missing eligible ancestors produce the query's unknown outcome; unsupported syntax is unavailable. Nested guards retain separate ordered nearest-container witnesses, and may select different ancestors.

The complete source checker excludes container-name declarations inside any container group, including descendants under false document-global conditions. This bounded dependency rule is checked before suppression. Visibility declarations and nested container groups are supported there. Global media/supports and import conditions keep their existing behavior. A container group registers its layers independently of whether any subject matches; false document-global conditions still suppress registration.

The rich source tree retains original headers, consumed tokens and source positions. A separate synthetic registration view reuses the accepted import and layer machinery, without asserting that invented conditions were parsed from CSS. Actual prepared-source witnesses prove restoration/enrichment and final lowering succeed. Imported syntax and metadata-scope failures return their real rich reason rather than the internal view sentinel. Final registry well-formedness and anonymous occurrence uniqueness are proved for the same stored run.

All globally active mixed-property declarations receive positions before property projection or container applicability. Ordered property projections preserve gaps and duplicate declaration positions; attached offsets use the complete mixed rule count. Actual metadata rules are proved guard-free. Candidate, rollback, terminal, selector and container-header origins reach real accepted source occurrences; same-forest defaulting retains per-subject traces for both properties. Old successful attached-style computations are preserved through exact source/preparation images, including imported resources and ancestor attributes; no old failure equality is claimed.

The isolated package contains 123 modules, 630 public laws and 437 ordered checks. Its HTTP research corpus has 105 scenarios, 115 visibility queries, three modeled inline style owners and ten actual nodes per scenario. It verifies 1,050 computed container-name readbacks separately from decoded semantic names and effective declaration CSSOM. Seventeen controls distinguish admission, computed metadata and admitted visibility changes. The research run agrees on 113/115 visibility queries and retains exactly the two inherited false-support import-order disagreements. Effective CSSOM duplicate collapse is not authored declaration history. Main, independent fresh, producer-bound native and committed-archive gates remain separate.

After `check.py` succeeds, run `python3 named_container_browser_check.py --firefox "/Applications/Firefox Nightly.app/Contents/MacOS/firefox" --lake /path/to/lake`. Evidence is written to `.lake/browser-check/named-container-visibility/report.json` and pins the executable before/after hashes and exact producer/source vector.

Size, style, scroll-state and other container features, container-type and container shorthand, comma queries, metadata inside container groups, arbitrary supports tests for the new property, substitutions, other origins, animations, broader sheet acquisition and general CSS recovery remain unavailable. Host/interface, resolver/resource and usable-CSS premises remain explicit. This is a bounded latest-spec extension; the broad coverage inventory remains unfinished. The admitted comment-separated attribute-operator gap, excluded reserved layer-name observations and two false-support import-order disagreements remain separately documented.

## Bounded user/agent source acquisition and origin rollback

The origin profile extends the strict source pipeline with ordered user-agent, user and author inputs, each with its own source-derived layer registry and actual import graph. Installed roots retain their resource base and address; author owner attributes remain tied to their actual eligible element. The model computes visibility and container-name with explicit source `revert`, full origin/layer rollback intervals and source-backed UA unset terminals.

`CssOriginEvaluation.observe` retains the actual per-origin runs, owner acquisition, mixed rules, metadata and direct trace. The proof companions connect every selected, removed and retained candidate to supplied root/catalog bytes or the actual owner attribute, while defaulting uses each ancestor's own trace. `CssOriginCompiledEmbedding.compute` preserves every old successful author-only computation, deriving the required admitted-sheet catalog transport.

The finite privileged browser runner is `origin_cascade_browser_check.py`. It installs actual HTTP user/agent sheets into rendered documents, reads installation origin and recursive CSSOM, checks every modeled node for unmodeled built-in contributions to the two properties or `all`, checks unmodeled layer inventories, and verifies removal restores the baseline. It does not model the browser's complete UA stylesheet inventory.

Research execution currently records 138/141 computed agreements and all 21 protocol controls. The two inherited false-support import failures and the new important user-layer-order failure remain explicit disagreements. Eight reduced origin-layer cases distinguish passing normal user order and author important reversal from failing installed user/agent important reversal. Final producer-bound evidence and committed archive acceptance are separate gates; no new full-package acceptance is claimed here.

## Static owner-derived implicit scope checkpoint

The owner-scope extension adds 61 modules, 270 audited laws and 61 executable
checks. `CssOwnerScopeHostEvaluation` derives author sources from actual static
HTML style owners and their child text; omitted scope roots use the owner parent.
Every reached nested assignment must contain that parent, otherwise the whole
public result is unavailable, including empty blocks. The disputed above-outer
configuration is not assigned a conformance expectation.

`CssOwnerScopeHostProvenance` and `CssOwnerScopePublicFailure` retain actual owner,
source, assignment, candidate/trace and unavailable-header evidence. The explicit
rule image preserves candidate lists and both property computations; there is no
blanket old parser/acquisition compatibility claim. No imports, shadow/adopted
ownership or non-element root fallback are added. Actual enabled stylesheet/CSP
and complete owner inventory remain host admission premises.

The separate finite browser suite contains 20 scenarios/20 visibility comparisons,
240 metadata records and 15 exact phase or admitted-computation controls.
Use the command and gate requirements in [ARTIFACT.md](ARTIFACT.md); the complete
[contract](research/owner-scope-contract.md) records scope and interpretation limits.
Research snapshots and prior native results remain separate from acceptance.

## Ordinary imports composed with raw scopes

The `ordinary-import-source-scope` coverage entry connects ordinary import graphs to raw scope roots/limits and static inline owner acquisition. `CssScopeImportHostEvaluation` is the public owner-derived source-to-computed facade. Repeated imports retain exact instance/source identity, imported children stay ownerless, and each origin registers its complete shared hierarchy before per-subject assignment and cascade evaluation.

The bounded profile rejects omitted scopes in reached imported or ownerless source, scoped-import modifiers and nested imports. Inline omitted roots keep the accepted all-reached-outer compatibility check. Compatibility preserves successful source parsing under `NoImportTokens`; it does not assert whole-host old/new computation equality. See [the contract](research/import-scope-contract.md) and `coverage.json` for assumptions and exclusions.

Run `python3 import_scope_browser_check.py --firefox /path/to/firefox --binary-kind local-build --lake /path/to/lake` after `check.py`. The generated 20-scenario corpus has 20 visibility comparisons, 240 metadata observations and 15 admission/computation controls. The runner distinguishes protocol acceptance from model agreement and binds actual owner text, imported CSSOM relationships, HTTP responses, URL bases and browser binaries to the proof producer. Actual gate status belongs to the producer and independent review records; historical native evidence remains unchanged.

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

## Supplied-factor unit conversion

`UnitConversion` relates an executable rational conversion to the independent
`Preserves` relation: target representation and current user-space meaning must
agree. It proves soundness/completeness, uniqueness for a nonzero target factor,
round trips and sufficient source-plus-target factor agreement.
`SvgLengthConversionExamples` retains the five reviewed percentage witnesses,
including the stale-destination counterexample and same-unit identity.

SVG2 `SVGLength.convertToSpecifiedUnits` supplies the motivating value and unit
conversion steps. CSS Values relative-length contexts motivate the supplied
factors; this module does not acquire them. Freshness, coherent context and
IEEE/native correspondence remain external obligations. It complements
`ProviderObservation` sequencing and `CssUnitFactor` lookup without proving
that a browser flush satisfies either. Fourteen previously reviewed theorems
are audited once, with five executable witness checks; see coverage.json.

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

## Conditional counter descriptor representation support

`ImplementationSupport.CounterRangeRepresentation` separates inline, boxed-resolved
and unresolved integers from semantic finite/infinite endpoints. Its eight existing
results connect independent finite-bound validation and ordering to total, inclusive
resolved export. An infinite peer never licenses skipping finite-bound validation;
a successful short-circuited lookup does not establish the publication invariant.
`ImplementationSupport.AdditiveOrdering` imports that representation once and adds
three existing laws connecting a supplied resolved finite list to strict adjacent
ordering and representation-independent results. CSS admission requires a nonempty
list and nonnegative weights; the mathematical empty-list convention is not admission.
The negative example shows why supplied raw negative values cannot replace correct
nonnegative resolution. Parser/export must use the same resolution policy.

These modules are conditional implementation support, not new normative CSS feature
coverage. The independent reference functions `member`, `ordered` and `descending`
reflect CSS Counter Styles Level 3 range and additive-symbols rules (retained primary
sources reviewed 2026-10-24). `admitted` is an implementation publication invariant;
it does not prove that every contextual expression is normatively invalid. `inlineGet`,
`oldAdmitted` and `inlineGreater` are explicitly historical accessor/countermodels,
not CSS definitions. No machine rounding, saturation, expression evaluator, specified
serialization, native parse/FFI/lifetime correspondence or browser refinement is proved.
Stable supplied resolution and preservation by every publication/mutation route remain
external. Range-list union, fallback and additive symbol generation are outside scope.

Eleven previously reviewed results are registered once: eight range declarations plus
three ordering results; the eight imported declarations receive no duplicate credit.
Twenty-two anonymous proof examples and eight executable controls (two expected false)
are retained. `coverage.json` remains unchanged; no overall CSS coverage percentage or
new research theorem credit is claimed.

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


### Conditional Round special-value knowledge support

`ImplementationSupport.RoundSpecialKnowledge` transfers four existing class-level results and four original examples from the reviewed standalone audit (2026-10-24). Eight registered controls include four expected-false claims. These are implementation-support obligations, not additional normative coverage or new research theorem credit. The seven-class abstraction deliberately forgets finite magnitude; `special = none` leaves finite-finite behavior outside this partial classifier. The local strategy type is not silently identified with `CssFiniteRound.Strategy`.

NaN priority and infinite-value retention characterize the supplied classifier. The two no-constant laws exhibit incompatible possible class outcomes; applicability to an unresolved AST requires a separate reachability premise. There is no proved scalar-to-class bridge, IEEE or native/compiler refinement, contextual unit/provider model, integer admission proof, or complete Round semantics. Existing finite-Round coverage exclusions remain unchanged. Primary context: CSS Values 4 `#round-infinities` and `#simplify-a-calculation-tree`, retained audit read 2026-10-24; this integration does not re-fetch or expand those claims.

### Installed counter descriptor correspondence

Accepted counter repairs 123/124 retain the eleven existing descriptor support proofs unchanged. The archived installed plan `css-counter-additive-install-plan-v1` (FILES `93dba57650187be68db6f0a6fb4ae691e371351e54b97f42a98a6451b897aff8`) and runtime `css-counter-additive-install-runtime-v1` (FILES `dfe49f900d2ba34410520beabc165b0cb40639ca06fcc19ebe8dab1316b51bb5`) agree on `counter_style/mod.rs` SHA256 `80afcf21539c512338670bc76ff61d8748ed718cf8419e11a0fc0b19a8cedb01` and `geckolib/glue.rs` SHA256 `0ac3857da5b7a4536cc62366c14e4a12824f73339f2b87b41c6581162da332fa`. These versioned archive pins supplement historical mappings; they are not live-epoch guards.

Every finite range bound is resolved before publication, then finite ordering and inclusive export use resolved values. Additive ordering and export share `AdditiveTuple::resolve_weight`; supplied `Meaning` values must be its post-zero-clamp results. Nonempty admission, numeric normalization and native correspondence remain external premises. Preserve inline-only countermodels as historical negative examples. The separate clamp-equivalence SMT evidence is not Lean theorem credit.

### Finite ModRem implementation support

`ImplementationSupport.FiniteModRemWitness` and `FiniteModRemContract` transfer the reviewed standalone finite arithmetic results. They reuse `Binary32Magnitude` and `RoundRemainderCapacity`; `FiniteModRemTypes` preserves only the four shared operation/value/backend types from the historical exceptional-dispatch model. The exceptional-dispatch theorems are not duplicated. Twenty-eight existing declarations are audited, including spacing/support lemmas, interface consequences and the existing capacity application; this transfer adds zero research theorem credit and no normative CSS coverage. Fourteen original proof examples remain. Twenty-four executable checks include eleven expected-false controls.

The witness derives loss of the exact remainder in the old quotient/product reconstruction under explicit nearest-rounding contracts and native/spec correspondence. The replacement contract proves signed truncating remainder adjustment, operation-specific zero signs and nearest projection into a closed divisor interval. A proved nearest endpoint certificate shows why a rounded result equal to the divisor must be permitted. Projection allows ties; it does not identify a universal native tie-to-even implementation. Rust `%`, native addition rounding, operand/sign encoding and compiler/hardware correspondence remain external premises. Neither module asserts mandatory infinite-precision CSS intermediates or complete native backend refinement.

Versioned source correspondence is accepted fix 128's tested two-path patch, SHA256 `a0330954c31ead2d800eddbf4340f25ce887ee83d76e86811ca888a6f5e4e987`, from `css-finite-mod-rem-acceptance-v1`. It changes `ModRemOp::apply` in generic calc and its own WPT. This is an archive mapping, not a live source/installation guard. The browser evidence and source review remain separate from the mathematical model. The capacity wrapper, inherited types, signed-zero representation and imported decoder receive no new theorem credit.


### Animation context and endpoint implementation support

Four support modules transfer the reviewed exact-rational common-context, finite-DAG cache/schedule and typed endpoint-history obligations. Canonical VariableExpr.substitute_congr and VariableProperty.compute/defaulting are reused rather than duplicated. Numeric initial/default metadata is distinct from missing var fallback: present empty and multi-token wrong types do not use that fallback. The single-token research fragment correspondence is separately proved in css-keyframe-token-list-adapter-v1.

Ranks, complete dependencies, winning operations, current provider context, registration profile and coherent sample remain supplied; no CSS-cycle/SCC, native arithmetic, scheduler, taint/URL, parser or whole-animation refinement is claimed. All are ImplementationSupport; normative coverage is unchanged. Copying proofs adds zero research theorem credit. Source mappings and deduplicated registrations are recorded in css-keyframe-animation-library-proposal-v1. Earlier negative-control reduction failures are distinguished from the newly decisive replay; actual canonical totals require a full check.

CommitStyles prefix refresh support (`ImplementationSupport.CommitRefresh`) transfers the already-reviewed covering-refresh theorem and its bridge to `KeyframeSchedule`. It preserves ordered per-property composition while refreshing every contributing effect against a supplied current provider context. Six audit declarations and nine executable cases (three deliberately false) are transferred research support, not new proof-discovery or normative coverage. Native context freshness, complete prefix selection, endpoint semantics, scheduling delivery and source refinement remain assumptions.


Endpoint source indices (`ImplementationSupport.KeyframeEndpointIndices`) transfer the reviewed finite-block prefix/recovery and conditional machine-bound model. Empty input blocks retain slots, and skipped outputs do not shift source declaration indices. Fourteen existing audits (eight primary lemmas, three helpers and three refutations) and eight executable cases (three deliberately false) are implementation support only, with zero new proof-discovery credit or normative CSS coverage. Stable prioritized traversal, immutable declarations, successful bounded storage and source correspondence are premises; input-block count has a separate machine bound from declaration count. The archived descriptor-v2 mapping and transfer accounting are recorded in `css-keyframe-endpoint-index-library-proposal-v1`; allocator behavior, native publication/lifetime, provider correctness and CSS semantics are not proved.


Computed property-name support (`GuardedNames`, `GuardedNamesExamples`) preserves the old guarded solver through a full value/state embedding. Its name parser remains a supplied normalized-token adapter, with no raw CSS/native correspondence claim. The 25 transferred audits and 15 executable controls add no proof-discovery or numeric normative coverage credit. Full assumptions and exclusions are recorded in ARTIFACT.md; exact transfer/preimages are in `css-variables-computed-name-library-proposal-v2`. Existing fixed-name profile claims remain unchanged.


Steps origin/range support (`StepsOrigin`, `StepsOriginExamples`) transfers ten reviewed consumer laws without changing their proof bodies. Eleven original proof examples remain, with fourteen executable observations including three same-claim false controls. The normalized calculation origin is preserved separately from authored literals; resolved calculations clamp to the position minimum while unresolved values retain rejection. Existing numeric censoring, integer rounding and bounded finalization are reused. This is a transfer with zero new proof-discovery or normative-coverage credit, not a parser or native refinement. Native origin classification, context-free resolution, positive normalization, IEEE conversion and machine bounds remain external premises. See `research/steps-origin-range.md` for the exact mapping and excluded behavior. Proposed totals require the later full canonical checker; this artifact does not update live results.
