# Registered unused-fallback unit dependency audit

Status: **research lead; not an accepted bug or native proof**. The installed Firefox probe exhibits an unused-fallback effect, but no browser built from this branch was tested. The requested length case has a specification integration ambiguity. A non-length control also fails and deserves separate investigation after the active build finishes.

## Observation

Fresh-profile installed Firefox reports version 158.0. With a parent font size of 19px, these declarations produce `font-size:19px` and computed `--x:3px`:

```css
@property --x { syntax: "<length>"; inherits: false; initial-value: 3px; }
--known: 5px;
--x: var(--known, 1em);
font-size: var(--x);
```

Direct `--x:5px`, a valid primary without fallback, and a valid primary with `1px` fallback each produce 5px. The missing-primary `1em` fallback and direct `1em` controls produce the genuine-cycle result of 19px / 3px. An inherited valid provider still produces 19px / 3px with the unused `1em` fallback. A universal registration produces 5px, and an inherited already-computed registered length behaves normally. Moving the unused fallback into an unregistered provider also produces 5px.

The unexpected non-length control is more specific:

```css
@property --n { syntax: "<number>"; inherits: false; initial-value: 3; }
--known: 5;
--n: var(--known, 1em);
font-size: calc(var(--n) * 1px);
```

This produces 19px / computed `--n:3`, whereas the prepared hypothesis expected 5px. The runner therefore **exited 1 at its calibration assertion**. All eleven rows were delivered, repeat reads agreed, source and binary pins stayed stable, and the owned browser/profile were cleaned up. This is not an all-pass probe. The copied runner's assertion text says “Attribute calibration”; that text is only a harness label. `SUMMARY.json` identifies the actual failed row as `number-unused-em`.

## Manual normative trace and version boundary

The captured Properties and Values API Level 1 ED is dated 6 August 2026. Registered values initially accept generic custom-property syntax. Typed computation and serialization occur before their value is substituted into a consumer. Its extra unit-cycle edges are explicitly limited to registrations containing length or length-percentage syntax. See [parse-time behavior](https://drafts.css-houdini.org/css-properties-values-api-1/#parsing-custom-properties), [computed values](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values), and [unit dependency cycles](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles).

The Variables Level 1 ED dated 9 October 2026 first gets the primary property's computed value; replacement step 4 evaluates a fallback only if the primary result is guaranteed-invalid. Thus a valid `--known` does not invoke its fallback through this algorithm. [Replace a var()](https://drafts.csswg.org/css-variables-1/#replace-a-var-function).

The Values Level 5 ED dated 27 October 2026 delegates substitution-function arguments to their individual replacement algorithm. Guarded property computation supplies cycle detection. This establishes the reached-call-chain argument for excluding unused fallback evaluation; it does not itself rewrite the older unit-edge clause. [Generic substitution](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function), [property replacement](https://drafts.csswg.org/css-values-5/#property-replacement), [guarded evaluation](https://drafts.csswg.org/css-values-5/#guarded), and [cyclic contexts](https://drafts.csswg.org/css-values-5/#cyclic-substitution-contexts).

**Requested length-case verdict: INCONCLUSIVE as a normative violation.** The registration specification still describes an extra edge when a property contains a relative unit, without spelling out whether this scan happens before or after substitution. Reading that clause as a raw-token scan permits the observed length case; reading it as a dependency on computed evaluation yields 5px. The more recent short-circuit algorithm is strong motivation for clarification, but is not enough to silently discard the explicit extra graph rule.

**Number control: stronger candidate, still unaccepted.** The registration clause's length-syntax precondition does not apply to `<number>`. With valid numeric primary substitution, there is no reached font-relative conversion. Its unexpected reset is therefore not explained by that extra edge rule. A branch/browser reproduction and focused number controls are still needed before acceptance; this audit does not claim to have completed them.

The immutable [16 June 2022 Variables CR](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/#cycles) used a different graph rule that included fallback custom-property references. Do not conflate that obsolete fallback-reference rule with either the current short-circuit algorithm or the still-present relative-unit registration clause. Prior artifact `css-variables-fallback-cycle-version-trace-v2` records the ordinary var-cycle version split in detail.

`webspec-index` was unavailable, so this is a manual primary-source trace with checked anchor IDs, not an exhaustive machine-indexed caller analysis.

## Exact implementation evidence

`SOURCE-PINS.json` identifies HEAD and the separate local snapshots. Upstream files were fetched using Searchfox CLI `--get-file`; that command serves GitHub main bodies, so captures are content-pinned snapshots, not invented revision permalinks.

In all captured HEAD/local/upstream versions, `References.flags` contains fallback flags via `references.flags |= fb.references.flags`. `find_non_custom_references` initially filters unit references by the registration's dependent data types. Ordinary SCC traversal then initializes its non-custom reference accumulator from that result and calls `visit_value_references`. The visitor unconditionally ORs each visited `refs.flags` into the accumulator before deciding whether individual fallback expressions are used. Later, any non-universal registration traverses those accumulated non-custom edges. This bypasses the initial length-type filter as well as retaining unused nested unit flags. It is a concrete explanation candidate for the non-length observation.

The active local prototype adds pending-demand and resolved-token dependency support. Its `resolved_token_dependencies` helper classifies emitted token text; it does not remove the raw root flags already accumulated by this ordinary SCC path. No native source was edited for this audit. Static correspondence is not a branch runtime result, and no Lean theorem verifies these concrete Rust paths.

## Existing work and limits

A narrow duplicate-ledger review found registered initial-value, inherited invalid-value, substituted inherit restyle, token-boundary, keyframe substitution, and font-priority fixes; no clearly identical unused-unit-fallback item was identified. This is not proof of absence. The upstream `unit-cycles.html` covers real unit cycles and inherited computed lengths. `registered-property-dependency-through-fallback.html` covers a used fallback to a registered color. Neither captured file establishes this unused unit oracle.

The run uses no WPT environment, no shared objdir, no Mach command, and no existing profile. There is no security claim, no new accepted bug, no coverage-count change, and no canonical library or ledger edit. The next bounded step is to reproduce the `<number>` row on the completed local browser and add direct-number / no-fallback / px-fallback controls, while treating the length case as a separate specification question.
