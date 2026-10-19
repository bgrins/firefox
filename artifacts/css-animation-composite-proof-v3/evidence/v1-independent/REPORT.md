# Independent review of the composite-only setter companion

## Verdict

**Corrections required before formal acceptance.** The native fix and separately reviewed browser evidence remain supported. This review found two model/bridge gaps and one replay-integrity defect in the frozen companion. These findings concern the verification artifact; none establishes an additional Firefox bug.

The reviewed producer is `css-animation-composite-proof-v1`, frozen under SHA-256 `3729e3ab586484e0e50b0ed6f361e8c08e7896f82afc3946cfd747d6d742054b`. Its input manifest is `cd83bbc3fd716ce25303e03077805d7b7998d5f463913a66b997efaedd0f2a67`, checker is `d01de82deae1f80229e3b71fbd6f4ecc6c83e0e28e059383fa67195d046d3685`, and report is `ca35be303f64d6e85e53b8c472dd0c3370866b65f94f80efa1a81d0711a9a8b7`. Those supplied pins and all 69 inputs authenticated before the independent replay. The producer was not edited.

I read the complete scope and addendum, Lean model and witnesses, oracle, corpus, mutation definitions, generator/extractor, checker, all three C++ adapters, the 29 extracted definitions, the listed provider definitions, and the existing native/WPT independent report. The analysis below preserves the approved scope rather than accepting a weaker claim because current checks pass.

## Required correction 1: executable import closure

The checker verifies each listed file but then adds its source directory to `sys.path`. Python prefers an importable package over a same-name module. A new, unlisted `generate/__init__.py` therefore runs instead of the authenticated `generate.py`.

The safe independent probe used unchanged `INPUTS.json` and unchanged `check.py`, added a package that prints `UNAUTHENTICATED_PACKAGE_EXECUTED` and exits 73, and invoked the checker with `python3 -I -S`. All original hashes passed; the unlisted code executed before the output directory was created. A control modifying the listed `generate.py` instead correctly failed its hash check. `TAMPER-v1.json` and the retained probe logs record both results. Thus isolated Python invocation alone does not fix this particular post-authentication path insertion.

This does not invalidate the fresh source-only run below: its capsule contained only the 69 authenticated inputs and manifest when started. It does invalidate the standalone checker's assurance that the modules it executes necessarily came from the authenticated dependency list.

A corrected version must enforce exact executable dependency closure before project imports. A suitable approach is to validate normalized, unique, contained regular-file manifest paths, reject symlinks and escaping paths, copy only authenticated inputs into a fresh exact-inventory capsule, and execute under isolated/no-site Python with bytecode caching disabled. Alternatively, load every project helper explicitly from authenticated source bytes and prevent sibling packages or bytecode from replacing those helpers. Do not describe an unverified existing directory as source-only. Retain tamper tests for listed changes, extra packages/modules, duplicate/escaping paths, and symlinks. The original frozen artifact must remain intact.

## Required correction 2: property and base cache coherence

The approved scope requires valid offsets **and property/base caches** when an equal-input setter skips work, or restoration by a real refresh path. In the current Lean model, `Valid s` means only `s.derived = derive s.environment s.frames`. `Represents` checks only the raw-to-specified frame projection. Neither predicate constrains `properties` or `base`.

Furthermore, `Action.context` takes an entire `Environment`. It can replace `styleVersion`, target/style availability and other provider inputs. `contextRefresh` rebuilds only when derived offsets change and target/style are available. An ordinary percentage keyframe keeps the same offset after a style-version change, so the action can leave the consumer caches stale while both existing invariants remain true.

`CACHE-COUNTEREXAMPLE.lean` supplies nine successful kernel theorems, with only the usual `propext`, `Classical.choice` and `Quot.sound` axioms:

1. Start from the producer's concrete empty state and successfully install an additive property frame.
2. Verify that its property and base caches both agree with independently supplied version-sensitive providers.
3. Deliver a context action that changes only `styleVersion` from 0 to 1.
4. Verify `Valid` and `Represents` still hold.
5. Submit identical specified frames and verify the optimized setter skips unchanged.
6. Verify its retained properties and base values both disagree with the current providers.
7. Deliver the existing style-refresh action and verify that it restores both caches.

