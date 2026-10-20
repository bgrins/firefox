# Independent review: selected flex-property destruction

Verdict: **ACCEPT_SELECTED_MODEL_WITH_EXPLICIT_NATIVE_ADMISSIONS**.

The selected mathematical contract is soundly bounded. It does not close native primary-bit coherence across the destruction callback sequence, global exclusive ownership, descriptor/payload decoding, or captured-cache lifetime. No native bug, unsafe reentrant caller, or complete allocation F1–F16/F11/F12 acceptance follows from this component.

## Authenticated target and work performed

The reviewed producer is css-primary-destruction-callback-proof-v1, externally pinned FILES6af2a8ca93ea6129c2c37384e373bd1a9e65aa50ac0f8aa16dfbca4e99dfdfc5. All27 payloads and their closed regular-file roster were authenticated;23 retained source-body slices were independently matched to their full-source bytes and body hashes. A manifest-only producer copy is retained in the review capsule.

I read Deletion, PropertyPhase, Witnesses, the checker/extractor, source descriptors/macros and destructor/member/array paths. The parent supplied an already successful full51-audit/4-negative/23-binding replay, so I did not repeat that controller or its15 guard campaign. I freshly compiled the three substantive producer modules as dependencies of four independent kernel boundary witnesses. All four witnesses compile and audit with only standard propext. No native compiler, shared build, browser, Git or production source changes were used.

The first review runner wrongly expected these four audits to use zero axioms; the theorems compiled successfully and reported propext. That harness assertion, complete logs and original capsule remain under development. The corrected runner requires the exact observed propext-only output. No theorem was weakened to fix the harness.

## Why the selected contract is acceptable

| Obligation | Review finding |
| --- | --- |
| Actual modeled deletion rather than an untouched ownership product | Heap has frame, content and role-tagged allocation cells in one address space. freeOne reads the cell before erasing it. Frame/content preservation is derived from those cases, not stored in an automatically unchanged separate component. |
| Completeness without assuming deletion succeeds | freeMany_complete uses initial typed allocated releases and address uniqueness. phase_complete derives readiness after detaching the live table, then calls that completeness result. |
| Independent final-state description | referenceErase uses address membership; freeMany_reference proves the stateful recursion agrees after successful execution. It is a specification of the final deletion footprint, not independent evidence that the decoded native footprint is complete. |
| Detach before callbacks | removeAll replaces the live frame table before processing its saved plan. Retained FrameProperties::RemoveAll moves mProperties before dispatch. The ordinary non-auto move takes the old header and replaces it with EmptyHdr; the detached table buffer is freed last. |
| Preserve primary lookup/coherence in the selected phase | Role-valid deletion cannot erase modeled content/frame cells. Initial Coherent is an explicit premise; detach_primary, primary_preserved and phase_contract derive the resulting relation. No proof that native setter/callback history establishes that premise is supplied. |
| Distinguish raw frame references from owned allocations | footprint ignores frames in LinePayload; it deletes item/line buffers and scalar roots. Repeated and dangling raw references do not become ownership edges. This matches the retained raw nsIFrame* member shape subject to the stated implicit-destructor/type-trait contracts. |
| Distinguish owner survival from cache survival | The successful fixture preserves the owner and primary pointer while erasing cache30. That directly prevents interpreting owner coherence as captured-cache validity. |
| Bound repeat-cleanup reasoning | immediate_repeat_empty is immediate only. The intervening-addition witness correctly refutes extending it through arbitrary later callbacks. |

The source chain through NotifyDestroyingFrame and RemoveAllProperties is genuinely present. DeleteValue is a scalar delete behind the selected ordinary destructor descriptors, not a with-frame callback. Shared data owns a line array, each line owns an item array, and the selected scalar cache/fragment roots hold inline numeric records. Destruction order in the modeled release list is consistent with these selected owning fields: item buffers, line buffer, shared root, then detached property storage.

