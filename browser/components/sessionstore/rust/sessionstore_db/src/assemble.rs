/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

//! Assembles the rows of the database into one JSON document.
//!
//! Each fragment is already JSON, so assembly splices text instead of parsing
//! it: an object's members come from its own payload and from its sections,
//! followed by one member per split property holding its child nodes.

use std::collections::{BTreeMap, HashMap};

use nsstring::nsCString;
use serde::de::IgnoredAny;
use storage::Conn;

use crate::error::{Error, Result};

/// The parent id of the top-level state's children.
const ROOT_PARENT: i64 = 0;

struct Node {
    parent: i64,
    prop: nsCString,
    payload: Option<nsCString>,
}

enum Children {
    Array(Vec<i64>),
    Single(i64),
}

struct Assembler {
    nodes: HashMap<i64, Node>,
    orders: HashMap<i64, Vec<(nsCString, nsCString)>>,
    sections: HashMap<i64, Vec<nsCString>>,
    validate: bool,
    dropped: usize,
}

/// Reads the whole database and returns
/// `{"meta": {...}, "state": <state or null>, "dropped": <count>}`.
pub fn read(conn: &Conn, validate: bool) -> Result<nsCString> {
    let meta = read_meta(conn)?;
    let mut out = b"{\"meta\":".to_vec();
    out.extend_from_slice(meta.as_bytes());
    out.extend_from_slice(b",\"state\":");
    let dropped = match write_state(conn, validate, 64, &mut out)? {
        Some(dropped) => dropped,
        None => {
            out.extend_from_slice(b"null");
            0
        }
    };
    out.extend_from_slice(format!(",\"dropped\":{}}}", dropped).as_bytes());
    Ok(nsCString::from(out))
}

/// Appends the assembled session state to `out`, after reserving room for it
/// and `extra` more bytes. Returns the number of nodes left out, or None if the
/// database holds no state.
pub fn write_state(
    conn: &Conn,
    validate: bool,
    extra: usize,
    out: &mut Vec<u8>,
) -> Result<Option<usize>> {
    let mut roots = read_roots(conn)?;
    let Some(state) = roots.remove("state") else {
        return Ok(None);
    };
    let mut assembler = Assembler::load(conn, validate)?;

    let mut size = extra + state.len();
    size += roots
        .values()
        .map(|payload| payload.len() + 16)
        .sum::<usize>();
    size += assembler.size_hint();
    out.try_reserve(size).map_err(|_| Error::OutOfMemory)?;

    let members: Vec<(String, nsCString)> = roots.into_iter().collect();
    assembler.object(ROOT_PARENT, &state, &members, out)?;
    assembler.check_consumed()?;
    Ok(Some(assembler.dropped))
}

fn read_meta(conn: &Conn) -> Result<String> {
    let mut meta = serde_json::Map::new();
    let mut statement = conn.prepare("SELECT key, value FROM meta")?;
    while let Some(step) = statement.step()? {
        let key = step.get_utf8_by_index(0)?.unwrap_or_else(nsCString::new);
        let value = step.get_utf8_by_index(1)?.unwrap_or_else(nsCString::new);
        meta.insert(
            key.to_string(),
            serde_json::Value::String(value.to_string()),
        );
    }
    serde_json::to_string(&meta).map_err(|err| Error::Corrupt(err.to_string()))
}

/// Returns the root payloads by name, in a stable order.
fn read_roots(conn: &Conn) -> Result<BTreeMap<String, nsCString>> {
    let mut roots = BTreeMap::new();
    let mut statement = conn.prepare("SELECT name, payload FROM root")?;
    while let Some(step) = statement.step()? {
        let name = step.get_utf8_by_index(0)?.unwrap_or_else(nsCString::new);
        let payload = step.get_utf8_by_index(1)?.unwrap_or_else(nsCString::new);
        roots.insert(name.to_string(), payload);
    }
    Ok(roots)
}

impl Assembler {
    fn load(conn: &Conn, validate: bool) -> Result<Assembler> {
        let mut nodes = HashMap::new();
        let mut statement = conn.prepare("SELECT id, parent, prop, payload FROM nodes")?;
        while let Some(step) = statement.step()? {
            let id = step.get_by_index::<i64>(0)?;
            let node = Node {
                parent: step.get_by_index::<i64>(1)?,
                prop: step.get_utf8_by_index(2)?.unwrap_or_else(nsCString::new),
                payload: step.get_utf8_by_index(3)?,
            };
            nodes.insert(id, node);
        }

        let mut orders: HashMap<i64, Vec<(nsCString, nsCString)>> = HashMap::new();
        let mut statement =
            conn.prepare("SELECT parent, prop, ids FROM child_order ORDER BY parent, prop")?;
        while let Some(step) = statement.step()? {
            let parent = step.get_by_index::<i64>(0)?;
            let prop = step.get_utf8_by_index(1)?.unwrap_or_else(nsCString::new);
            let ids = step.get_utf8_by_index(2)?.unwrap_or_else(nsCString::new);
            orders.entry(parent).or_default().push((prop, ids));
        }

        let mut sections: HashMap<i64, Vec<nsCString>> = HashMap::new();
        let mut statement =
            conn.prepare("SELECT node, payload FROM sections ORDER BY node, name")?;
        while let Some(step) = statement.step()? {
            let node = step.get_by_index::<i64>(0)?;
            let payload = step.get_utf8_by_index(1)?.unwrap_or_else(nsCString::new);
            sections.entry(node).or_default().push(payload);
        }

        Ok(Assembler {
            nodes,
            orders,
            sections,
            validate,
            dropped: 0,
        })
    }

