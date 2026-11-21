/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

#ifndef DOM_QUOTA_ARTIFICIALFAILURECHECKS_H_
#define DOM_QUOTA_ARTIFICIALFAILURECHECKS_H_

#include "mozilla/dom/quota/ForwardDecls.h"

namespace mozilla::dom::quota {

Result<Ok, nsresult> CheckDatabaseFileRemovalFailure();

}  // namespace mozilla::dom::quota

#endif  // DOM_QUOTA_ARTIFICIALFAILURECHECKS_H_
