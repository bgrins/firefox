# Grid absolute-positioning endpoint policy

This companion precedes the native/WPT repair. It checks the distinction between
normal-flow subgrid clamping and absolute-positioned nonexistent-line handling.
It does not verify all Grid placement or name resolution.

## Replay

```sh
python3 artifacts/css-grid-abspos-proof-v1/check.py /tmp/grid-abspos-replay --live
```

The output directory must not exist. Omit `--live` to replay the frozen source
snapshots without requiring the current checkout to match their full native
file hash. `tooling-paths-v1.txt` is the source-only commit inventory. Generated
binaries, replay logs, receipts, and earlier attempts are not companion inputs.
The toolchain record pins the existing local Lean and Clang executables and
versions, and selects the macOS SDK explicitly. The SDK, system libraries,
Python runtime, and Lean installed library files are trusted, not exhaustively
hashed by this package.

## Normative target

[CSS Grid 2, absolute positioning](https://drafts.csswg.org/css-grid-2/#abspos)
requires nonexistent line references to act as auto; absolute positioning does
not create new grid tracks. A span-only placement becomes auto on both sides.
Normal-flow subgrid items instead use the
[subgrid clamping procedure](https://drafts.csswg.org/css-grid-2/#subgrid-implicit).
[Placement conflicts](https://drafts.csswg.org/css-grid-2/#grid-placement-errors)
include reversed and equal endpoints. These current primary-source sections
were read on 2026-10-18. The model below deliberately identifies a preserved
limitation concerning equal endpoints.

## Universal theorem scope

`GridAbspos.lean` defines an integer endpoint model independently of native
storage. `project` represents membership in the finite existing grid; its
inside, outside, and iff theorems characterize the auto/definite result.
`specPair` sorts two distinct resolved endpoints, then projects each endpoint.
The native model separates helper preclamping, final numeric clamping, legacy
placement fixup, policy selection, and projection.

The 26 audited theorems include:

- Clamping absorbs the helper's lower-start and upper-end preclamps. The two
  lower-start native branches share the same theorem.
- All three helper result classes refine the raw endpoint finalizer.
- The selected normal-flow policy is exactly the original map-bound policy,
  including arbitrary map bounds beyond the UA interval. No map-within-UA
  premise is used.
- The selected abspos policy is independent of map numeric bounds.
- Every pair result class refines `specPair` when the two raw resolved
  endpoints are distinct and already within the UA interval.
- Span-only abspos results are auto/auto.
- For a nonempty clamp interval the finalized range is inside the interval
  and has positive extent. When the upper limit is below the auto sentinel,
  neither finalized endpoint equals that sentinel.

There are no `sorry`, custom axioms, or unchecked native-decision proofs.
Each theorem's printed axioms must be a subset of Lean's `propext`,
`Classical.choice`, and `Quot.sound`. Seven compiled model mutations must fail
inside theorem checking, including wrong bound policy, dropped endpoint
inclusion, broken swapping/fixup, and span-only handling.

## Native bridge

`prepare.py` authenticates the source snapshots and checks the exact token
changes from the old functions to the candidate. The only helper changes are
two explicit numeric-bound parameters and the three corresponding bound
references. The finalizer selects map or UA bounds, passes the selected bounds
to the helper, and uses them throughout. The both-non-auto abspos call alone
selects the new policy. `ResolveLine`, its name-map input, and `AutoIfOutside`
are unchanged. The declaration retains the default normal-flow policy.

`bridge.py` compiles the complete extracted helper, finalizer, and abspos caller
bodies in two namespaces, using `int32_t`, `uint32_t`, actual constants, and the
native `LineRange` constructor/storage/auto methods. Debug-only constructor
checks are not enabled; the bridge models release storage. Helper assertions
remain active. Standard arithmetic runs with UndefinedBehaviorSanitizer.
The adapter substitutes a small style-line/name-map shell and a scripted
`ResolveLine`: numeric inputs use the supplied origin and capped ordinal;
named inputs return controlled values. The resolver call arguments are logged
and compared. This substitutes neither a verified CSS parser nor native named
line lookup.

The finite inventory performs 567,000 normal-flow before/after comparisons,
542,080 abspos policy/finalizer checks, and 344,120 bounded distinct-endpoint
projection checks. It includes a subgrid map upper bound of 20001, endpoints
near the UA limits, named-line responses, both span directions, missing or
reversed endpoints, and the potential 23457 auto-sentinel arithmetic value.
Nine independent numeric endpoint witnesses check expected auto/definite
outputs. Eight compiled native-body mutations must fail a semantic assertion.
The finite checks support the manual source correspondence; they are not a
universal C++ correctness proof.

## Explicit boundaries

The correspondence from parsed styles and native name lookup to resolved raw
endpoints remains a premise. So do valid clamp bounds, unambiguous sentinel
encoding, integer arithmetic fitting native types, and correct adapter/type
correspondence. The Lean model uses unbounded integers, not a verified compiler
or complete machine-integer semantics. Native compilation and browser WPTs
are separate gates owned by the repair artifact.

The spec-refinement theorem excludes equal raw endpoints. Native legacy fixup
turns equality into a one-track range; CSS abspos conflict handling requires a
separate analysis and repair. `equal_endpoint_limitation` records that gap.

The theorem also requires both raw endpoints within the UA limits. Beyond
those limits, clamping can erase information before projection. Even a grid
strictly inside the UA interval is insufficient: raw endpoints (10001,10002)
produce (9999,10000), exposing a false existing endpoint if the grid ends at
9999. Both this example and the exact-UA-boundary example are proved as
limitations. No claim is made that this repair fixes them.

Earlier attempts are retained under `attempts/` and `replay-1/`. Initial Lean
proof scripts required tactic corrections. The first packaged C++ invocation
lacked the macOS SDK path; it failed before compiling the bridge. `replay-2/`
passed before the final source-record hardening and declaration snapshot.
