/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use crate::SelectorImpl;
use cssparser::ToCss;
use precomputed_hash::PrecomputedHash;
use std::fmt;

#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct Atom {
    pub identity: u32,
    pub hash: u32,
}
impl From<&str> for Atom {
    fn from(_: &str) -> Self {
        Self::default()
    }
}
impl AsRef<str> for Atom {
    fn as_ref(&self) -> &str {
        ""
    }
}
impl ToCss for Atom {
    fn to_css<W: fmt::Write>(&self, _: &mut W) -> fmt::Result {
        Ok(())
    }
}
impl PrecomputedHash for Atom {
    fn precomputed_hash(&self) -> u32 {
        self.hash
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Never {}
impl ToCss for Never {
    fn to_css<W: fmt::Write>(&self, _: &mut W) -> fmt::Result {
        match *self {}
    }
}
impl crate::parser::PseudoElement for Never {}
impl crate::parser::NonTSPseudoClass for Never {
    fn is_active_or_hover(&self) -> bool {
        match *self {}
    }
    fn is_user_action_state(&self) -> bool {
        match *self {}
    }
}

#[derive(Clone, Debug)]
pub struct Impl;
impl SelectorImpl for Impl {
    type ExtraMatchingData<'a> = ();
    type AttrValue = Atom;
    type Identifier = Atom;
    type LocalName = Atom;
    type NamespaceUrl = Atom;
    type NamespacePrefix = Atom;
    type BorrowedLocalName = Atom;
    type BorrowedNamespaceUrl = Atom;
    type NonTSPseudoClass = Never;
    type PseudoElement = Never;
    fn should_collect_attr_hash(name: &Atom) -> bool {
        name.identity > 3
    }
}
