# Guarded implicit cleanup verifier finding

The pinned local Creusot toolchain accepts a false assertion after implicit
cleanup of a `Guarded` mutable reference. This reduced program has no caller
precondition and uses the existing verification library:

```rust
use creusot_std::{invariant::Guarded, prelude::*};

fn main() {
    let mut value = 0u32;
    {
        let guard = Guarded::new_m(&mut value, snapshot!(|x: u32| x == 0u32));
        *guard.inner = 1;
    }
    assert_eq!(value, 0u32);
}
```

Both generated proof obligations pass. Ordinary execution fails the assertion:
the actual value is one. The archived source includes one additional unused
import, which has no effect on the program.

## Evidence

Independent reproduction uses a fresh Cargo compilation of the isolated,
unmodified `creusot-std` source, with erasure checking enabled. It regenerates
one model, proves both obligations and executes the identical source with
ordinary Cargo. The executable exits with the expected assertion failure.
No new native-cell primitive, `NonAtomicInvariant` or custom owner is involved.

The generated model updates `guard.inner.current`, then assumes resolution of
that inner reference without checking the outer `Guarded` invariant. An explicit
`core::mem::drop(guard)` instead requires the guard invariant and leaves that
obligation unproved. A plain mutable-reference control leaves the false assertion
unproved; restoring zero before implicit cleanup passes. Solver failures in the
controls are sensitivity checks; the contradictory runtime result establishes
the defect in the checked toolchain.

The local independent reproduction is under
`artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/reviews/guarded-implicit-drop-root-v1`.
Its scripts record the exact compiler, solver and runtime commands. The report
authenticates the baseline library source and recorded outputs; it does not
claim a complete compiler or operating-system dependency replay.

Record paths below are relative to `native-storage-pop-concrete`.

| Record | SHA-256 |
| --- | --- |
| `reviews/guarded-implicit-drop-root-v1/REVIEW-v1.json` | `838f9a87117569c81f06400e54882f86e4512d7691b43824fb79d952e6b05d9f` |
| `native-owner-lifecycle-v1/native-permission-boundary-v1/loan-api-v1/reduction-v1/GUARDED-IMPLICIT-CLEANUP-DEFECT-v1.json` | `7e5e6f1554c46a280e99d9b0956ef737429247cdc0960b43f7c97056af7215fa` |

## Scope and next step

This is a pinned-verifier defect, not a new Firefox bug or a claim about the
current upstream release. A bounded scan of native fixture sources found no
uses of `Guarded` or `NonAtomicInvariant`; emitted models and indirect library
uses still need separate impact review. The experimental permission protocol
uses `Guarded<FullBorrow>` and needs that review before further reliance on it.
The Lean proofs and their stated assumptions are not changed by this finding.

Do not use implicit guard cleanup to close the native lifecycle obligation.
The next step is a compiler regression test and an isolated correction to
invariant enforcement before partial-field resolution. Explicit-drop controls
must continue to fail when the invariant is violated. Existing accepted
compiler binaries and evidence remain unchanged during that experiment.
