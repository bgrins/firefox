nsContainerFrame::ComputeSizeWithIntrinsicDimensions(
    gfxContext* aRenderingContext, WritingMode aWM,
    const IntrinsicSize& aIntrinsicSize, const AspectRatio& aAspectRatio,
    const LogicalSize& aCBSize, const LogicalSize& aMargin,
    const LogicalSize& aBorderPadding, const StyleSizeOverrides& aSizeOverrides,
    ComputeSizeFlags aFlags) {
  const nsStylePosition* stylePos = StylePosition();
  const auto anchorResolutionParams = AnchorPosResolutionParams::From(this);
  const auto styleISize =
      aSizeOverrides.mStyleISize
          ? AnchorResolvedSizeHelper::Overridden(*aSizeOverrides.mStyleISize)
          : stylePos->ISize(aWM, anchorResolutionParams);

  const auto styleBSize = [&] {
    auto styleBSizeConsideringOverrides =
        aSizeOverrides.mStyleBSize
            ? AnchorResolvedSizeHelper::Overridden(*aSizeOverrides.mStyleBSize)
            : stylePos->BSize(aWM, anchorResolutionParams);
    if (styleBSizeConsideringOverrides->BehavesLikeStretchOnBlockAxis() &&
        aCBSize.BSize(aWM) != NS_UNCONSTRAINEDSIZE) {
      // We've got a 'stretch' BSize; resolve it to a length:
      nscoord stretchBSize = nsLayoutUtils::ComputeStretchSize(
          aCBSize.BSize(aWM), aMargin.BSize(aWM), aBorderPadding.BSize(aWM),
          stylePos->mBoxSizing);
      // Note(dshin): This allocates.
      return AnchorResolvedSizeHelper::LengthPercentage(
          LengthPercentage::FromAppUnits(stretchBSize));
    }
    return styleBSizeConsideringOverrides;
  }();

  const auto& aspectRatio =
      aSizeOverrides.mAspectRatio ? *aSizeOverrides.mAspectRatio : aAspectRatio;

  auto* parentFrame = GetParent();
  const bool isGridItem = IsGridItem();

  // flexItemMainAxis is set if this frame is a flex item in a modern flexbox
  // layout. It indicates which logical axis (in this frame's own WM)
  // corresponds to its flex container's main axis.
  Maybe<LogicalAxis> flexItemMainAxis;
  if (IsFlexItem() && !parentFrame->HasAnyStateBits(
                          NS_STATE_FLEX_IS_EMULATING_LEGACY_WEBKIT_BOX)) {
    flexItemMainAxis = Some(nsFlexContainerFrame::IsItemInlineAxisMainAxis(this)
                                ? LogicalAxis::Inline
                                : LogicalAxis::Block);
  }

  // Handle intrinsic sizes and their interaction with
  // {min-,max-,}{width,height} according to the rules in
  // https://www.w3.org/TR/CSS22/visudet.html#min-max-widths and
  // https://drafts.csswg.org/css-sizing-3/#intrinsic-sizes

  // Note: throughout the following section of the function, I avoid
  // a * (b / c) because of its reduced accuracy relative to a * b / c
  // or (a * b) / c (which are equivalent).

  const bool isAutoOrMaxContentISize =
      styleISize->IsAuto() || styleISize->IsMaxContent();
  const bool isAutoBSize =
      nsLayoutUtils::IsAutoBSize(*styleBSize, aCBSize.BSize(aWM));

  const auto boxSizingAdjust = stylePos->mBoxSizing == StyleBoxSizing::BorderBox
                                   ? aBorderPadding
                                   : LogicalSize(aWM);
  // We don't expect these initial values of iSize/bSize to be used, but this
  // silences a GCC warning about them being uninitialized.
  nscoord minISize, maxISize, minBSize, maxBSize, iSize = 0, bSize = 0;
  enum class FillCB {
    // No stretching or clamping in the relevant axis.
    No,
    // Stretch to fill the containing block size in the relevant axis while
    // preserving the aspect-ratio. If both axes are stretched, the aspect-ratio
    // will be disregarded.
    Stretch,
    // Clamp to fill the containing block size in the relevant axis while
    // preserving the aspect-ratio. If both axes are clamped, the aspect-ratio
    // is respected, and the dimensions do not overflow the containing block
    // size.
    Clamp,
  };

  FillCB inlineFillCB = FillCB::No;  // fill CB behavior in the inline axis
  FillCB blockFillCB = FillCB::No;   // fill CB behavior in the block axis

  const LogicalSize fallbackIntrinsicSize(aWM, kFallbackIntrinsicSize);
  const Maybe<nscoord>& maybeIntrinsicISize = aIntrinsicSize.ISize(aWM);
  const bool hasIntrinsicISize = maybeIntrinsicISize.isSome();
  nscoord intrinsicISize = std::max(0, maybeIntrinsicISize.valueOr(0));

  const auto& maybeIntrinsicBSize = aIntrinsicSize.BSize(aWM);
  const bool hasIntrinsicBSize = maybeIntrinsicBSize.isSome();
  nscoord intrinsicBSize = std::max(0, maybeIntrinsicBSize.valueOr(0));

  Maybe<nscoord> iSizeToFillCB;
  Maybe<nscoord> bSizeToFillCB;
  if (!isAutoOrMaxContentISize) {
    iSize = ComputeISizeValue(aRenderingContext, aWM, aCBSize, aMargin,
                              aBorderPadding, *styleISize, *styleBSize,
                              aspectRatio, aFlags)
                .mISize;
  } else if (MOZ_UNLIKELY(isGridItem) &&
             !parentFrame->IsMasonry(aWM, LogicalAxis::Inline)) {
    MOZ_ASSERT(!IsTrueOverflowContainer());
    // 'auto' inline-size for grid-level box - apply 'stretch' as needed:
    auto cbSize = aCBSize.ISize(aWM);
    if (cbSize != NS_UNCONSTRAINEDSIZE) {
      if (!StyleMargin()->HasInlineAxisAuto(
              aWM, AnchorPosResolutionParams::From(this))) {
        auto inlineAxisAlignment = stylePos->UsedSelfAlignment(
            aWM, LogicalAxis::Inline, parentFrame->GetWritingMode(),
            parentFrame->Style());
        if (inlineAxisAlignment == StyleAlignFlags::STRETCH) {
          inlineFillCB = FillCB::Stretch;
        }
      }
      if (inlineFillCB != FillCB::No ||
          aFlags.contains(ComputeSizeFlag::IClampMarginBoxMinSize)) {
        iSizeToFillCB.emplace(std::max(
            0, cbSize - aBorderPadding.ISize(aWM) - aMargin.ISize(aWM)));
      }
    } else {
      // Reset this flag to avoid applying the clamping below.
      aFlags -= ComputeSizeFlag::IClampMarginBoxMinSize;
    }
  }

  // Flex items ignore their min & max sizing properties in their flex
  // container's main-axis. (Those properties get applied later in the flexbox
  // algorithm.)
  const bool isFlexItemInlineAxisMainAxis =
      flexItemMainAxis && *flexItemMainAxis == LogicalAxis::Inline;
  const auto maxISizeCoord = stylePos->MaxISize(aWM, anchorResolutionParams);
  if (!maxISizeCoord->IsNone() && !isFlexItemInlineAxisMainAxis) {
    maxISize = ComputeISizeValue(aRenderingContext, aWM, aCBSize, aMargin,
                                 aBorderPadding, *maxISizeCoord, *styleBSize,
                                 aspectRatio, aFlags)
                   .mISize;
  } else {
    maxISize = nscoord_MAX;
  }

  const auto minISizeCoord = stylePos->MinISize(aWM, anchorResolutionParams);
  if (!minISizeCoord->IsAuto() && !isFlexItemInlineAxisMainAxis) {
    minISize = ComputeISizeValue(aRenderingContext, aWM, aCBSize, aMargin,
                                 aBorderPadding, *minISizeCoord, *styleBSize,
                                 aspectRatio, aFlags)
                   .mISize;
  } else {
    // Treat "min-width: auto" as 0.
    // NOTE: Technically, "auto" is supposed to behave like "min-content" on
    // flex items. However, we don't need to worry about that here, because
    // flex items' min-sizes are intentionally ignored until the flex
    // container explicitly considers them during space distribution.
    minISize = 0;
  }

  if (!isAutoBSize) {
    bSize = nsLayoutUtils::ComputeBSizeValueHandlingStretch(
        aCBSize.BSize(aWM), aMargin.BSize(aWM), aBorderPadding.BSize(aWM),
        boxSizingAdjust.BSize(aWM), *styleBSize);
  } else if (MOZ_UNLIKELY(isGridItem) &&
             !parentFrame->IsMasonry(aWM, LogicalAxis::Block)) {
    MOZ_ASSERT(!IsTrueOverflowContainer());
    // 'auto' block-size for grid-level box - apply 'stretch' as needed:
    auto cbSize = aCBSize.BSize(aWM);
    if (cbSize != NS_UNCONSTRAINEDSIZE) {
      if (!StyleMargin()->HasBlockAxisAuto(
              aWM, AnchorPosResolutionParams::From(this))) {
        auto blockAxisAlignment = stylePos->UsedSelfAlignment(
            aWM, LogicalAxis::Block, parentFrame->GetWritingMode(),
            parentFrame->Style());
        if (blockAxisAlignment == StyleAlignFlags::STRETCH) {
          blockFillCB = FillCB::Stretch;
        }
      }
      if (blockFillCB != FillCB::No ||
          aFlags.contains(ComputeSizeFlag::BClampMarginBoxMinSize)) {
        bSizeToFillCB.emplace(std::max(
            0, cbSize - aBorderPadding.BSize(aWM) - aMargin.BSize(aWM)));
      }
    } else {
      // Reset this flag to avoid applying the clamping below.
      aFlags -= ComputeSizeFlag::BClampMarginBoxMinSize;
    }
  }

  // Flex items ignore their min & max sizing properties in their flex
  // container's main-axis. (Those properties get applied later in the flexbox
  // algorithm.)
  const bool isFlexItemBlockAxisMainAxis =
      flexItemMainAxis && *flexItemMainAxis == LogicalAxis::Block;
  const auto maxBSizeCoord = stylePos->MaxBSize(aWM, anchorResolutionParams);
  if (!nsLayoutUtils::IsAutoBSize(*maxBSizeCoord, aCBSize.BSize(aWM)) &&
      !isFlexItemBlockAxisMainAxis) {
    maxBSize = nsLayoutUtils::ComputeBSizeValueHandlingStretch(
        aCBSize.BSize(aWM), aMargin.BSize(aWM), aBorderPadding.BSize(aWM),
        boxSizingAdjust.BSize(aWM), *maxBSizeCoord);
  } else {
    maxBSize = nscoord_MAX;
  }

  const auto minBSizeCoord = stylePos->MinBSize(aWM, anchorResolutionParams);
  if (!nsLayoutUtils::IsAutoBSize(*minBSizeCoord, aCBSize.BSize(aWM)) &&
      !isFlexItemBlockAxisMainAxis) {
    minBSize = nsLayoutUtils::ComputeBSizeValueHandlingStretch(
        aCBSize.BSize(aWM), aMargin.BSize(aWM), aBorderPadding.BSize(aWM),
        boxSizingAdjust.BSize(aWM), *minBSizeCoord);
  } else {
    minBSize = 0;
  }

  NS_ASSERTION(aCBSize.ISize(aWM) != NS_UNCONSTRAINEDSIZE,
               "Our containing block must not have unconstrained inline-size!");
  MOZ_ASSERT(!(inlineFillCB != FillCB::No ||
               aFlags.contains(ComputeSizeFlag::IClampMarginBoxMinSize)) ||
                 iSizeToFillCB,
             "iSizeToFillCB must be valid when stretching or clamping in the "
             "inline axis!");
  MOZ_ASSERT(!(blockFillCB != FillCB::No ||
               aFlags.contains(ComputeSizeFlag::BClampMarginBoxMinSize)) ||
                 bSizeToFillCB,
             "bSizeToFillCB must be valid when stretching or clamping in the "
             "block axis!");

  // Now calculate the used values for iSize and bSize:
  if (isAutoOrMaxContentISize) {
    if (isAutoBSize) {
      // 'auto' iSize, 'auto' bSize

      // Get tentative values - CSS 2.1 sections 10.3.2 and 10.6.2:

      nscoord tentISize, tentBSize;

      if (hasIntrinsicISize) {
        tentISize = intrinsicISize;
      } else if (hasIntrinsicBSize && aspectRatio) {
        tentISize = aspectRatio.ComputeRatioDependentSize(
            LogicalAxis::Inline, aWM, intrinsicBSize, boxSizingAdjust);
      } else if (aspectRatio) {
        tentISize =
            aCBSize.ISize(aWM) - aBorderPadding.ISize(aWM) - aMargin.ISize(aWM);
        if (tentISize < 0) {
          tentISize = 0;
        }
      } else {
        tentISize = fallbackIntrinsicSize.ISize(aWM);
      }

      // If we need to clamp the inline size to fit the CB, we use the 'stretch'
      // or 'normal' codepath.  We use the ratio-preserving 'normal' codepath
      // unless we have 'stretch' in the other axis.
      if (aFlags.contains(ComputeSizeFlag::IClampMarginBoxMinSize) &&
          inlineFillCB != FillCB::Stretch && tentISize > *iSizeToFillCB) {
        inlineFillCB =
            (blockFillCB == FillCB::Stretch ? FillCB::Stretch : FillCB::Clamp);
      }

      // Honor aspect ratio if there's an intrinsic isize, even if there's an
      // intrinsic bsize.
      if (aspectRatio && (!hasIntrinsicBSize || hasIntrinsicISize)) {
        tentBSize = aspectRatio.ComputeRatioDependentSize(
            LogicalAxis::Block, aWM, tentISize, boxSizingAdjust);
      } else if (hasIntrinsicBSize) {
        tentBSize = intrinsicBSize;
      } else {
        tentBSize = fallbackIntrinsicSize.BSize(aWM);
      }

      // (ditto the comment about clamping the inline size above)
      if (aFlags.contains(ComputeSizeFlag::BClampMarginBoxMinSize) &&
          blockFillCB != FillCB::Stretch && tentBSize > *bSizeToFillCB) {
        blockFillCB =
            (inlineFillCB == FillCB::Stretch ? FillCB::Stretch : FillCB::Clamp);
      }

      // The slash notation is the used value of "align-self / justify-self".
      if (inlineFillCB == FillCB::Stretch) {
        tentISize = *iSizeToFillCB;  // * / 'stretch'
        if (blockFillCB == FillCB::Stretch) {
          tentBSize = *bSizeToFillCB;  // 'stretch' / 'stretch'
        } else if (aspectRatio) {
          // * (except 'stretch') / 'stretch'
          tentBSize = aspectRatio.ComputeRatioDependentSize(
              LogicalAxis::Block, aWM, *iSizeToFillCB, boxSizingAdjust);
        }
      } else if (blockFillCB == FillCB::Stretch) {
        tentBSize = *bSizeToFillCB;  // 'stretch' / * (except 'stretch')
        if (aspectRatio) {
          tentISize = aspectRatio.ComputeRatioDependentSize(
              LogicalAxis::Inline, aWM, *bSizeToFillCB, boxSizingAdjust);
        }
      } else if (inlineFillCB == FillCB::Clamp && aspectRatio) {
        tentISize = *iSizeToFillCB;  // * (except 'stretch') / 'normal'
        tentBSize = aspectRatio.ComputeRatioDependentSize(
            LogicalAxis::Block, aWM, *iSizeToFillCB, boxSizingAdjust);
        if (blockFillCB == FillCB::Clamp && tentBSize > *bSizeToFillCB) {
          // Clamp within the CB size with preserved aspect ratio.
          tentBSize = *bSizeToFillCB;  // 'normal' / 'normal'
          tentISize = aspectRatio.ComputeRatioDependentSize(
              LogicalAxis::Inline, aWM, *bSizeToFillCB, boxSizingAdjust);
        }
      } else if (blockFillCB == FillCB::Clamp && aspectRatio) {
        // 'normal' / * (except 'normal' and 'stretch')
        tentBSize = *bSizeToFillCB;
        tentISize = aspectRatio.ComputeRatioDependentSize(
            LogicalAxis::Inline, aWM, *bSizeToFillCB, boxSizingAdjust);
      }

      // ComputeAutoSizeWithIntrinsicDimensions preserves the ratio when
      // applying the min/max-size.  We don't want that when we have 'stretch'
      // in either axis because tentISize/tentBSize is likely not according to
      // ratio now.
      if (aspectRatio && inlineFillCB != FillCB::Stretch &&
          blockFillCB != FillCB::Stretch) {
        nsSize autoSize = nsLayoutUtils::ComputeAutoSizeWithIntrinsicDimensions(
            minISize, minBSize, maxISize, maxBSize, tentISize, tentBSize);
        // The nsSize that ComputeAutoSizeWithIntrinsicDimensions returns will
        // actually contain logical values if the parameters passed to it were
        // logical coordinates, so we do NOT perform a physical-to-logical
        // conversion here, but just assign the fields directly to our result.
        iSize = autoSize.width;
        bSize = autoSize.height;
      } else {
        // Not honoring an intrinsic ratio: clamp the dimensions independently.
        iSize = CSSMinMax(tentISize, minISize, maxISize);
        bSize = CSSMinMax(tentBSize, minBSize, maxBSize);
      }
    } else {
      // 'auto' iSize, non-'auto' bSize
      bSize = CSSMinMax(bSize, minBSize, maxBSize);
      if (inlineFillCB == FillCB::Stretch) {
        iSize = *iSizeToFillCB;
      } else if (aspectRatio) {
        iSize = aspectRatio.ComputeRatioDependentSize(LogicalAxis::Inline, aWM,
                                                      bSize, boxSizingAdjust);
      } else if (hasIntrinsicISize) {
        iSize = aFlags.contains(ComputeSizeFlag::IClampMarginBoxMinSize) &&
                        intrinsicISize > *iSizeToFillCB
                    ? *iSizeToFillCB
                    : intrinsicISize;
      } else {
        iSize = fallbackIntrinsicSize.ISize(aWM);
      }
      iSize = CSSMinMax(iSize, minISize, maxISize);
    }
  } else {
    if (isAutoBSize) {
      // non-'auto' iSize, 'auto' bSize
      iSize = CSSMinMax(iSize, minISize, maxISize);
      if (blockFillCB == FillCB::Stretch) {
        bSize = *bSizeToFillCB;
      } else if (aspectRatio) {
        bSize = aspectRatio.ComputeRatioDependentSize(LogicalAxis::Block, aWM,
                                                      iSize, boxSizingAdjust);
      } else if (hasIntrinsicBSize) {
        bSize = aFlags.contains(ComputeSizeFlag::BClampMarginBoxMinSize) &&
                        intrinsicBSize > *bSizeToFillCB
                    ? *bSizeToFillCB
                    : intrinsicBSize;
      } else {
        bSize = fallbackIntrinsicSize.BSize(aWM);
      }
      bSize = CSSMinMax(bSize, minBSize, maxBSize);
    } else {
      // non-'auto' iSize, non-'auto' bSize
      iSize = CSSMinMax(iSize, minISize, maxISize);
      bSize = CSSMinMax(bSize, minBSize, maxBSize);
    }
  }

  return LogicalSize(aWM, iSize, bSize);
}
