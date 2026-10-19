enum class HyphenType : uint8_t {
    // Code in BreakAndMeasureText depends on the ordering of these values!
    None,
    Explicit,
    Soft,
    AutoWithManualInSameWord,
    AutoWithoutManualInSameWord
  };
