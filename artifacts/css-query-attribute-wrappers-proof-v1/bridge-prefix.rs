use std::collections::BTreeSet;
use std::io::{self, Read};

type AttrReferenceSet = BTreeSet<u32>;
type QueryFeatureExpression = u32;
type DashedIdent = u32;
type MozPrefFeature = u32;
type UrlExtraData = u8;
type FeatureFlags = u8;

pub struct StyleQuery(u32);

impl StyleQuery {
    fn collect_attribute_references(&self, references: &mut AttrReferenceSet) {
        for a in dependencies(self.0) {
            references.insert(a);
        }
    }
}

fn dependencies(id: u32) -> Vec<u32> {
    match id % 6 {
        0 => vec![],
        1 => vec![3, 5],
        2 => vec![3, 3],
        3 => vec![11],
        4 => vec![5, 11, 19],
        _ => vec![id, 23],
    }
}
