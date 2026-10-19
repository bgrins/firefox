from pathlib import Path
import difflib

FILES = (
    'servo/components/style/custom_properties.rs',
    'servo/components/style/properties/cascade.rs',
)

def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)

def candidate(path, text):
    if path == FILES[0]:
        text = once(text,
            '/// Removes the named registered custom property and inserts its uncomputed initial value.',
            '/// Removes the named registered custom property and inserts its computed initial value.')
        text = once(text,
            'pub(crate) fn remove_and_insert_initial_value(\n    name: &Name,\n    registration: &PropertyDescriptors,\n',
            'pub(crate) fn remove_and_insert_initial_value(\n    name: &Name,\n    registration: &PropertyDescriptors,\n    initial_values: &ComputedCustomProperties,\n')
        text = once(text,
            '    if let Some(ref initial_value) = registration.initial_value {\n        let value = ComputedRegisteredValue::universal(Arc::clone(initial_value));\n        substitution_functions.insert_var(registration, name, value);\n    }\n',
            '    if let Some(value) = initial_values.get(registration, name) {\n        substitution_functions.insert_var(registration, name, value.clone());\n    }\n')
        text = once(text,
            '                    remove_and_insert_initial_value(\n                        name,\n                        registration,\n',
            '                    remove_and_insert_initial_value(\n                        name,\n                        registration,\n                        stylist.get_custom_property_initial_values(),\n')
    else:
        assert path == FILES[1]
        text = once(text,
            '                        remove_and_insert_initial_value(\n                            name,\n                            registration,\n',
            '                        remove_and_insert_initial_value(\n                            name,\n                            registration,\n                            initial_values,\n')
    return text

def patch(originals):
    return ''.join('diff --git a/' + p + ' b/' + p + '\n' + ''.join(
        difflib.unified_diff(originals[p].splitlines(True), candidate(p, originals[p]).splitlines(True),
            fromfile='a/' + p, tofile='b/' + p)) for p in FILES)

if __name__ == '__main__':
    raise SystemExit('Generation helper; import only after manifest authentication.')
