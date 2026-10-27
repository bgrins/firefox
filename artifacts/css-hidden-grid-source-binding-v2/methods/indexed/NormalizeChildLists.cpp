void nsContainerFrame::NormalizeChildLists() {
  MOZ_ASSERT(IsFlexOrGridContainer(),
             "Only Flex / Grid containers can call this!");

  // Note: the following description uses grid container as an example. Flex
  // container is similar.
  //
  // First we gather child frames we should include in our reflow/placement,
  // i.e. overflowed children from our prev-in-flow, and pushed first-in-flow
  // children (that might now fit). It's important to note that these children
  // can be in arbitrary order vis-a-vis the current children in our lists.
  // E.g. grid items in the document order: A, B, C may be placed in the rows
  // 3, 2, 1.  Assume each row goes in a separate grid container fragment,
  // and we reflow the second fragment.  Now if C (in fragment 1) overflows,
  // we can't just prepend it to our mFrames like we usually do because that
  // would violate the document order invariant that other code depends on.
  // Similarly if we pull up child A (from fragment 3) we can't just append
  // that for the same reason.  Instead, we must sort these children into
  // our child lists.  (The sorting is trivial given that both lists are
  // already fully sorted individually - it's just a merge.)
  //
  // The invariants that we maintain are that each grid container child list
  // is sorted in the normal document order at all times, but that children
  // in different grid container continuations may be in arbitrary order.

  const auto didPushItemsBit = IsFlexContainerFrame()
                                   ? NS_STATE_FLEX_DID_PUSH_ITEMS
                                   : NS_STATE_GRID_DID_PUSH_ITEMS;
  const auto hasChildNifBit = IsFlexContainerFrame()
                                  ? NS_STATE_FLEX_HAS_CHILD_NIFS
                                  : NS_STATE_GRID_HAS_CHILD_NIFS;

  auto* prevInFlow = static_cast<nsContainerFrame*>(GetPrevInFlow());
  // Merge overflow frames from our prev-in-flow into our principal child list.
  if (prevInFlow) {
    AutoFrameListPtr overflow(prevInFlow->StealOverflowFrames());
    if (overflow) {
      ReparentFrames(*overflow, prevInFlow, this);
      MergeSortedFrameLists(mFrames, *overflow, GetContent());

      // Move trailing next-in-flows into our overflow list.
      nsFrameList continuations;
      for (nsIFrame* f = mFrames.FirstChild(); f;) {
        nsIFrame* next = f->GetNextSibling();
        nsIFrame* pif = f->GetPrevInFlow();
        if (pif && pif->GetParent() == this) {
          mFrames.RemoveFrame(f);
          continuations.AppendFrame(nullptr, f);
        }
        f = next;
      }
      MergeSortedOverflow(continuations);

      // Move prev-in-flow's excess overflow containers list into our own
      // overflow containers list. If we already have an excess overflow
      // containers list, any child in that list which doesn't have a
      // prev-in-flow in this frame is also merged into our overflow container
      // list.
      nsFrameList* overflowContainers =
          DrainExcessOverflowContainersList(MergeSortedFrameListsFor);

      // Move trailing OC next-in-flows into our excess overflow containers
      // list.
      if (overflowContainers) {
        nsFrameList moveToEOC;
        for (nsIFrame* f = overflowContainers->FirstChild(); f;) {
          nsIFrame* next = f->GetNextSibling();
          nsIFrame* pif = f->GetPrevInFlow();
          if (pif && pif->GetParent() == this) {
            overflowContainers->RemoveFrame(f);
            moveToEOC.AppendFrame(nullptr, f);
          }
          f = next;
        }
        if (overflowContainers->IsEmpty()) {
          DestroyOverflowContainers();
        }
        MergeSortedExcessOverflowContainers(moveToEOC);
      }
    }
  }

  // For each item in aItems, pull up its next-in-flow (if any), and reparent it
  // to our next-in-flow, unless its parent is already ourselves or our
  // next-in-flow (to avoid leaving a hole there).
  auto PullItemsNextInFlow = [this](const nsFrameList& aItems) {
    auto* firstNIF = static_cast<nsContainerFrame*>(GetNextInFlow());
    if (!firstNIF) {
      return;
    }
    nsFrameList childNIFs;
    nsFrameList childOCNIFs;
    for (auto* child : aItems) {
      if (auto* childNIF = child->GetNextInFlow()) {
        if (auto* parent = childNIF->GetParent();
            parent != this && parent != firstNIF) {
          parent->StealFrame(childNIF);
          ReparentFrame(childNIF, parent, firstNIF);
          if (childNIF->HasAnyStateBits(NS_FRAME_IS_OVERFLOW_CONTAINER)) {
            childOCNIFs.AppendFrame(nullptr, childNIF);
          } else {
            childNIFs.AppendFrame(nullptr, childNIF);
          }
        }
      }
    }
    // Merge aItems' NIFs into our NIF's respective overflow child lists.
    firstNIF->MergeSortedOverflow(childNIFs);
    firstNIF->MergeSortedExcessOverflowContainers(childOCNIFs);
  };

  // Merge our own overflow frames into our principal child list,
  // except those that are a next-in-flow for one of our items.
  DebugOnly<bool> foundOwnPushedChild = false;
  {
    nsFrameList* ourOverflow = GetOverflowFrames();
    if (ourOverflow) {
      nsFrameList items;
      for (nsIFrame* f = ourOverflow->FirstChild(); f;) {
        nsIFrame* next = f->GetNextSibling();
        nsIFrame* pif = f->GetPrevInFlow();
        if (!pif || pif->GetParent() != this) {
          MOZ_ASSERT(f->GetParent() == this);
          ourOverflow->RemoveFrame(f);
          items.AppendFrame(nullptr, f);
          if (!pif) {
            foundOwnPushedChild = true;
          }
        }
        f = next;
      }

      if (ourOverflow->IsEmpty()) {
        DestroyOverflowList();
        ourOverflow = nullptr;
      }
      if (items.NotEmpty()) {
        PullItemsNextInFlow(items);
      }
      MergeSortedFrameLists(mFrames, items, GetContent());
    }
  }

  // Push any child next-in-flows in our principal list to OverflowList.
  if (HasAnyStateBits(hasChildNifBit)) {
    nsFrameList framesToPush;
    nsIFrame* firstChild = mFrames.FirstChild();
    // Note that we potentially modify our mFrames list as we go.
    for (auto* child = firstChild; child; child = child->GetNextSibling()) {
      if (auto* childNIF = child->GetNextInFlow()) {
        if (childNIF->GetParent() == this) {
          for (auto* c = child->GetNextSibling(); c; c = c->GetNextSibling()) {
            if (c == childNIF) {
              // child's next-in-flow is in our principal child list, push it.
              mFrames.RemoveFrame(childNIF);
              framesToPush.AppendFrame(nullptr, childNIF);
              break;
            }
          }
        }
      }
    }
    if (!framesToPush.IsEmpty()) {
      MergeSortedOverflow(framesToPush);
    }
    RemoveStateBits(hasChildNifBit);
  }

  // Pull up any first-in-flow children we might have pushed.
  if (HasAnyStateBits(didPushItemsBit)) {
    RemoveStateBits(didPushItemsBit);
    nsFrameList items;
    auto* nif = static_cast<nsContainerFrame*>(GetNextInFlow());
    DebugOnly<bool> nifNeedPushedItem = false;
    while (nif) {
      nsFrameList nifItems;
      for (nsIFrame* nifChild = nif->PrincipalChildList().FirstChild();
           nifChild;) {
        nsIFrame* next = nifChild->GetNextSibling();
        if (!nifChild->GetPrevInFlow()) {
          nif->StealFrame(nifChild);
          ReparentFrame(nifChild, nif, this);
          nifItems.AppendFrame(nullptr, nifChild);
          nifNeedPushedItem = false;
        }
        nifChild = next;
      }
      MergeSortedFrameLists(items, nifItems, GetContent());

      if (!nif->HasAnyStateBits(didPushItemsBit)) {
        MOZ_ASSERT(!nifNeedPushedItem || mDidPushItemsBitMayLie,
                   "The state bit stored in didPushItemsBit lied!");
        break;
      }
      nifNeedPushedItem = true;

      for (nsIFrame* nifChild =
               nif->GetChildList(FrameChildListID::Overflow).FirstChild();
           nifChild;) {
        nsIFrame* next = nifChild->GetNextSibling();
        if (!nifChild->GetPrevInFlow()) {
          nif->StealFrame(nifChild);
          ReparentFrame(nifChild, nif, this);
          nifItems.AppendFrame(nullptr, nifChild);
          nifNeedPushedItem = false;
        }
        nifChild = next;
      }
      MergeSortedFrameLists(items, nifItems, GetContent());

      nif->RemoveStateBits(didPushItemsBit);
      nif = static_cast<nsContainerFrame*>(nif->GetNextInFlow());
      MOZ_ASSERT(nif || !nifNeedPushedItem || mDidPushItemsBitMayLie,
                 "The state bit stored in didPushItemsBit lied!");
    }

    if (!items.IsEmpty()) {
      PullItemsNextInFlow(items);
    }

    MOZ_ASSERT(
        foundOwnPushedChild || !items.IsEmpty() || mDidPushItemsBitMayLie,
        "The state bit stored in didPushItemsBit lied!");
    MergeSortedFrameLists(mFrames, items, GetContent());
  }
}
