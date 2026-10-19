import hashlib
import re


def definition(text, name, indent=0, prefix=None):
    if prefix:
        assert text.count(prefix) == 1
        text = text.split(prefix, 1)[1].split("\n}", 1)[0]
    pattern = r"^" + " " * indent + r"(?:pub(?:\([^\n]*\))? )?fn " + re.escape(name) + r"(?:<[^\n]*>)?\("
    found = list(re.finditer(pattern, text, re.M))
    assert len(found) == 1, (name, len(found))
    start = found[0].start()
    close = "\n" + " " * indent + "}"
    end = text.index(close, start) + len(close)
    return text[start:end] + "\n"


def inspect(root):
    records = {}
    def put(key, file, name, indent=0, prefix=None):
        body = definition((root / file).read_text(), name, indent, prefix)
        records[key] = {'source': file, 'sha256': hashlib.sha256(body.encode()).hexdigest(), 'body': body}
    for variant in ('source', 'candidate'):
        put(variant + '/substitute', 'source/' + variant + '/custom_properties.rs', 'substitute_references_if_needed_and_apply')
    base = 'providers/servo/components/style/'
    for name in ('new', 'add_flags', 'build'):
        put('builder/' + name, base + 'properties/properties.mako.rs', name, 4, "impl<'a> StyleBuilder<'a> {")
    put('difference', base + 'gecko/restyle_damage.rs', 'compute_style_difference', 4)
    put('hint', base + 'matching.rs', 'accumulate_damage_for', 4)
    put('consume', base + 'data.rs', 'needs_to_recascade_self')
    for name in ('restyle_kind', 'restyle_kind_for_animation'):
        put(name, base + 'data.rs', name, 4)
    put('root-input', base + 'properties/cascade.rs', 'apply_declarations')
    put('root-read', base + 'values/computed/mod.rs', 'is_root_element', 4)
    cpp = (root / 'providers/layout/style/GeckoBindings.cpp').read_text()
    marker = 'uint32_t Gecko_CalcStyleDifference('
    assert cpp.count(marker) == 1
    start = cpp.index(marker)
    body = cpp[start:cpp.index('\n}', start) + 2] + '\n'
    records['difference-provider'] = {'source': 'providers/layout/style/GeckoBindings.cpp', 'sha256': hashlib.sha256(body.encode()).hexdigest(), 'body': body}
    addition = "                    if !registration.inherits() {\n                        context\n                            .style()\n                            .add_flags(ComputedValueFlags::INHERITS_RESET_STYLE);\n                    }\n"
    candidate = records['candidate/substitute']['body']
    original = records['source/substitute']['body']
    assert candidate.count(addition) == 1 and candidate.replace(addition, '') == original
    assert 'pseudo.is_none() && element.is_some_and(|e| e.is_root())' in records['root-input']['body']
    return records
