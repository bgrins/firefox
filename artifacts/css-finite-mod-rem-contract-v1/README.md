# Finite ModRem replacement contract

This artifact proves general laws for the proposed finite replacement, using the existing exact binary32 remainder capacity and signed-zero representation. It does not integrate the canonical library or modify Gecko. No native source, index, binary, fixture, or browser state was read or changed by this work.

`Contract.lean` works with signed integers on the common binary32 grid (one unit is 2^-149). `SignedEncoding` is the existing finite representability predicate; the imported decoder already relates that predicate to finite binary32 patterns. `NearestProjection` compares against every signed representable value, allowing both nearest choices at a tie.

The main results are:

- `adjustment_mod_relation`: for any integer dividend and nonzero divisor, the signed truncating remainder, adjusted by one divisor exactly when its nonzero sign differs, has the divisor-directed exact interval and differs from the dividend by an integer multiple of the divisor.
- `mod_projected_relation`: under explicit supplied-remainder equality and nearest-addition premises, the replacement Mod result is a nearest representable projection of that exact mathematical result. The non-adjusting branch reuses the existing exact remainder-capacity theorem without new theorem credit. `rem_exact` exposes the direct supplied-remainder correspondence for Rem; it is a small interface consequence, not a new proof of Rust `%`.
- `nearest_closed_interval` and `mod_projected_closed_interval`: projection remains between zero and the divisor, with both endpoints allowed. `zero_sign_preserved` and `exact_multiple_zero` preserve the existing operation-specific signed-zero representation, even for an arbitrary projector: Mod takes the divisor sign; Rem takes the dividend sign. Exact-zero remainders never invoke the addition projector.
- `strict_projected_interval_false`: with dividend -1 and divisor 33554432 grid units, exact Mod is 33554431. That odd value is not representable, while 33554432 is a nearest representable projection. The projected divisor endpoint therefore violates a strict interval. The proof quantifies over all signed encodings; it does not assume the endpoint is nearest. It permits ties and does not separately certify a native tie-to-even implementation.

The model has 12 audited declarations, including support lemmas and interface consequences. These are four groups of conclusions, not 12 additional CSS features or bugs. Inherited decoder, capacity, and exceptional-dispatch results receive no new credit. The prior old-formula witness is referenced for context and is not re-proved or used as an arithmetic oracle.

## Remaining correspondence obligations

The supplied integer operands must faithfully encode finite native operands, with a nonzero divisor; supplied sign bits must match those operands, retaining the dividend sign at zero. Native `%` must supply `Int.tmod` on this grid. Native opposite-sign addition must produce a nearest finite encoding of the exact adjusted value. The model uses a branch on remainder sign rather than reproducing hardware sign bits; their interpretation remains part of that source correspondence. No result verifies compiler lowering, hardware instructions, flush-to-zero settings, or the Rust/IEEE pipeline universally.

This proves the replacement's mathematical structure and narrows the former opaque finite-backend premise. It does not fully discharge the earlier dispatch theorem's equality premise: a concrete floating-point spec backend, consistent tie selection, and the native correspondence still need to be connected. NaN/infinite operands and zero divisors remain covered by the separately established exceptional-dispatch model, outside the finite theorem's domain. No infinite-precision intermediate guarantee is claimed for CSS implementations.

## Replay

Run `python3 -I -S -B artifacts/css-finite-mod-rem-contract-v1/replay.py --output ABSENT_EXTERNAL_DIRECTORY` from the repository root. The runner authenticates pinned inputs, compiles imports and the model with the pinned Lean executable, audits theorem axioms, and checks eight positive examples plus six rejected false claims. The false strict-bound claim is paired with the proved nearest endpoint certificate. The other false claims exercise omitted sign adjustment, adding the divisor to zero, both wrong zero-sign policies, and omission of the remainder correspondence premise.

`results/CHECK.json` records a passing replay. No new model warnings occur. The imported historical dispatch module emits its existing 18 unused-simp warnings, explicitly limited to that module. Ordinary Lean axioms `propext`, `Classical.choice`, and `Quot.sound` occur; there are no new axioms, `sorry`, or native decision shortcuts. Earlier authoring failures are retained as logs and are not successful proof receipts. All temporary compiled products were removed.
