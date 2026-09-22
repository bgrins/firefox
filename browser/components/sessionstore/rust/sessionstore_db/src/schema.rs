/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

use storage::{Conn, TransactionBehavior};

use crate::error::{Error, Result};

pub const VERSION: i64 = 1;

const SCHEMA: &str = "
  CREATE TABLE meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
  ) STRICT;

  CREATE TABLE root (
    name TEXT PRIMARY KEY,
    payload TEXT NOT NULL
  ) STRICT;

  CREATE TABLE nodes (
    id INTEGER PRIMARY KEY,
    parent INTEGER NOT NULL,
    prop TEXT NOT NULL,
    payload TEXT
  ) STRICT;

  CREATE TABLE child_order (
    parent INTEGER NOT NULL,
    prop TEXT NOT NULL,
    ids TEXT NOT NULL,
    PRIMARY KEY (parent, prop)
  ) STRICT;

  CREATE TABLE sections (
    node INTEGER NOT NULL,
    name TEXT NOT NULL,
    payload TEXT NOT NULL,
    PRIMARY KEY (node, name)
  ) STRICT;
";

pub fn init(conn: &Conn) -> Result<i64> {
    // `page_size` only applies before the database has content, so it has to
    // come before switching to WAL, which writes the header.
    conn.exec("PRAGMA page_size = 4096")?;
    conn.exec("PRAGMA journal_mode = WAL")?;
    conn.exec("PRAGMA cache_size = -512")?;
    // Checkpoints aren't scheduled in idle yet, so bound the WAL to 1 MiB.
    conn.exec("PRAGMA wal_autocheckpoint = 256")?;

    match user_version(conn)? {
        0 => {
            let mut conn = conn.clone();
            let tx = conn.transaction_with_behavior(TransactionBehavior::Immediate)?;
            tx.exec(SCHEMA)?;
            tx.exec(format!("PRAGMA user_version = {}", VERSION))?;
            tx.commit()?;
        }
        VERSION => {}
        version if version > VERSION => return Err(Error::NewerSchema(version)),
        version => {
            return Err(Error::Corrupt(format!(
                "unknown schema version {}",
                version
            )))
        }
    }
    Ok(VERSION)
}

fn user_version(conn: &Conn) -> Result<i64> {
    let mut statement = conn.prepare("PRAGMA user_version")?;
    let version = match statement.step()? {
        Some(step) => step.get_by_index::<i64>(0)?,
        None => 0,
    };
    Ok(version)
}
