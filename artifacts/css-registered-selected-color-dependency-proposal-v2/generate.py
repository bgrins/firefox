from pathlib import Path
import difflib
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCES = {
    'servo/components/style/custom_properties.rs': 'artifacts/css-registered-provider-default-v5-design-v1/original/servo/components/style/custom_properties.rs',
    'servo/components/style/properties/cascade.rs': 'artifacts/css-animation-active-value-taint-proposal-v1/base/servo/components/style/properties/cascade.rs',
    'servo/components/style/properties_and_values/value.rs': 'artifacts/css-animation-active-value-taint-proposal-v1/base/servo/components/style/properties_and_values/value.rs',
}

def replace(text, old, new):
    assert text.count(old) == 1, (old[:100], text.count(old))
    return text.replace(old, new)

classifier = r'''
    /// Whether computing this selected value reads the element's used color scheme.
    pub(crate) fn depends_on_color_scheme(&self) -> bool {
        fn color(value: &specified::Color) -> bool {
            use specified::Color;
            match value {
                Color::System(_) | Color::LightDark(_) => true,
                Color::ColorFunction(function) => function.origin_color().is_some_and(color),
                Color::ColorMix(mix) => mix.items.iter().any(|item| color(&item.color)),
                Color::ContrastColor(inner) => color(inner),
                Color::CurrentColor | Color::Absolute(_) | Color::InheritFromBodyQuirk => false,
            }
        }
        fn stops<T>(items: &[crate::values::generics::image::GradientItem<specified::Color, T>]) -> bool {
            use crate::values::generics::image::GradientItem;
            items.iter().any(|item| match item {
                GradientItem::SimpleColorStop(value)
                | GradientItem::ComplexColorStop { color: value, .. } => color(value),
                GradientItem::InterpolationHint(_) => false,
            })
        }
        fn image(value: &specified::Image) -> bool {
            use crate::values::generics::image::{CrossFadeImage, Gradient, Image};
            match value {
                Image::LightDark(_) => true,
                Image::Image(value) => color(value),
                Image::Gradient(gradient) => match &**gradient {
                    Gradient::Linear { items, .. } | Gradient::Radial { items, .. } => stops(items),
                    Gradient::Conic { items, .. } => stops(items),
                },
                Image::CrossFade(fade) => fade.elements.iter().any(|item| match &item.image {
                    CrossFadeImage::Image(value) => image(value),
                    CrossFadeImage::Color(value) => color(value),
                }),
                Image::ImageSet(set) => set.items.iter().any(|item| image(&item.image)),
                Image::None | Image::Url(_) => false,
                #[cfg(feature = "gecko")]
                Image::Element(_) | Image::MozSymbolicIcon(_) => false,
                #[cfg(feature = "servo")]
                Image::PaintWorklet(_) => false,
            }
        }
        fn component(value: &SpecifiedValueComponent) -> bool {
            use GenericValueComponent::*;
            match value {
                Color(value) => color(value),
                Image(value) => image(value),
                TransformList(list) => list.components.iter().any(component),
                Length(_) | Number(_) | Percentage(_) | LengthPercentage(_) | Url(_)
                | Integer(_) | Angle(_) | Time(_) | Resolution(_) | TransformFunction(_)
                | CustomIdent(_) | String(_) => false,
            }
        }
        match &self.v {
            ValueInner::Component(value) => component(value),
            ValueInner::List(list) => list.components.iter().any(component),
            ValueInner::Universal(_) => false,
        }
    }
'''

