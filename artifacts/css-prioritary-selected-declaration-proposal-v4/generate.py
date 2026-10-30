from pathlib import Path
import difflib
import hashlib
import json
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V3 = ROOT / 'artifacts/css-prioritary-selected-declaration-proposal-v3'
A = ROOT / 'artifacts/css-registered-selected-color-union-only-proposal-v1'
REL = 'servo/components/style/properties/cascade.rs'
FORMAT = Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustfmt')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def span(text, start, end):
    first = text.index(start)
    return text[first:text.index(end, first)]


def replace(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def compose(v3, source):
    result = replace(v3, '    remove_and_insert_initial_value, substitute_references_if_needed_and_apply,',
                     '    invalid_custom_value_depends_on_color_scheme, prepare_custom_value,\n'
                     '    remove_and_insert_initial_value, substitute_references_if_needed_and_apply,')
    result = replace(result, '        let mut registered = false;\n',
                     '        let mut registered = false;\n        let mut color_eligible = false;\n')
    eligibility = span(source, '                color_eligible = registration.syntax', '                let has_dependency')
    result = replace(result, '                registered = !registration.is_universal();\n',
                     '                registered = !registration.is_universal();\n' + eligibility)
    result = replace(result, '        let mut lowlink = index;\n',
                     '        let mut lowlink = index;\n        let mut prepared_custom = None;\n')
    preparation = span(source, '            if let VarType::Custom(ref name) = var\n                && color_eligible',
                       '            // ... Then the non-custom properties')
    marker = '            // ... Then the non-custom properties'
    result = replace(result, marker, preparation + marker)
    hook = span(source, '        if let VarType::Custom(ref name) = var {\n            let cyclic',
                '        context.var_info[index].lowlink = lowlink;')
    hook = hook.replace('VarType::NonCustom(SingleNonCustomReference::ColorScheme)',
                        'VarType::NonCustom(LonghandId::ColorScheme)')
    marker = '        context.var_info[index].lowlink = lowlink;'
    result = replace(result, marker, hook + marker)
    result = replace(result, '                if let Some(ref v) = value {\n',
                     '                if let Some(prepared) = prepared_custom {\n'
                     '                    prepared.apply(name, context.stylist, context.computed_context);\n'
                     '                } else if let Some(ref v) = value {\n')
    return result


if __name__ == '__main__':
    assert sha(V3 / 'FILES.json') == '832d247da7050b1038bcf1b96a8fa72fa2cef9f63c2f514da37fc182de9cfbc6'
    assert sha(A / 'FILES.json') == '8c9697943910f1c90341e6a24d5d5e447e052123fda96e7c7f8d60e5db67e740'
    for parent in [V3, A]:
        for name, record in json.loads((parent / 'FILES.json').read_bytes()).items():
            assert sha(parent / name) == record['sha256'] and (parent / name).stat().st_size == record['bytes']
    assert sha(FORMAT) == 'ab19d01d0a7a3a901c62b6b013a98452d38084b5d7f446ccb20c5e83c10db99f'
    roles = json.loads((A / 'SOURCE-ROLES.json').read_bytes())
    for rel in roles:
        for tree in ['base', 'candidate']:
            target = HERE / tree / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(A / tree / rel, target)
    assert (V3 / 'base' / REL).read_bytes() == (A / 'base' / REL).read_bytes()
    (HERE / 'candidate' / REL).write_text(compose((V3 / 'candidate' / REL).read_text(), (A / 'candidate' / REL).read_text()))
    shutil.copyfile(A / 'rustfmt.toml', HERE / 'rustfmt.toml')
    subprocess.run([str(FORMAT), '--config-path', str(HERE / 'rustfmt.toml'), str(HERE / 'candidate' / REL)], check=True)
    patches = {name: [] for name in ['native.patch', 'V3-DELTA.patch', 'A-DELTA.patch']}
    result = {}
    for rel in roles:
        candidate = HERE / 'candidate' / rel
        base = HERE / 'base' / rel
        v3 = V3 / 'candidate' / rel if rel == REL else base
        source = A / 'candidate' / rel
        result[rel] = {'base': {'path': str(base.relative_to(ROOT)), 'sha256': sha(base)},
                       'v3': {'path': str(v3.relative_to(ROOT)), 'sha256': sha(v3)},
                       'color_only': {'path': str(source.relative_to(ROOT)), 'sha256': sha(source)},
                       'candidate': {'path': str(candidate.relative_to(ROOT)), 'sha256': sha(candidate)}}
        for name, before in [('native.patch', base), ('V3-DELTA.patch', v3), ('A-DELTA.patch', source)]:
            patches[name].extend(difflib.unified_diff(before.read_text().splitlines(True), candidate.read_text().splitlines(True), fromfile='a/' + rel, tofile='b/' + rel))
    for name, lines in patches.items():
        (HERE / name).write_text(''.join(lines))
    (HERE / 'SOURCE-ROLES.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({rel: row['candidate']['sha256'] for rel, row in result.items()}))
