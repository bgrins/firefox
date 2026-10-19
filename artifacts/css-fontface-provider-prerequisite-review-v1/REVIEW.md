# FontFace provider worker-rebuild prerequisite

## Verdict

**Behavioral independence is not established and the worker rebuild is a substantive source prerequisite.** V2 native acceptance remains pending. The previous narrowed risk review is preserved. Root reports 68 current matrix passes and one improved style/family regression with the other 26 tuples unchanged; those runs include repair #50. This capsule does not invent a reverse-#50 runtime result.

## Exact source basis

The authenticated provider candidate FREEZE is b8f0ccd0bf557b5abc7611cd328fdb852be45ca4a4fc4ee6a01fc98d08f3c4e7; integration-v2 FREEZE is a5fd5a73cb71da6e176fbc20b1ba5992d847b050795cdbd70dd35910de9b39ac. Complete original/candidate bytes for its 16 native paths are retained. No provider hunk edits FontFaceSetWorkerImpl.cpp. The integration context is byte-identical to #50's worker candidate.

Repair #50 is native commit 32ba35ffb9a17f5e91df5c56f01a06a452dfdc8a. Its pre-fix worker file is 506ddf121815b18c6f082d4e2074ddceebbfcb5601099bdc51aabcd12a8b9158; its fixed file is a631561784f71dc3a81941e9737fae8c5d40c2e0920600347774a5a4b218cd33. The exact difference is the four-line family detach loop before reinsertion. Existing standalone evidence records apply/reverse at 7962023938cab2f91384bf1bfff9a0cf43eecf04 and 32226ddf3a29d58a52291babebdff2a5a7ce46c6, not an isolated build.

Parent identifies upstream baseline as 976279. This agent has not read Git and does not infer a full commit ID or whole-tree correspondence from that abbreviation. Fresh replay here proves exact patch application/reversal against the retained 17-file baseline (16 provider originals plus pre-#50 worker). Root must additionally bind those files to the exact upstream tree and check the eventual native/WPT patch there. Source applicability alone is not behavioral independence.

## Complete relevant transition

1. FontFaceImpl::SetDescriptor parses a changed descriptor into a detached rule when a provider exists. FontFaceSetImpl::UpdateFontFaceDescriptorOnMainThread creates a fresh wrapper when the old entry is loaded and initializes a new provider from it.
2. FontFaceImpl::SetUserFontEntry removes the face from the old Entry owner list and attaches it to the new entry. Entry::RemoveFontFace and CheckUserFontSetLocked update owner/set references; they do not remove old entries from family lists or clear their loaded platform provider.
3. DescriptorUpdated marks every current membership dirty through NonRuleFontFaceChanged. It does not delete the face from its set.
4. Without #50, worker FlushUserFontSet reinserts current faces into existing families. InsertNonRuleFontFace uses the new descriptor family and new wrapper. gfxUserFontFamily::AddFontEntry appends, with only a last-element pointer shortcut. A distinct old wrapper remains strongly retained by the old family. Pruning removes only empty families. GetPlatformFontEntry continues to return the old loaded provider.
5. With #50, all family entry lists are cleared before current membership is reinserted. Old wrappers vanish from matching unless another current member still requires one. This is exactly the invariant needed for descriptor replacement as well as removal.

The indexed AddFontEntry and GetPlatformFontEntry lookup matched these retained candidate definitions. Indexed source is discovery only; the retained local files govern this conclusion.

## Descriptor-only witnesses and limits

The proposed test has four cases per global, eight overall: buffer/URL crossed with family rename/unicodeRange narrowing. No delete or clear occurs before the observations. Both faces remain members; cleanup deletes only after the test. An independent 75% Ahem fallback calibrates 60px; original Ahem XXXX at 20px calibrates 80px. Family rename must make the old family use fallback while the new family still produces 80px. Narrowing coverage to Y must make X use fallback. Existing and fresh contexts are checked.

Source prediction: provider v2 without #50 retains obsolete worker entries, producing 80px where 60px is required in four worker cases; the four window cases should pass. With #50 all eight should pass. **The probe is unexecuted in this capsule.** Native matching, font resources and browser behavior remain runtime obligations. No claim is made that every existing sizeAdjust-only row requires the support: newest-entry matching can hide retained older entries. The existing deletion/peer-selection rows independently depend on membership cleanup.

The oracle follows current descriptor values and current membership, not a new removal requirement. FontFace descriptors feed matching and valid setter values replace the attribute; unicode-range limits coverage. See [CSS Font Loading §2](https://drafts.csswg.org/css-font-loading/#fontface-interface) and [CSS Fonts unicode-range](https://drafts.csswg.org/css-fonts/#descdef-font-face-unicode-range), freshly read for this review. These imply retiring the prior family/coverage from matching when no other current face supplies it.

## Principled packaging resolution

A standalone provider repair against upstream can legitimately include the same four-line rebuild support. It is necessary shared infrastructure for publishing fresh descriptor wrappers, not unrelated removal code smuggled into the patch. Preserve attribution to #50 and explain this overlapping prerequisite explicitly. The source patch `standalone-native-with-rebuild.patch` contains exact v2 provider native changes plus that exact support. It is a draft native-only application artifact, not a tested upstream commit or complete submission.

Recommended root packaging:

- Keep #50 as its existing standalone removal code+WPT fix.
- Retain a separately applicable upstream provider code+WPT patch including the rebuild hunk, the exact reviewed 68-case tests, and the descriptor-only witness if validated. Root owns HEAD/add-file treatment and whole-tree applicability.
- On the current stack, record that the shared hunk is already satisfied by #50 and therefore omitted from the integration commit. A side-branch standalone patch may demonstrate independent application with shared support; the stacked commit itself must not be described as independent of #50.
- Validate source equivalence of standalone final state and stacked final state. Run the isolated no-support descriptor witness to establish the dependency, then validate the support-containing candidate. Do not silently delete affected tests to claim independence.

A custom setter-only removal mechanism is not recommended merely to change the stack shape: shared peers, repeated entries, multiple sets and retained family objects require the same current-membership invariant. Duplication of the small necessary hunk across alternative upstream patches is honest when only one copy is applied in any actual tree. If the user's independence rule forbids overlapping shared support too, this requires an explicit packaging decision, not an unqualified acceptance.

## Remaining gates

Exact upstream native/WPT applicability, controlled reverse-#50 runtime, standalone-source binary pairing, cross-platform compile/runtime and the earlier timing/ownership limitations remain open. No full provider/heap correctness or whole FontFace formal proof is claimed. This review does not reopen unrelated sealed formal scopes.
