/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */

#include "mozilla/dom/quota/ArtificialFailure.h"

#include "mozilla/Result.h"
#include "mozilla/StaticPrefs_dom.h"
#include "mozilla/dom/quota/ArtificialFailureChecks.h"

namespace mozilla::dom::quota {

Result<Ok, nsresult> ArtificialFailure(
    nsIQuotaArtificialFailure::Category aCategory) {
  MOZ_ASSERT(aCategory != 0 && ((aCategory & (aCategory - 1)) == 0));

  if ((StaticPrefs::dom_quotaManager_artificialFailure_categories() &
       aCategory) == 0) {
    return Ok{};
  }

  uint32_t probability =
      StaticPrefs::dom_quotaManager_artificialFailure_probability();
  if (probability == 0) {
    return Ok{};
  }

  uint32_t randomValue = std::rand() % 100;
  if (randomValue >= probability) {
    return Ok{};
  }

  uint32_t errorCode =
      StaticPrefs::dom_quotaManager_artificialFailure_errorCode();

  nsresult rv = static_cast<nsresult>(errorCode);
  return Err(rv);
}

Result<Ok, nsresult> CheckDatabaseFileRemovalFailure() {
  return ArtificialFailure(
      nsIQuotaArtificialFailure::CATEGORY_REMOVE_DATABASE_FILES);
}

Result<Ok, nsresult> CheckDirectoryMetadataCreationFailure() {
  return ArtificialFailure(
      nsIQuotaArtificialFailure::CATEGORY_CREATE_DIRECTORY_METADATA2);
}

Result<Ok, nsresult> CheckOriginInitializationFailure() {
  return ArtificialFailure(
      nsIQuotaArtificialFailure::CATEGORY_INITIALIZE_ORIGIN);
}

Result<Ok, nsresult> CheckClientDirectoryOpenFailure() {
  return ArtificialFailure(
      nsIQuotaArtificialFailure::CATEGORY_OPEN_CLIENT_DIRECTORY);
}

}  // namespace mozilla::dom::quota