    fn size_hint(&self) -> usize {
        let nodes: usize = self
            .nodes
            .values()
            .map(|node| node.payload.as_ref().map_or(4, |p| p.len()) + node.prop.len() + 8)
            .sum();
        let sections: usize = self.sections.values().flatten().map(|p| p.len() + 1).sum();
        nodes + sections
    }

    /// Writes an object whose own members come from `payload` and from the
    /// sections of `id`, followed by `extra` members and the split
    /// properties of `id`.
    fn object(
        &mut self,
        id: i64,
        payload: &[u8],
        extra: &[(String, nsCString)],
        out: &mut Vec<u8>,
    ) -> Result<()> {
        let sections = self.sections.remove(&id).unwrap_or_default();
        let orders = self.orders.remove(&id).unwrap_or_default();

        let mut first = true;
        out.push(b'{');
        for fragment in std::iter::once(payload).chain(sections.iter().map(|s| &s[..])) {
            let members = self.members(fragment)?;
            if !members.is_empty() {
                if !first {
                    out.push(b',');
                }
                out.extend_from_slice(members);
                first = false;
            }
        }
        for (name, value) in extra {
            self.check(value)?;
            member_key(name.as_bytes(), first, out)?;
            out.extend_from_slice(value);
            first = false;
        }
        for (prop, ids) in orders {
            member_key(&prop, first, out)?;
            first = false;
            match parse_children(&ids)? {
                Children::Single(child) => self.node(child, id, &prop, out)?,
                Children::Array(children) => {
                    out.push(b'[');
                    let mut written = 0;
                    for child in children {
                        let mark = out.len();
                        if written > 0 {
                            out.push(b',');
                        }
                        match self.node(child, id, &prop, out) {
                            Ok(()) => written += 1,
                            Err(Error::InvalidFragment(_)) if self.validate => {
                                out.truncate(mark);
                                self.dropped += 1;
                            }
                            Err(err) => return Err(err),
                        }
                    }
                    out.push(b']');
                }
            }
        }
        out.push(b'}');
        Ok(())
    }

    fn node(&mut self, id: i64, parent: i64, prop: &[u8], out: &mut Vec<u8>) -> Result<()> {
        let node = self
            .nodes
            .remove(&id)
            .ok_or_else(|| Error::Corrupt(format!("node {} is missing or referenced twice", id)))?;
        if node.parent != parent || &node.prop[..] != prop {
            return Err(Error::Corrupt(format!(
                "node {} is listed under a different parent",
                id
            )));
        }
        match node.payload {
            Some(payload) if payload.first() == Some(&b'{') => self.object(id, &payload, &[], out),
            Some(payload) => {
                self.check(&payload)?;
                out.extend_from_slice(&payload);
                Ok(())
            }
            None => {
                out.extend_from_slice(b"null");
                Ok(())
            }
        }
    }

    /// Returns the members of an object fragment, without its braces.
    fn members<'a>(&self, fragment: &'a [u8]) -> Result<&'a [u8]> {
        self.check(fragment)?;
        match fragment {
            [b'{', members @ .., b'}'] => Ok(members),
            _ => Err(Error::InvalidFragment("expected an object".into())),
        }
    }

    fn check(&self, fragment: &[u8]) -> Result<()> {
        if self.validate {
            serde_json::from_slice::<IgnoredAny>(fragment)
                .map_err(|err| Error::InvalidFragment(err.to_string()))?;
        }
        Ok(())
    }

    /// Fails if any row wasn't reached from the top-level state. When
    /// validating, unreachable rows count as dropped instead: they belong to
    /// nodes that were left out.
    fn check_consumed(&mut self) -> Result<()> {
        let left = self.nodes.len() + self.orders.len() + self.sections.len();
        if left == 0 {
            return Ok(());
        }
        if self.validate {
            self.dropped += self.nodes.len();
            return Ok(());
        }
        Err(Error::Corrupt(format!("{} rows are unreachable", left)))
    }
}

fn member_key(key: &[u8], first: bool, out: &mut Vec<u8>) -> Result<()> {
    let key = std::str::from_utf8(key).map_err(|err| Error::Corrupt(err.to_string()))?;
    if !first {
        out.push(b',');
    }
    serde_json::to_writer(&mut *out, key).map_err(|err| Error::Corrupt(err.to_string()))?;
    out.push(b':');
    Ok(())
}

fn parse_children(ids: &[u8]) -> Result<Children> {
    if let Ok(children) = serde_json::from_slice::<Vec<i64>>(ids) {
        return Ok(Children::Array(children));
    }
    serde_json::from_slice::<i64>(ids)
        .map(Children::Single)
        .map_err(|err| Error::Corrupt(format!("invalid child order: {}", err)))
}
