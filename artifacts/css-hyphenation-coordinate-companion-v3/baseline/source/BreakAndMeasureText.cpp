uint32_t gfxTextRun::BreakAndMeasureText(
    uint32_t aStart, uint32_t aMaxLength, bool aLineBreakBefore,
    gfxFloat aWidth, const PropertyProvider& aProvider,
    SuppressBreak aSuppressBreak, gfxFont::BoundingBoxType aBoundingBoxType,
    DrawTarget* aRefDrawTarget, bool aCanWordWrap, bool aCanWhitespaceWrap,
    bool aIsBreakSpaces,
    // output params:
    TrimmableWS* aOutTrimmableWhitespace, Metrics& aOutMetrics,
    bool& aOutUsedHyphenation, uint32_t& aOutLastBreak,
    gfxBreakPriority& aBreakPriority) {
  aMaxLength = std::min(aMaxLength, GetLength() - aStart);

  NS_ASSERTION(aStart + aMaxLength <= GetLength(), "Substring out of range");

  constexpr uint32_t kMeasurementBufferSize = 100;
  Range bufferRange(aStart,
                    aStart + std::min(aMaxLength, kMeasurementBufferSize));
  PropertyProvider::Spacing spacingBuffer[kMeasurementBufferSize];
  bool haveSpacing = !!(mFlags & gfx::ShapedTextFlags::TEXT_ENABLE_SPACING);
  if (haveSpacing) {
    GetAdjustedSpacing(this, bufferRange, aProvider, spacingBuffer);
  }
  AutoTArray<HyphenType, 4096> hyphenBuffer;
  HyphenationState wordState;
  wordState.mostRecentBoundary = aStart;
  // GetHyphensOption() is a virtual call returning a value that is constant
  // for the whole measurement, so fetch it once instead of on every use.
  const StyleHyphens hyphensOption = aProvider.GetHyphensOption();
  // Hyphenation data is only consulted in the break-detection block below,
  // which is skipped entirely when all breaks are suppressed. In that case we
  // avoid fetching and classifying hyphenation data (which can involve per-word
  // dictionary lookups) since it would never be used.
  bool haveHyphenation =
      aSuppressBreak != eSuppressAllBreaks &&
      (hyphensOption == StyleHyphens::Auto ||
       (hyphensOption == StyleHyphens::Manual &&
        !!(mFlags & gfx::ShapedTextFlags::TEXT_ENABLE_HYPHEN_BREAKS)));
  if (haveHyphenation) {
    if (hyphenBuffer.AppendElements(bufferRange.Length(), fallible)) {
      aProvider.GetHyphenationBreaks(bufferRange, hyphenBuffer.Elements());
      if (hyphensOption == StyleHyphens::Auto) {
        ClassifyAutoHyphenations(aStart, bufferRange, hyphenBuffer, &wordState);
      }
    } else {
      haveHyphenation = false;
    }
  }

  gfxFloat width = 0;
  gfxFloat advance = 0;
  // The number of space characters that can be trimmed or hang at a soft-wrap
  uint32_t trimmableChars = 0;
  // The amount of space removed by ignoring trimmableChars
  gfxFloat trimmableAdvance = 0;
  int32_t lastBreak = -1;
  int32_t lastBreakTrimmableChars = -1;
  gfxFloat lastBreakTrimmableAdvance = -1;
  // Cache the last candidate break
  int32_t lastCandidateBreak = -1;
  int32_t lastCandidateBreakTrimmableChars = -1;
  gfxFloat lastCandidateBreakTrimmableAdvance = -1;
  bool lastCandidateBreakUsedHyphenation = false;
  gfxBreakPriority lastCandidateBreakPriority = gfxBreakPriority::eNoBreak;
  bool aborted = false;
  uint32_t end = aStart + aMaxLength;
  bool lastBreakUsedHyphenation = false;
  Range ligatureRange(aStart, end);
  ShrinkToLigatureBoundaries(&ligatureRange);

  // Cache the glyph array pointer in a local so the compiler doesn't reload
  // the member on every iteration across the calls made in the loop below;
  // it does not change while we're measuring.
  const CompressedGlyph* charGlyphs = mCharacterGlyphs;

  // LetterSpacing() is a virtual call returning a value that is constant for
  // the whole measurement, so hoist it out of the per-character loop.
  const nscoord letterSpacing = aProvider.LetterSpacing();

  // We may need to move `i` backwards in the following loop, and re-scan
  // part of the textrun; we'll use `rescanLimit` so we can tell when that
  // is happening: if `i < rescanLimit` then we're rescanning.
  uint32_t rescanLimit = aStart;
  for (uint32_t i = aStart; i < end; ++i) {
    if (i >= bufferRange.end) {
      // Fetch more spacing and hyphenation data
      uint32_t oldHyphenBufferLength = hyphenBuffer.Length();
      bufferRange.start = i;
      bufferRange.end =
          std::min(aStart + aMaxLength, i + kMeasurementBufferSize);
      // For spacing, we always overwrite the old data with the newly
      // fetched one. However, for hyphenation, hyphenation data sometimes
      // depends on the context in every word (if "hyphens: auto" is set).
      // To ensure we get enough information between neighboring buffers,
      // we grow the hyphenBuffer instead of overwrite it.
      // NOTE that this means bufferRange does not correspond to the
      // entire hyphenBuffer, but only to the most recently added portion.
      // Therefore, we need to add the old length to hyphenBuffer.Elements()
      // when getting more data.
      if (haveSpacing) {
        GetAdjustedSpacing(this, bufferRange, aProvider, spacingBuffer);
      }
      if (haveHyphenation) {
        if (hyphenBuffer.AppendElements(bufferRange.Length(), fallible)) {
          aProvider.GetHyphenationBreaks(
              bufferRange, hyphenBuffer.Elements() + oldHyphenBufferLength);
          if (hyphensOption == StyleHyphens::Auto) {
            uint32_t prevMostRecentWordBoundary = wordState.mostRecentBoundary;
            ClassifyAutoHyphenations(aStart, bufferRange, hyphenBuffer,
                                     &wordState);
            // If the buffer boundary is in the middle of a word,
            // we need to go back to the start of the current word.
            // So, we can correct the wrong candidates that we set
            // in the previous runs of the loop.
            if (prevMostRecentWordBoundary < oldHyphenBufferLength) {
              rescanLimit = i;
              i = prevMostRecentWordBoundary - 1;
              continue;
            }
          }
        } else {
          haveHyphenation = false;
        }
      }
    }

    // There can't be a word-wrap break opportunity at the beginning of the
    // line: if the width is too small for even one character to fit, it
    // could be the first and last break opportunity on the line, and that
    // would trigger an infinite loop.
    if (aSuppressBreak != eSuppressAllBreaks &&
        (aSuppressBreak != eSuppressInitialBreak || i > aStart)) {
      bool atNaturalBreak = charGlyphs[i].CanBreakBefore() ==
                            CompressedGlyph::FLAG_BREAK_TYPE_NORMAL;
      // atHyphenationBreak indicates we're at a "soft" hyphen, where an extra
      // hyphen glyph will need to be painted. It is NOT set for breaks at an
      // explicit hyphen present in the text.
      //
      // NOTE(emilio): If you change this condition you also need to change
      // nsTextFrame::AddInlineMinISizeForFlow to match.
      bool atHyphenationBreak = !atNaturalBreak && haveHyphenation &&
                                (!aLineBreakBefore || i > aStart) &&
                                IsOptionalHyphenBreak(hyphenBuffer[i - aStart]);
      bool atAutoHyphenWithManualHyphenInSameWord =
          atHyphenationBreak &&
          hyphenBuffer[i - aStart] == HyphenType::AutoWithManualInSameWord;
      bool atBreak = atNaturalBreak || atHyphenationBreak;
      bool wordWrapping =
          (aCanWordWrap ||
           (aCanWhitespaceWrap &&
            charGlyphs[i].CanBreakBefore() ==
                CompressedGlyph::FLAG_BREAK_TYPE_EMERGENCY_WRAP)) &&
          charGlyphs[i].IsClusterStart() &&
          aBreakPriority <= gfxBreakPriority::eWordWrapBreak;

      bool whitespaceWrapping = false;
      if (i > aStart) {
        // The spec says the breaking opportunity is *after* whitespace.
        auto const& g = charGlyphs[i - 1];
        whitespaceWrapping =
            aIsBreakSpaces &&
            (g.CharIsSpace() || g.CharIsTab() || g.CharIsNewline());
      }

      if (atBreak || wordWrapping || whitespaceWrapping) {
        gfxFloat hyphenatedAdvance = advance;
        if (atHyphenationBreak) {
          hyphenatedAdvance += aProvider.GetHyphenWidth();
        }

        if (lastBreak < 0 ||
            width + hyphenatedAdvance - trimmableAdvance <= aWidth) {
          // We can break here.
          lastBreak = i;
          lastBreakTrimmableChars = trimmableChars;
          lastBreakTrimmableAdvance = trimmableAdvance;
          lastBreakUsedHyphenation = atHyphenationBreak;
          aBreakPriority = (atBreak || whitespaceWrapping)
                               ? gfxBreakPriority::eNormalBreak
                               : gfxBreakPriority::eWordWrapBreak;
        }

        width += advance;
        advance = 0;
        if (width - trimmableAdvance > aWidth) {
          // No more text fits. Abort
          aborted = true;
          break;
        }
        // There are various kinds of break opportunities:
        // 1. word wrap break,
        // 2. natural break,
        // 3. manual hyphenation break,
        // 4. auto hyphenation break without any manual hyphenation
        //    in the same word,
        // 5. auto hyphenation break with another manual hyphenation
        //    in the same word.
        // Allow all of them except the last one to be a candidate.
        // So, we can ensure that we don't use an automatic
        // hyphenation opportunity within a word that contains another
        // manual hyphenation, unless it is the only choice.
        if (wordWrapping || !atAutoHyphenWithManualHyphenInSameWord) {
          lastCandidateBreak = lastBreak;
          lastCandidateBreakTrimmableChars = lastBreakTrimmableChars;
          lastCandidateBreakTrimmableAdvance = lastBreakTrimmableAdvance;
          lastCandidateBreakUsedHyphenation = lastBreakUsedHyphenation;
          lastCandidateBreakPriority = aBreakPriority;
        }
      }
    }

    // If we're re-scanning part of a word (to re-process potential
    // hyphenation types) then we don't want to accumulate widths again
    // for the characters that were already added to `advance`.
    if (i < rescanLimit) {
      continue;
    }

    gfxFloat charAdvance;
    if (i >= ligatureRange.start && i < ligatureRange.end) {
      charAdvance = GetAdvanceForGlyph(i, letterSpacing);
      if (haveSpacing) {
        PropertyProvider::Spacing* space =
            &spacingBuffer[i - bufferRange.start];
        charAdvance += space->mBefore + space->mAfter;
      }
    } else {
      charAdvance = ComputePartialLigatureWidth(Range(i, i + 1), &aProvider);
    }

    advance += charAdvance;
    if (aOutTrimmableWhitespace) {
      if (charGlyphs[i].CharIsSpace()) {
        ++trimmableChars;
        trimmableAdvance += charAdvance;
      } else {
        trimmableAdvance = 0;
        trimmableChars = 0;
      }
    }
  }

  if (!aborted) {
    width += advance;
  }

  // There are three possibilities:
  // 1) all the text fit (width <= aWidth)
  // 2) some of the text fit up to a break opportunity (width > aWidth &&
  //    lastBreak >= 0)
  // 3) none of the text fits before a break opportunity (width > aWidth &&
  //    lastBreak < 0)
  uint32_t charsFit;
  aOutUsedHyphenation = false;
  if (width - trimmableAdvance <= aWidth) {
    charsFit = aMaxLength;
  } else if (lastBreak >= 0) {
    if (lastCandidateBreak >= 0 && lastCandidateBreak != lastBreak) {
      lastBreak = lastCandidateBreak;
      lastBreakTrimmableChars = lastCandidateBreakTrimmableChars;
      lastBreakTrimmableAdvance = lastCandidateBreakTrimmableAdvance;
      lastBreakUsedHyphenation = lastCandidateBreakUsedHyphenation;
      aBreakPriority = lastCandidateBreakPriority;
    }
    charsFit = lastBreak - aStart;
    trimmableChars = lastBreakTrimmableChars;
    trimmableAdvance = lastBreakTrimmableAdvance;
    aOutUsedHyphenation = lastBreakUsedHyphenation;
  } else {
    charsFit = aMaxLength;
  }

  // Get the overall metrics of the range that fit (including any potentially
  // trimmable or hanging whitespace).
  aOutMetrics = MeasureText(Range(aStart, aStart + charsFit), aBoundingBoxType,
                            aRefDrawTarget, &aProvider);

  if (aOutTrimmableWhitespace) {
    aOutTrimmableWhitespace->mAdvance = trimmableAdvance;
    aOutTrimmableWhitespace->mCount = trimmableChars;
  }

  if (charsFit == aMaxLength) {
    if (lastBreak < 0) {
      aOutLastBreak = UINT32_MAX;
    } else {
      aOutLastBreak = lastBreak - aStart;
    }
  }

  return charsFit;
}