This starts from coherent, reachable state; it is not merely an arbitrary invalid initial cache. The combined checked source and successful axiom log are retained. An initial development run needed explicit unfolding of the two proposition definitions for kernel decision; its failure log is retained separately and is not acceptance evidence.

The finite-sequence theorem itself is sound for its actual statement: optimized and direct setters agree under the offset and representation invariants, and the other actions share helper definitions. That theorem cannot establish the stronger cache obligation absent from those invariants. Prose freshness language is not a machine-checked substitute.

The correction must introduce an explicit consumer-cache relation and prove its preservation/restoration over the admitted finite sequence. Separate geometry/context inputs from style-provider versions, or encode the dispatch conditions needed when those inputs change. Context actions must not silently alter style or target/provider identity while bypassing the corresponding rebuild. Make provider extensionality/freshness premises about raw provider inputs and delivered calls, not assumptions that final caches already equal the expected answer. Keep style changes and context refreshes in scope. Prove nonvacuous fresh and stale-then-restored examples, including absent target/style paths and default changes. The real implementation's scheduler remains an external obligation, but the modeled delivered actions must enforce the stated contract.

The real native entry paths support the distinction: ordinary `GetKeyframes` refreshes named offsets only when an associated timeline exists; `MaybeUpdateKeyframeComputedOffsets` rebuilds only after changed range offsets; `SetComposite` follows target/style gates; and supplied-style actions invoke `UpdateProperties`. Do not invent an unconditional getter rebuild to make the proof pass. A missing timeline cannot silently satisfy the delivered-refresh premise for stale named offsets.

## Required correction 3: preserve null computed values

The retained real `Servo_GetComputedKeyframeValues` implementation handles a null `mServoDeclarationBlock` by appending `None` as the `AnimationValue`. That null endpoint is preserved through segment construction and participates in base-style eligibility; it is not replaced there by the numeric base value.

In contrast, `ProviderBaseStyleSet::GetComputedKeyframeValuesFor` in `adapter-middle.cpp` substitutes `style->base` for null declarations. The independent Python oracle repeats the same substitution. Lean's `Providers.computedValues` returns `(Nat × Rat)`, and `Entry.value` is a `Rat`, so an existing declaration with a null computed animation value cannot be represented there. Optional missing-endpoint segment values do not cover this case.

I compiled a separate diagnostic variant changing only that provider adaptation to leave `AnimationValue` null. Both variants executed the frozen five-action `null-provider` case successfully. Four observations differed: SET, GET, STYLE and GET. The first segment's `fromValue` is null in the real-provider-compatible variant, versus 10 initially and 30 after the style update in the frozen adapter. The style update also takes the base-only refresh path instead of treating the resolved endpoint value as a changed segment. Exact sources, compiler log, raw observations and summary are in `null-provider-diagnostic/`.

This is a concrete correspondence error, not a suggestion to broaden the artifact to all CSS values. Preserve the already admitted null-provider cases, make raw computed-value outputs optional, and propagate null through the independent oracle and typed model. Let the actual extracted `EnsureBaseStyle` and getter serialization consumers use the separately supplied base values. Do not feed them already resolved expected answers. Add controls demonstrating that an existing null endpoint and a synthesized missing endpoint retain their proper semantics. The ordinary parsed-WAAPI domain and CSS-generated synthetic declarations may be distinguished explicitly, but dropping current cases is not the correction requested by the approved scope.

## Additional witness correction

All twenty native mutations compiled and executed successfully, and all twenty corresponding Lean declarations passed kernel checking. Their intended semantic classes match. One witness should be tightened in the corrected version: `mutant_suppress_base_restyle` filters every restyle from accumulated event history, including a prior setter's restyle. The native mutation suppresses only the current base-update restyle. Reset the witness event log before the action, or compare the unchanged historical prefix plus the altered current suffix. The selected inputs do cause a current base change, but the current assertion is weaker than an exact model of that native mutant.

## Fresh replay and independent observations

