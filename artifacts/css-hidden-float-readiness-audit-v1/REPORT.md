# Skipped block lines and float ownership

SOURCE_BOUNDARY_IDENTIFIED; no native candidate or acceptance in this artifact. Root's compact18 diagnostic has two baseline float failures (root/leaf). The current main candidate campaign must establish whether they persist after line-child marking; this source analysis predicts they can.

## Actual graph edge missing from principal-root marking

A direct float's in-flow placeholder is a principal line child. The real float belongs to the block's FrameChildListID::Float list, not the placeholder's child lists. nsPlaceholderFrame derives directly from nsIFrame, stores mOutOfFlowFrame as a separate pointer, and exposes GetRealFrameForPlaceholder. MarkSubtreeDirty traverses ChildLists only; it does not call that placeholder accessor. Marking a placeholder can therefore leave the real float and its leaf clean.

The default nsIFrame::GetChildLists contributes owned absolute lists where applicable, not the placeholder's mOutOfFlowFrame. Merely marking every skipped line root, rather than just the first, does not bridge this edge. Conversely, if a marked ordinary block subtree actually owns a Float child list, the helper can reach that float through the owner. Do not claim that all float descendants are excluded everywhere.

## Source ordering and where a mark can help

ReflowLine returns before normal inline reflow when its first child is hidden by its in-flow parent. Normal BlockReflowState::AddFloat runs during placeholder line layout and calls FlowAndPlaceFloat; ReflowFloat later uses an already constructed float RI, ReflowBlock, SetSize and DidReflow. A dirty mark added only in ReflowFloat or AddFloat would not execute on a completely skipped line. A mark must occur on the skip/owner path before the geometry query sees the float as clean.

Do not rely on cached line floats. Actual nsBlockFrame::CheckFloats explicitly documents that hidden line skipping can omit floats from lines or leave stale line float caches. The owner's Float list is the more relevant storage source, but has continuation qualifications.

TrialReflow first DrainOverflowLines, then creates state/handles overflow containers, then DrainPushedFloats and ReflowPushedFloats, then line resize/dirty bookkeeping and ReflowDirtyLines. A bounded implementation direction for the ordinary own-hidden block fixture is an owner Float-list dirty pass in this trial flow, gated on that owner's content being skipped, rather than rescanning the entire float list for every skipped line. This is a design direction only: exact placement relative to pushed-float reflow, active forced-layout state, and multiple trial passes must be reviewed before coding. No unconditional visible-float traversal is recommended.

A placeholder-following alternative in the skip branch needs a descendant walk for placeholders nested in inline frames, must restrict to the appropriate float/owner, and must preserve lifetime/continuation invariants. Applying GetRealFrameForPlaceholder only to immediate line children is not a complete nested-inline solution. Globally changing MarkSubtreeDirty to follow every OOF pointer would broaden many unrelated callers and is not justified by these two fixtures.

## Continuation and dirty-barrier limits

DrainPushedFloats moves ownership across continuations. AddFloat can pull a first-in-flow back from another continuation; skipped lines bypass that operation. Current Float list does not automatically include every pushed/overflow continuation or external OOF provider. Already-IS_DIRTY float roots prune subtree traversal, so a clean leaf below an incoherent dirty barrier still requires a real history argument. These are existing subtree-model limitations, not resolved by naming the helper.

Pinned HEAD snapshots are the source baseline; working hashes are separately recorded because parent runtime owns live candidates. No source identity is inferred from indexed definition line numbers. Complete relevant local methods and Searchfox discovery are retained. This audit does not diagnose native locals from CSSOM failures or establish a release regression.

## Next discriminators

Wait for compact18 candidate outcomes. If float root/leaf still fail, retain that as a separate ownership-boundary result; do not weaken the block candidate's WPT. Before accepting a float repair, cover direct placeholder, placeholder nested in inline content, nested ordinary block owner, visible control, leaf-first/repeat queries, and a relevant pushed/fragmented ownership control. First confirm ordinary no-continuation path with the smallest targeted candidate; do not expand into whole float fragmentation verification.

No production/index/Git mutation, browser, build or compiler activity. Searchfox and read-only HEAD capture only; all output is in this artifact.
