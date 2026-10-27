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
#include "mozilla/dom/Document.h"
#include "mozilla/dom/Element.h"
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

}  // namespace
