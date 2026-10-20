# Initial View Transition types: independent native and WPT review

Decision: **ACCEPT the scoped repair and its standalone WPT.** No native or test correction required. This review is static source adjudication plus independent authentication and interpretation of the producer's recorded runs. It did not execute a browser, build, Git command, or formal proof.

## Normative contract

The current CSS View Transitions 2 draft delegates `Document.startViewTransition()` to the document root's Element algorithm. That algorithm initializes active types by cloning the options' types as a set. The `types` getter exposes those active types through `ViewTransitionTypeSet`, a mutable setlike of DOMString values. The root's `:active-view-transition-type()` matches when an active transition contains an argument. These are the applicable requirements for the visible, active document and ordinary identifiers in this test. [Document startup](https://drafts.csswg.org/css-view-transitions-2/#dom-document-startviewtransition), [Element startup](https://drafts.csswg.org/css-view-transitions-2/#dom-element-startviewtransition), [active types](https://drafts.csswg.org/css-view-transitions-2/#viewtransition-active-types), [selector](https://drafts.csswg.org/css-view-transitions-2/#the-active-view-transition-type-pseudo).

Infra's ordered set forbids equal duplicates. Appending an existing member leaves it in its original position. Web IDL requires unique ordered set entries; successful deletion removes the member and reports prior membership, while clear empties the set. This provides an independent oracle for order, membership and deletion, rather than treating the implementation's public set as authoritative. [Infra ordered sets](https://infra.spec.whatwg.org/#ordered-set), [append](https://infra.spec.whatwg.org/#set-append), [Web IDL setlike](https://webidl.spec.whatwg.org/#idl-setlike), [delete](https://webidl.spec.whatwg.org/#es-set-delete), [clear](https://webidl.spec.whatwg.org/#es-set-clear).

Current primary snapshots, response headers, retrieval times and SHA-256 are retained in `spec/`. The newer draft's scoped transitions and other lifecycle changes are outside this repair. Neither unsupported Element transitions nor reserved identifiers are used to establish this defect.

## Actual implementation chain

1. The generated options binding supplies the native string sequence to `Document::StartViewTransition`. Its options branch builds `nsTArray<RefPtr<nsAtom>> types`, and the same-document `ViewTransition` constructor moves that vector into `mTypeList`. The active document and root state are installed before the returned transition is synchronously inspected by this WPT. Null/default types, callback handling, hidden-document handling and previous-transition handling are unchanged.
2. `ViewTransition::Types()` lazily creates `ViewTransitionTypeSet`. It populates the generated backing set using `SetlikeHelpers::Add`. The JavaScript set collapses duplicate strings; before this patch, `mTypeList` still retained all duplicates.
3. Native `ViewTransitionTypeSet::Add` queries the backing set, returns for existing membership, otherwise inserts there and appends one atom. `Clear` clears both representations after successful backing clear. `Delete` first deletes in the backing set, returns false for absence/error, then removes one matching native vector element. `nsTArray::RemoveElement` finds and removes the first occurrence. That operation is correct only while the native uniqueness invariant holds.
4. The retained generated `ViewTransitionBinding.cpp` wraps objects into the correct realm, obtains the reserved backing object, converts strings and uses `JS::SetAdd`, `JS::SetHas`, `JS::SetDelete` and `JS::SetClear`. Public enumeration and membership use this backing set. The generated source hash matches all three runtime receipts, although the original drivers excluded objdir sources from their snapshot directories.
5. Gecko's actual Stylo `NonTSPseudoClass::ActiveViewTransitionType` branch requires the active-transition state flag and calls `Gecko_HasActiveViewTransitionTypes` on the element's owner document. That bridge reads the active transition's **native** `TypeList` and checks atom membership, with an additional validity filter. The WPT's `a`, `b`, `A`, `absent` identifiers avoid that filter's reserved-keyword questions. The generic `style/selector_parser.rs` retained by the drivers is not this Gecko-specific branch; this review additionally retains `style/gecko/{selector_parser.rs,wrapper.rs}`.

The failing native sequence is consequently concrete: initialize `[a,a]`; materialize public `{a}`; delete `a` in the public set and remove one native occurrence; public membership is false but direct selector membership remains true. This is representational disagreement with the required set contract, not evidence about missed style invalidation.

## Candidate and provider review

The only native hunk introduces a local `nsTHashSet<nsAtom*> seenTypes` and appends an atom only when `EnsureInserted` reports a new key. No iteration over the hashset contributes output order. Thus first occurrences stay in input order.

The provider path is explicit: `NS_AtomizeMainThread` uses the atom table's exact string lookup; `nsAtom::Equals` compares UTF-16 length and bytes. `nsTHashSet<nsAtom*>` selects `nsWeakAtomHashKey`; equality is pointer equality and hashing uses the atom's hash. `EnsureInserted` calls the infallible insertion operation and reports whether the count grew. Atom interning connects pointer identity to exact string identity; it does not case-fold `a` into `A`.

The temporary set does not own atoms. For a first occurrence, the local `RefPtr` owns the atom through insertion and is then moved into the owning vector. For subsequent occurrences, the existing vector entry keeps the atom alive while the duplicate temporary reference is released. The local set dies before the vector moves into the transition. Vector reallocation moves owning references, not atoms. `Document.h` already includes `nsTHashSet.h`; no include addition is needed.

Successful public mutation preserves agreement once initialization is unique: Add appends only absent values, Delete removes the single occurrence, and Clear empties both. These are reviewed arguments, not machine-checked theorems. Atom interning, allocation behavior, generated binding helpers and JS Set semantics remain provider premises. Existing `IgnoreErrors()` during lazy set initialization and failure/OOM behavior were not repaired or proved. The new hashset adds temporary memory and allocation work; no performance measurement is claimed.

## Independently derived WPT oracle

Seven input sequences cross three operations (`delete a`, `delete b`, `clear`) for 21 cases. `ORACLES.json` derives ordered unique contents, post-operation contents, deletion return and the old vector's predicted residual membership using an independent Python representation. The checker compares every raw test identity with that derivation.

The test first checks visibility and active transition identity, initial ordered public enumeration and four selector memberships. It then checks deletion return, updated enumeration, public membership and selector membership. The comparisons run synchronously before capture proceeds. Cleanup skips the transition and awaits its finished promise; testharness queues promise tests and runs cleanup before completing a test. A catch handles the expected ready rejection from skipping. A thrown assertion still has registered cleanup.

The five predicted failing cells are:

| Initial sequence | Operation | Residual old selector member |
| --- | --- | --- |
| `[a,a]` | delete a | a |
| `[a,b,a]` | delete a | a |
| `[b,a,a]` | delete a | a |
| `[a,b,b]` | delete b | b |
| `[a,A,a]` | delete a | a |

Each recorded baseline failure occurs at the updated selector assertion with `expected false but got true`. The deletion return, updated enumeration and immediately preceding public membership assertion already passed. Sixteen baseline controls pass: empty/singleton sets, deletion of an absent or nonrepeated value, clear and case distinction. All 21 candidate cases pass. The new test therefore observes the native/backing-set disagreement, even though public enumeration alone hid it.

The existing `view-transition-types-mutable.html` contributes three candidate passes: type object presence; successful add/delete/duplicate add and unrestricted strings; and mutation after finished. It does not cover initial duplicates or certify active-selector invalidation. It has no paired baseline in this evidence set.

## Runtime and resource authentication

`check.py` authenticates all 109 retained origin files and the complete local manifest. For each recorded run it checks 22 before/after pins, 19 originally retained source snapshots, the now-retained generated binding hash, input receipt equality, all raw status rows, unique identities, exact counts, exit status, one terminal suite event and metadata absence stability. It independently discovers each HTML's two resource scripts; there are no other resource loads in these tests. Configuration and the three ancestor metadata files are retained. The View Transition directory disables tests for `useDrawSnapshot`; these recorded headless runs actually executed them. Missing per-file metadata is not used as evidence of passing.

| Recorded run | Subtests | Harness | Exit |
| --- | --- | --- | --- |
| Original new WPT | 5 FAIL, 16 PASS | 1 OK | 1 |
| Candidate new WPT | 21 PASS | 1 OK | 0 |
| Candidate existing mutable WPT | 3 PASS | 1 OK | 0 |

The paired runs have 21 shared pinned paths; only `Document.cpp`, XUL and firefox differ. Their separately captured driver scripts differ only in the accepted phase string. All 20 common pins between candidate new and existing runs agree, including both binaries and generated binding. The actual Gecko selector wrapper/parser are supplemental static snapshots: they match the earlier scout's retained source hashes, but were not pinned before/after the runtime runs. This distinction prevents overstating the recorded closure.

Build and format exit 0. Lint exits 1 with zero errors and one ignored-HTML ESLint warning; it is not reported as a clean lint pass. Root's formatting receipt records unrelated changes restored; this review independently binds the final candidate bytes, without re-auditing the unrelated work. Binary hashes identify the tested binaries but do not prove a reproducible source-to-binary derivation. No second platform or independent browser run is claimed.

## Standalone scope and exact identities

Patch SHA-256: `c9e520ea2d2a991635f9af70531957e01635c1bdbd83e91607898466bc26c345`.

The patch has exactly two paths: the one startup hunk in `dom/base/Document.cpp`, and the 43-line WPT. No tools, artifacts, expected-failure metadata or other native changes are included. The checker independently applies the exact hunks in memory to retained branch-base and HEAD source bytes. Both reproduce the candidate Document hash and the WPT bytes exactly. Root's application receipts also record successful check/apply against revisions `32226ddf3a29d58a52291babebdff2a5a7ce46c6` and `11482ee213bf63c749b6d205c2c7591d783bdaa8`. This review did not independently query Git object identity, and no isolated worktree build was performed.

| Source | SHA-256 |
| --- | --- |
| Original and both retained base Document.cpp | `631dc71bf5e6c06c0e3996e2a0b3f04f6f09fdfb50fe4a1ac85d00b183c997af` |
| Candidate Document.cpp | `fee2870b6beabb47c2a67d118c74e914c0840ce0cb88151bb0216b8d84f88576` |
| New WPT | `1bf157cf9bf2c879a1c78e8a1ad227f6984fbb7f6e8faebd25c1e9bd89986b3c` |
| Generated ViewTransitionBinding.cpp | `d781bfe47958e35a8b4ab104693b2dec8af92c42ba753abd0f6ea114921b0f02` |
| Gecko wrapper.rs | `8be23a881af313800ebc9645834f88b37770faecc7ec0b35bd186f57471a9b38` |
| Gecko selector_parser.rs | `dceb3021db73a430adf50b6ea65047544fee726f809477be2f2ece57d75a6027` |

Every other reviewed source has an exact origin, retained copy and hash in `ORIGINS.json`; each runtime source additionally has its receipt pin. The candidate is independently reviewable and landable for this one defect, subject to normal project review.

## Formal companion proposal and boundaries

A useful next contract would connect three representations: input DOMString sequence, native atom vector and public backing ordered set. Prove that each processed input prefix yields its stable first-occurrence deduplication, with an auxiliary hashset containing exactly the vector's members. Then prove successful Add/Delete/Clear preserve uniqueness, ordered equality of public/native contents and membership agreement. Derive direct selector membership only under explicit active-document ownership, root-state and valid-custom-ident premises.

The source bridge must separately establish exact string-to-atom identity, owned atom lifetime while keys are weak, helper success, first-match vector deletion, and generated backing-set behavior. An abstract ordered-set proof alone cannot discharge those premises. No formal companion is supplied or accepted here.

Late type mutation invalidation, completed-transition interference, custom DocumentTimeline lifetime, equal-z capture order, cross-document initialization, scoped transitions, invalid/reserved identifiers, OOM/GC and general asynchronous lifecycle correctness remain separate. The scout's other leads and its hand-written finite model are retained as context, not promoted to verified defects or proofs by this review.

Recheck: `python3 -B artifacts/css-view-transition-types-independent-v1/check.py`; add `--live` to verify retained origins, current candidate sources and recorded absent metadata against the workspace. Binary hashing is intentionally omitted from live rechecks; recorded before/after binary identities remain authenticated as receipt data. Frozen checks fail on missing, added or changed artifact files.