The reviewer created a new capsule by copying only manifest-listed source inputs plus the input manifest. No historical executable or replay output was copied. The fresh replay compiled the original, candidate and twenty mutation variants and terminated successfully. The initial command had a mistyped external manifest digest and failed immediately; its log is retained. The corrected command is the successful `replay-v1` run.

| Check | Independent result |
| --- | --- |
| Authenticated producer inputs | 69 |
| Complete extracted definitions | 29 |
| Corpus cases | 662 |
| Action observations | 4,998 |
| SET / GET / CONTEXT | 1,573 / 2,069 / 360 |
| RESET / DEFAULT / STYLE / RUNNING | 662 / 213 / 25 / 96 |
| Candidate disagreements under declared numeric tolerance | 0 |
| Original disagreement rows | 1,458 |
| Lean theorem declarations | 60 |
| Successfully compiled and executed semantic mutants | 20 |
| Cost samples | 50 |
| Deterministic receipts matching the canonical run byte-for-byte | 94 |

Candidate observations are not all bit-identical to the rational oracle: 24 rows differ under strict structural/numeric equality and agree within the explicitly declared absolute/relative tolerance of `2e-14`. This is finite arithmetic evidence. Signed-zero flags are separately compared exactly. Unresolved derived NaNs use a distinct serialized null representation, not a finite specified percentage.

The independent checker rederives the extraction hashes with a separate comment/string-masking and brace-walk implementation. It verifies every generated definition equals the full authenticated source definition after removing only the declared entry log insertion. Original and candidate extractions differ solely in the production comparator. All listed provider-definition hashes also rederive. The patch does not use the unrelated DEBUG comparator as a preservation guarantee.

The checker independently parses all raw output rows, rechecks every mutant's successful semantic disagreement, and verifies omitted-composite observations exactly equal the original variant. The skip-recompute mutant deliberately runs only two rows to observe the wrong cache before a later assertion; it is a semantic mismatch, not a crash kill. It separately checks all 256 operation/environment matrix cases directly from raw getter observations. Deterministic replay receipt equality excludes cost timings and elapsed runtime; all cost checksums agree and the 50 samples remain bounded harness measurements.

## Full-scope source and model audit

### Specified state and ownership

The model keeps four specified operations distinct, with a separate three-operation resolved domain. Ordered offsets, easing tokens, declaration properties and immutable allocation ownership participate in projection equality; ignored derived offsets do not. The pointer shortcut is proved sound under the fixed allocation-to-content map. Native input handling rejects reuse of an allocation ID with different numeric contents. Distinct equal-content allocations are tested. Structural equality/serialization congruence of real Servo declarations and timing functions remains an admitted boundary; no universal CSS equivalence proof was found or claimed.

The recursive comparator equivalence, changed-assignment branch, getter retention and unchanged valid-offset retention proofs are meaningful and kernel checked. The arbitrary finite sequence proof proceeds by state induction and invariant preservation, not bounded enumeration. Its missing consumer-cache invariant is the specific defect described above; the theorem is not rejected merely because it is abstract.

### Entry paths and getter

Both complete ordinary `SetKeyframes` overloads are compiled. Processing failure returns before style acquisition and the array setter. This is atomic only at the admitted parsed-record/error boundary; JS iteration and reentrant callbacks are excluded explicitly. The complete ordinary `GetComputedKeyframes` returns false, and the complete `GetKeyframes` performs actual typed dictionary writes, composite/easing/offset output, range conversion, property naming, declaration/base serialization dispatch, JS conversion/definition and error returns. The typed adapter records writes rather than replacing the getter with a projection.

Five native property categories cover the IDL-name cases used here. CSS-specific style flushing and augmentation are retained in source but not executed through an ordinary-effect adapter. Typed OM is enabled in this corpus; the disabled-pref branch is retained, not exhaustively exercised. These are coverage limits, not claims that every Gecko getter branch has been tested.

### Offsets and segments