prepared = r'''
enum PreparedCustomKind {
    Existing,
    Typed(SpecifiedRegisteredValue),
    Initial(SpecifiedRegisteredValue),
    Invalid,
}

pub(crate) struct PreparedCustomValue {
    substitution: Result<Substitution<'static>, ()>,
    url_data: UrlExtraData,
    kind: PreparedCustomKind,
}

impl PreparedCustomValue {
    pub fn depends_on_color_scheme(&self) -> bool {
        match &self.kind {
            PreparedCustomKind::Typed(value) | PreparedCustomKind::Initial(value) => value.depends_on_color_scheme(),
            PreparedCustomKind::Existing | PreparedCustomKind::Invalid => false,
        }
    }

    pub fn apply(self, name: &Name, stylist: &Stylist, context: &mut computed::Context) {
        let registration = stylist.get_custom_property_registration(name);
        match self.kind {
            PreparedCustomKind::Typed(specified) => {
                let mut value = specified.to_computed_value(context);
                value.attr_tainted |= self.substitution.unwrap().attr_tainted;
                context.builder.substitution_functions.insert_var(registration, name, value);
            },
            PreparedCustomKind::Initial(specified) => {
                let value = specified.to_computed_value(context);
                context.builder.substitution_functions.insert_var(registration, name, value);
            },
            PreparedCustomKind::Invalid => handle_invalid_at_computed_value_time(name, registration, context),
            PreparedCustomKind::Existing => apply_substituted_value(
                name, None, &self.url_data, self.substitution, stylist, context,
            ),
        }
    }
}

pub(crate) fn prepare_custom_value(
    name: &Name,
    value: &VariableValue,
    stylist: &Stylist,
    context: &computed::Context,
    attribute_tracker: &mut AttributeTracker,
) -> PreparedCustomValue {
    let substitution = substitute_internal(
        value, Some(PropertyIdRef::from(name)), &context.builder.substitution_functions,
        stylist, context, attribute_tracker, &mut SmallVec::new(), None,
    ).map(|value| Substitution {
        css: Cow::Owned(value.css.into_owned()),
        first_token_type: value.first_token_type,
        last_token_type: value.last_token_type,
        attr_tainted: value.attr_tainted,
    });
    let registration = stylist.get_custom_property_registration(name);
    let mut kind = match substitution.as_ref() {
        Err(()) => PreparedCustomKind::Invalid,
        Ok(value) => {
            let mut parser = Parser::new(&value.css);
            if parser.try_parse(CSSWideKeyword::parse).is_ok() || registration.is_universal() {
                PreparedCustomKind::Existing
            } else if let Some(syntax) = registration.syntax.as_ref() {
                let taint = if value.attr_tainted {
                    AttrTaint::new_fully_tainted(value.css.len())
                } else {
                    AttrTaint::default()
                };
                let mut parser = Parser::new(&value.css);
                match SpecifiedRegisteredValue::parse(
                    &mut parser, syntax, &value.url_data_placeholder(), None,
                    AllowComputationallyDependent::Yes, taint, Some(PropertyIdRef::from(name)),
                ) {
                    Ok(parsed) => PreparedCustomKind::Typed(parsed),
                    Err(_) => PreparedCustomKind::Invalid,
                }
            } else {
                PreparedCustomKind::Invalid
            }
        },
    };
    if matches!(kind, PreparedCustomKind::Invalid) {
        kind = prepare_invalid_custom_kind(name, registration, context);
    }
    PreparedCustomValue { substitution, url_data: value.url_data.clone(), kind }
}

fn prepare_invalid_custom_kind(
    name: &Name,
    registration: &PropertyDescriptors,
    context: &computed::Context,
) -> PreparedCustomKind {
    if !registration.is_universal()
        && (!registration.inherits() || context.builder.is_root_element)
        && let (Some(initial), Some(syntax)) = (&registration.initial_value, &registration.syntax)
    {
        let mut parser = Parser::new(&initial.css);
        if let Ok(parsed) = SpecifiedRegisteredValue::parse(
            &mut parser, syntax, &initial.url_data, None,
            AllowComputationallyDependent::Yes, AttrTaint::default(), Some(PropertyIdRef::from(name)),
        ) {
            return PreparedCustomKind::Initial(parsed);
        }
    }
    PreparedCustomKind::Invalid
}

pub(crate) fn invalid_custom_value_depends_on_color_scheme(
    name: &Name,
    stylist: &Stylist,
    context: &computed::Context,
) -> bool {
    match prepare_invalid_custom_kind(name, stylist.get_custom_property_registration(name), context) {
        PreparedCustomKind::Initial(value) => value.depends_on_color_scheme(),
        _ => false,
    }
}
'''.replace('&value.url_data_placeholder()', '&url_data')

