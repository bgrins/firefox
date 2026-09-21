/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

#ifndef mozilla_sessionstore_SessionStoreDatabase_h_
#define mozilla_sessionstore_SessionStoreDatabase_h_

#include "nsError.h"
#include "nsID.h"

extern "C" {

// Implemented in Rust, in the `sessionstore_db` crate.
nsresult NS_NewSessionStoreDatabase(REFNSIID aIID, void** aResult);

}  // extern "C"

#endif  // mozilla_sessionstore_SessionStoreDatabase_h_