Complete ordinary offset distribution, range detection, named-range affine mapping and attachment normalization, NaN comparison and refresh functions are extracted. The independent oracle uses rational anchors and interpolation; the Lean model builds its own concrete derived offsets. Empty, singleton, missing and percentage cases, duplicate offsets, unresolved/zero-width ranges and resolved ranges establish nonvacuity. Native range geometry is an admitted affine provider, and not every named map is varied independently. Mixed named/missing behavior is identified as an implementation contract with specification gaps.

Complete segment construction, stable sorting, entry comparison, initial/final missing-segment helpers, endpoint composite resolution and segment/property equality execute. The independent oracle groups sorted offsets and properties and derives segments from raw computed values; it does not receive prebuilt expected segments. The Lean model uses stable insertion sorting and explicit groups. Native float narrowing is outside the rational universal theorem. Null values supplied by an existing declaration are the required correction above.

### Property rebuilding and other state

Complete `BuildProperties`, `UpdateProperties`, `EnsureBaseStyles` and `EnsureBaseStyle` execute. Clone/restore retains full specified frames, and outputs observe composite directly. Property equality excludes compositor flags; the update path preserves running property IDs, resets cumulative state, and logs effect publication, cascade dirtying, effect updates and restyle requests. Base change detection correctly checks entries in the new map rather than claiming symmetric map inequality. The separate provider services remain numeric/logging adapters, not effect-set or rendering implementations.

The model explicitly carries property segments, base values, running/cumulative identities, event history, default operation, environment and compute count. This is useful state coverage, but shared helper definitions and arbitrary base providers alone do not prove cache coherence. The native corpus fixes normalized delays at zero. Positive scroll-timeline delay eligibility is retained in the full extracted body and source trace, not exhaustively executed or proved as timing behavior. Custom-property names and property order need an explicit encoding into abstract property identity/order when describing the model bridge.

## Specification and browser evidence boundaries

The authenticated current specification snapshots support the observable claim: successful setKeyframes replaces the processed keyframes, processing errors preserve them, and getKeyframes exposes each frame's composite field. Operation resolution is distinct from specified getter retention. See the retained source text and the original sections [setKeyframes](https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-setkeyframes) and [getKeyframes](https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-getkeyframes). The model's internal no-op event counts are implementation contracts, not specified browser events. Web Animations Level 2 and CSS-generated paths do not expand the ordinary model into an all-animation or all-CSS theorem.

The existing independent native/WPT report pins final candidate C++ `e17ad778f6279f17eda31b764ea2d52edbe82de50aa44d69a1a995d4d51b75d8` and WPT `a140ac383d46dbfb9b922876e768c9e06069cdc82bd6a0a4e909c277fcbf241c`. It reports the paired 70 cases: original 52 failures and 18 passes, candidate 70 passes, plus 340 unchanged existing passes and seven OK harness results. This review read that report and the root receipt; it did not rerun a browser or reinterpret those counts as formal proof. The CSSOM case reaches the shared setter, but CSS-generated augmentation and override bookkeeping remain outside the universal ordinary-WAAPI theorem.

There is no verified translation from the extracted C++ to Lean, no proof that Python is equivalent to Lean, and no compiler/IEEE/layout/shaping/sampling/painting proof. The full Rust computed-value and sampling services are source-traced boundaries. Toolchain executable and SDK-settings pins do not make the complete compiler, SDK or Lean library installation hermetic.

## Reproduction and next gate

Use an externally supplied SHA-256 of this review's `MANIFEST.json`, verify this checker's own hash, then run:

```
python3 -I -S check.py --expected-manifest <review-manifest-sha>
```

The review checker authenticates an exact closed inventory before reading its evidence and imports no project modules. It rederives extraction integrity, raw disagreements, mutation results, the operation matrix, canonical receipt agreement and the three findings. `--full-output /private/tmp/fresh-animation-review` additionally creates an authenticated source-only capsule, reruns the complete producer compilation/Lean replay, and reruns the nine cache-counterexample theorems. It will still report `CORRECTIONS_REQUIRED`: a passing replay is not acceptance of the disproved scope obligations.

The next acceptance gate is a separate corrected producer version, preserving the complete approved scope, followed by a fresh source-only replay and independent review of all corrections and their interactions. Do not overwrite the frozen v1 evidence or remove difficult cases to obtain a passing summary.
