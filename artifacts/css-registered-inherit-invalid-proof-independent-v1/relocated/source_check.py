import hashlib
import re


def extract(text, name, impl=None):
    if impl:
        marker = "impl " + impl + " {"
        assert text.count(marker) == 1
        text = text.split(marker, 1)[1].split("\n}", 1)[0]
    pattern = r"^    (?:pub(?:\([^\n]*\))? )?fn " + re.escape(name) + r"\("
    matches = list(re.finditer(pattern, text, re.M))
    assert len(matches) == 1, name
    start = matches[0].start()
    end = text.index("\n    }", start) + len("\n    }")
    body = text[start:end] + "\n"
    assert body.count("{") == body.count("}"), name
    return body


def inspect(root):
    records = {}
    for variant in ["original", "candidate"]:
        text = (root / "source" / variant / "cascade.rs").read_text()
        for name in ["init_custom_properties", "value_may_affect_style", "cascade_custom_property"]:
            body = extract(text, name)
            records[variant + "/" + name] = {"source": "source/" + variant + "/cascade.rs", "sha256": hashlib.sha256(body.encode()).hexdigest(), "body": body}
    text = (root / "source/custom_properties.rs").read_text()
    for impl, names in [("ComputedCustomProperties", ["get", "insert", "remove", "map_mut"]), ("ComputedSubstitutionFunctions", ["insert_var", "remove_var"])]:
        for name in names:
            body = extract(text, name, impl)
            records[impl + "/" + name] = {"source": "source/custom_properties.rs", "sha256": hashlib.sha256(body.encode()).hexdigest(), "body": body}
    assert records["original/init_custom_properties"]["body"] == records["candidate/init_custom_properties"]["body"]
    candidate = records["candidate/cascade_custom_property"]["body"]
    assert candidate.count(".add_flags(ComputedValueFlags::INHERITS_RESET_STYLE)") == 1
    assert "CustomDeclarationValue::CSSWideKeyword(keyword) => match keyword.revert_kind()" in candidate
    assert "let inherited_value = context" in candidate
    assert "                            .non_inherited" in candidate
    assert candidate.count(".remove_var(registration, name);") == 1
    return records
