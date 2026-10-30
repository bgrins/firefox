# Overridden font-size declaration and registered em value

**Question:** Should the registered `--actual` below compute to 40px, despite the losing variable declaration?

**Scenario:** A non-root element has a successful `<length>` registration for `--actual`, initial value `0px`, and `inherits: false`. Separate matching rules declare `--actual: 2em`, `font-size: var(--actual)`, and `font-size: 20px !important`. There are no transitions, animations, other winning declarations, or rollback keywords. The second phase changes the important size to 30px.

1. [Cascade sorting](https://drafts.csswg.org/css-cascade-5/#cascade-sort) places the important author declaration ahead of the normal one. [Cascaded values](https://drafts.csswg.org/css-cascade-5/#cascaded), [specified values](https://drafts.csswg.org/css-cascade-5/#specified), and [computed values](https://drafts.csswg.org/css-cascade-5/#computed) carry that winning literal into computation. These are prose value-processing rules, not numbered algorithm calls.
2. [Resolving in Properties](https://drafts.csswg.org/css-values-5/#resolve-property) places substitution during computation. [Property replacement](https://drafts.csswg.org/css-values-5/#property-replacement) step 1 invokes substitution on the property's value. The selected font size contains no substitution function; the discarded declaration's `var()` is not part of that value.
3. [Substitute arbitrary substitution functions](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function) step 2 traverses functions in the passed value. For `20px` there are none; step 4 is:
   > Return values.
   The [cyclic-context definition](https://drafts.csswg.org/css-values-5/#cyclic-substitution-contexts) requires re-entering a matching guarded context. No variable read re-enters `--actual` through this selected font size.
4. [Registered computed values](https://www.w3.org/TR/css-properties-values-api-1/#calculation-of-computed-values) convert the valid length to its canonical unit. [Relative-unit dependency rules](https://www.w3.org/TR/css-properties-values-api-1/#dependency-cycles) require the current element's font size. The [em definition](https://drafts.csswg.org/css-values-4/#font-relative-lengths) supplies that reference. Thus 2em computes to 40px, then 60px after the literal font-size change.

**Verdict: REACHED** — the scenario specifies 40px then 60px. This is a composed argument from cascade prose and the substitution algorithm, not a machine-proved end-to-end spec trace.

| Candidate failure route | Why it is not taken in this scenario |
|---|---|
| Immediate cyclic return at substitution step 1 | The selected literal introduces no re-entrant property read. |
| Cyclic return at step 3 (two indexed routes) | Step 2 visits no substitution functions in the literal and cannot create the alleged backedge. |
| The losing var() reads --actual | It is absent from the selected property's computed-value input. |

`CASCADE-TRACE.md` records all three step-reference routes at depth nine, without truncation. Their existence does not prove their guards hold. The deciding loop/return is preserved in `SUBSTITUTE.md`; all cited indexed anchors passed `ANCHOR-CHECKS.json`.

## Evidence and limits

The frozen nine-case installed-browser fixture reports Firefox 4 PASS / 5 FAIL and Chrome 9 PASS / 0 FAIL. Its length witness gives 0px in both Firefox phases while the literal font sizes and reference controls are correct. Reports are in `../css-registered-overridden-color-scheme-firefox-runtime-1/` and `../css-registered-overridden-color-scheme-chrome-runtime-1/`. The five failing callbacks share a suspected source cause; they are not five established distinct bugs. The other four failing callbacks involve color-scheme and are not adjudicated by this length-only trace.

Queries ran on 2026-10-30. CSS Values 5's editor draft is dated 2026-10-27. The current Variables draft moved cycle handling into Values 5; unsuccessful guessed older anchors are retained as query failures, not evidence. The index accepts the published Properties and Values API URL but not its Houdini host; the current Houdini editor draft was separately checked with the web tool and retains the relative-unit rules used here. Files preserve individual specification content hashes. Source analysis supports an eager losing-declaration edge as the implementation explanation; the browser reports alone do not trace internal graph construction.

The repair must also support computed substitution yielding rollback and eligibility changes. This witness does not justify a literal-winner-only special case, nor prove the proposed Rust repair.
