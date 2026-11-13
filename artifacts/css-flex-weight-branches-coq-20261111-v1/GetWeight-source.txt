  double GetWeight(bool aIsUsingFlexGrow) {
    MOZ_ASSERT(!IsFrozen(), "shouldn't need weight after item is frozen");

    if (aIsUsingFlexGrow) {
      return mFlexGrow;
    }

    // We're using flex-shrink --> return mFlexShrink * mFlexBaseSize
    if (mFlexBaseSize == 0) {
      // Special-case for mFlexBaseSize == 0 -- we have no room to shrink, so
      // regardless of mFlexShrink, we should just return 0.
      // (This is really a special-case for when mFlexShrink is infinity, to
      // avoid performing mFlexShrink * mFlexBaseSize = inf * 0 = undefined.)
      return 0.0f;
    }
    return double(mFlexShrink) * mFlexBaseSize;
  }
