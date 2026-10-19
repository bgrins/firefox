# Independent review: payload-and-taint map histories

## Verdict

Accept the producer's stated conditional mathematical component. No blocking
proof, source-transfer, or replay issue was found. This does not newly accept
native declaration histories, substitution, URL handling, COW representation,
or complete CSSOM behavior.

Reviewed producer: `css-custom-properties-map-taint-history-proof-v1`, externally
authenticated with FREEZE
`1e316cc64b53514fc75288cddb4e341a1edcbaf4293467fd144b2903865df20c`,
MANIFEST `0ef4607c65f7accc541dd25fde3cf0c28954854cb3b5e393775f6cf63ab760f9`,
and checker `4f2fee2daefad0f01fac1ba3b7466ed1b72aa75b9b60fa228e6321b543e9b15f`.
All 32 manifest inputs matched before execution. The replay used only those
inputs plus the two seal files and the pinned installed Lean toolchain.

## Proof audit

I read the complete new `TaintHistory.lean`, all twelve imported modules,
`Driver.lean`, the audit roster, mutation definitions and checker. I also read
the predecessor taint scope, report and source-mapping admissions. The new
results are seven general results and two concrete kernel-checked witnesses.

| Result | Independent assessment |
| --- | --- |
| `compare_sound` | Instantiates `LiveCount.CompareSound` using `metadata_same_sound`. The Boolean predicate derives equality of both payload and taint; it does not assume skip correctness. `PayloadSound` remains an explicit one-way premise. |
| `lookup_reference` | Uses the independently defined functional last-update reference and the source-shaped insertion/COW model. Arbitrary finite optional-value updates and arbitrary initial modeled stores are admitted. Lookup correctness does not need the stronger count/unique-node premises. |
| `lookup_url` | Substitution of equal modeled states preserves an arbitrary fixed scalar URL observation. This is not a theorem about actual URL resolution or taint-range construction. |
| `indexed_reference` | Derives nearest-owner lookup from the composed count/iterator history invariant, then uses comparator soundness. It does not assume raw enumeration as a fresh theorem premise. The returned-index premise is useful, with separate imported in-bounds/existence results preventing an interpretation as empty enumeration only. |
| `indexed_url` | Correctly applies the indexed value result and the scalar observer definition, including tainted values returning `none`. |
| `prefix_indexed_taint` | Instantiates the finite-history theorem on `ops.take n`. It covers every finite prefix of already-admitted map operations, not the upstream producer of those operations. |
| `exact_count` | Correct without payload comparator soundness: either a skip preserves representation, or the actual insertion updates the count. Count agreement alone does not establish reference value agreement. |
| Two witnesses | The old comparator preserves a count of one while retaining stale untainted data. The repaired comparator preserves the incoming taint at the indexed observation. Both are genuine propositions discharged in the kernel. |

The imported count model separately tracks `stored`, the chain, optional
tombstones, and lookup; it does not define the stored count by its desired
result. `finite_history` establishes readiness from the empty initial map.
The iterator uses a cursor with descendants, suffix and parent chain; its
reference is nearest-owner filtering, and the composition proves their
agreement and live filtering. The new component therefore joins existing
substantive invariants rather than replacing them with a comparator-only claim.

The source/model boundary remains important. Unique/shared outcomes are supplied
Booleans, nodes are finite ordered lists, and native ownership/aliasing is not
proved. A list of updates is not a complete graph of aliased native maps and
mutating ancestors. The reported admissions correctly retain those obligations.

## Source transfer

I inspected the complete retained map implementation, complete
`Cascade::value_may_affect_style` and its `cascade_custom_property` caller,
plus the predecessor provider/observer mapping. Independently generated full
file diffs are retained in `map-transfer.diff` and `cascade-transfer.diff`.
They contain exactly the two declared changes:

- `CustomPropertiesMap::do_insert` changes its shared-map shortcut to
  `can_deduplicate_values`, which already compares wrapper taint in addition
  to native payload equality. The unique-ownership early route remains first.
- The universal branch of `value_may_affect_style` compares wrapper taint with
  incoming `is_attr_tainted()` before treating equal CSS payload as unchanged.

The map's insertion, live-count updates, tombstone lookup, expansion threshold,
iterator and index filter are otherwise byte-identical. Full-file hashes also
connect to both retained predecessor manifests. This is exact source transfer
plus reviewed correspondence, not a verified Rust translation or fresh Rust
execution.

Crucially, `LiveCount.run` starts after the earlier cascade shortcut: its input
operations already contain the computed optional values reaching the map.
The cascade change is source-bound but is not executed by this model. The
earlier scalar taint component requires reference-free eligibility/provider
premises; the actual universal shortcut has no explicit reference-free guard.
This composition does not derive those premises for arbitrary declarations or
state-dependent recascades. The producer states this limitation correctly.

`PayloadSound` concerns equality in the chosen abstract payload domain. It
cannot be instantiated as equality of the whole native struct merely because
native `PartialEq` returns true. URL data and other omitted metadata need a
valid observation quotient; actual consumers must factor through it. The
scalar `observeURL` has a fixed parsing environment and carries no native
URL-data field. Registration routing, inherited/reset domain separation,
substitution/reference bookkeeping, observer flags and machine bounds remain
external. Root's native fix and browser gates are separate evidence.

## Fresh execution and adversarial checks

The independent manifest-only relocation completed with exit 0. It compiled
13 model modules and audited the exact nine new names. Transitive axiom reports
contain only `propext`, `Quot.sound` and, where used, `Classical.choice`; no
new local axiom or placeholder was found. The full logs and command/exit records
are retained in `replay-receipts/`.

Four driver variants each elaborated successfully with `-o` and then executed
with Lean `--run`. These are Lean model executions, **not native Rust mutation
tests**. The seven observations are count/lookup/index for taint addition,
count/lookup/index for taint removal, and deletion. I independently derived
their expected patterns from the two same-key, same-payload updates:

| Wiring | Addition count / lookup / index | Removal count / lookup / index | Deletion |
| --- | --- | --- | --- |
| Metadata comparator | true / true / true | true / true / true | true |
| Payload-only | true / false / false | true / false / false | true |
| Ignores taint addition | true / false / false | true / true / true | true |
| Ignores taint removal | true / true / true | true / false / false | true |

The mutants change only comparator selection. They do not change driver inputs
or expected observations, and none is counted on a compilation failure.
This does not rerun all predecessor mutation suites or broaden native coverage.

Thirteen independent negative guard checks reject changed proof bytes, Python
and Lean shadow files, an extra empty directory, a symlink, FIFO, duplicate
JSON key, missing input, nonisolated/site-enabled/optimized Python, internal
output, and already-existing output. Exact expected diagnostics and exits are
retained in `GUARDS.json`. These are integrity/invocation tests, not semantic
proofs. The producer's source-only closure, import provenance and external
toolchain/library pins are appropriate for the stated replay trust boundary.

## Reproduction and retained scope

Externally authenticate this review's seal/checker first. Run
`python3 -I -S check.py` to authenticate the retained evidence and verify the
recorded verdict gates. Add `--replay-output /absolute/fresh/external/path` for
another fresh producer replay using `inputs/producer`. `challenge.py --output
/absolute/fresh/external/path` reproduces the thirteen guard challenges after
authentication. Output must be outside the frozen review capsule.

The retained producer copy is unchanged. `inputs/predecessor-context` contains
three additional explanatory documents consulted; their text is review
context, not a replacement for the imported modules' pinned provenance.
Only this review's completed temporary work and generated Lean outputs were
cleaned after preserving receipts. No live native, WPT, browser, build or Git
state was changed.
