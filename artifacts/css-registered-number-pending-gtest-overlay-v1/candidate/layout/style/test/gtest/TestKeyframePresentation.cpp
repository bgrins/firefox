/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

#include "gtest/gtest.h"
#include "mozilla/ComputedStyle.h"
#include "mozilla/ErrorResult.h"
#include "mozilla/Keyframe.h"
#include "mozilla/PresShell.h"
#include "mozilla/PresShellInlines.h"
#include "mozilla/ServoBindings.h"
#include "mozilla/ServoStyleSet.h"
#include "mozilla/StyleAnimationValue.h"
#include "mozilla/TimingParams.h"
#include "mozilla/dom/CSSBinding.h"
#include "mozilla/dom/Document.h"
#include "mozilla/dom/Element.h"
#include "mozilla/dom/KeyframeEffect.h"
#include "nsComputedDOMStyle.h"
#include "nsContentUtils.h"
#include "nsGkAtoms.h"
#include "nsIAppShellService.h"
#include "nsIBaseWindow.h"
#include "nsIDocShell.h"
#include "nsIDocumentViewer.h"
#include "nsIWindowlessBrowser.h"
#include "nsServiceManagerUtils.h"
#include "nsString.h"
#include "nsStyleStruct.h"
#include "nsThreadUtils.h"

using namespace mozilla;
using namespace mozilla::dom;

namespace {

class KeyframePresentation : public ::testing::Test {
 protected:
  void SetUp() override {
    ASSERT_TRUE(NS_IsMainThread());
    ASSERT_TRUE(nsContentUtils::IsSafeToRunScript());
    nsCOMPtr<nsIAppShellService> appShell =
        do_GetService("@mozilla.org/appshell/appShellService;1");
    ASSERT_TRUE(appShell);
    ASSERT_EQ(NS_OK, appShell->CreateWindowlessBrowser(
                         false, 0, getter_AddRefs(mBrowser)));
    ASSERT_TRUE(mBrowser);

    nsCOMPtr<nsIDocShell> docShell;
    ASSERT_EQ(NS_OK, mBrowser->GetDocShell(getter_AddRefs(docShell)));
    ASSERT_TRUE(docShell);
    nsCOMPtr<nsIBaseWindow> window = do_QueryInterface(docShell);
    ASSERT_TRUE(window);
    ASSERT_EQ(NS_OK, window->SetPositionAndSize(0, 0, 320, 240, 0));
    nsCOMPtr<nsIDocumentViewer> viewer;
    ASSERT_EQ(NS_OK, docShell->GetDocViewer(getter_AddRefs(viewer)));
    ASSERT_TRUE(viewer);
    ASSERT_EQ(NS_OK, viewer->Show());
    ASSERT_EQ(NS_OK, mBrowser->GetDocument(getter_AddRefs(mDocument)));
    ASSERT_TRUE(mDocument);

    RefPtr<PresShell> shell = mDocument->GetPresShell();
    ASSERT_TRUE(shell);
    ASSERT_TRUE(shell->GetPresContext());
    if (!shell->DidInitialize()) {
      ASSERT_EQ(NS_OK, shell->Initialize());
    }
    ASSERT_TRUE(shell->DidInitialize());
    ASSERT_EQ(shell.get(), mDocument->GetPresShell());
  }

  void TearDown() override {
    if (mBrowser) {
      EXPECT_TRUE(nsContentUtils::IsSafeToRunScript());
      EXPECT_EQ(NS_OK, mBrowser->Close());
      mBrowser = nullptr;
    }
    if (mDocument) {
      EXPECT_EQ(nullptr, mDocument->GetPresShell());
      mDocument = nullptr;
    }
  }

