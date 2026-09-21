/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

use std::collections::{hash_map::Entry, HashMap};

use nsstring::nsCString;
use storage::{Conn, Statement, TransactionBehavior};

use crate::error::{Error, Result};

pub enum Op {
    Guard {
        key: nsCString,
        expected: nsCString,
    },
    Clear,
    Node {
        id: i64,
        parent: i64,
        prop: nsCString,
        payload: Option<nsCString>,
    },
    DeleteNode {
        id: i64,
    },
    Order {
        parent: i64,
        prop: nsCString,
        ids: nsCString,
    },
    DeleteOrder {
        parent: i64,
        prop: nsCString,
    },
    Section {
        node: i64,
        name: nsCString,
        payload: nsCString,
    },
    DeleteSection {
        node: i64,
        name: nsCString,
    },
    Root {
        name: nsCString,
        payload: nsCString,
    },
    DeleteRoot {
        name: nsCString,
    },
    Meta {
        key: nsCString,
        value: nsCString,
    },
}

/// Parses a batch flattened into strings, as described in
/// SessionStoreDB.sys.mjs. Strings are shared, not copied.
pub fn parse(args: &[nsCString]) -> Result<Vec<Op>> {
    let mut ops = Vec::new();
    let mut args = args.iter();
    while let Some(name) = args.next() {
        let mut next = || {
            args.next()
                .cloned()
                .ok_or_else(|| Error::InvalidOp(format!("missing argument for {}", name)))
        };
        let op = match &name[..] {
            b"guard" => Op::Guard {
                key: next()?,
                expected: next()?,
            },
            b"clear" => Op::Clear,
            b"node" => Op::Node {
                id: int(&next()?)?,
                parent: int(&next()?)?,
                prop: next()?,
                payload: Some(next()?),
            },
            b"nullnode" => Op::Node {
                id: int(&next()?)?,
                parent: int(&next()?)?,
                prop: next()?,
                payload: None,
            },
            b"delnode" => Op::DeleteNode { id: int(&next()?)? },
            b"order" => Op::Order {
                parent: int(&next()?)?,
                prop: next()?,
                ids: next()?,
            },
            b"delorder" => Op::DeleteOrder {
                parent: int(&next()?)?,
                prop: next()?,
            },
            b"section" => Op::Section {
                node: int(&next()?)?,
                name: next()?,
                payload: next()?,
            },
            b"delsection" => Op::DeleteSection {
                node: int(&next()?)?,
                name: next()?,
            },
            b"root" => Op::Root {
                name: next()?,
                payload: next()?,
            },
            b"delroot" => Op::DeleteRoot { name: next()? },
            b"meta" => Op::Meta {
                key: next()?,
                value: next()?,
            },
            _ => return Err(Error::InvalidOp(format!("unknown operation {}", name))),
        };
        ops.push(op);
    }
    Ok(ops)
}

fn int(value: &nsCString) -> Result<i64> {
    std::str::from_utf8(value)
        .ok()
        .and_then(|s| s.parse().ok())
        .ok_or_else(|| Error::InvalidOp(format!("{} isn't an integer", value)))
}

/// Applies a batch in one transaction. Dropping the transaction on an error
/// rolls the whole batch back.
pub fn apply(conn: &Conn, ops: Vec<Op>) -> Result<()> {
    let mut conn = conn.clone();
    let tx = conn.transaction_with_behavior(TransactionBehavior::Immediate)?;
    {
        let mut statements = Statements::new(&tx);
        for op in ops {
            statements.apply(op)?;
        }
    }
    tx.commit()?;
    Ok(())
}

const SELECT_META: &str = "SELECT value FROM meta WHERE key = ?1";
const UPSERT_NODE: &str = "INSERT INTO nodes(id, parent, prop, payload) VALUES(?1, ?2, ?3, ?4)
                           ON CONFLICT(id) DO UPDATE SET parent = excluded.parent,
                             prop = excluded.prop, payload = excluded.payload";
const DELETE_NODE: &str = "DELETE FROM nodes WHERE id = ?1";
const DELETE_NODE_SECTIONS: &str = "DELETE FROM sections WHERE node = ?1";
const DELETE_NODE_ORDERS: &str = "DELETE FROM child_order WHERE parent = ?1";
const UPSERT_ORDER: &str = "INSERT INTO child_order(parent, prop, ids) VALUES(?1, ?2, ?3)
                            ON CONFLICT(parent, prop) DO UPDATE SET ids = excluded.ids";
