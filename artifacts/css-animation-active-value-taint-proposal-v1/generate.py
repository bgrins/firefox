import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
edits = []
roles = {}
patches = []
recording = True

def edit(text, old, new, count=1):
    assert text.count(old) == count, (old, text.count(old), count)
    if recording:
        edits.append({"path": name, "old": old, "new": new, "count": count})
    return text.replace(old, new)

def finish(name, original, changed):
    target = HERE / "candidate" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(changed)
    roles[name] = {"base_capture": str((HERE / "base" / name).relative_to(HERE.parents[1])),
                   "base_sha256": hashlib.sha256(original.encode()).hexdigest(),
                   "candidate_capture": str(target.relative_to(HERE.parents[1])),
                   "candidate_sha256": hashlib.sha256(changed.encode()).hexdigest()}
    patches.extend(difflib.unified_diff(original.splitlines(True), changed.splitlines(True),
                                      fromfile="a/" + name, tofile="b/" + name))

name = "servo/components/style/properties_and_values/value.rs"
s = original = (HERE / "base" / name).read_text()
s = edit(s, "    pub attr_tainted: bool,", "    pub attr_tainted: bool,\n    /// Whether the winning value carries animation provenance.\n    #[css(skip)]\n    pub animation_tainted: bool,")
s = edit(s, "            attr_tainted: self.attr_tainted.to_computed_value(context),", "            attr_tainted: self.attr_tainted.to_computed_value(context),\n            animation_tainted: self.animation_tainted,")
s = edit(s, "            attr_tainted: ToComputedValue::from_computed_value(&computed.attr_tainted),", "            attr_tainted: ToComputedValue::from_computed_value(&computed.attr_tainted),\n            animation_tainted: computed.animation_tainted,")
s = edit(s, "            attr_tainted: self.attr_tainted || other.attr_tainted,", "            attr_tainted: self.attr_tainted || other.attr_tainted,\n            animation_tainted: self.animation_tainted || other.animation_tainted,")
s = edit(s, "            attr_tainted: Default::default(),", "            attr_tainted: Default::default(),\n            animation_tainted: false,")
s = edit(s, "        let attr_tainted = var.is_attr_tainted();", "        let attr_tainted = var.is_attr_tainted();\n        let animation_tainted = var.explicitly_animation_tainted;")
s = edit(s, "            attr_tainted,\n        }", "            attr_tainted,\n            animation_tainted,\n        }")
s = edit(s, "            return (**value).clone();", "            let mut value = (**value).clone();\n            value.explicitly_animation_tainted |= self.animation_tainted;\n            return value;")
s = edit(s, "        ComputedPropertyValue::new(css, &self.url_data, first, last)", "        let mut value = ComputedPropertyValue::new(css, &self.url_data, first, last);\n        value.explicitly_animation_tainted = self.animation_tainted;\n        value")
s = edit(s, "            if self.attr_tainted && !var.is_attr_tainted() {", "            if (self.attr_tainted && !var.is_attr_tainted())\n                || (self.animation_tainted && !var.explicitly_animation_tainted)\n            {")
s = edit(s, "                tainted.explicitly_attr_tainted = true;", "                tainted.explicitly_attr_tainted |= self.attr_tainted;\n                tainted.explicitly_animation_tainted |= self.animation_tainted;")
finish(name, original, s)

name = "servo/components/style/custom_properties_map.rs"
s = original = (HERE / "base" / name).read_text()
s = edit(s, "            a == b && a.attr_tainted == b.attr_tainted", "            a == b\n                && a.attr_tainted == b.attr_tainted\n                && a.animation_tainted == b.animation_tainted")
finish(name, original, s)

