  // NOTE: I claim that this chunk of the algorithm (the looping part) needs to
  // run the loop at MOST NumItems() times.  This claim should hold up
  // because we'll freeze at least one item on each loop iteration, and once
  // we've run out of items to freeze, there's nothing left to do.  However,
  // in most cases, we'll break out of this loop long before we hit that many
  // iterations.
  for (uint32_t iterationCounter = 0; iterationCounter < NumItems();
       iterationCounter++) {
    // Set every not-yet-frozen item's used main size to its
    // flex base size, and subtract all the used main sizes from our
    // total amount of space to determine the 'available free space'
    // (positive or negative) to be distributed among our flexible items.
    AuCoord64 availableFreeSpace = spaceAvailableForFlexItemsContentBoxes;
    for (FlexItem& item : Items()) {
      if (!item.IsFrozen()) {
        item.SetMainSize(item.FlexBaseSize());
      }
      availableFreeSpace -= item.MainSize();
    }

    FLEX_LOGV("Available free space: %" PRId64 "; flex items should \"%s\"",
              availableFreeSpace.value, isUsingFlexGrow ? "grow" : "shrink");

    // The sign of our free space should agree with the type of flexing
    // (grow/shrink) that we're doing. Any disagreement should've made us use
    // the other type of flexing, or should've been resolved in
    // FreezeItemsEarly.
    //
    // Note: it's possible that an individual flex item has huge
    // margin/border/padding that makes either its
    // MarginBorderPaddingSizeInMainAxis() or OuterMainSize() negative due to
    // integer overflow. If that happens, the accumulated
    // mTotalOuterHypotheticalMainSize or mTotalItemMBP could be negative due to
    // that one item's negative (overflowed) size. Likewise, a huge main gap
    // size between flex items can also make our accumulated SumOfGaps()
    // negative. In these case, we throw up our hands and don't require
    // isUsingFlexGrow to agree with availableFreeSpace. Luckily, we won't get
    // stuck in the algorithm below, and just distribute the wrong
    // availableFreeSpace with the wrong grow/shrink factors.
    MOZ_ASSERT(!(mTotalOuterHypotheticalMainSize >= 0 && mTotalItemMBP >= 0 &&
                 totalItemMBPAndGaps >= 0) ||
                   (isUsingFlexGrow && availableFreeSpace >= 0) ||
                   (!isUsingFlexGrow && availableFreeSpace <= 0),
               "availableFreeSpace's sign should match isUsingFlexGrow");

    AuCoord64 totalViolation = 0;

    // If we have any free space available, give each flexible item a portion
    // of availableFreeSpace.
    if (availableFreeSpace != AuCoord64(0)) {
      // The first time we do this, we initialize origAvailableFreeSpace.
      if (!origAvailableFreeSpace) {
        origAvailableFreeSpace.emplace(availableFreeSpace);
      }

      // STRATEGY: On each item, we compute & store its "share" of the total
      // weight that we've seen so far:
      //   curWeight / weightSum
      //
      // Then, when we go to actually distribute the space (in the next loop),
      // we can simply walk backwards through the elements and give each item
      // its "share" multiplied by the remaining available space.
      //
      // SPECIAL CASE: If the sum of the weights is larger than the
      // maximum representable double (overflowing to infinity), then we can't
      // sensibly divide out proportional shares anymore. In that case, we
      // simply treat the flex item(s) with the largest weights as if
      // their weights were infinite (dwarfing all the others), and we
      // distribute all of the available space among them.
      double weightSum = 0.0;
      double flexFactorSum = 0.0;
      double largestWeight = 0.0;
      uint32_t numItemsWithLargestWeight = 0;

      // Since this loop only operates on unfrozen flex items, we can break as
      // soon as we have seen all of them.
      uint32_t numUnfrozenItemsToBeSeen = NumItems() - mNumFrozenItems;
      for (FlexItem& item : Items()) {
        if (numUnfrozenItemsToBeSeen == 0) {
          break;
        }

        if (!item.IsFrozen()) {
          numUnfrozenItemsToBeSeen--;

          const double curWeight = item.GetWeight(isUsingFlexGrow);
          const double curFlexFactor = item.GetFlexFactor(isUsingFlexGrow);
          MOZ_ASSERT(curWeight >= 0.0, "weights are non-negative");
          MOZ_ASSERT(curFlexFactor >= 0.0, "flex factors are non-negative");

          weightSum += curWeight;
          flexFactorSum += curFlexFactor;

          if (std::isfinite(weightSum)) {
            if (curWeight == 0.0) {
              item.SetShareOfWeightSoFar(0.0);
            } else {
              item.SetShareOfWeightSoFar(curWeight / weightSum);
            }
          }  // else, the sum of weights overflows to infinity, in which
             // case we don't bother with "SetShareOfWeightSoFar" since
             // we know we won't use it. (instead, we'll just give every
             // item with the largest weight an equal share of space.)

          // Update our largest-weight tracking vars
          if (curWeight > largestWeight) {
            largestWeight = curWeight;
            numItemsWithLargestWeight = 1;
          } else if (curWeight == largestWeight) {
            numItemsWithLargestWeight++;
          }
        }
      }

      MOZ_ASSERT(numUnfrozenItemsToBeSeen == 0, "miscounted frozen items?");

      if (weightSum != 0.0) {
        MOZ_ASSERT(flexFactorSum != 0.0,
                   "flex factor sum can't be 0, if a weighted sum "
                   "of its components (weightSum) is nonzero");
        if (flexFactorSum < 1.0) {
          // Our unfrozen flex items don't want all of the original free space!
          // (Their flex factors add up to something less than 1.)
          // Hence, make sure we don't distribute any more than the portion of
          // our original free space that these items actually want.
          auto totalDesiredPortionOfOrigFreeSpace =
              AuCoord64::FromRound(*origAvailableFreeSpace * flexFactorSum);

          // Clamp availableFreeSpace to be no larger than that ^^.
          // (using min or max, depending on sign).
          // This should not change the sign of availableFreeSpace (except
          // possibly by setting it to 0), as enforced by this assertion:
          NS_ASSERTION(totalDesiredPortionOfOrigFreeSpace == AuCoord64(0) ||
                           ((totalDesiredPortionOfOrigFreeSpace > 0) ==
                            (availableFreeSpace > 0)),
                       "When we reduce available free space for flex "
                       "factors < 1, we shouldn't change the sign of the "
                       "free space...");

          if (availableFreeSpace > 0) {
            availableFreeSpace = std::min(availableFreeSpace,
                                          totalDesiredPortionOfOrigFreeSpace);
          } else {
            availableFreeSpace = std::max(availableFreeSpace,
                                          totalDesiredPortionOfOrigFreeSpace);
          }
        }

        FLEX_LOGV("Distributing available space:");
        // Since this loop only operates on unfrozen flex items, we can break as
        // soon as we have seen all of them.
        numUnfrozenItemsToBeSeen = NumItems() - mNumFrozenItems;

        // NOTE: It's important that we traverse our items in *reverse* order
        // here, for correct width distribution according to the items'
        // "ShareOfWeightSoFar" progressively-calculated values.
        uint32_t itemIndex = NumItems();
        for (FlexItem& item : Reversed(Items())) {
          if (numUnfrozenItemsToBeSeen == 0) {
            break;
          }
          --itemIndex;

          if (!item.IsFrozen()) {
            numUnfrozenItemsToBeSeen--;

            // To avoid rounding issues, we compute the change in size for this
            // item, and then subtract it from the remaining available space.
            AuCoord64 sizeDelta = 0;
            if (std::isfinite(weightSum)) {
              double myShareOfRemainingSpace = item.ShareOfWeightSoFar();

              MOZ_ASSERT(myShareOfRemainingSpace >= 0.0 &&
                             myShareOfRemainingSpace <= 1.0,
                         "my share should be nonnegative fractional amount");

              if (myShareOfRemainingSpace == 1.0) {
                // (We special-case 1.0 to avoid float error from converting
                // availableFreeSpace from integer*1.0 --> double --> integer)
                sizeDelta = availableFreeSpace;
              } else if (myShareOfRemainingSpace > 0.0) {
                sizeDelta = AuCoord64::FromRound(availableFreeSpace *
                                                 myShareOfRemainingSpace);
              }
            } else if (item.GetWeight(isUsingFlexGrow) == largestWeight) {
              // Total flexibility is infinite, so we're just distributing
              // the available space equally among the items that are tied for
              // having the largest weight (and this is one of those items).
              sizeDelta = AuCoord64::FromRound(
                  availableFreeSpace / double(numItemsWithLargestWeight));
              numItemsWithLargestWeight--;
            }

            availableFreeSpace -= sizeDelta;

            // Preserve cancellation before narrowing, without hiding min/max
            // violations by clamping to the preferred coordinate range.
            const AuCoord64 mainSize = AuCoord64(item.MainSize()) + sizeDelta;
            item.SetMainSize(nscoord(
                std::clamp<int64_t>(mainSize.value, INT32_MIN, INT32_MAX)));
            // Retain the violation contribution lost when narrowing the target.
            totalViolation += AuCoord64(item.MainSize()) - mainSize;
            if (mainSize < AuCoord64(INT32_MIN)) {
              item.SetHadMinViolation();
            } else if (mainSize > AuCoord64(INT32_MAX)) {
              item.SetHadMaxViolation();
            }
            if (aLineInfo) {
              aLineInfo->mItems[itemIndex].mMainDeltaSize = sizeDelta.value;
            }
            FLEX_LOGV("  Flex item %p receives %" PRId64 ", for a total of %d",
                      item.Frame(), sizeDelta.value, item.MainSize());
          }
        }

        MOZ_ASSERT(numUnfrozenItemsToBeSeen == 0, "miscounted frozen items?");
      }
    }

    // Fix min/max violations:
    FLEX_LOGV("Checking for violations:");

    // Since this loop only operates on unfrozen flex items, we can break as
    // soon as we have seen all of them.
    uint32_t numUnfrozenItemsToBeSeen = NumItems() - mNumFrozenItems;
    for (FlexItem& item : Items()) {
      if (numUnfrozenItemsToBeSeen == 0) {
        break;
      }

      if (!item.IsFrozen()) {
        numUnfrozenItemsToBeSeen--;

        if (item.MainSize() < item.MainMinSize()) {
          // min violation
          totalViolation +=
              AuCoord64(item.MainMinSize()) - AuCoord64(item.MainSize());
          item.SetMainSize(item.MainMinSize());
          item.SetHadMinViolation();
        } else if (item.MainSize() > item.MainMaxSize()) {
          // max violation
          totalViolation +=
              AuCoord64(item.MainMaxSize()) - AuCoord64(item.MainSize());
          item.SetMainSize(item.MainMaxSize());
          item.SetHadMaxViolation();
        }
      }
    }

    MOZ_ASSERT(numUnfrozenItemsToBeSeen == 0, "miscounted frozen items?");

    FreezeOrRestoreEachFlexibleSize(totalViolation,
                                    iterationCounter + 1 == NumItems());

    FLEX_LOGV("Total violation: %" PRId64, totalViolation.value);

