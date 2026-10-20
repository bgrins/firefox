#![allow(dead_code)]
mod custom_properties { pub type Name = String; }
#[derive(Clone, Debug, PartialEq)]
struct ComputedValue { tokens: Vec<u32>, attr_tainted: bool }
type ComputedRegisteredValue = ComputedValue;
impl ComputedValue {
    fn to_declared_value(&self) -> properties::CustomDeclarationValue {
        properties::CustomDeclarationValue::Parsed(self.clone())
    }
}
mod properties {
    use super::ComputedValue;
    #[derive(Debug, PartialEq)]
    pub enum CSSWideKeyword { Initial }
    #[derive(Debug, PartialEq)]
    pub enum CustomDeclarationValue { GuaranteedInvalid, Parsed(ComputedValue), CSSWideKeyword(CSSWideKeyword) }
    #[derive(Debug, PartialEq)]
    pub struct CustomDeclaration { pub name: String, pub value: CustomDeclarationValue }
    #[derive(Debug, PartialEq)]
    pub enum PropertyDeclaration { Custom(CustomDeclaration) }
}
use properties::{CustomDeclarationValue, CSSWideKeyword};
struct CustomAnimatedValue { name: String, value: Option<ComputedValue> }
impl CustomAnimatedValue {
    pub fn from_computed(
        name: &crate::custom_properties::Name,
        value: Option<&ComputedValue>,
    ) -> Self {
        Self {
            name: name.clone(),
            value: value.cloned(),
        }
    }
    pub(crate) fn to_declaration(&self) -> properties::PropertyDeclaration {
        properties::PropertyDeclaration::Custom(properties::CustomDeclaration {
            name: self.name.clone(),
            value: match &self.value {
                Some(value) => value.to_declared_value(),
                None => CustomDeclarationValue::Parsed(ComputedValue { tokens: vec![], attr_tainted: false }),
            },
        })
    }
}
fn can_deduplicate_values(
    a: Option<&ComputedRegisteredValue>,
    b: Option<&ComputedRegisteredValue>,
) -> bool {
    match (a, b) {
        (Some(a), Some(b)) => {
            // TODO(emilio): Seems we should compare `url_data` as well? It doesn't seem to matter
            // much in practice since url values would be already-computed against the right base
            // URI here, I think...
            a == b && a.attr_tainted == b.attr_tainted
        },
        (None, None) => true,
        _ => false,
    }
}
fn main() {
    let mut rows = 0;
    for name in ["", "--x", "--other"] {
        for tokens in [None, Some(vec![]), Some(vec![20]), Some(vec![44, 55])] {
            for attr_tainted in [false, true] {
                let input = tokens.clone().map(|tokens| ComputedValue { tokens, attr_tainted });
                let endpoint = CustomAnimatedValue::from_computed(&name.to_string(), input.as_ref());
                assert_eq!(&endpoint.name, name);
                assert_eq!(endpoint.value, input);
                let properties::PropertyDeclaration::Custom(result) = endpoint.to_declaration();
                assert_eq!(&result.name, name);
                match input {
                    None => {
                        #[cfg(original)] assert_eq!(result.value, CustomDeclarationValue::CSSWideKeyword(CSSWideKeyword::Initial));
                        #[cfg(not(original))] assert_eq!(result.value, CustomDeclarationValue::GuaranteedInvalid);
                    },
                    Some(value) => assert_eq!(result.value, CustomDeclarationValue::Parsed(value)),
                }
                rows += 1;
            }
        }
    }
    assert!(can_deduplicate_values(None, None));
    for attr_tainted in [false, true] {
        let old = ComputedValue { tokens: vec![], attr_tainted };
        assert!(!can_deduplicate_values(Some(&old), None));
    }
    println!("conversion_rows={rows};removal_rows=3");
}
