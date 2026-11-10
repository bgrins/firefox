# Bounded obligation trace review

The recorded trace supports the narrow claim that twenty selected request
cohorts reached actual hint insertion and primary-style installation within
the two marked activation intervals. It does not establish general native
obligation conservation, generation freshness, or termination.

Reviewed inputs:

| Input | SHA-256 |
| --- | --- |
| analyze.py, initial review version | 4877df0fde33fe9b4f8dfba9abea9874941c576243ae4cd0619f90a0547f1be4 |
| runtime1/wpt-raw.jsonl | f811d35b92b6a5585bb9e12da0d499f6f51e0bf24594905faa454b8babd67e57 |
| instrumentation.patch | 214682791a29e32746717bf6aeb85e2f290be20a9dc84c712ae15931c5c65686 |
| font-dependency-ledger.html | 4da4db708bd68133f9f05b4c5c6a66943cc3a553606d28bba14a4a999872186f |

## Observations

Each activation contains one selected compositor and one style set in PID
33155. Startup drains belong to call 9; the second activation drains belong
to call 20. Each contains four drain iterations selecting 4, 3, 2, and 1
targets. All relevant Rust admission and installation events use
`ThreadId(4)`. Selected entries are all level 0, pseudo 95, null pseudo
argument, and posted=1. The corresponding requests form 21 and 22 observed
request events, respectively; these counts are not independent generations.

The instrumentation observes `hint-posted` after `data.hint.insert` and
`installed` after `data.set_styles`. Thus the installation event is stronger
evidence than merely computing a keyframe endpoint. `select-remove` precedes
`iter.Remove()` and correctly remains labeled removal intent.

The selected key joins include compositor, target node, pseudo type, pseudo
argument, and cascade level. Hint mapping preserves the target/pseudo fields
and checks the level-specific hint before joining the normalized node to
traversal and installation. New observed requests are retained separately
from older selected cohorts. All process-output rows inside the marked
intervals parse, and none contains a cap marker. The 146 malformed tagged
rows outside these intervals prevent whole-run completeness claims.

The unrelated mutation interval contains one ordinary style installation,
zero requests, and zero selections. Its lack of animation work is a control,
not an additional delivery witness.

## Required replay hardening

The initial checker accepted two altered traces: changing the first drain's
call from 9 to 999, and changing its first installation thread from 4 to 999.
The actual trace has neither discrepancy. Before presenting the checker as
enforcing these attribution assumptions, bind drains to their active
document call/style set and require matching admission/installation thread
identity. Checking the actual per-episode single-compositor/single-style-set
and single-Rust-thread conditions makes the stated bounded scope explicit.

The checker relies on Python assertions; reject optimized execution so
`python -O` cannot disable verification. Keep these improvements as analysis
changes over the saved trace; another browser run is unnecessary.

## Reporting boundaries

The JS markers carry neither native PID nor document identity. PID attribution
uses the unique selected process and the inspected fixture, rather than an
independent cross-language identity token. Node and pseudo-identifier pointers
are interval-local identities, not durable lifetime or generation IDs.

Although the join checks all key fields, this fixture exercises ordinary
targets at the animation cascade level only. It supplies no positive witness
for transitions, named pseudo-elements, failed posting, missing EffectSets,
throttled requests, concurrent traversal, or target destruction/reuse. Its
request ledger starts at each marker; native queue snapshots should remain
separate from claims about requests observed inside that interval.

These limitations do not invalidate the recorded twenty delivery joins.
They do preclude promoting the held repair on the strength of this trace
alone. No native defect was identified by this review.

## Follow-up review

The revised analyzer at SHA-256
`38500ea9a235ae115858312dd672af6104af712c4fcec38c522738c44cbb36ee`
checks singleton compositor, style set, document, and Rust thread per interval;
document-call entry/exit matching; same-call/same-thread installation; and
agreement between the observed pending-key ledger and every native queue
count snapshot. Independent replay still matched twenty deliveries and now
rejected both altered call and thread traces.

The final entry-point correction uses an explicit conditional and exception,
rather than an `assert` that `python -O` itself removes. Independent execution
of `python3 -I -O analyze.py` rejected optimized execution with `RuntimeError`
before analysis; the checked analyzer SHA-256 is
`6bb38abb33c0a0e8a24217be76e6a568153bd8c901a42187bd88e75c63eb6fca`.
The review requests are resolved. General native refinement and
cross-language marker identity remain outside the checked claim.