name = "servo/components/style/custom_properties.rs"
def transform_custom(s):
    s = edit(s, "    pub explicitly_attr_tainted: bool,", "    pub explicitly_attr_tainted: bool,\n    /// Preserves animation provenance through uncomputation.\n    pub explicitly_animation_tainted: bool,")
    s = edit(s, "            explicitly_attr_tainted: false,", "            explicitly_attr_tainted: false,\n            explicitly_animation_tainted: false,", 4)
    s = edit(s, "    attr_tainted: bool,\n}\n\nimpl<'a> Substitution<'a>", "    attr_tainted: bool,\n    animation_tainted: bool,\n}\n\nimpl<'a> Substitution<'a>")
    s = edit(s, "            css: v.css.into(),", "            animation_tainted: v.explicitly_animation_tainted,\n            css: v.css.into(),")
    s = edit(s, "            value.attr_tainted |= self.attr_tainted;", "            value.attr_tainted |= self.attr_tainted;\n            value.animation_tainted |= self.animation_tainted;")
    s = edit(s, "        v.attr_tainted |= self.attr_tainted;", "        v.attr_tainted |= self.attr_tainted;\n        v.animation_tainted |= self.animation_tainted;")
    s = edit(s, "            last_token_type,\n            attr_tainted,\n        }\n    }\n}\n\n/// Result of var()", "            last_token_type,\n            attr_tainted,\n            animation_tainted: false,\n        }\n    }\n}\n\n/// Result of var()")
    s = edit(s, "    let mut attr_tainted = false;", "    let mut attr_tainted = false;\n    let mut animation_tainted = false;")
    s = edit(s, "        attr_tainted |= substitution.attr_tainted;", "        attr_tainted |= substitution.attr_tainted;\n        animation_tainted |= substitution.animation_tainted;")
    s = edit(s, "    Ok(Substitution::from_value(substituted, attr_tainted))", "    substituted.explicitly_animation_tainted = animation_tainted;\n    Ok(Substitution::from_value(substituted, attr_tainted))")
    indent = next(line[:len(line) - len(line.lstrip())] for line in s.splitlines() if "substitution.attr_tainted |= v.attr_tainted;" in line)
    s = edit(s, "substitution.attr_tainted |= v.attr_tainted;", "substitution.attr_tainted |= v.attr_tainted;\n" + indent + "substitution.animation_tainted |= v.animation_tainted;")
    s = edit(s, "    if let Some(s) = substitution {\n        return Ok(s);\n    }", "    let substitution = substitution.filter(|value| {\n        !(reference.substitution_kind == SubstitutionFunctionKind::Var\n            && value.animation_tainted\n            && !suppress_animation_taint_sink\n            && matches!(property_id, Some(PropertyIdRef::NonCustom(id)) if !id.is_animatable()))\n    });\n    if let Some(s) = substitution {\n        return Ok(s);\n    }")
    s = edit(s, "    do_substitute_chunk(\n        &variable_value.css,", "    let mut result = do_substitute_chunk(\n        &variable_value.css,")
    s = edit(s, "        seen,\n        attr_taint,\n    )\n}\n\n/// Replace var()", "        seen,\n        attr_taint,\n    )?;\n    result.animation_tainted |= variable_value.explicitly_animation_tainted;\n    Ok(result)\n}\n\n/// Replace var()")

    s = edit(s, "            return;\n        }\n    }\n\n    match namespace {", "            if substitution.animation_tainted {\n                let value = context.builder.substitution_functions.get_var(registration, name).cloned();\n                if let Some(mut value) = value {\n                    value.animation_tainted = true;\n                    context.builder.substitution_functions.insert_var(registration, name, value);\n                }\n            }\n            return;\n        }\n    }\n\n    match namespace {")

    for function in ["do_substitute_chunk", "substitute_one_reference", "substitute_internal"]:
        start = s.index("fn " + function + "<'a>(")
        opening = s.index("(", start)
        depth = 1
        end = opening + 1
        while depth:
            depth += (s[end] == "(") - (s[end] == ")")
            end += 1
        old = s[start:end]
        new = old[:-1] + "    suppress_animation_taint_sink: bool,\n)"
        s = edit(s, old, new)
        position = 0
        needle = function + "("
        while True:
            start = s.find(needle, position)
            if start < 0:
                break
            opening = start + len(needle) - 1
            depth = 1
            end = opening + 1
            while depth:
                depth += (s[end] == "(") - (s[end] == ")")
                end += 1
            old = s[start:end]
            indent = old.splitlines()[-1][:-1]
            value = "suppress_animation_taint_sink"
            if function == "substitute_internal":
                value = "true" if old.splitlines()[1].strip() == "u," else "false"
            new = old[:-len(indent)-1] + indent + "    " + value + ",\n" + indent + ")"
            s = edit(s, old, new)
            position = start + len(new)
    return s

original = (HERE / "base" / name).read_text()
s = transform_custom(original)
finish(name, original, s)
recording = False
clean_base_path = HERE.parents[1] / "artifacts/css-registered-provider-default-v5-design-v1/original" / name
clean_original = clean_base_path.read_text()
clean_candidate = transform_custom(clean_original)
clean_output = HERE / "clean-provider-candidate.rs"
clean_output.write_text(clean_candidate)
recording = True

