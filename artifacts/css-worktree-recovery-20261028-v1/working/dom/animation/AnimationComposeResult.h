/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

#ifndef mozilla_AnimationComposeResult_h
#define mozilla_AnimationComposeResult_h

#include "mozilla/Variant.h"

namespace mozilla {

struct StyleAnimationValueMap;
struct StyleAnimationRuleSample;

// Both pointers borrow the caller-owned sink for synchronous composition only.
using AnimationComposeResult =
    Variant<StyleAnimationValueMap*, StyleAnimationRuleSample*>;

}  // namespace mozilla

#endif
