# Four registered-length expectations after variable selection and rollback

**Verdict: REACHED for the four computed-value expectations below**, under the fixture's successful registration and supported-keyword preconditions. This is a manual chain through current primary specification text, not an exhaustive machine-generated trace or native implementation proof. These are four witnesses of the same suspected losing-declaration dependency problem, not four established distinct bugs.

Research date: 2026-10-30. The inputs are the sealed preservation fixture and its sealed Zoom capture replacement. Authentication checks all three referenced package closures; the replacement adds only a recorder script and a diagnostic-only call. The four case bodies and assertions are unchanged. No live runtime, source, app, index, or process state was read.

The fresh iframe registers `--actual` as `<length>`, non-inherited, with initial `0px`, then declares `--actual: 2em`. Each phase replaces the stylesheet. Parent font sizes are 11px and 17px; explicit target sizes are 20px and 30px. There are no declarations or registrations for `--missing`, no animations or transitions, and no user/UA font-size override on the ordinary target div is assumed. Literal reference and keyword-support checks remain required setup evidence.

| Exact callback suffix after `Prioritary selection preservation: ` | Effective font-size, phases 0/1 | Registered --actual, phases 0/1 | Verdict |
|---|---|---|---|
| winning-variable | 20px / 30px | 40px / 60px | REACHED |
| fallback-revert | 11px / 17px | 22px / 34px | REACHED |
| fallback-revert-layer | 20px / 30px | 40px / 60px | REACHED |
| fallback-revert-rule | 20px / 30px | 40px / 60px | REACHED |

1. [Cascade sorting](https://drafts.csswg.org/css-cascade-5/#cascade-sort) selects the last equal-specificity declaration within each normal layer. Its deciding rule is: “The last declaration in document order wins.” The winning-variable case therefore selects `font-size: var(--size)`, not the preceding `var(--actual)`. For the layer case, upper wins initially.
2. [Property replacement, step 1](https://drafts.csswg.org/css-values-5/#property-replacement) substitutes the selected property's value using its property-name context. [Replacing var(), steps 2, 4, 5](https://drafts.csswg.org/css-variables-1/#using-variables) looks up the named custom property and uses the fallback when that value is guaranteed-invalid. `--size` supplies the valid absolute length; missing `--missing` selects the authored rollback token. None of these selected inputs reads `--actual`.
3. [Resolving in properties](https://drafts.csswg.org/css-values-5/#resolve-property) says a sole substituted CSS-wide keyword is treated as specified “all along.” Thus these are actual rollback operations, not failed grammar parsing followed by generic unset behavior. The relevant rule is normative prose immediately before the numbered property-replacement algorithm.
4. [revert](https://drafts.csswg.org/css-cascade-5/#valdef-all-revert) removes the target's author-origin font-size declarations, leaving inherited parent size. [Font size is inherited and computes to an absolute length](https://drafts.csswg.org/css-fonts-4/#font-size-prop). [revert-layer](https://drafts.csswg.org/css-cascade-5/#valdef-all-revert-layer) removes the upper layer's font-size declarations, selecting lower's literal. [revert-rule](https://drafts.csswg.org/css-cascade-5/#valdef-all-revert-rule) removes only the last rule, selecting the immediately preceding literal. The earlier self-reference remains lower priority and is not selected.
5. [Registered computed values](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values) convert the valid length to its canonical unit. [Relative-unit dependency rules](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles) add the current element's font-size dependency for this registered em length. [The em definition](https://drafts.csswg.org/css-values-4/#em) supplies that computed size. Doubling the selected sizes gives the table.

| Alternative route | Why it does not decide these four cases |
|---|---|
| Substitute the lower `font-size: var(--actual)` | It is overridden or removed by the applicable rollback operation. It is not the selected computation input. |
| All fallback results are IACVT | These fallbacks are supported CSS-wide keywords, whose explicit defaulting behavior applies. |
| Default --actual to 0px because it contains em | An outgoing font-size dependency alone is not a cycle. The selected font-size computation has no return reference to --actual. The separate active-cycle control does have that return reference and must remain covered. |
| Ignore all evaluated rollback dependencies | Not justified: the selected `var(--missing, keyword)` still must be evaluated. Only the irrelevant lower declaration is excluded here. |

The current Values 5 substitution algorithm returns the selected token sequence when its guarded context is not cyclic; its cycle rule concerns re-entering a matching guarded context. This trace does not specify a Tarjan graph representation. The Properties API's remaining graph terminology and the newer substitution-context formulation are used only for this simple acyclic selection, not claimed equivalent in general.

The four callbacks are justified repair targets for the planned candidate comparison, alongside preserving original PASS callbacks and the genuine-cycle control. The source cause remains an inference until separately demonstrated; the root's provisional lane summary is not imported as a frozen observation receipt here. No whole-suite, candidate, restoration, acceptance, or commit result follows from this trace.

**INCONCLUSIVE / outside this endpoint trace:** a separate claim about exact native scheduling at the first getter, general rollback-cycle equivalence, or all future cascade inputs. The fixture's first getter plus three frame samples must remain separate evidence; later correct values cannot retroactively establish the first value.

Current primary snapshots were read via the web tool: Cascade 5 (13 April 2026), Variables 1 (9 October 2026), Values 5 (27 October 2026), Properties API editor draft (6 August 2026), and Fonts 4 (22 October 2026). Cascade 6 is a diff specification and does not contain the rollback section; Cascade 5 is the applicable source. These are editor-draft expectations, particularly revert-rule, not a claim of existing cross-browser support.

`PRIMARY-*.txt` retains the current web-tool excerpts. Prior successful indexed captures are pinned in `REFERENCES.json`. All new index queries, eleven `exists` checks, and the trace attempt failed with the read-only database error; their receipts are retained. The direct HTTP capture attempt also failed DNS resolution. No successful new index/anchor enumeration is claimed. The primary pages' linked definitions and section text were inspected manually; this manual positive argument does not rely on absence-search results.
