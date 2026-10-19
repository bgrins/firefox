void gfxTextRun::ClassifyAutoHyphenations(uint32_t aStart, Range aRange,
                                          nsTArray<HyphenType>& aHyphenBuffer,
                                          HyphenationState* aWordState) {
  MOZ_ASSERT(
      aRange.end - aStart <= aHyphenBuffer.Length() && aRange.start >= aStart,
      "Range out of bounds");
  MOZ_ASSERT(aWordState->mostRecentBoundary >= aStart,
             "Unexpected aMostRecentWordBoundary!!");

  uint32_t start =
      std::min<uint32_t>(aRange.start, aWordState->mostRecentBoundary);

  for (uint32_t i = start; i < aRange.end; ++i) {
    if (aHyphenBuffer[i - aStart] == HyphenType::Explicit &&
        !aWordState->hasExplicitHyphen) {
      aWordState->hasExplicitHyphen = true;
    }
    if (!aWordState->hasManualHyphen &&
        (aHyphenBuffer[i - aStart] == HyphenType::Soft ||
         aHyphenBuffer[i - aStart] == HyphenType::Explicit)) {
      aWordState->hasManualHyphen = true;
      // This is the first manual hyphen in the current word. We can only
      // know if the current word has a manual hyphen until now. So, we need
      // to run a sub loop to update the auto hyphens between the start of
      // the current word and this manual hyphen.
      if (aWordState->hasAutoHyphen) {
        for (uint32_t j = aWordState->mostRecentBoundary; j < i; j++) {
          if (aHyphenBuffer[j - aStart] ==
              HyphenType::AutoWithoutManualInSameWord) {
            aHyphenBuffer[j - aStart] = HyphenType::AutoWithManualInSameWord;
          }
        }
      }
    }
    if (aHyphenBuffer[i - aStart] == HyphenType::AutoWithoutManualInSameWord) {
      if (!aWordState->hasAutoHyphen) {
        aWordState->hasAutoHyphen = true;
      }
      if (aWordState->hasManualHyphen) {
        aHyphenBuffer[i - aStart] = HyphenType::AutoWithManualInSameWord;
      }
    }

    // If we're at the word boundary, clear/reset couple states.
    if (mCharacterGlyphs[i].CharIsSpace() || mCharacterGlyphs[i].CharIsTab() ||
        mCharacterGlyphs[i].CharIsNewline() ||
        // Since we will not have a boundary in the end of the string, let's
        // call the end of the string a special case for word boundary.
        i == GetLength() - 1) {
      // We can only get to know whether we should raise/clear an explicit
      // manual hyphen until we get to the end of a word, because this depends
      // on whether there exists at least one auto hyphen in the same word.
      if (!aWordState->hasAutoHyphen && aWordState->hasExplicitHyphen) {
        for (uint32_t j = aWordState->mostRecentBoundary; j <= i; j++) {
          if (aHyphenBuffer[j - aStart] == HyphenType::Explicit) {
            aHyphenBuffer[j - aStart] = HyphenType::None;
          }
        }
      }
      aWordState->mostRecentBoundary = i;
      aWordState->hasManualHyphen = false;
      aWordState->hasAutoHyphen = false;
      aWordState->hasExplicitHyphen = false;
    }
  }
}
