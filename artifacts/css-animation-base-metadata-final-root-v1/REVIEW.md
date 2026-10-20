# Underlying animation value metadata

## Native and browser result

The repair changes one predicate in EnsureBaseStyles. Ordinary AnimationValue
inequality remains first; equal values with a custom key and two nonnull handles
also compare attribute taint. The existing base-change path requests the restyle.
Global equality, base-map construction and endpoint handling remain unchanged.

The strengthened eight-case baseline has four failures at the final immediate
URL-taint assertion. Both taint directions fail for implicit initial and final
endpoints. Different-payload changes and explicit replacement controls pass.
All initial and nonanimated-base checks pass. A second target read after the
control/reference flushes stays stale; the subsequent time seek yields the
correct result. This supports the source diagnosis without directly inspecting
the internal map or proving the complete scheduling chain.

The candidate build exits zero and the complete local matrix has 189 passing
subtests and 14 OK harness results. Exactly those four failures improve; the
other 185 statuses are unchanged. The reference is a join of the fresh eight
cases and historical 101-case and 80-case runs on the same baseline binaries,
with the recorded endpoint formatting transfer. It is not a single fresh
189-case baseline invocation. Supplemental before/after hashing binds the
additional setKeyframes test. Existing conditional attr-security assertions
retain their limitations; a reported pass does not establish that all branches
ran. No performance comparison or isolated upstream run is claimed.

Independent source and runtime reviewers accepted their scoped gates. Root
read both reports and replayed the authenticated source packaging and raw-result
reconstructions. Four known build-monitor export KeyErrors remain in the log;
the build and browser runs completed successfully. Final format and scoped lint
exit zero with one warning and no changes to the tested bytes.

## Formal component

Root read the new model and laws and ran a fresh kernel replay: 23 audited
results, 14 complete source bindings and one compiled omission mutant. The
mutant loses both metadata-change decisions and both immediate sampled-bit
observations; payload, ordinary-property, forced-tick, removed-key, null and
guaranteed-invalid controls remain intact. Exact axiom inventories allow only
the recorded propext and Quot.sound uses.

The scan theorem covers arbitrary finite new-entry lists and old lookups. It
derives the exact added decision without assuming incoming taint equality or
payload-comparator reflexivity. A selected custom entry whose scan reports no
change must match the old same-key taint. Outer nulls remain distinct from
nonnull custom values whose internal value is missing. Old-only removed keys
remain outside the scan, explicitly; this is not whole-map equality.

The request theorem concerns the branch's call decision. Actual enqueue and
delivery require target, context, animation and presentation-shell readiness,
then queue consumption and publication. The small synchronous tick model assumes
those effects; it does not verify Gecko's scheduler. Its no-notification case
uses prior sample coherence, not assumed new output freshness. Full provider,
representation, traversal, lifetime, compiler, interpolation and URL-data
correspondence remain open. Independent formal review is a separate acceptance
record, not implied by root's successful replay.

## Packaging and discovery

The stack patch has two files: KeyframeEffect.cpp and the eight-case WPT. It
reuses the getter/FFI from fix78. The upstream alternative includes those two
accessors, the base comparison and WPT, totaling four files; it omits fix78's
endpoint loop and fix76's map comparison. Source analysis establishes why this
noninherited fixture with a distinct initial value avoids those other repairs.
Root checked exact application/reversal and all resulting blobs against actual
Git objects. This is source/prerequisite evidence, not upstream runtime.

The two standalone animation alternatives share accessor definitions. Use the
stack patch when those definitions are already present; the upstream alternative
is for landing this repair without them.

Discovery came from a source audit of a remaining metadata comparison followed
by browser reproduction. Formalization followed and checked the local repair
obligation. It did not automatically discover the observable bug. The original
probe and its intervening-flush ambiguity are preserved separately; the stronger
probe supplies the later causal discrimination.

Independent formal review accepts this scoped component after authenticated
relocated replay, seven additional kernel challenges and six rejected integrity
corruptions. Root read its report and challenge statements and checked its
sealed receipts. Producer canonical/relocated receipts and eight guards also
verify. The custom value's embedded name must agree with its map key; the
abstract guaranteed-invalid value does not retain that name. This remains an
explicit native construction premise.