This is still a manual conditional source relation. Role checking is a model admission check, not a native runtime guard. The native delete operation does not reject a wrong role by returning none. The retained nsTArray providers are indexed discovery inputs, explicitly not established as the same native revision as the frozen frame/flex source. The lexical extractor is not a C++ parser or a translation proof. Implicit member destructors, specialized traits, allocator pairing and runtime descriptor identity remain unproved.

## Concrete boundary A: incomplete nonempty-array encoding

The producer's successful sampleTable includes the line payload ⟨none,[0]⟩. Its raw-item list is nonempty but its item-buffer address is absent. The retained actual FlexLine::mItems is ordinary nsTArray<FlexItem>; unlike an inline AutoTArray, a nonempty ordinary array needs owned dynamic storage. A static empty header cannot contain one item.

Two independent kernel witnesses confirm both that this entry occurs in the fixture and that a selected table with such an omitted nonempty buffer is accepted by removeAll. Therefore allocated role-correct releases plus uniqueness are sufficient for the mathematical executor, but do not establish completeness of a native owned-buffer decoding. No theorem is false: footprint only erases the addresses supplied to it.

The producer acknowledged that no sealed invariant excludes this encoding. The fixture must be described as an abstract model witness, not a fully decoded native fixture. For a future native relation, require nonempty ordinary item/line/property arrays to decode an owned buffer; preserve the valid opposite case of an empty array retaining allocated capacity. Replace this fixture entry with a fresh correctly allocated buffer if using the complete fixture as a native representation demonstration. The broad optional-buffer wording about inline/nonowned storage does not itself justify that case for these particular ordinary array members.

## Concrete boundary B: local uniqueness is not global ownership

The selected footprint's uniqueness says nothing about other live frames' installed property tables. My second fixture has two distinct live owners, distinct allocated property-table buffers90/91, and a shared scalar cache root30. Each owner's selected plan is individually unique and role-correct. Cleaning the first owner succeeds, frees30, and leaves the second owner live with its original table referring to30. Its primary-bit and content-pointer read still agree. A subsequent cleanup of that second table is rejected by the model because30 is already absent.

Two independent kernel witnesses establish those observations. The producer acknowledged that no global-exclusive-ownership invariant was intended in the sealed model. This is an additional required native decoder/installation/generation contract, not an observed C++ aliasing bug. Preserving a frame cell and primary lookup is weaker than preserving every pointer reachable from its properties.

The model uses abstract base-address identities, not byte ranges, interior pointers, pointer provenance, allocator generations or reuse. Thus even address uniqueness within a plan must not be presented as full native nonoverlap/lifetime safety. Actual property installation and generation identity are the next useful joins; simply adding a callback-preserves-coherence assumption would not supply them.

## Remaining obligations and acceptance boundary

The accepted result covers the mathematical selected cleanup phase, conditional on its representation/readiness premises, and the retained source's ownership shape. It does not include arbitrary descriptors in a real frame table, nullable/wrongly decoded native payloads, all implicit/specialized destructors, or complete allocator behavior. Native callbacks before/between/after the two primary-bit reads, including SVG/virtual reflow, reference-count releases, event cleanup and ClearFrameRefs, remain outside the executor. Address reuse and captured-cache revalidation are not modeled.

Keep the producer's complete lifecycle/native projection open. No scope reduction or theorem-unsoundness claim is needed: the two boundary witnesses make existing admissions precise. Future closure should bind actual descriptor-to-payload-to-buffer decoding, enforce globally exclusive live ownership where required, and relate property generations to actual capture/callback/use paths.

## Replay and cleanup

The review capsule is closed. Run:

```
python3 -I -S -B capsule/replay.py --files-sha256 e968c0a408a2024f50b4c92b8c172365e67a1d790e3de85d0e777f54cd28342f /tmp/NEW-UNUSED-OUTPUT
```

This authenticates its own inputs and the producer roster, checks the pinned Lean executable, compiles the three producer modules plus Challenges, and verifies exactly four propext-only audits. Installed Lean runtime/Std remains a toolchain admission. Temporary olean products are removed automatically, including on the retained first harness failure. Final run exit0; no compiler sessions remain. Parent timing hold is respected after this handoff.
