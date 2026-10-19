struct HyphenationState {
    uint32_t mostRecentBoundary = 0;
    bool hasManualHyphen = false;
    bool hasExplicitHyphen = false;
    bool hasAutoHyphen = false;
  };
