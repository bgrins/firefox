# Writing-mode cycle policy review

The 16 measured axis failures establish missing scheduling for acyclic registered logical units. They do not justify the proposed unconditional `LhUnits -> WritingMode` SCC edge. That edge has a concrete false-cycle witness even when no logical unit occurs in the custom property. Keep the sealed experimental repair unactivated.

This is a manual trace of official drafts fetched on 2026-10-27, using the spec-trace workflow. `webspec-index` is unavailable in this environment; the HTML anchors were checked directly. No exhaustive machine route enumeration, browser experiment, native compilation, or proof of Rust behavior is claimed. The source witness below is an inspection prediction to test, not a newly accepted bug.

## Fixed line-height counterexample

```css
@property --n { syntax: "<length>"; inherits: false; initial-value: 17px; }
.parent { writing-mode: vertical-rl; }
.target { font-size: 16px; line-height: 40px; --n: 1lh; writing-mode: var(--n); }
```

1. [API computed-value calculation](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values) admits `1lh` as a length and computes it according to that type.
2. [Values 4 `lh`](https://drafts.csswg.org/css-values-4/#lh) uses the element's computed line-height. The special parent-metric rule applies when the unit itself is used in line-height or a font-affecting property, not when it occurs in this registered property. Here line-height is the independent absolute value 40px.
3. The [API additional graph rules](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles) add `--n -> font-size` and `--n -> line-height`. Both targets have independent absolute values. No value in either property needs writing-mode.
4. [Registered substitution](https://drafts.css-houdini.org/css-properties-values-api-1/#substitution) supplies the computed 40px to `var(--n)`. [Values 5 property replacement](https://drafts.csswg.org/css-values-5/#property-replacement) substitutes before parsing the consuming grammar. Its step 3 says: “Parse result according to prop’s grammar.” A length cannot satisfy [writing-mode's keyword grammar](https://drafts.csswg.org/css-writing-modes-4/#propdef-writing-mode).
5. [Invalid substitution](https://drafts.csswg.org/css-values-5/#invalid-at-computed-value-time) therefore defaults the inherited writing-mode property to its parent's vertical-rl value. It does not invalidate the successfully computed provider merely because the consumer rejects its type.

**Verdict: REACHED** — `--n:40px` and inherited `writing-mode:vertical-rl` are the specified acyclic result for this fixed-value scenario. Rejecting the longhand before substitution would be the wrong explanation; the provider can be computed independently first.

The captured experimental `traverse` adds `LhUnits -> WritingMode` unconditionally. Its `maybe_note_non_custom_dependency` records `WritingMode -> --n`, while `--n:1lh` already contributes `--n -> LhUnits`. These create a new SCC despite fixed line-height having no writing-mode dependency. The prepared-value refinement only examines an existing WRITING_MODE bit on a custom property's own value; `1lh` has no such bit, so it cannot remove this spurious path. The finite adjacency check in CHECK.json demonstrates that topology, not native execution.

A useful extended diagnostic replaces the invalid consumer with `writing-mode:if(style(--n:40px):vertical-rl;else:horizontal-tb)`. Both branches are valid keywords and the tested provider is still independent of writing-mode. This requires actual if()/style() support and a separate implementation trace; it is not needed to establish the simpler counterexample and is not an executed conformance test.

## A genuine logical-unit back edge

Change `--n` to `100vi` in the same non-square viewport, retaining `writing-mode:var(--n)`. The length now really needs the target's writing-mode. The consuming grammar still rejects the eventual length, but property replacement fetches the provider before grammar rejection. Hence pre-validating the longhand or declaring this a nonexistent evaluation dependency is unjustified.

The API's published extra relative-unit graph edges enumerate font and line-height dependencies; they do not specify a writing-mode edge. Current Values 5 guards repeated substitution contexts, but the captured Values 4 unit-resolution text does not say that computing vi/vb enters a writing-mode property guard. Merely computing the registered provider can occur after that provider's substitution guard has returned. The published algorithms therefore do not complete the route from the unit read to cyclic invalidation of the custom property.

[Values 4 viewport units](https://drafts.csswg.org/css-values-4/#viewport-relative-lengths) use initial writing-mode when there is no element or it has not yet been styled, with media queries as the example. This is not an explicit rule for a cycle during computation of a styled element. Treating any temporarily unavailable builder field as that exception would also excuse the 16 already observed ordinary acyclic failures. Inherited axes are separately justified by invalid/defaulted writing-mode, not by a generic unit-cycle exception.

**Verdict: INCONCLUSIVE** — the latest published unit/context rules do not settle whether this genuine recursive read defaults the registered property, defaults the longhand first, or uses a special axis fallback. Do not turn the initial-value media-query exception into an invented cycle rule, and do not assume ordinary Tarjan invalidation is specified.

## Valid writing-mode results can nevertheless depend on units

Without value-dependent branching or a similar conversion facility, substituting a registered computed length/number into writing-mode cannot produce one of its keywords. A plain ready keyword provider has no logical length to resolve; an unused fallback containing one is excluded by selected substitution. Typed attr() that actually returns a length still fails writing-mode's grammar. Merely mentioning attr() is not a demonstrated keyword-producing cycle.

A genuine valid-grammar construction is the primary example in [CSSWG issue 13189](https://github.com/w3c/csswg-drafts/issues/13189): writing-mode chooses a valid keyword by testing an em value, while font-size uses vi. Both branches are valid, and the contextual reads are reciprocal. The 2026-03-27 [editor response](https://github.com/w3c/csswg-drafts/issues/13189#issuecomment-4145213087) agrees that property-dependent units should guard their dependency. The fetched API reports the issue **open**, with `Closed Accepted as Obvious Bugfix` and `Needs Edits` labels; the label alone must not be reported as issue closure or landed normative text. This example establishes a real policy problem, not approval for unconditional edges on values that do not read the property.

The current [if() rules](https://drafts.csswg.org/css-values-5/#if-notation) also distinguish a style query that would introduce a cyclic context (false condition) from blanket invalidation of every syntactically referenced branch. The precise new unit-guard integration remains the missing edit.

**Verdict: INCONCLUSIVE** — a valid-keyword dependency cycle is constructible and acknowledged, but its complete normative handling is still pending the unit-guard integration. This does not authorize assigning a conformance oracle to the genuine vi cycle above.

## Required implementation direction

Remove the unconditional LineHeight-to-WritingMode SCC edge from any proposed landable repair. That is necessary but not sufficient: actual line-height values using vi/cqi or orientation-dependent normal font metrics still need the correct computation prerequisite. Distinguish a scheduling barrier from a dependency that participates in cyclic invalidation; derive new SCC edges from actual admitted/selected reads, and keep fixed absolute line-height out of that edge set.

Before activating any writing-mode repair, run the existing 16 acyclic controls, the sealed four unused-fallback/invalid-admission controls, and the fixed-40px-lh witness (including declaration/query-order permutations). Treat the genuine vi and if() cycles as observations until the missing spec integration is resolved. Preserve the entire earlier syntax scope; do not fix the issue by excluding troublesome registrations.

[Issue 9517](https://github.com/w3c/csswg-drafts/issues/9517) remains open: its discussion explicitly recognizes numeric registered math and proposes replacing the older dependency mapping. [Issue 8169](https://github.com/w3c/csswg-drafts/issues/8169) is the earlier mixed-unit math dependency discussion. These are related scheduling policy work, not separate newly counted bugs.
