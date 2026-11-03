# Repeated saved-authority validation

The checker expands a shared lineage as a tree. This is a concrete source-level cause of redundant work, not a browser/native issue. No checker, validator or live process was executed, restarted or modified for this review. The author subsequently reported the original checker completed normally (b5a7d1/session29274/21ce5b/exit0).

`check.py::validate_policy` calls `admission.validate_current`. That calls the capture adapter's `native_head_view`, which calls `validate_refresh`, and then calls `validate_refresh` again directly. Each recent refresh bridge calls its parent validator once and its completed refresh owner's `saved(policy)` once. That saved replay calls the historical native owner's admission, which calls the same parent validator twice. The saved bindings confirm both routes reach exactly the same prior capture directory. Each new bridge multiplies prior replay by three.

| Bridge, newest first | Refresh calls per full admission | Calls across eight full admissions |
| --- | ---: | ---: |
| keyframe capture v2 / combined taint refresh |2|16|
| combined taint capture / typed-reparse refresh |6|48|
| typed-reparse capture / minimum-font refresh |18|144|
| minimum-font capture / fallback candidate refresh |54|432|
| integrated post-pair capture / integrated pair refresh |162|1,296|
| integrated pair capture / integrated native refresh |486|3,888|
| integrated native capture / V118 validator |1,458|11,664|

The complete checker has a valid-policy call, six negative mutations reaching full admission before later rejection, and a both-gates-enabled positive call. Five other negative cases reject before this recursive route. CALLGRAPH.json names each case and exact source path. These are planned counts if earlier positive checks succeed, not measured stack samples or the running process's progress.

Totals are17,488 recent refresh calls and5,824 saved-runtime replays. Earlier V118 ancestry is deliberately not expanded. Every V118 call directly reads/parses five JSON records totaling15,878,693 bytes. Across11,664 calls that alone is185,209,075,152 logical input bytes (~172.5GiB), excluding ancestor parsing, manifest authentication, raw-event replay, imports and repeated reference hashes. OS caching can avoid physical I/O but not Python decoding/object traversal. No wall-time speedup or profiler attribution is claimed.

`load`/`exec_module` creates new module instances, repeating module-global reference checks. A per-module lru_cache would not join identical work loaded through different ancestors. Caching by path/mtime or trusting FILES.json alone would miss changed payloads.

## Bounded future wrapper

Use a new scoped process-local wrapper around only the seven identified saved `validate_refresh` functions, leaving historical files byte-identical. Do not cache validate_policy, receipt/schema gates, source/inode claims, live observe/verify_current, signatures, process/quiescence checks, staging or negative tests. Cache only the successful historical JSON snapshot. A reviewed entrypoint installs the wrapper for a saved validation operation and removes it afterward. No running owner changes.

A shared table must survive fresh loaders. Its key binds repository root, canonical module path, exact code identity, complete on-disk bindings and in-memory binding values, function identity, serialized direct arguments, and complete top-level mutable policy/roles/receipt inputs. Different negative mutations therefore cannot borrow a result from another policy. Every admission retains its normal control flow; only identical repeated subproblems within that scope can hit. Never cache exceptions, partial evaluations or in-progress recursion. Return deep copies so projection/mutation cannot poison later results.

On a miss, execute the exact original validator. Record all consumed file content hashes AND consulted filesystem facts: imported code, bindings, policies, manifests and their actual payload bytes, receipts, source captures, raw streams, assessments, file sizes/types/identities, symlink targets and tested absences. Merge every child's complete ledger into its parent, including cache hits. Reject untracked I/O or inconsistent repeated reads; do not make an incomplete ledger reusable. Revalidate the ledger before publishing the successful entry.

On every hit, freshly read/hash all consumed files and recheck the recorded existence/type/identity/absence facts before returning a deep copy. Manifest-only, stat-only and persistent-success shortcuts are excluded. Changed content invalidates the entry; reexecute the original logic or fail if pinned bytes no longer match. This authenticates transitive payloads even when a top-level capture/manifest is unchanged. Live current-state guards remain entirely uncached. Coarse full-closure hashing on hits is acceptable: the target is exponential JSON decoding and evidence replay, not removing authentication.

An in-memory loader wrapper can install these function wrappers on exact allowlisted modules without changing sealed files. A narrowly scoped read/fact recorder or an explicit audited dependency inventory with a fail-closed read allowlist is needed. Completeness is the new review obligation: direct Path reads, import-time source loads, exists/is_symlink/stat and dependency propagation must all be covered. If it cannot be established for these seven validators and saved callees, do not deploy a partial recorder. No wrapper, import hook or filesystem shim is implemented here.

With a distinct complete-policy scope for each of eight cases, each of seven recent validators need execute at most once per scope:56 executions rather than17,488, with V118 at most8 rather than11,664. Fresh full-closure hashing on hits remains necessary and is excluded from these structural counts. Earlier V118 recursion can remain unchanged in the first bounded optimization.

## Required validation

Retain all11 binding negatives,14 stream negatives, both staging lanes, active-gates positive and real same-byte/replaced-inode control. Add cache controls changing a raw payload without its manifest; changing code/bindings/receipt/policy after a hit; changing a consulted symlink/absence/identity; mutating returned snapshots; making a valid dependency invalid; and attempting to cache failure/incomplete work. They must reject or recompute and reject through original guards. A small duplicate-branch fixture should demonstrate one evaluation per identical content scope, then one future real saved replay should match the existing result and rejection behavior. Aggregate test counts alone are insufficient.

Root review precedes any implementation in a separate artifact. Native/commit priority is unchanged. No implementation, native operation, persistent cache or accepted-fix increment is claimed.
