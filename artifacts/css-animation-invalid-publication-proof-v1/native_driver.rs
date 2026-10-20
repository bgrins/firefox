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
    // EXACT_FROM_COMPUTED
    // EXACT_TO_DECLARATION
}
// EXACT_REMOVAL_COMPARATOR
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
