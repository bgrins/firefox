# Initial admission trace review

The instrumentation separates StyleDocument calls/iterations from nested
StyleNewSubtree calls and their default/final input passes. A default pass
can contain an internal animation prepass. The Rust flags, rather than the
input pass name, determine whether an observed admission is AnimationOnly.
The new subtree exit guard is constructed before AutoPrepareTraversal, so
its exit includes that object's destructor and sequential task execution.

The task-queued record follows the actual push. Task-execute precedes the
Gecko_UpdateAnimations call and task-return follows its return. An execution
entry alone is not callback completion. Initial installation is recorded
after the actual primary style assignment. Fixed role strings reveal only
the six fixture roles; native document identity uses the nsINode base on
both sides of the FFI boundary.

The seven existing Rust RFDP writes now prepare a line before locking stderr
and writing it. This reduces interleaving but does not guarantee interprocess
atomicity; malformed records and cap markers remain rejection conditions.
The existing per-file cap limits remain, with new events consuming the same
budgets.

The prepared analyze.py rejects ambiguous same-node/same-mask queued task
matches instead of assuming FIFO identity. It requires admission/management/
queue/installation to agree on node, document, role, flags, thread and call
context. Sequential callback execution can use a different thread from the
traversal; execution/return must agree with each other. C++ request records
have no thread field. A request bracketed by a synchronous callback in the
same process is a source-backed callback interval association; the trace
alone cannot independently establish its C++ thread identity.

No runtime existed at preparation time. The parser and call/task classifier
are preparation only, with delivery_verified explicitly false. Actual trace
validation still needs the full-key request/delivery ledger, host SMIL map
and insertion joins, callback status/value checks, and controls derived from
the observed trace. No synthetic success fixture is counted as native
evidence. Epoch-zero initial work is not evidence of renewed initialization
inside a later drain iteration, termination, or native-to-Lean refinement.
