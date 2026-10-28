# Constant Round bound reconstruction lead

The current parse-time finite Round simplifier has a small source-backed numerical discrepancy that the runtime quotient candidate does not change. No browser execution, universal CSS violation, or additional bug count is claimed here.

For `round(up, .65, .1)`, the current Number-leaf operations produce binary32 `3f333334` (0.7000000476837158203125). Exact selection of seven represented steps, rounded once to binary32, produces `3f333333` (0.699999988079071044921875), the same represented value as literal `.7`. The source first rounds the lower bound to binary32, then adds the step in another binary32 operation. This second rounding moves the upper bound one ULP above the single-rounding oracle.

The proposed browser witness is `opacity: sign(round(up, .65, .1) - .7)`: current source predicts 1, while the oracle/control result is 0. Nearest with `.66` and negative down/nearest mirrors expose the same reconstruction boundary. Sign deliberately amplifies internal precision; CSS permits implementation-defined numeric precision, so this observation alone is not a universal conformance verdict. The parse-time reconstruction is distinct from premature quotient rounding in the runtime branch, despite belonging to the broader Round arithmetic family.

## Actual source extraction

Searchfox located the Round lower/upper reconstruction and `try_op` route. The reviewed local generic-calc base is the sealed current SHA b9a36918…. Its finite simplifier body is copied byte-for-byte into EXTRACTED.txt and a minimal Number-scalar adapter. `CalcNode::try_op` calls the leaf operator; the specified Number implementation accepts `Fn(f32,f32)->f32` and wraps its result without retaining wider arithmetic. The adapter preserves the actual remainder, lower/upper reconstruction, sign-zero correction, strategy match and exact-multiple return. It supplies only the surrounding Number-leaf methods and replacement macros, with no parser or native refinement claim.

The compiled adapter checked six operand pairs across four strategies: 24 checks, six mismatches against the independently reviewed exact dyadic oracle, eighteen matching controls. Rustc 1.92.0 compiled only this private scalar adapter; the temporary executable was removed. Node syntax validation passed. Source capture pins are recorded in REFERENCES.json.

For the positive up witness, represented A is 10905190/16777216 and B is 13421773/134217728. The exact lower multiple is 6B and selected upper is 7B. The stored lower is 0.60000002384185791015625. Adding B to that rounded lower yields an exact midpoint between output floats 3f333333 and 3f333334; nearest-even chooses 3f333334. Direct multiplication 7B rounds to 3f333333. The intended directed bound decision is unambiguous under the represented-operand oracle.

## Runnable diagnostic and oracle distinction

Load observe.js and call `await observeRoundParseBounds()`. It creates and removes its own iframe and returns eight named rows. Five are predicted discrepancies (four strategy/sign mirrors plus an explicit-dyadic duplicate), and three are directed/exact-step controls. Expected amplified targets are 0 under the stated oracle. Each row records support, specified values, computed values, repeated reads, literal 0/1 calibration and a positive one-ULP sign amplifier. An additional scaled integer observation is diagnostic only and does not decide the opacity oracle.

For mathematical decimal operands, up(.65,.1) selects decimal .7. The binary32 operand interpretation instead selects exact7B, then rounds it once to the output format. Both happen to produce the same represented reference for this case, but these are different reasoning contracts. The explicit-dyadic row compares Round against `calc(7 * exact_step)`, so both expressions denote the same exact selected multiple before implementation rounding. It deliberately avoids comparing the exact dyadic result against a pre-rounded literal, which would create a nonzero ideal-real difference.

Unsupported syntax or failed calibration remains visible and is not counted as success. The script imposes no required number of observed failures and does not identify or control the browser; root owns that provenance.

## Candidate hypothesis and limits

A coherent repair could compute finite scalar Round once in a shared wider helper and invoke it through one existing same-unit `try_op`, instead of storing a rounded lower endpoint before constructing the upper. This retains generic compatible-leaf handling without a type whitelist. Runtime and simplifier could share the reviewed arithmetic while existing special-value classification, exact-input preservation and negative-zero behavior remain explicit. No native patch is supplied here.

Do not simply defer every constant Round expression to contextual consumers or assume a binary64 value can be stored inside a binary32 leaf. The implementation needs an actual scalar boundary and existing consumer/serialization regressions. Relative-unit zero-basis eligibility is a separate unresolved simplification policy; this constant numeric lead does not authorize broader deferral.

The [CSS Values Round rules](https://drafts.csswg.org/css-values-4/#round-func) select adjacent multiples by strategy. The [numeric precision rules](https://drafts.csswg.org/css-values-4/#numeric-types) leave machine precision and closest-value policy implementation-defined. This exact-binary32 oracle is therefore an explicit arithmetic contract, not a universal required bit pattern for every CSS engine. The equality/product controls support bounded consistency observations, not a complete CSS numeric proof.

The runtime-only candidate leaves this simplifier body unchanged. Preserve the current paired experiment and do not relabel it as testing a repaired parse-time implementation. Browser reproduction and scope/acceptance decisions belong to root. No native source, Git/index, epoch, runtime or sealed predecessor was mutated.