const DELETE_ORDER: &str = "DELETE FROM child_order WHERE parent = ?1 AND prop = ?2";
const UPSERT_SECTION: &str = "INSERT INTO sections(node, name, payload) VALUES(?1, ?2, ?3)
                              ON CONFLICT(node, name) DO UPDATE SET payload = excluded.payload";
const DELETE_SECTION: &str = "DELETE FROM sections WHERE node = ?1 AND name = ?2";
const UPSERT_ROOT: &str = "INSERT INTO root(name, payload) VALUES(?1, ?2)
                           ON CONFLICT(name) DO UPDATE SET payload = excluded.payload";
const DELETE_ROOT: &str = "DELETE FROM root WHERE name = ?1";
const UPSERT_META: &str = "INSERT INTO meta(key, value) VALUES(?1, ?2)
                           ON CONFLICT(key) DO UPDATE SET value = excluded.value";

/// Statements prepared once per batch, on first use.
struct Statements<'c> {
    conn: &'c Conn,
    cache: HashMap<&'static str, Statement<'c>>,
}

impl<'c> Statements<'c> {
    fn new(conn: &'c Conn) -> Statements<'c> {
        Statements {
            conn,
            cache: HashMap::new(),
        }
    }

    fn get(&mut self, sql: &'static str) -> Result<&mut Statement<'c>> {
        let conn = self.conn;
        Ok(match self.cache.entry(sql) {
            Entry::Occupied(entry) => entry.into_mut(),
            Entry::Vacant(entry) => entry.insert(conn.prepare(sql)?),
        })
    }

    fn apply(&mut self, op: Op) -> Result<()> {
        match op {
            Op::Guard { key, expected } => {
                let statement = self.get(SELECT_META)?;
                statement.bind_by_index(0, key.clone())?;
                let actual = match statement.step()? {
                    Some(step) => step.get_utf8_by_index(0)?.unwrap_or_else(nsCString::new),
                    None => nsCString::new(),
                };
                statement.reset()?;
                if actual != expected {
                    return Err(Error::GuardMismatch {
                        key: key.to_string(),
                        expected: expected.to_string(),
                        actual: actual.to_string(),
                    });
                }
            }
            Op::Clear => {
                self.conn.exec(
                    "DELETE FROM nodes; DELETE FROM child_order;
                     DELETE FROM sections; DELETE FROM root",
                )?;
            }
            Op::Node {
                id,
                parent,
                prop,
                payload,
            } => {
                let statement = self.get(UPSERT_NODE)?;
                statement.bind_by_index(0, id)?;
                statement.bind_by_index(1, parent)?;
                statement.bind_by_index(2, prop)?;
                statement.bind_by_index(3, payload)?;
                statement.execute()?;
            }
            Op::DeleteNode { id } => {
                for sql in [DELETE_NODE, DELETE_NODE_SECTIONS, DELETE_NODE_ORDERS] {
                    let statement = self.get(sql)?;
                    statement.bind_by_index(0, id)?;
                    statement.execute()?;
                }
            }
            Op::Order { parent, prop, ids } => {
                let statement = self.get(UPSERT_ORDER)?;
                statement.bind_by_index(0, parent)?;
                statement.bind_by_index(1, prop)?;
                statement.bind_by_index(2, ids)?;
                statement.execute()?;
            }
            Op::DeleteOrder { parent, prop } => {
                let statement = self.get(DELETE_ORDER)?;
                statement.bind_by_index(0, parent)?;
                statement.bind_by_index(1, prop)?;
                statement.execute()?;
            }
            Op::Section {
                node,
                name,
                payload,
            } => {
                let statement = self.get(UPSERT_SECTION)?;
                statement.bind_by_index(0, node)?;
                statement.bind_by_index(1, name)?;
                statement.bind_by_index(2, payload)?;
                statement.execute()?;
            }
            Op::DeleteSection { node, name } => {
                let statement = self.get(DELETE_SECTION)?;
                statement.bind_by_index(0, node)?;
                statement.bind_by_index(1, name)?;
                statement.execute()?;
            }
            Op::Root { name, payload } => {
                let statement = self.get(UPSERT_ROOT)?;
                statement.bind_by_index(0, name)?;
                statement.bind_by_index(1, payload)?;
                statement.execute()?;
            }
            Op::DeleteRoot { name } => {
                let statement = self.get(DELETE_ROOT)?;
                statement.bind_by_index(0, name)?;
                statement.execute()?;
            }
            Op::Meta { key, value } => {
                let statement = self.get(UPSERT_META)?;
                statement.bind_by_index(0, key)?;
                statement.bind_by_index(1, value)?;
                statement.execute()?;
            }
        }
        Ok(())
    }
}
