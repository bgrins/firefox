/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

#include "mozilla/Compression.h"

using mozilla::Compression::LZ4;

// LZ4 for the sessionstore_db crate, which exports the session file in the
// format that IOUtils writes with `compress: true`.
extern "C" {

size_t sessionstore_lz4_max_compressed_size(size_t aInputSize) {
  return LZ4::maxCompressedSize(aInputSize);
}

size_t sessionstore_lz4_compress(const char* aSource, size_t aInputSize,
                                 char* aDest) {
  return LZ4::compress(aSource, aInputSize, aDest);
}
}
