static nsTArray<Keyframe> BuildGroupKeyframes(
    Document* aDoc, const CSSToCSSMatrix4x4Flagged& aTransform,
    const nsSize& aSize, const StyleOwnedSlice<StyleFilter>& aBackdropFilters) {
  Keyframe firstKeyframe;
  firstKeyframe.mOffset = Some(Keyframe::OffsetType::PercentageOffset(0.0));
  PropertyValuePair transform{
      CSSPropertyId(eCSSProperty_transform),
      Servo_DeclarationBlock_CreateEmpty().Consume(),
  };
  SetProp(transform.mServoDeclarationBlock, aDoc, eCSSProperty_transform,
          aTransform);
  PropertyValuePair width{
      CSSPropertyId(eCSSProperty_width),
      Servo_DeclarationBlock_CreateEmpty().Consume(),
  };
  CSSSize cssSize = CSSSize::FromAppUnits(aSize);
  SetProp(width.mServoDeclarationBlock, aDoc, eCSSProperty_width, cssSize.width,
          eCSSUnit_Pixel);
  PropertyValuePair height{
      CSSPropertyId(eCSSProperty_height),
      Servo_DeclarationBlock_CreateEmpty().Consume(),
  };
  SetProp(height.mServoDeclarationBlock, aDoc, eCSSProperty_height,
          cssSize.height, eCSSUnit_Pixel);
  PropertyValuePair backdropFilters{
      CSSPropertyId(eCSSProperty_backdrop_filter),
      Servo_DeclarationBlock_CreateEmpty().Consume(),
  };
  SetProp(backdropFilters.mServoDeclarationBlock, aDoc,
          eCSSProperty_backdrop_filter, aBackdropFilters);
  firstKeyframe.mPropertyValues.AppendElement(std::move(transform));
  firstKeyframe.mPropertyValues.AppendElement(std::move(width));
  firstKeyframe.mPropertyValues.AppendElement(std::move(height));
  firstKeyframe.mPropertyValues.AppendElement(std::move(backdropFilters));

  Keyframe lastKeyframe;
  lastKeyframe.mOffset = Some(Keyframe::OffsetType::PercentageOffset(1.0));
  lastKeyframe.mPropertyValues.AppendElement(
      PropertyValuePair{CSSPropertyId(eCSSProperty_transform)});
  lastKeyframe.mPropertyValues.AppendElement(
      PropertyValuePair{CSSPropertyId(eCSSProperty_width)});
  lastKeyframe.mPropertyValues.AppendElement(
      PropertyValuePair{CSSPropertyId(eCSSProperty_height)});
  lastKeyframe.mPropertyValues.AppendElement(
      PropertyValuePair{CSSPropertyId(eCSSProperty_backdrop_filter)});

  nsTArray<Keyframe> result;
  result.AppendElement(std::move(firstKeyframe));
  result.AppendElement(std::move(lastKeyframe));
  return result;
}
