NS_IMETHODIMP
nsDOMWindowUtils::GetMissingPseudoRecascadeForTesting(
    Element* aElement, const nsAString& aPseudoElement,
    Element* aAnimationDonor, const nsAString& aAnimationProperty,
    Element* aTransitionDonor, const nsAString& aTransitionProperty,
    const nsAString& aResultProperty, uint32_t aFlags, nsAString& aResult) {
  RefPtr<Document> document = GetDocument();
  RefPtr<PresShell> presShell = GetPresShell();
  RefPtr<Element> element = aElement;
  RefPtr<Element> animationDonor = aAnimationDonor;
  RefPtr<Element> transitionDonor = aTransitionDonor;
  if (!document || !presShell || (aFlags & ~7u)) {
    return NS_ERROR_INVALID_ARG;
  }
  for (Element* candidate :
       {element.get(), animationDonor.get(), transitionDonor.get()}) {
    if (!candidate || candidate->OwnerDoc() != document ||
        !candidate->IsInComposedDoc()) {
      return NS_ERROR_INVALID_ARG;
    }
  }
  auto pseudo = PseudoStyleRequest::Parse(aPseudoElement,
                                          document->DefaultStyleAttrURLData());
  if (!pseudo) {
    return NS_ERROR_INVALID_ARG;
  }
  const NS_ConvertUTF16toUTF8 resultName(aResultProperty);
  const auto resultId = nsCSSProps::LookupProperty(resultName);
  if (resultId == eCSSProperty_UNKNOWN || nsCSSProps::IsShorthand(resultId)) {
    return NS_ERROR_INVALID_ARG;
  }
  const auto property =
      CSSPropertyId::FromIdOrCustomProperty(resultId, resultName);
  document->FlushPendingNotifications(FlushType::Style);
  ServoStyleSet* styleSet = presShell->StyleSet();
  RefPtr<ComputedStyle> primary = styleSet->ResolveStyleLazily(*element);
  RefPtr<ComputedStyle> animationStyle =
      styleSet->ResolveStyleLazily(*animationDonor);
  RefPtr<ComputedStyle> transitionStyle =
      styleSet->ResolveStyleLazily(*transitionDonor);
  const PseudoStyleRequest basePseudo =
      (aFlags & 2u) ? PseudoStyleRequest(PseudoStyleType::After) : *pseudo;
  RefPtr<ComputedStyle> base =
      styleSet->ResolveStyleLazily(*element, basePseudo);
  if (!primary || !base || !animationStyle || !transitionStyle) {
    return NS_ERROR_FAILURE;
  }
  auto values = [](const nsAString& aProperty, const ComputedStyle& aStyle) {
    if (aProperty.IsEmpty()) {
      return UniquePtr<StyleAnimationValueMap>(
          Servo_AnimationValueMap_Create());
    }
    const NS_ConvertUTF16toUTF8 name(aProperty);
    const auto id = nsCSSProps::LookupProperty(name);
    if (id == eCSSProperty_UNKNOWN || nsCSSProps::IsShorthand(id)) {
      return UniquePtr<StyleAnimationValueMap>();
    }
    const auto property = CSSPropertyId::FromIdOrCustomProperty(id, name);
    return UniquePtr<StyleAnimationValueMap>(
        Servo_AnimationValueMap_FromComputedStyleForTesting(&aStyle,
                                                            &property));
  };
  auto animations = values(aAnimationProperty, *animationStyle);
  auto transitions = values(aTransitionProperty, *transitionStyle);
  if (!animations || !transitions) {
    return NS_ERROR_INVALID_ARG;
  }
  RefPtr<ComputedStyle> result = styleSet->RecascadeStyleForMissingPseudo(
      *element, *pseudo, *base, (aFlags & 1u) ? *animationStyle : *primary,
      *animations, *transitions);
  if (result && (aFlags & 4u)) {
    UniquePtr<StyleAnimationValueMap> empty(Servo_AnimationValueMap_Create());
    result = styleSet->RecascadeStyleForMissingPseudo(
        *element, *pseudo, *result, *primary, *empty, *empty);
  }
  JSONStringWriteFunc<nsCString> output;
  JSONWriter writer(output, JSONWriter::SingleLineStyle);
  writer.Start();
  writer.BoolProperty("admitted", !!result);
  writer.BoolProperty("originUnchanged",
                      Servo_Element_GetMaybeOutOfDateStyle(element) == primary);
  writer.BoolProperty("noPseudoCreated", !element->GetPseudoElement(*pseudo));
  writer.BoolProperty("pseudoMatches",
                      result && result->GetPseudoType() == pseudo->mType);
  writer.BoolProperty(
      "displayIsBlock",
      result && result->StyleDisplay()->mDisplay == StyleDisplay::Block);
  writer.BoolProperty(
      "displayIsInline",
      result && result->StyleDisplay()->mDisplay == StyleDisplay::Inline);
  RefPtr<StyleAnimationValue> value =
      result ? Servo_ComputedValues_ExtractAnimationValue(result, &property)
                   .Consume()
             : nullptr;
  if (value) {
    nsAutoCString text;
    Servo_AnimationValue_Serialize(value, &property, styleSet->RawData(),
                                   &text);
    writer.StringProperty("value",
                          Span<const char>(text.Data(), text.Length()));
  } else {
    writer.NullProperty("value");
  }
  writer.End();
  CopyUTF8toUTF16(output.StringCRef(), aResult);
  return NS_OK;
}
