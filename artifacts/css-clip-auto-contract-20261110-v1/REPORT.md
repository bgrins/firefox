# Clip auto: contract and repair boundary

The CSS contract is reached: matching auto components should survive while numeric rectangle components combine. The shared native ClipRect guard currently rejects that combination. However, an Accumulate-only relaxation would also change SMIL. Preserve the existing SVG admission separately; no native patch is proposed as accepted here.

Read CSS-TRACE.md for the REACHED CSS chain and SVG-TRACE.md for the INCONCLUSIVE SVG host-integration question. These are separate questions with separate verdicts. Current CSS Masking, Web Animations1/2 and CSS Values snapshots were queried through webspec-index on10 November2026. Current SVG Animations ED9 November2026 and the normative SMIL source were fetched directly after indexed queries failed. Primary source receipts and anchor validation are retained. Tool notices reported webspec-index0.15 available versus installed0.14; no tool was updated.

## Native operation mapping

Sources are pinned at `4d1607b92c59814d3bd4e234fec8fb917dc3c735`; later parent commits do not alter the source identity of this audit.

| Caller | Native path | Consequence |
| --- | --- | --- |
| WAAPI iterationComposite | glue.rs accumulate_endpoint → AnimationValue.animate(Accumulate{count}) → ClipRect::animate | Matching auto currently returns Err; original endpoint is retained. |
| WAAPI composite:add | Endpoint value composition → AnimationValue Add → ClipRect::animate | Same shared auto guard; matching-auto CSS Add also needs consideration. |
| SMIL from-by | SMILAnimationFunction obtains effectiveTo via `effectiveTo.Add(by)` → SMILCSSValueType::Add → AddOrAccumulate(Accumulate,count) | A Procedure::Accumulate relaxation reaches from-by too. |
| SMIL repetition | SMILAnimationFunction::ComposeResult uses `result.Add(lastValue,repeatIteration)` → same AddOrAccumulate(Accumulate,count) | Also affected by an operation-only relaxation. |
| SMIL sandwich addition | SMILCSSValueType::SandwichAdd → AddOrAccumulate(Add,1) | Uses Add, but that does not distinguish all SVG arithmetic from WAAPI. |

`ClipRect::animate` in animated_properties.mako.rs permits Interpolate, then rejects any animated component whose result is auto. Component calls use `?`, rejecting the entire rectangle. LengthOrAuto's derived matching Auto/Auto case otherwise succeeds. `accumulate_endpoint` drops failed accumulation; the composition path retains the original rectangle. For E=(auto,50,50,10), count2 retains E instead of3E=(auto,150,150,30), exactly matching the expected-failing baseline assertion. No new experiment or build was run by this audit.

`SMILCSSValueType::AddOrAccumulate` already owns property-specific nonadditive admission for other properties. It is a potential boundary for preserving clip's SVG rule if the general CSS value operation is corrected. This is an edit-point recommendation, not proof that a particular new guard is sufficient: zero-value finalization, wrappers, from-by failures, cumulative fallback and top-level auto versus rect(auto,...) require review. Do not introduce a generic Add/Accumulate switch and assume that preserves SVG.

## Guard history

`bed034ddc1f7d80e1c7fb21d7010de899d365874` (2017), Servo merge18210 / original Servo revision5624c0e3f16e0057bb228627eaf9018ef88e7786, introduces the non-interpolation auto rejection. Its message links bug1390352 and expressly says it enables existing Gecko SMIL tests. `73820f32c450096df47f729ac8a605e023bc723f` (2019), bug1532135 / D21863, changes Option<Length> to LengthOrAuto and adds today's FIXME, preserving the prior rejection. It is not the original behavioral introduction. Both patches are archived.

The pinned db_smilCSSFromBy.js expects noEffect for equal-auto rectangle addition; db_smilCSSFromTo.js permits equal-auto interpolation. This constrains regression testing independently of the unresolved current host-spec integration. Existing failure metadata and the prior baseline triage already document this behavior; this capsule adds zero bugs/fixes to the catalogue.

## Smallest prospective controls

1. Existing WAAPI mixed-auto iteration test unchanged: retain first-iteration midpoint and third-iteration start controls; require third-iteration midpoint3E.
2. One same-auto rectangle at both keyframes: iterationComposite accumulate, seek iteration2 midpoint; isolates matching-auto accumulation without discrete endpoint mismatch.
3. One CSS underlying rectangle plus constant matching-auto endpoint, composite:add; expect auto retained and numeric sums. Include all-numeric and mismatched-auto/length controls.
4. Existing SMIL from-by equal-auto and mixed-auto rejection tests, plus all-numeric from-by success and existing from-to equal-auto interpolation. Keep their current expectations.
5. One SMIL from-to repeat with accumulate=sum and matching auto: compare against its noncumulative sample to ensure a CSS repair does not start accumulating SVG numeric components unintentionally. This is a preservation control until the SVG integration question is resolved.

No control is added to WPT/SMIL here. A later candidate must validate all these caller classes rather than merely flip the existing WAAPI expected failure. No security, memory-safety, release-exposure or complete formal-verification claim follows from this arithmetic source audit.
