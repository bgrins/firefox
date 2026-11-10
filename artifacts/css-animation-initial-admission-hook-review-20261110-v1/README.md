# Minimal initial-admission trace hooks

This is a read-only hook review for the root-owned initial-admission
transaction. `SOURCE.json` pins six current API/source files;
`EXCERPTS.txt` retains the relevant definitions. Searchfox discovery preceded
the immutable local object reads. No instrumentation was installed or
compiled by this task.

## Target and document identity

Use `TElement::id()` to read the existing ID atom. Gecko implements it through
`snapshot_helpers::get_id(self.attrs())`, and `WeakAtom` implements Display.
Converting the atom with `ToString::to_string` is available. Match the result
against the fixed probe IDs `svg`, `host`, `first`, `second`, `third`, and
`leaf`; emit that fixed role or an absent-role sentinel. Do not print arbitrary
unescaped ID text. The generic GeckoElement Debug implementation enumerates
all attributes through FFI and is unnecessary here.

The generic Rust document-node identity is
`element.as_node().owner_doc().as_node().opaque().0`, with `TNode` and
`TDocument` in scope. Pair it with the existing element-node opaque identity.
GeckoNode::owner_doc reads its NodeInfo document, and GeckoDocument::as_node
returns that document's nsINode base. Match the C++ side with an explicit
`static_cast<const nsINode*>(mDocument)` before pointer formatting; do not
assume a direct Document pointer and its base are interchangeable.

Role IDs are unique only within each fixture document. Document/node identity
and PID remain necessary because the three callbacks reuse those IDs. These
are bounded observation identities, not lifetime-generation certificates.

## Entry, queueing, and execution

In Gecko's `matching::process_animations`, log entry after the `old_values`
binding and before its early return. Record the node/document/role,
old-primary presence, traversal flags, and thread. The intended witness has
AnimationOnly and no old primary style; an entry alone does not mean a task
was produced.

For nonempty task masks, save `tasks.bits()` before moving `tasks` into
`SequentialTask::update_animations`, then log after
`context.thread_local.tasks.push(task)`. This records actual queue insertion
and the exact u8 mask. It avoids labeling a pre-push intention as queued work.
The named flags in `context.rs::UpdateAnimationsTasks` are the source for
interpreting those bits.

To observe execution without adding context.rs to the native transaction,
use `GeckoElement::update_animations` in the already instrumented wrapper.rs.
`SequentialTask::execute` calls that method with the task mask. Record its
node/document/role and mask immediately before `Gecko_UpdateAnimations`.
An optional return event can distinguish entering the C++ consumer from
returning successfully. Preserve the original borrow and value lifetimes;
the logger only needs existing identifiers and mask values.

Queue and execution records should be joined as an ordered multiset per
node/document/mask within the relevant traversal. Repeated identical masks
are not unique task IDs. Claim execution only for unambiguous observed pairs;
do not infer a new request generation from a repeated mask alone.

## Call and phase boundaries

Retain StyleDocument's existing enter, document-root, drain-selected, and
exit events with the document-node identity. Iteration 0 may contain both
the animation-only prepass and the following normal pass inside one
`Servo_TraverseSubtree` call. The Rust traversal flags determine which pass
an individual admission belongs to; the C++ root event's raw flags alone do
not distinguish them.

Add StyleNewSubtree enter, normal/final pass markers, and exit, including its
own call token, style set, document node, and root node. Its final pass sets
AnimationOnly plus FinalAnimationTraversal and must remain distinct from
StyleDocument drain work. StyleNewSubtree can be nested within StyleDocument;
use a checked call stack rather than replacing the outer call identity.

`StyleNewSubtree` holds an `AutoPrepareTraversal` guard across its body. Its
destructor can run post-traversal tasks. A final source-line log before the
closing brace would precede that teardown. Declare a scope-exit logging guard
before `AutoPrepareTraversal`, so reverse destruction order logs exit after
the traversal guard has finished. Likewise, a final-pass marker is emitted
only when the conditional final traversal actually executes.

## Rust line transport

Format the entire event, including its newline, into an owned string first;
then call `Write::write_all` once on a locked stderr handle. This avoids
streaming formatter fragments through repeated stderr writes. The same
pattern should cover old Rust trace sites and their cap records.

This reduces fragmentation; it does not itself prove cross-process atomicity.
`write_all` may retry partial writes, and stderr locks are process-local.
Keep records short and reject malformed, interleaved, capped, or unmatched
records in the claimed interval. Filtering the new producer hooks to the
fixed probe roles is compatible with a role-scoped claim; it is not a
complete all-document producer inventory.

These hooks can establish finite initial-admission and delivery witnesses.
They do not establish repeated destruction/recreation or native termination.
