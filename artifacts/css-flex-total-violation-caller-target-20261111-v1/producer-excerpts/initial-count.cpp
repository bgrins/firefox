  // Stores this line's flex items.
  nsTArray<FlexItem> mItems;

  // Number of *frozen* FlexItems in this line, based on FlexItem::IsFrozen().
  // Mostly used for optimization purposes, e.g. to bail out early from loops
  // when we can tell they have nothing left to do.
  uint32_t mNumFrozenItems = 0;
  // Number of items that are not collapsed.
  uint32_t mNumNonCollapsedItems = 0;
