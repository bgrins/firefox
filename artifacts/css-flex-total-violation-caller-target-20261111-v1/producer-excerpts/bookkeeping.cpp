  nsTArray<FlexItem>& Items() { return mItems; }
  const nsTArray<FlexItem>& Items() const { return mItems; }

  // Adds the last flex item's hypothetical outer main-size and
  // margin/border/padding to our totals. This should be called exactly once for
  // each flex item, after we've determined that this line is the correct home
  // for that item.
  void AddLastItemToMainSizeTotals() {
    const FlexItem& lastItem = Items().LastElement();

    // Update our various bookkeeping member-vars:
    if (lastItem.IsFrozen()) {
      mNumFrozenItems++;
    }

    // If the item added was not the first non-collapsed item in the line,
    // we add in any gap space as needed.
    if (!lastItem.IsStrut()) {
      if (mNumNonCollapsedItems) {
        mTotalOuterHypotheticalMainSize += mMainGapSize;
      }
      mNumNonCollapsedItems++;
    }

    mTotalItemMBP += lastItem.MarginBorderPaddingSizeInMainAxis();
    mTotalOuterHypotheticalMainSize += lastItem.OuterMainSize();
  }
