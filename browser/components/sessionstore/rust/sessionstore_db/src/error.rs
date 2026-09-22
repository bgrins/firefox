/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

use std::{fmt, io::ErrorKind, result};

use nserror::{
    nsresult, NS_ERROR_ABORT, NS_ERROR_FAILURE, NS_ERROR_FILE_ACCESS_DENIED,
    NS_ERROR_FILE_CORRUPTED, NS_ERROR_FILE_NOT_FOUND, NS_ERROR_INVALID_ARG, NS_ERROR_NOT_AVAILABLE,
    NS_ERROR_NOT_INITIALIZED, NS_ERROR_OUT_OF_MEMORY, NS_ERROR_UNEXPECTED,
};

pub type Result<T> = result::Result<T, Error>;

#[derive(Debug)]
pub enum Error {
    /// The operation never ran on the connection's thread.
    DidNotRun,
    /// No connection was passed to `init`, or it was reset since.
    NotInitialized,
    Storage(storage::Error),
    /// The database has a schema version newer than this build can read.
    NewerSchema(i64),
    /// A batch contained a malformed operation.
    InvalidOp(String),
    /// A `guard` operation found a different value in `meta`.
    GuardMismatch {
        key: String,
        expected: String,
        actual: String,
    },
    /// A fragment isn't valid JSON, or isn't the kind of value its row needs.
    InvalidFragment(String),
    /// The rows don't form a session state.
    Corrupt(String),
    /// There is no session state to export.
    NoState,
    /// Writing the exported file failed.
    Io(std::io::Error),
    OutOfMemory,
}

impl From<std::io::Error> for Error {
    fn from(err: std::io::Error) -> Error {
        Error::Io(err)
    }
}

impl From<storage::Error> for Error {
    fn from(err: storage::Error) -> Error {
        Error::Storage(err)
    }
}

impl From<nsresult> for Error {
    fn from(rv: nsresult) -> Error {
        Error::Storage(rv.into())
    }
}

impl From<Error> for nsresult {
    fn from(err: Error) -> nsresult {
        match err {
            Error::DidNotRun => NS_ERROR_UNEXPECTED,
            Error::NotInitialized => NS_ERROR_NOT_INITIALIZED,
            Error::Storage(err) => err.into(),
            Error::NewerSchema(_) => NS_ERROR_NOT_AVAILABLE,
            Error::InvalidOp(_) => NS_ERROR_INVALID_ARG,
            Error::GuardMismatch { .. } => NS_ERROR_ABORT,
            Error::InvalidFragment(_) | Error::Corrupt(_) => NS_ERROR_FILE_CORRUPTED,
            Error::NoState => NS_ERROR_NOT_AVAILABLE,
            Error::Io(err) => match err.kind() {
                ErrorKind::NotFound => NS_ERROR_FILE_NOT_FOUND,
                ErrorKind::PermissionDenied => NS_ERROR_FILE_ACCESS_DENIED,
                _ => NS_ERROR_FAILURE,
            },
            Error::OutOfMemory => NS_ERROR_OUT_OF_MEMORY,
        }
    }
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Error::DidNotRun => f.write_str("Operation didn't run"),
            Error::NotInitialized => f.write_str("Database isn't initialized"),
            Error::Storage(err) => err.fmt(f),
            Error::NewerSchema(version) => write!(f, "Schema version {} is too new", version),
            Error::InvalidOp(message) => write!(f, "Invalid operation: {}", message),
            Error::GuardMismatch {
                key,
                expected,
                actual,
            } => write!(
                f,
                "Guard failed for {}: expected {:?}, found {:?}",
                key, expected, actual
            ),
            Error::InvalidFragment(message) => write!(f, "Invalid fragment: {}", message),
            Error::Corrupt(message) => write!(f, "Corrupt database: {}", message),
            Error::NoState => f.write_str("The database holds no session state"),
            Error::Io(err) => write!(f, "Export failed: {}", err),
            Error::OutOfMemory => f.write_str("Out of memory"),
        }
    }
}
