# CSS variable fallback cycles: versioned specification trace

**Question:** Does `--ok:20px; --a:var(--ok,var(--a)); width:var(--a,7px)` require 20px, and does ordinary Stylo cycle traversal already support that result?

**Scenario:** All declarations win on the same element. Custom properties are unregistered. There are no relevant inherited declarations, animations, attributes, environment variables, spread syntax or competing width constraints. `--missing` in the controls is absent. This is a computed-value question, not a keyframe endpoint or animation-composition question.

**Versions:** CSS Variables Level 1 Editor’s Draft dated 9 October 2026, CSS Values Level 5 Editor’s Draft dated 27 October 2026, and the immutable CSS Variables Level 1 Candidate Recommendation snapshot dated 16 June 2022. The primary HTML captures are hash-pinned in SOURCES.json. The live pages were also read on 27 October 2026. Editor’s Draft expectations are work in progress; they must not be attributed to the 2022 snapshot.

## Current draft chain

1. [Values 5 property replacement, step 1](https://drafts.csswg.org/css-values-5/#property-replacement) substitutes the value under a property-name context.
2. [Substitution, steps 1–2](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function) guards that context and processes the outer function. Nested arbitrary substitution functions are excluded from this pass; no early invocation applies because the scenario has no spread syntax.
3. [Variables 1 var replacement, step 2](https://drafts.csswg.org/css-variables-1/#replace-a-var-function) obtains `--ok`’s computed value, 20px. Step 4 evaluates the fallback only if that result is guaranteed-invalid. The self-reference is therefore not visited. Step 5 returns 20px.
4. Substitution’s final cyclic check succeeds. Property replacement validates the resulting tokens. The later `width` reference obtains `--a:20px`, so its own fallback is also unused.

The [Variables changelog](https://drafts.csswg.org/css-variables-1/#changes-20220616) explicitly records “Made var() short-circuiting.” and links [CSSWG issue 11500](https://github.com/w3c/csswg-drafts/issues/11500).

## Published 2022 snapshot

The [2022 cycle graph rule](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/#cycles) includes var references in fallback arguments. The example consequently has a self-edge on `--a`, which becomes guaranteed-invalid. The [2022 substitution algorithm, step 3](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/#substitute-a-var) then selects `width`’s 7px fallback. This does not contradict short-circuiting within the old substitution algorithm: its separate graph construction already invalidated `--a`.

## Taken cycles and rejected alternatives

Current [guarding](https://drafts.csswg.org/css-values-5/#guarded) marks every participant when an active context is re-entered. Substitution checks that marking again after nested functions return. A literal fallback inside a detected cycle cannot rescue a participating declaration. An outside consumer can still recover from an invalid cyclic provider.

| Route or control | Current ED width | 2022 CR width | Reason |
|---|---:|---:|---|
| Unused self fallback, question above | 20px | 7px | Primary succeeds; ED omits fallback edge. |
| `--a:var(--missing,var(--a))` | 7px | 7px | Taken fallback re-enters active `--a`. |
| `--a:var(--a,20px)` | 7px | 7px | Fallback cannot clear cyclic marking. |
| `--a:var(--b,20px); --b:var(--a,30px)` | 7px | 7px | Both properties participate. |
| `--ok:20px; --a:var(--ok,var(--b)); --b:var(--ok,var(--a))` | 20px | 7px | Both fallback edges are unused in ED. |
| `--a:var(--missing,20px)` | 20px | 20px | Ordinary acyclic recovery. |
| `--a:var(--b,20px); --b:var(--b)` | 20px | 20px | Only `--b` participates; `--a` recovers. |

Each row uses `width:var(--a,7px)`. These are manually derived expectations, not executed tests; CASES.json preserves the exact declarations and assumptions. Eagerly visiting every nested var would contradict the current substitution traversal and its function-controlled argument evaluation. Ignoring all fallback dependencies would fail the taken-cycle controls.

## Ordinary Stylo correspondence

The current upstream source fetched by `searchfox-cli --get-file servo/components/style/properties/cascade.rs` and the local branch snapshot both already implement conditional fallback traversal. The upstream fetch is byte-identical to the preceding v1 capture. The local body differs in attribute namespace and prioritary-context plumbing; its ordinary var logic has the same primary-first behavior. This is source evidence, not a browser result.

`visit_value_references` calls `visit_link` for the primary name before consulting its resolved value. A universal value with no references makes `primary_valid` true; a computed typed value does likewise. Only `!primary_valid` pushes the fallback’s reference set. For the question’s unregistered `--ok:20px`, `traverse` has no dependency to resolve, and the unused `var(--a)` is skipped. The source comment explicitly cites issue 11500.

`visit_link` records a direct self-reference or propagates the lowlink of an unresolved dependency. `traverse` removes an entire strongly connected component through `handle_loop` when it finds a self-reference or a multi-node cycle. `handle_loop` invokes `handle_invalid_at_computed_value_time` for custom properties. Noncyclic nodes proceed to `substitute_references_if_needed_and_apply`. Thus a skipped fallback does not create a spurious cycle, while a taken fallback still contributes edges; these paths support the seven predictions above.

This removes the simple example as a supported new-bug lead. It does not establish correctness for registered values, typed attributes, prioritary properties, pending animation winners, custom function contexts, arbitrary evaluation-order interactions or every substitution function. The animation prototype must preserve this behavior while defining its own cycle owner and incomplete-work semantics. Replacing the existing ordinary traversal with a lexical all-reference graph would regress the current draft behavior.

## Evidence boundary and next action

`webspec-index` is absent. No installation or bootstrap was performed under this artifact-only task. The trace uses direct primary algorithm text and exact HTML anchor checks, not an exhaustive reference-graph enumeration. The installed Searchfox CLI lacks `--permalink` and `--spec-refs`; source is identified by function name and captured hash, without inventing a revision permalink. Initial sandbox DNS failures and the successful source-fetch retry are retained in SOURCE-CHECK.json. The tool should be updated before relying on the newer flags.

No browser, compiler, build, native edit, canonical library edit, ledger update, staging or commit occurred. A later browser control run can verify these seven ordinary cases before extending animation completion; failure would justify investigation. This trace contributes no new fix or formal coverage count.

**Verdict: REACHED** — the captured current drafts require 20px for the question’s unused-self-fallback case, while the 2022 snapshot requires 7px; ordinary Stylo source already supports the current-draft behavior.