  nsCOMPtr<nsIWindowlessBrowser> mBrowser;
  RefPtr<Document> mDocument;
};

TEST_F(KeyframePresentation, LiteralOpacity) {
  RefPtr<Element> target = mDocument->GetHtmlChildElement(nsGkAtoms::body);
  ASSERT_TRUE(target);
  ErrorResult error;
  target->SetAttr(nsGkAtoms::style, u"opacity: 0.375"_ns, error);
  ASSERT_EQ(NS_OK, error.StealNSResult());
  RefPtr<const ComputedStyle> style =
      nsComputedDOMStyle::GetComputedStyle(target);
  ASSERT_TRUE(style);
  ASSERT_FLOAT_EQ(0.375f, style->StyleEffects()->mOpacity);

  RefPtr<StyleLockedDeclarationBlock> block =
      Servo_DeclarationBlock_CreateEmpty().Consume();
  ASSERT_TRUE(block);
  const nsCString value("0.625");
  ASSERT_TRUE(Servo_DeclarationBlock_SetPropertyById(
      block, eCSSProperty_opacity, &value, false,
      mDocument->DefaultStyleAttrURLData(), StyleParsingMode::DEFAULT,
      eCompatibility_FullStandards, nullptr, StyleCssRuleType::Style, {}));
  nsTArray<Keyframe> keyframes;
  auto& keyframe = *keyframes.AppendElement();
  keyframe.mComputedOffset = 0.0;
  keyframe.mPropertyValues.AppendElement(
      PropertyValuePair(CSSPropertyId(eCSSProperty_opacity), std::move(block)));
  RefPtr<PresShell> shell = mDocument->GetPresShell();
  ASSERT_TRUE(shell);
  ASSERT_TRUE(shell->StyleSet());
  bool referencesAttributes = true;
  auto values = shell->StyleSet()->GetComputedKeyframeValuesFor(
      keyframes, target, {}, style, referencesAttributes);
  ASSERT_EQ(1u, values.Length());
  ASSERT_EQ(1u, values[0].Length());
  ASSERT_EQ(CSSPropertyId(eCSSProperty_opacity), values[0][0].mProperty);
  ASSERT_FALSE(values[0][0].mValue.IsNull());
  EXPECT_FLOAT_EQ(0.625f, values[0][0].mValue.GetOpacity());
  EXPECT_FALSE(referencesAttributes);
}

extern "C" void Rust_CheckTransitionEndpoint(const StyleKeyframeEndpoint*,
                                             float, size_t);

class InspectableKeyframeEffect final : public KeyframeEffect {
 public:
  using KeyframeEffect::KeyframeEffect;
  const nsTArray<Keyframe>& InputKeyframes() const { return mKeyframes; }

