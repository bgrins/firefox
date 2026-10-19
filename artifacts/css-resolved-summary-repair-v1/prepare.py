from pathlib import Path
import difflib

ROOT = Path(__file__).resolve().parent
source = (ROOT / "original/custom_properties.rs").read_text()
helper = """fn resolved_token_dependencies(mut css: &str) -> Option<ReferenceFlags> {
    let mut flags = ReferenceFlags::empty();
    while !css.is_empty() {
        // Restart at each token to visit block contents without recursion.
        let mut input = Parser::new(css);
        match input.next_including_whitespace_and_comments().ok()? {
            Token::Dimension { unit, .. } => flags.insert(ReferenceFlags::from_unit(unit)),
            Token::Function(name) if SubstitutionFunctionKind::from_ident(name).is_ok() => {
                return None;
            },
            Token::BadUrl(_) | Token::BadString(_) => return None,
            _ => {},
        }
        let consumed = input.position().byte_index();
        debug_assert!(consumed > 0);
        css = &css[consumed..];
    }
    Some(flags)
}

"""
constructor = """    fn new_resolved(
        css: String,
        url_data: &UrlExtraData,
        first_token_type: TokenSerializationType,
        last_token_type: TokenSerializationType,
    ) -> Self {
        let mut value = Self::new(css, url_data, first_token_type, last_token_type);
        // Unresolved env payloads keep the previous empty summary.
        if let Some(flags) = resolved_token_dependencies(&value.css) {
            value.references.flags = flags;
        }
        value
    }

"""
assert source.count("impl VariableValue {") == 1
candidate = source.replace("impl VariableValue {", helper + "impl VariableValue {", 1)
anchor = "    fn push(\n        &mut self,\n        css: &str,"
assert candidate.count(anchor) == 1
candidate = candidate.replace(anchor, constructor + anchor, 1)
needle = "ComputedRegisteredValue::universal(Arc::new(VariableValue::new("
assert candidate.count(needle) == 2
candidate = candidate.replace(needle, "ComputedRegisteredValue::universal(Arc::new(VariableValue::new_resolved(")
(ROOT / "candidate").mkdir(exist_ok=True)
(ROOT / "candidate/custom_properties.rs").write_text(candidate)
patch = "".join(difflib.unified_diff(source.splitlines(True), candidate.splitlines(True), fromfile="a/servo/components/style/custom_properties.rs", tofile="b/servo/components/style/custom_properties.rs"))
(ROOT / "native.patch").write_text(patch)