name = "servo/components/style/properties/cascade.rs"
s = original = (HERE / "base" / name).read_text()
old = """        let initial_values = self.stylist.get_custom_property_initial_values();
        if !Self::value_may_affect_style(context, name, registration, initial_values, value) {"""
new = """        let initial_values = self.stylist.get_custom_property_initial_values();
        let animation_tainted = std::ptr::eq(registration, PropertyDescriptors::unregistered())
            && priority.cascade_level() == CascadeLevel::Animations;
        let mark_animation_taint = |context: &mut computed::Context| {
            if animation_tainted {
                let value = context
                    .builder
                    .substitution_functions
                    .get_var(registration, name)
                    .cloned();
                if let Some(mut value) = value {
                    value.animation_tainted = true;
                    context
                        .builder
                        .substitution_functions
                        .insert_var(registration, name, value);
                }
            }
        };
        if !Self::value_may_affect_style(context, name, registration, initial_values, value, animation_tainted) {"""
s = edit(s, old, new)
s = edit(s, "            entry.insert(false);\n            return;", "            entry.insert(false);\n            mark_animation_taint(context);\n            return;")
s = edit(s, "            CustomDeclarationValue::Unparsed(unparsed_value) => {\n                if !has_references {", "            CustomDeclarationValue::Unparsed(unparsed_value) => {\n                let unparsed_value = if animation_tainted {\n                    let mut value = (**unparsed_value).clone();\n                    value.explicitly_animation_tainted = true;\n                    Arc::new(value)\n                } else {\n                    Arc::clone(unparsed_value)\n                };\n                if !has_references {")
s = edit(s, "                        unparsed_value,\n                        self.stylist,", "                        &unparsed_value,\n                        self.stylist,")
s = edit(s, "                let value = ComputedRegisteredValue::universal(Arc::clone(unparsed_value));", "                let value = ComputedRegisteredValue::universal(unparsed_value);")
s = edit(s, "        }\n    }\n\n    /// Fast check to avoid calling maybe_note_non_custom_dependency", "        }\n        mark_animation_taint(context);\n    }\n\n    /// Fast check to avoid calling maybe_note_non_custom_dependency")
s = edit(s, "                    return existing_value.attr_tainted != value.is_attr_tainted()", "                    return existing_value.animation_tainted != (animation_tainted || value.explicitly_animation_tainted)\n                        || existing_value.attr_tainted != value.is_attr_tainted()")
s = edit(s, "                            return existing_value.attr_tainted || existing_value != initial_value;", "                            return existing_value.attr_tainted\n                                || existing_value.animation_tainted != initial_value.animation_tainted\n                                || existing_value != initial_value;")
s = edit(s, "        value: &CustomDeclarationValue,\n    ) -> bool {", "        value: &CustomDeclarationValue,\n        animation_tainted: bool,\n    ) -> bool {")
s = edit(s, "                        .insert(name.clone(), (priority, revert_kind));\n                },", "                        .insert(name.clone(), (priority, revert_kind));\n                    return;\n                },")
finish(name, original, s)
(HERE / "native.patch").write_text("".join(patches))
(HERE / "SOURCE-ROLES.json").write_text(json.dumps(roles, indent=2) + "\n")
(HERE / "EDITS.json").write_text(json.dumps(edits, indent=2) + "\n")
print(json.dumps({"files": len(roles), "edits": len(edits)}))

clean_patch = []
for path, role in roles.items():
    before = clean_original if path.endswith("/custom_properties.rs") else (HERE.parents[1] / role["base_capture"]).read_text()
    after = clean_candidate if path.endswith("/custom_properties.rs") else (HERE.parents[1] / role["candidate_capture"]).read_text()
    clean_patch.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="a/"+path, tofile="b/"+path))
(HERE / "native-clean-provider.patch").write_text("".join(clean_patch))
(HERE / "CLEAN-PROVIDER.json").write_text(json.dumps({"base_capture":str(clean_base_path.relative_to(HERE.parents[1])),"base_sha256":hashlib.sha256(clean_original.encode()).hexdigest(),"candidate_capture":str(clean_output.relative_to(HERE.parents[1])),"candidate_sha256":hashlib.sha256(clean_candidate.encode()).hexdigest(),"same_transform_succeeded":True,"native_compiled":False},indent=2)+"\n")