 private:
  ~InspectableKeyframeEffect() override = default;
};

static void AppendOpacityKeyframe(Document* aDocument,
                                  nsTArray<Keyframe>& aKeyframes,
                                  const char* aValue, double aOffset) {
  RefPtr<StyleLockedDeclarationBlock> block =
      Servo_DeclarationBlock_CreateEmpty().Consume();
  ASSERT_TRUE(block);
  const nsCString value(aValue);
  ASSERT_TRUE(Servo_DeclarationBlock_SetPropertyById(
      block, eCSSProperty_opacity, &value, false,
      aDocument->DefaultStyleAttrURLData(), StyleParsingMode::DEFAULT,
      eCompatibility_FullStandards, nullptr, StyleCssRuleType::Style, {}));
  auto& keyframe = *aKeyframes.AppendElement();
  keyframe.mOffset = Some(Keyframe::OffsetType::PercentageOffset(aOffset));
  keyframe.mPropertyValues.AppendElement(
      PropertyValuePair(CSSPropertyId(eCSSProperty_opacity), std::move(block)));
}

TEST_F(KeyframePresentation, TransitionConcreteEndpoint) {
  RefPtr<Element> target = mDocument->GetHtmlChildElement(nsGkAtoms::body);
  ASSERT_TRUE(target);
  ErrorResult error;
  target->SetAttr(nsGkAtoms::style, u"opacity: 0.1"_ns, error);
  ASSERT_EQ(NS_OK, error.StealNSResult());
  RefPtr<const ComputedStyle> style =
      nsComputedDOMStyle::GetComputedStyle(target);
  ASSERT_TRUE(style);
  ASSERT_FLOAT_EQ(0.1f, style->StyleEffects()->mOpacity);

  nsTArray<Keyframe> keyframes;
  ASSERT_NO_FATAL_FAILURE(
      AppendOpacityKeyframe(mDocument, keyframes, "0.2", 0));
  ASSERT_NO_FATAL_FAILURE(
      AppendOpacityKeyframe(mDocument, keyframes, "0.8", 1));
  RefPtr<InspectableKeyframeEffect> effect = new InspectableKeyframeEffect(
      mDocument, OwningAnimationTarget(target, {}), TimingParams{},
      KeyframeEffectParams{});
  effect->SetKeyframes(std::move(keyframes), style, nullptr, nullptr);
  ASSERT_EQ(1u, effect->Properties().Length());
  ASSERT_EQ(1u, effect->Properties()[0].mSegments.Length());
  const auto& before = effect->Properties()[0].mSegments[0];
  ASSERT_FLOAT_EQ(0.2f, before.mFromValue.GetOpacity());
  ASSERT_FLOAT_EQ(0.8f, before.mToValue.GetOpacity());
  RefPtr<StyleKeyframeEndpoint> oldFrom = before.mFromEndpoint;
  RefPtr<StyleKeyframeEndpoint> oldTo = before.mToEndpoint;
  RefPtr<StyleAnimationValue> oldToValue = before.mToValue.mServo;
  ASSERT_TRUE(oldFrom);
  ASSERT_TRUE(oldTo);
  Rust_CheckTransitionEndpoint(oldFrom, 0.2f, 0);
  Rust_CheckTransitionEndpoint(oldTo, 0.8f, 1);
  ASSERT_FALSE(::testing::Test::HasFailure());

  RefPtr<StyleAnimationValue> replacement =
      Servo_AnimationValue_Opacity(0.4f).Consume();
  ASSERT_TRUE(replacement);
  effect->ReplaceTransitionStartValue(AnimationValue(replacement));
  const auto& current = effect->Properties()[0].mSegments[0];
  ASSERT_FALSE(current.mFromValue.IsNull());
  EXPECT_FLOAT_EQ(0.4f, current.mFromValue.GetOpacity());
  EXPECT_EQ(nullptr, current.mFromEndpoint);
  EXPECT_EQ(oldTo.get(), current.mToEndpoint.get());
  EXPECT_EQ(oldToValue.get(), current.mToValue.mServo.get());
  EXPECT_FLOAT_EQ(0.8f, current.mToValue.GetOpacity());
  EXPECT_FLOAT_EQ(0.f, current.mFromKey);
  EXPECT_FLOAT_EQ(1.f, current.mToKey);

  RefPtr<PresShell> shell = mDocument->GetPresShell();
  ASSERT_TRUE(shell);
  bool referencesAttributes = true;
  auto recomputed = shell->StyleSet()->GetComputedKeyframeValuesFor(
      effect->InputKeyframes(), target, {}, style, referencesAttributes);
  ASSERT_EQ(2u, recomputed.Length());
  ASSERT_EQ(1u, recomputed[0].Length());
  ASSERT_EQ(1u, recomputed[1].Length());
  EXPECT_FLOAT_EQ(0.4f, recomputed[0][0].mValue.GetOpacity());
  EXPECT_FLOAT_EQ(0.8f, recomputed[1][0].mValue.GetOpacity());
  EXPECT_FALSE(referencesAttributes);

  RefPtr<StyleAnimationValue> underlying =
      Servo_AnimationValue_Opacity(0.1f).Consume();
  RefPtr<StyleAnimationValue> concrete =
      Servo_ComposeAnimationSegment(&current, underlying, nullptr,
                                    IterationCompositeOperation::Replace, 0.5,
                                    0)
          .Consume();
  ASSERT_TRUE(concrete);
  EXPECT_FLOAT_EQ(0.6f, AnimationValue(concrete).GetOpacity());

  nsTArray<Keyframe> implicitKeyframes;
  ASSERT_NO_FATAL_FAILURE(
      AppendOpacityKeyframe(mDocument, implicitKeyframes, "0.8", 1));
  RefPtr<InspectableKeyframeEffect> implicitEffect =
      new InspectableKeyframeEffect(mDocument,
                                    OwningAnimationTarget(target, {}),
                                    TimingParams{}, KeyframeEffectParams{});
  implicitEffect->SetKeyframes(std::move(implicitKeyframes), style, nullptr,
                               nullptr);
  ASSERT_EQ(1u, implicitEffect->Properties().Length());
  ASSERT_EQ(1u, implicitEffect->Properties()[0].mSegments.Length());
  const auto& implicit = implicitEffect->Properties()[0].mSegments[0];
  ASSERT_TRUE(implicit.mFromValue.IsNull());
  ASSERT_FALSE(implicit.mFromEndpoint);
  ASSERT_FALSE(implicit.mToValue.IsNull());
  RefPtr<StyleAnimationValue> composedImplicit =
      Servo_ComposeAnimationSegment(&implicit, underlying, nullptr,
                                    IterationCompositeOperation::Replace, 0.5,
                                    0)
          .Consume();
  ASSERT_TRUE(composedImplicit);
  EXPECT_FLOAT_EQ(0.45f, AnimationValue(composedImplicit).GetOpacity());
  EXPECT_NE(AnimationValue(concrete).GetOpacity(),
            AnimationValue(composedImplicit).GetOpacity());

  effect = nullptr;
  Rust_CheckTransitionEndpoint(oldFrom, 0.2f, 0);
  Rust_CheckTransitionEndpoint(oldTo, 0.8f, 1);
}

static void RegisterEndpointNumber(ServoStyleSet* aStyleSet,
                                   const nsCString& aName) {
  PropertyDefinition definition;
  definition.mName = aName;
  definition.mSyntax.AssignLiteral("<number>");
  definition.mInherits = false;
  definition.mInitialValue.Construct().AssignLiteral("10");
  ErrorResult error;
  aStyleSet->RegisterProperty(definition, error);
  ASSERT_EQ(NS_OK, error.StealNSResult());
}

static void AppendCustomEndpoint(Document* aDocument,
                                 nsTArray<Keyframe>& aKeyframes,
                                 const nsCString& aName, const char* aValue,
                                 double aOffset) {
  RefPtr<StyleLockedDeclarationBlock> block =
      Servo_DeclarationBlock_CreateEmpty().Consume();
  const nsCString value(aValue);
  ASSERT_TRUE(Servo_DeclarationBlock_SetProperty(
      block, &aName, &value, false, aDocument->DefaultStyleAttrURLData(),
      StyleParsingMode::DEFAULT, eCompatibility_FullStandards, nullptr,
      StyleCssRuleType::Style, {}));
  auto& keyframe = *aKeyframes.AppendElement();
  keyframe.mComputedOffset = aOffset;
  keyframe.mPropertyValues.AppendElement(PropertyValuePair(
      CSSPropertyId::FromCustomProperty(aName), std::move(block)));
}

static void ExpectResolvedEndpoint(ServoStyleSet* aStyleSet, Element* aTarget,
                                   const ComputedStyle* aProviders,
                                   const StyleKeyframeEndpoint* aEndpoint,
                                   const nsCString& aName,
                                   const char* aExpected,
                                   bool aAttributes = false) {
  auto status = StyleEndpointResolutionStatus::UnsupportedDeclaration;
  bool referencesAttributes = !aAttributes;
  RefPtr<StyleAnimationValue> value =
      Servo_KeyframeEndpoint_ResolveRegistered(
          aEndpoint, aTarget, PseudoStyleType::NotPseudo, aProviders,
          aStyleSet->RawData(), &status, &referencesAttributes)
          .Consume();
  ASSERT_EQ(StyleEndpointResolutionStatus::Resolved, status);
  ASSERT_TRUE(value);
  EXPECT_EQ(aAttributes, referencesAttributes);
  auto property = CSSPropertyId::FromCustomProperty(aName);
  nsAutoCString serialized;
  Servo_AnimationValue_Serialize(value, &property, aStyleSet->RawData(),
                                 &serialized);
  EXPECT_STREQ(aExpected, serialized.get());
}

TEST_F(KeyframePresentation, RetainedEndpointCurrentProviders) {
  RefPtr<Element> target = mDocument->GetHtmlChildElement(nsGkAtoms::body);
  ASSERT_TRUE(target);
  auto* styleSet = mDocument->GetPresShell()->StyleSet();
  const nsCString name("--retained-consumer");
  ASSERT_NO_FATAL_FAILURE(RegisterEndpointNumber(styleSet, name));
  ErrorResult error;
  target->SetAttr(nsGkAtoms::style,
                  u"--retained-provider: 20; --retained-consumer: 99"_ns,
                  error);
  ASSERT_EQ(NS_OK, error.StealNSResult());
  RefPtr<const ComputedStyle> initial =
      nsComputedDOMStyle::GetComputedStyle(target);
  ASSERT_TRUE(initial);
  nsTArray<Keyframe> keyframes;
  ASSERT_NO_FATAL_FAILURE(AppendCustomEndpoint(
      mDocument, keyframes, name, "var(--retained-provider, 5)", 0));
  ASSERT_NO_FATAL_FAILURE(
      AppendCustomEndpoint(mDocument, keyframes, name, "30", 1));
  ASSERT_NO_FATAL_FAILURE(AppendCustomEndpoint(mDocument, keyframes, name,
                                               "var(--retained-provider)", 1));
  bool attributes = true;
  auto values = styleSet->GetComputedKeyframeValuesFor(keyframes, target, {},
                                                       initial, attributes);
  ASSERT_EQ(3u, values.Length());
  ASSERT_EQ(1u, values[0].Length());
  ASSERT_EQ(1u, values[1].Length());
  ASSERT_EQ(1u, values[2].Length());
  ASSERT_FALSE(attributes);
  RefPtr<StyleKeyframeEndpoint> from = values[0][0].mEndpoint;
  RefPtr<StyleKeyframeEndpoint> to = values[1][0].mEndpoint;
  ASSERT_TRUE(from);
  ASSERT_TRUE(to);
  RefPtr<StyleKeyframeEndpoint> withoutFallback = values[2][0].mEndpoint;
  ASSERT_TRUE(withoutFallback);
  RefPtr<StyleAnimationValue> originalValue = values[0][0].mValue.mServo;
  ASSERT_TRUE(originalValue);
  values.Clear();
  keyframes.Clear();
  const struct {
    const char16_t* style;
    const char* expected;
  } cases[] = {
      {u"--retained-provider: 20; --retained-consumer: 99", "20"},
      {u"--retained-provider: red !important; --retained-consumer: 99", "10"},
      {u"--retained-consumer: 99", "5"},
      {u"--retained-provider: var(--leaf); --leaf: 40; --retained-consumer: 99",
       "40"},
      {u"--retained-provider: var(--leaf); --leaf: var(--retained-provider); "
       u"--retained-consumer: 99",
       "5"},
      {u"--retained-provider: 20; --retained-consumer: 99", "20"},
  };
  for (const auto& test : cases) {
    target->SetAttr(nsGkAtoms::style, nsDependentString(test.style), error);
    ASSERT_EQ(NS_OK, error.StealNSResult());
    RefPtr<const ComputedStyle> providers =
        nsComputedDOMStyle::GetComputedStyle(target);
    ASSERT_TRUE(providers);
    ASSERT_NO_FATAL_FAILURE(ExpectResolvedEndpoint(styleSet, target, providers,
                                                   from, name, test.expected));
    ASSERT_NO_FATAL_FAILURE(
        ExpectResolvedEndpoint(styleSet, target, providers, to, name, "30"));
    ASSERT_NO_FATAL_FAILURE(ExpectResolvedEndpoint(
        styleSet, target, providers, withoutFallback, name,
        nsDependentCString(test.expected).EqualsLiteral("5") ? "10"
                                                             : test.expected));
    ASSERT_NO_FATAL_FAILURE(ExpectResolvedEndpoint(styleSet, target, providers,
                                                   from, name, test.expected));
  }
  ASSERT_NO_FATAL_FAILURE(
      ExpectResolvedEndpoint(styleSet, target, initial, from, name, "20"));
  auto property = CSSPropertyId::FromCustomProperty(name);
  nsAutoCString original;
  Servo_AnimationValue_Serialize(originalValue, &property, styleSet->RawData(),
                                 &original);
  EXPECT_STREQ("20", original.get());
}

TEST_F(KeyframePresentation, RetainedEndpointIsolationAndAttributes) {
  RefPtr<Element> target = mDocument->GetHtmlChildElement(nsGkAtoms::body);
  ASSERT_TRUE(target);
  auto* styleSet = mDocument->GetPresShell()->StyleSet();
  const nsCString name("--isolated-consumer");
  ASSERT_NO_FATAL_FAILURE(RegisterEndpointNumber(styleSet, name));
  ErrorResult error;
  target->SetAttr(nsGkAtoms::style,
                  u"--isolated-consumer: 99; --provider: red"_ns, error);
  ASSERT_EQ(NS_OK, error.StealNSResult());
  const RefPtr<nsAtom> attribute = NS_Atomize("data-endpoint");
  target->SetAttr(attribute, u"20"_ns, error);
  ASSERT_EQ(NS_OK, error.StealNSResult());
  RefPtr<const ComputedStyle> providers =
      nsComputedDOMStyle::GetComputedStyle(target);
  ASSERT_TRUE(providers);
  nsTArray<Keyframe> keyframes;
  ASSERT_NO_FATAL_FAILURE(AppendCustomEndpoint(
      mDocument, keyframes, name, "attr(data-endpoint type(<number>))", 0));
  ASSERT_NO_FATAL_FAILURE(
      AppendCustomEndpoint(mDocument, keyframes, name, "var(--provider)", 1));
  ASSERT_NO_FATAL_FAILURE(AppendCustomEndpoint(mDocument, keyframes, name,
                                               "var(--isolated-consumer)", 1));
  bool attributes = false;
  auto values = styleSet->GetComputedKeyframeValuesFor(keyframes, target, {},
                                                       providers, attributes);
  ASSERT_EQ(3u, values.Length());
  for (const auto& frame : values) {
    ASSERT_EQ(1u, frame.Length());
    ASSERT_TRUE(frame[0].mEndpoint);
  }
  ASSERT_TRUE(attributes);
  RefPtr<StyleKeyframeEndpoint> attrEndpoint = values[0][0].mEndpoint;
  RefPtr<StyleKeyframeEndpoint> invalidEndpoint = values[1][0].mEndpoint;
  RefPtr<StyleKeyframeEndpoint> providerEndpoint = values[2][0].mEndpoint;
  ASSERT_NO_FATAL_FAILURE(ExpectResolvedEndpoint(
      styleSet, target, providers, attrEndpoint, name, "20", true));
  target->SetAttr(attribute, u"40"_ns, error);
  ASSERT_EQ(NS_OK, error.StealNSResult());
  ASSERT_NO_FATAL_FAILURE(ExpectResolvedEndpoint(styleSet, target, providers,
                                                 invalidEndpoint, name, "10"));
  ASSERT_NO_FATAL_FAILURE(ExpectResolvedEndpoint(styleSet, target, providers,
                                                 providerEndpoint, name, "99"));
  ASSERT_NO_FATAL_FAILURE(ExpectResolvedEndpoint(
      styleSet, target, providers, attrEndpoint, name, "40", true));
  ASSERT_NO_FATAL_FAILURE(ExpectResolvedEndpoint(styleSet, target, providers,
                                                 providerEndpoint, name, "99"));

  nsTArray<Keyframe> ordinary;
  ASSERT_NO_FATAL_FAILURE(AppendOpacityKeyframe(mDocument, ordinary, "0.4", 0));
  auto ordinaryValues = styleSet->GetComputedKeyframeValuesFor(
      ordinary, target, {}, providers, attributes);
  ASSERT_EQ(1u, ordinaryValues.Length());
  ASSERT_EQ(1u, ordinaryValues[0].Length());
  ASSERT_TRUE(ordinaryValues[0][0].mEndpoint);
  auto status = StyleEndpointResolutionStatus::Resolved;
  RefPtr<StyleAnimationValue> unsupported =
      Servo_KeyframeEndpoint_ResolveRegistered(
          ordinaryValues[0][0].mEndpoint, target, PseudoStyleType::NotPseudo,
          providers, styleSet->RawData(), &status, &attributes)
          .Consume();
  EXPECT_FALSE(unsupported);
  EXPECT_EQ(StyleEndpointResolutionStatus::NotRegisteredCustomProperty, status);
  ASSERT_NO_FATAL_FAILURE(ExpectResolvedEndpoint(styleSet, target, providers,
                                                 providerEndpoint, name, "99"));
  ASSERT_NO_FATAL_FAILURE(ExpectResolvedEndpoint(styleSet, target, providers,
                                                 invalidEndpoint, name, "10"));
}

TEST_F(KeyframePresentation, RetainedEndpointProviderDemand) {
  RefPtr<Element> target = mDocument->GetHtmlChildElement(nsGkAtoms::body);
  ASSERT_TRUE(target);
  auto* styleSet = mDocument->GetPresShell()->StyleSet();
  const nsCString name("--demand-consumer");
  ASSERT_NO_FATAL_FAILURE(RegisterEndpointNumber(styleSet, name));
  const nsCString lengthName("--demand-length");
  PropertyDefinition lengthDefinition;
  lengthDefinition.mName = lengthName;
  lengthDefinition.mSyntax.AssignLiteral("<length>");
  lengthDefinition.mInherits = false;
  lengthDefinition.mInitialValue.Construct().AssignLiteral("10px");
  ErrorResult error;
  styleSet->RegisterProperty(lengthDefinition, error);
  ASSERT_EQ(NS_OK, error.StealNSResult());
  target->SetAttr(
      nsGkAtoms::style,
      u"font-size: 20px; --provider: 20; --ready: 20; --wrong: red; --demand-consumer: 99"_ns,
      error);
  ASSERT_EQ(NS_OK, error.StealNSResult());
  target->SetAttr(kNameSpaceID_None, nsGkAtoms::data, u"40"_ns, true);
  RefPtr<const ComputedStyle> providers =
      nsComputedDOMStyle::GetComputedStyle(target);
  ASSERT_TRUE(providers);
  using Status = StyleEndpointDemandStatus;
  const struct {
    const char* input;
    const char* pending;
    Status status;
    const char* expected;
    const char* demanded;
    const char* attribute = "40";
    bool pendingFontSize = false;
    bool length = false;
  } cases[] = {
      {"var(--provider, 5)", "--provider", Status::Provider, nullptr,
       "provider"},
      {"var(--provider, 5)", "", Status::Resolved, "20", ""},
      {"var(--ready, var(--provider))", "--provider", Status::Resolved, "20",
       ""},
      {"var(--missing, var(--provider))", "--provider", Status::Provider,
       nullptr, "provider"},
      {"var(--wrong, var(--provider))", "--provider", Status::Resolved, "10",
       ""},
      {"calc(var(--missing) + var(--provider))", "--provider", Status::Resolved,
       "10", ""},
      {"calc(var(--provider) + var(--missing))", "--provider", Status::Provider,
       nullptr, "provider"},
      {"attr(data type(<number>))", "--provider", Status::Resolved, "40", ""},
      {"attr(data type(<number>))", "", Status::Resolved, "40", ""},
      {"var(--ready, attr(data type(<number>)))", "--provider",
       Status::Resolved, "20", "", "var(--provider)"},
      {"var(--missing, attr(data type(<number>)))", "--provider",
       Status::Provider, nullptr, "provider", "var(--provider)"},
      {"attr(data type(<number>))", "--provider", Status::Provider, nullptr,
       "provider", "var(--provider)"},
      {"attr(data type(<number>))", "--unrelated", Status::Resolved, "20", "",
       "var(--ready, var(--provider))"},
      {"attr(data type(<number>), 7)", "--provider", Status::Provider, nullptr,
       "provider", "var(--provider)"},
      {"attr(data type(<number>), 7)", "--unrelated", Status::Resolved, "7", "",
       "var(--missing)"},
      {"attr(data type(<number>), 7)", "--unrelated", Status::Resolved, "7", "",
       nullptr},
      {"attr(data type(<number>))", "--unrelated", Status::Resolved, "10", "",
       nullptr},
      {"attr(data type(<number>))", "--provider", Status::Provider, nullptr,
       "provider", "attr(title type(<number>))"},
      {"attr(data type(<number>), 7)", "--unrelated", Status::Resolved, "7", "",
       "attr(data type(<number>), 9)"},
      {"attr(data type(<length>))", "--unrelated", Status::Prioritary, nullptr,
       "font-size", "2em", true, true},
      {"attr(data type(<length>))", "--unrelated", Status::Resolved, "40px", "",
       "2em", false, true},
      {"var(--provider)", "", Status::Resolved, "20", ""},
  };
  for (const auto& test : cases) {
    target->SetAttr(kNameSpaceID_None, nsGkAtoms::data, u"40"_ns, true);
    target->SetAttr(kNameSpaceID_None, nsGkAtoms::title, u"var(--provider)"_ns,
                    true);
    const nsCString& testName = test.length ? lengthName : name;
    nsTArray<Keyframe> keyframes;
    ASSERT_NO_FATAL_FAILURE(
        AppendCustomEndpoint(mDocument, keyframes, testName, test.input, 0));
    bool attributes = false;
    auto values = styleSet->GetComputedKeyframeValuesFor(keyframes, target, {},
                                                         providers, attributes);
    ASSERT_EQ(1u, values.Length());
    ASSERT_EQ(1u, values[0].Length());
    RefPtr<StyleKeyframeEndpoint> endpoint = values[0][0].mEndpoint;
    ASSERT_TRUE(endpoint);
    if (test.attribute) {
      target->SetAttr(kNameSpaceID_None, nsGkAtoms::data,
                      NS_ConvertUTF8toUTF16(test.attribute), true);
    } else {
      target->UnsetAttr(kNameSpaceID_None, nsGkAtoms::data, true);
    }
    const nsCString pending(test.pending);
    nsAutoCString demanded;
    auto status = Status::Unsupported;
    RefPtr<StyleAnimationValue> value =
        Servo_KeyframeEndpoint_ResolvePendingForTesting(
            endpoint, target, PseudoStyleType::NotPseudo, providers,
            styleSet->RawData(), &pending, test.pendingFontSize, &demanded,
            &status, &attributes)
            .Consume();
    EXPECT_EQ(test.status, status) << test.input;
    EXPECT_STREQ(test.demanded, demanded.get()) << test.input;
    if (test.expected) {
      ASSERT_TRUE(value);
      auto property = CSSPropertyId::FromCustomProperty(testName);
      nsAutoCString serialized;
      Servo_AnimationValue_Serialize(value, &property, styleSet->RawData(),
                                     &serialized);
      EXPECT_STREQ(test.expected, serialized.get()) << test.input;
    } else {
      EXPECT_FALSE(value);
    }
  }
}

static void ExpectPendingNumberResolution(
    ServoStyleSet* aStyleSet, Element* aTarget, const ComputedStyle* aProviders,
    const StyleKeyframeEndpoint* aEndpoint, const nsCString& aName,
    const char* aPending, bool aPendingFontSize,
    StyleEndpointDemandStatus aExpectedStatus, const char* aExpectedValue,
    const char* aExpectedDemand) {
  const nsCString pending(aPending);
  nsAutoCString demanded;
  auto status = StyleEndpointDemandStatus::Unsupported;
  bool attributes = true;
  RefPtr<StyleAnimationValue> value =
      Servo_KeyframeEndpoint_ResolvePendingForTesting(
          aEndpoint, aTarget, PseudoStyleType::NotPseudo, aProviders,
          aStyleSet->RawData(), &pending, aPendingFontSize, &demanded, &status,
          &attributes)
          .Consume();
  ASSERT_EQ(aExpectedStatus, status);
  ASSERT_STREQ(aExpectedDemand, demanded.get());
  ASSERT_FALSE(attributes);
  if (aExpectedValue) {
    ASSERT_TRUE(value);
    auto property = CSSPropertyId::FromCustomProperty(aName);
    nsAutoCString serialized;
    Servo_AnimationValue_Serialize(value, &property, aStyleSet->RawData(),
                                   &serialized);
    EXPECT_STREQ(aExpectedValue, serialized.get());
  } else {
    EXPECT_FALSE(value);
  }
}

TEST_F(KeyframePresentation, RegisteredNumberAdmissionDemand) {
  RefPtr<Element> target = mDocument->GetHtmlChildElement(nsGkAtoms::body);
  ASSERT_TRUE(target);
  RefPtr<Element> parent = target->GetParentElement();
  ASSERT_TRUE(parent);
  auto* styleSet = mDocument->GetPresShell()->StyleSet();
  const nsCString name("--number-admission");
  ASSERT_NO_FATAL_FAILURE(RegisterEndpointNumber(styleSet, name));
  ErrorResult error;
  parent->SetAttr(nsGkAtoms::style, u"--number-admission: 17"_ns, error);
  ASSERT_EQ(NS_OK, error.StealNSResult());
  target->SetAttr(nsGkAtoms::style,
                  u"font-size: 20px; --ready: 5; --wrong: red; --provider: 20; "
                  u"--number-admission: 99"_ns,
                  error);
  ASSERT_EQ(NS_OK, error.StealNSResult());
  RefPtr<const ComputedStyle> providers =
      nsComputedDOMStyle::GetComputedStyle(target);
  ASSERT_TRUE(providers);
  using Status = StyleEndpointDemandStatus;
  const struct {
    const char* label;
    const char* input;
    const char* pending;
    Status status;
    const char* expected;
    const char* demanded;
  } cases[] = {
      {"invalid-direct-length", "1em", "", Status::Resolved, "10", ""},
      {"invalid-selected-length", "var(--missing, 1em)", "", Status::Resolved,
       "10", ""},
      {"ready-primary-unused-length", "var(--ready, 1em)", "", Status::Resolved,
       "5", ""},
      {"wrong-primary-unused-length", "var(--wrong, 1em)", "", Status::Resolved,
       "10", ""},
      {"nested-ready-primary", "var(--missing, var(--ready, 1em))", "",
       Status::Resolved, "5", ""},
      {"unused-admitted-math", "var(--ready, calc(1em / 1px))", "",
       Status::Resolved, "5", ""},
      {"pending-provider-masks-cache", "var(--provider, 1em)", "--provider",
       Status::Provider, nullptr, "provider"},
      {"substituted-inherit", "var(--missing, inherit)", "", Status::Resolved,
       "17", ""},
      {"substituted-initial", "var(--missing, initial)", "", Status::Resolved,
       "10", ""},
  };
  for (const auto& test : cases) {
    SCOPED_TRACE(test.label);
    nsTArray<Keyframe> keyframes;
    ASSERT_NO_FATAL_FAILURE(
        AppendCustomEndpoint(mDocument, keyframes, name, test.input, 0));
    bool attributes = true;
    auto values = styleSet->GetComputedKeyframeValuesFor(keyframes, target, {},
                                                         providers, attributes);
    ASSERT_EQ(1u, values.Length());
    ASSERT_EQ(1u, values[0].Length());
    ASSERT_FALSE(attributes);
    RefPtr<StyleKeyframeEndpoint> endpoint = values[0][0].mEndpoint;
    ASSERT_TRUE(endpoint);
    ASSERT_NO_FATAL_FAILURE(ExpectPendingNumberResolution(
        styleSet, target, providers, endpoint, name, test.pending, true,
        test.status, test.expected, test.demanded));
  }
}

TEST_F(KeyframePresentation, RegisteredNumberMathDemandCompletion) {
  RefPtr<Element> target = mDocument->GetHtmlChildElement(nsGkAtoms::body);
  ASSERT_TRUE(target);
  auto* styleSet = mDocument->GetPresShell()->StyleSet();
  const nsCString name("--number-math");
  ASSERT_NO_FATAL_FAILURE(RegisterEndpointNumber(styleSet, name));
  ErrorResult error;
  target->SetAttr(nsGkAtoms::style, u"font-size: 20px; --number-math: 99"_ns,
                  error);
  ASSERT_EQ(NS_OK, error.StealNSResult());
  RefPtr<const ComputedStyle> initial =
      nsComputedDOMStyle::GetComputedStyle(target);
  ASSERT_TRUE(initial);
  nsTArray<Keyframe> keyframes;
  ASSERT_NO_FATAL_FAILURE(
      AppendCustomEndpoint(mDocument, keyframes, name, "calc(1em / 1px)", 0));
  bool attributes = true;
  auto values = styleSet->GetComputedKeyframeValuesFor(keyframes, target, {},
                                                       initial, attributes);
  ASSERT_EQ(1u, values.Length());
  ASSERT_EQ(1u, values[0].Length());
  ASSERT_FALSE(attributes);
  RefPtr<StyleKeyframeEndpoint> endpoint = values[0][0].mEndpoint;
  RefPtr<StyleAnimationValue> original = values[0][0].mValue.mServo;
  ASSERT_TRUE(endpoint);
  ASSERT_TRUE(original);
  values.Clear();
  keyframes.Clear();
  using Status = StyleEndpointDemandStatus;
  ASSERT_NO_FATAL_FAILURE(ExpectPendingNumberResolution(
      styleSet, target, initial, endpoint, name, "", true, Status::Prioritary,
      nullptr, "font-size"));
  ASSERT_NO_FATAL_FAILURE(ExpectPendingNumberResolution(
      styleSet, target, initial, endpoint, name, "--unrelated", false,
      Status::Resolved, "20", ""));
  target->SetAttr(nsGkAtoms::style, u"font-size: 30px; --number-math: 99"_ns,
                  error);
  ASSERT_EQ(NS_OK, error.StealNSResult());
  RefPtr<const ComputedStyle> completed =
      nsComputedDOMStyle::GetComputedStyle(target);
  ASSERT_TRUE(completed);
  ASSERT_NO_FATAL_FAILURE(ExpectPendingNumberResolution(
      styleSet, target, completed, endpoint, name, "--unrelated", false,
      Status::Resolved, "30", ""));
  auto property = CSSPropertyId::FromCustomProperty(name);
  nsAutoCString serialized;
  Servo_AnimationValue_Serialize(original, &property, styleSet->RawData(),
                                 &serialized);
  EXPECT_STREQ("20", serialized.get());
}

}  // namespace
