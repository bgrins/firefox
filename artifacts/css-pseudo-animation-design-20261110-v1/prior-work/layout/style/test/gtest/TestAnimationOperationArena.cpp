/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

#include "ReferrerInfo.h"
#include "gtest/gtest.h"
#include "mozilla/AnimationPropertySegment.h"
#include "mozilla/NullPrincipal.h"
#include "mozilla/ServoStyleConsts.h"
#include "mozilla/URLExtraData.h"

using namespace mozilla;
using namespace mozilla::net;

extern "C" void Rust_RunAnimationOperationArenaCases(URLExtraData*,
                                                     URLExtraData*);

static RefPtr<URLExtraData> CreateArenaURLData() {
  RefPtr<nsIURI> uri = NullPrincipal::CreateURI();
  nsCOMPtr<nsIReferrerInfo> referrerInfo = new ReferrerInfo(nullptr);
  return MakeRefPtr<URLExtraData>(
      uri.forget(), referrerInfo.forget(),
      NullPrincipal::CreateWithoutOriginAttributes());
}

TEST(AnimationOperationArena, NativeArithmeticAndMetadata)
{
  auto left = CreateArenaURLData();
  auto right = CreateArenaURLData();
  ASSERT_NE(left.get(), right.get());
  Rust_RunAnimationOperationArenaCases(left, right);
}

extern "C" void Rust_RunAnimationOperationArenaDifferential(URLExtraData*,
                                                            URLExtraData*);
extern "C" void Rust_CompareAnimationOperationArenaValues(const void*,
                                                          const void*);

extern "C" void GTest_CompareAnimationSegment(
    const char* aLabel, void* aFrom, void* aTo, void* aUnderlying, void* aLast,
    dom::CompositeOperation aFromComposite,
    dom::CompositeOperation aToComposite,
    dom::IterationCompositeOperation aIteration, uint64_t aCount,
    double aProgress, bool aSameOffset, const void* aExpected) {
  SCOPED_TRACE(aLabel);
  // The Rust caller holds genuine servo_arc allocations through this call.
  RefPtr<StyleAnimationValue> from = static_cast<StyleAnimationValue*>(aFrom);
  RefPtr<StyleAnimationValue> to = static_cast<StyleAnimationValue*>(aTo);
  RefPtr<StyleAnimationValue> underlying =
      static_cast<StyleAnimationValue*>(aUnderlying);
  RefPtr<StyleAnimationValue> last = static_cast<StyleAnimationValue*>(aLast);
  AnimationPropertySegment segment;
  segment.mFromKey = 0.0;
  segment.mToKey = aSameOffset ? 0.0 : 1.0;
  segment.mFromValue = AnimationValue(from);
  segment.mToValue = AnimationValue(to);
  segment.mFromComposite = aFromComposite;
  segment.mToComposite = aToComposite;
  RefPtr<StyleAnimationValue> actual =
      Servo_ComposeAnimationSegment(&segment, underlying, last, aIteration,
                                    aProgress, aCount)
          .Consume();
  ASSERT_TRUE(actual);
  // Both borrows end before their C++ or Rust owners leave this synchronous
  // call.
  Rust_CompareAnimationOperationArenaValues(actual, aExpected);
}

TEST(AnimationOperationArena, NativeDifferential)
{
  auto left = CreateArenaURLData();
  auto right = CreateArenaURLData();
  ASSERT_NE(left.get(), right.get());
  Rust_RunAnimationOperationArenaDifferential(left, right);
}

extern "C" void Rust_AnimationRuleSample_FrozenOwnership();

TEST(AnimationRuleSample, FrozenOwnership)
{
  Rust_AnimationRuleSample_FrozenOwnership();
}

extern "C" void Rust_AnimationRuleSample_AdditiveRecipe();

TEST(AnimationRuleSample, AdditiveRecipe)
{
  Rust_AnimationRuleSample_AdditiveRecipe();
}

extern "C" void Rust_AnimationRuleSample_Replacement();

TEST(AnimationRuleSample, Replacement)
{
  Rust_AnimationRuleSample_Replacement();
}

extern "C" void Rust_AnimationRuleSample_EndpointError();

TEST(AnimationRuleSample, EndpointError)
{
  Rust_AnimationRuleSample_EndpointError();
}

extern "C" void Rust_AnimationRuleSample_MissingUnderlying();

TEST(AnimationRuleSample, MissingUnderlying)
{
  Rust_AnimationRuleSample_MissingUnderlying();
}

extern "C" void Rust_AnimationRuleSample_ConcreteBulk();

TEST(AnimationRuleSample, ConcreteBulk)
{
  Rust_AnimationRuleSample_ConcreteBulk();
}

extern "C" void Rust_AnimationRuleSample_RepeatedRoots();

TEST(AnimationRuleSample, RepeatedRoots)
{
  Rust_AnimationRuleSample_RepeatedRoots();
}

extern "C" void Rust_AnimationRuleSample_InvalidRoots();

TEST(AnimationRuleSample, InvalidRoots)
{
  Rust_AnimationRuleSample_InvalidRoots();
}

extern "C" void Rust_AnimationRuleSample_OwnerIdentity();

TEST(AnimationRuleSample, OwnerIdentity)
{
  Rust_AnimationRuleSample_OwnerIdentity();
}

extern "C" void Rust_AnimationRuleSample_OwnerLifetime();

TEST(AnimationRuleSample, OwnerLifetime)
{
  Rust_AnimationRuleSample_OwnerLifetime();
}

extern "C" void Rust_AnimationRuleSample_OwnerLayout();

TEST(AnimationRuleSample, OwnerLayout)
{
  Rust_AnimationRuleSample_OwnerLayout();
}

extern "C" void Rust_KeyframeEndpoint_OwnedSourceAssociation(URLExtraData*,
                                                            URLExtraData*);

TEST(KeyframeEndpoint, OwnedSourceAssociation)
{
  auto left = CreateArenaURLData();
  auto right = CreateArenaURLData();
  ASSERT_NE(left.get(), right.get());
  Rust_KeyframeEndpoint_OwnedSourceAssociation(left, right);
}

extern "C" void Rust_AnimationRuleSample_MetadataBulk(URLExtraData*,
                                                      URLExtraData*);

TEST(AnimationRuleSample, MetadataBulk)
{
  auto left = CreateArenaURLData();
  auto right = CreateArenaURLData();
  ASSERT_NE(left.get(), right.get());
  Rust_AnimationRuleSample_MetadataBulk(left, right);
}
