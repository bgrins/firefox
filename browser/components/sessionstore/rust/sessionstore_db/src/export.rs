/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

//! Writes the session state as a JSON session file, compressed the way
//! IOUtils compresses with `compress: true`: an 8 byte magic number, the
//! uncompressed size as a little endian u32, then one LZ4 block.

use std::{
    fs,
    io::{self, ErrorKind},
};

use nsstring::nsCString;
use serde::de::IgnoredAny;
use storage::Conn;

use crate::{
    assemble,
    error::{Error, Result},
};

const MAGIC_NUMBER: &[u8; 8] = b"mozLz40\0";
const HEADER_SIZE: usize = MAGIC_NUMBER.len() + 4;

extern "C" {
    fn sessionstore_lz4_max_compressed_size(input_size: usize) -> usize;
    fn sessionstore_lz4_compress(source: *const u8, input_size: usize, dest: *mut u8) -> usize;
}

/// Writes the file to `tmp_path`, moves the file at `path` to `backup_path`
/// if one is given, then moves the new file to `path`. Returns the size of the
/// file.
pub fn export(conn: &Conn, path: &str, tmp_path: &str, backup_path: &str) -> Result<nsCString> {
    let mut json = Vec::new();
    assemble::write_state(conn, false, 0, &mut json)?.ok_or(Error::NoState)?;
    // The assembler only checks the structure, and a file that doesn't parse
    // would lose the session.
    serde_json::from_slice::<IgnoredAny>(&json)
        .map_err(|err| Error::InvalidFragment(err.to_string()))?;

    let contents = compress(&json)?;
    drop(json);
    fs::write(tmp_path, &contents)?;
    if !backup_path.is_empty() {
        match fs::rename(path, backup_path) {
            Err(err) if err.kind() != ErrorKind::NotFound => return Err(err.into()),
            _ => {}
        }
    }
    fs::rename(tmp_path, path)?;
    Ok(nsCString::from(contents.len().to_string()))
}

fn compress(data: &[u8]) -> Result<Vec<u8>> {
    let size = u32::try_from(data.len()).map_err(|_| Error::OutOfMemory)?;
    let bound = unsafe { sessionstore_lz4_max_compressed_size(data.len()) };
    let mut out = Vec::new();
    out.try_reserve_exact(HEADER_SIZE + bound)
        .map_err(|_| Error::OutOfMemory)?;
    out.extend_from_slice(MAGIC_NUMBER);
    out.extend_from_slice(&size.to_le_bytes());
    // The capacity holds the header and the largest block LZ4 can produce.
    let written = unsafe {
        sessionstore_lz4_compress(data.as_ptr(), data.len(), out.as_mut_ptr().add(HEADER_SIZE))
    };
    if written == 0 {
        return Err(io::Error::other("LZ4 compression failed").into());
    }
    unsafe { out.set_len(HEADER_SIZE + written) };
    Ok(out)
}