output = []
refs = {}
for rel, source in SOURCES.items():
    original = (ROOT / source).read_text()
    s = original
    if rel.endswith('/value.rs'):
        s = replace(s, 'impl SpecifiedValue {\n', 'impl SpecifiedValue {\n' + classifier)
    elif rel.endswith('/custom_properties.rs'):
        s = replace(s, 'use crate::values::computed;', 'use crate::values::computed;\nuse crate::values::computed::ToComputedValue;')
        start = s.index('    let Ok(substitution) = substitution else {', s.index('pub fn substitute_references_if_needed_and_apply('))
        end = s.index('\n#[derive(Default, Debug)]\nstruct Substitution', start)
        tail = s[start:end]
        header = '''    apply_substituted_value(name, namespace, url_data, substitution, stylist, context);
}

fn apply_substituted_value(
    name: &Name,
    namespace: Option<&Namespace>,
    url_data: &UrlExtraData,
    substitution: Result<Substitution, ()>,
    stylist: &Stylist,
    context: &mut computed::Context,
) {
    let is_var = namespace.is_none();
    let registration = stylist.get_custom_property_registration(name);
'''
        s = s[:start] + header + tail + prepared.replace('    let substitution = substitute_internal(\n', '    let url_data = value.url_data.clone();\n    let substitution = substitute_internal(\n') + s[end:]
    else:
        s = replace(s, '    remove_and_insert_initial_value, substitute_references_if_needed_and_apply,', '    invalid_custom_value_depends_on_color_scheme, prepare_custom_value, remove_and_insert_initial_value, substitute_references_if_needed_and_apply,')
        s = replace(s, '    if dependent_types.intersects(DependentDataTypes::COLOR) {', '''    let may_reference_image = syntax.components.iter().any(|component| {
        use crate::properties_and_values::syntax::{ComponentName, data_type::DataType};
        matches!(component.name(), ComponentName::DataType(DataType::Image))
    });
    if dependent_types.intersects(DependentDataTypes::COLOR) || may_reference_image {''')
        s = replace(s, '// The value depends on the used color-scheme (e.g. a `<color>` property referencing\n        // `light-dark()` or a system color).', '// Defer possible color computation; selected values determine the graph edge.')
        s = replace(s, '        let mut self_ref = false;\n        let mut lowlink = index;', '        let mut self_ref = false;\n        let mut lowlink = index;\n        let mut prepared_custom = None;')
        needle = '            // ... Then the non-custom properties this value depends on (font-size, line-height,\n'
        insert = '''            if let VarType::Custom(ref name) = var {
                let may_compute_color = value_non_custom_refs.intersects(ReferenceFlags::COLOR_SCHEME);
                value_non_custom_refs.remove(ReferenceFlags::COLOR_SCHEME);
                if registered && may_compute_color && lowlink == index && !self_ref
                    && context.stack.last() == Some(&index)
                {
                    let prepared = prepare_custom_value(
                        name, v, context.stylist, context.computed_context, attribute_tracker,
                    );
                    if prepared.depends_on_color_scheme() {
                        value_non_custom_refs |= ReferenceFlags::COLOR_SCHEME;
                    }
                    prepared_custom = Some(prepared);
                }
            }

'''
        s = replace(s, needle, insert + needle)
        s = replace(s, '        context.var_info[index].lowlink = lowlink;', """        if let VarType::Custom(ref name) = var {
            let cyclic = self_ref || lowlink < index || context.stack.last() != Some(&index);
            if registered && cyclic
                && !value_non_custom_refs.intersects(ReferenceFlags::COLOR_SCHEME)
                && invalid_custom_value_depends_on_color_scheme(
                    name, context.stylist, context.computed_context,
                )
            {
                visit_link(
                    VarType::NonCustom(SingleNonCustomReference::ColorScheme), index,
                    references_from_non_custom_properties, context, &mut lowlink,
                    &mut self_ref, attribute_tracker,
                );
            }
        }

        context.var_info[index].lowlink = lowlink;""")
        needle = '                if let Some(ref v) = value {\n                    // We know we\'re not in a loop now, perform substitution.'
        s = replace(s, needle, '''                if let Some(prepared) = prepared_custom {
                    prepared.apply(name, context.stylist, context.computed_context);
                } else if let Some(ref v) = value {
                    // We know we're not in a loop now, perform substitution.''')
    for directory, body in [('base', original), ('candidate', s)]:
        p = HERE / directory / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    output.extend(difflib.unified_diff(original.splitlines(True), s.splitlines(True), fromfile='a/'+rel, tofile='b/'+rel))
    refs[rel] = {'source': source, 'base_sha256': hashlib.sha256(original.encode()).hexdigest(), 'candidate_sha256': hashlib.sha256(s.encode()).hexdigest()}
(HERE / 'native.patch').write_text(''.join(output))
(HERE / 'SOURCE-ROLES.json').write_text(json.dumps(refs, indent=2)+'\n')
print(json.dumps(refs, indent=2))
