import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def extract(path, signature, indent, scope=''):
    text = (ROOT / path).read_text()
    start = text.index(signature, text.index(scope) if scope else 0)
    end = text.index('\n' + ' ' * indent + '}', start) + indent + 2
    body = text[start:end]
    return dict(file=path, signature=signature, scope=scope, indent=indent,
                start_byte=len(text[:start].encode()), end_byte=len(text[:end].encode()),
                body=body, sha256=hashlib.sha256(body.encode()).hexdigest())

def bindings():
    rows = []
    for version in ['original', 'landing']:
        base = f'source/{version}/servo/components/style/'
        for signature in ['pub fn from_computed(', 'pub(crate) fn from_declaration(', 'pub(crate) fn to_declaration(']:
            rows.append(extract(base+'properties_and_values/value.rs', signature, 4, 'impl CustomAnimatedValue'))
        rows.append(extract(base+'properties_and_values/value.rs', 'fn to_declared_value(', 4))
        for signature in ['fn cascade_custom_property(', 'fn value_may_affect_style(']:
            rows.append(extract(base+'properties/cascade.rs', signature, 4))
        rows.append(extract(base+'properties/mod.rs', 'pub enum CustomDeclarationValue', 0))
    base = 'source/providers/servo/components/'
    for signature in ['pub fn remove(', 'fn map_mut(', 'pub(crate) fn remove_var(']:
        rows.append(extract(base+'style/custom_properties.rs', signature, 4))
    for signature in ['fn can_deduplicate_values(', 'fn do_insert(', 'pub fn remove(', 'pub fn get(']:
        rows.append(extract(base+'style/custom_properties_map.rs', signature, 0 if signature.startswith('fn can') else 4,
                            'impl CustomPropertiesMap' if signature != 'fn can_deduplicate_values(' else ''))
    for signature in ['pub fn substitute_references_if_needed_and_apply(', 'fn remove_and_insert_initial_value(']:
        rows.append(extract(base+'style/custom_properties.rs', signature, 0))
    for f in ['to_css', 'to_typed']:
        rows.append(extract(base+f'style_derive/{f}.rs', 'fn derive_variant_arm(', 0))
    for signature in ['pub fn uncompute(', 'pub fn from_computed_values(']:
        rows.append(extract(base+'style/properties/helpers/animated_properties.mako.rs', signature, 4))
    for signature in ['fn Servo_AnimationCompose(', 'fn Servo_AnimationValue_Uncompute(']:
        rows.append(extract('source/providers/servo/ports/geckolib/glue.rs', signature, 0))
    return rows

if __name__ == '__main__':
    print(json.dumps(bindings(), indent=2))
