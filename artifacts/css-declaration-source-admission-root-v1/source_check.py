import hashlib
import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def inspect():
    source = ROOT / 'source'
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())
    for name, expected in pins.items():
        assert hashlib.sha256((source / name).read_bytes()).hexdigest() == expected
    metadata = ROOT / 'PROVIDERS.json'
    assert hashlib.sha256(metadata.read_bytes()).hexdigest() == 'e95e9ac4be7ff584a7faa0ca4c0bb412cb59ac4d02c22208ee6536ac0099f30b'
    generated = json.loads(metadata.read_text())
    props = source / 'servo/components/style/properties'
    longhands = tomllib.loads((props / 'longhands.toml').read_text())
    shorthands = tomllib.loads((props / 'shorthands.toml').read_text())
    assert len(shorthands) == 94
    for row in generated['longhands']:
        info = longhands[row['name']]
        group = None if row['group'] is None else generated['groups'][row['group']]
        assert group == info.get('logical_group')
        assert row['logical'] == info.get('logical', False)
    maximum = 0
    for name, info in shorthands.items():
        names = info.get('sub_properties', []) + info.get('extra_gecko_sub_properties', [])
        actual = [generated['longhands'][i]['name'] for i in generated['shorthands'][name]]
        assert names == actual and len(set(names)) == len(names), name
        groups = {}
        for sub in names:
            info = longhands[sub]
            if info.get('logical_group'):
                groups.setdefault(info['logical_group'], set()).add(info.get('logical', False))
        assert all(len(kinds) == 1 for kinds in groups.values()), name
        maximum = max(maximum, len(names))
    assert maximum == 19

    reader = {'__name__': 'retained_reader', '__file__': str(ROOT / 'rust_reader.py')}
    exec(compile((ROOT / 'rust_reader.py').read_text(), str(ROOT / 'rust_reader.py'), 'exec'), reader)
    glue = (source / 'servo/ports/geckolib/glue.rs').read_text()
    names = ['set_property_to_declarations', 'set_property',
             'Servo_DeclarationBlock_SetPropertyToAnimationValue',
             'Servo_DeclarationBlock_SetPropertyTypedValue',
             'Servo_DeclarationBlock_SetKeywordValue',
             'Servo_DeclarationBlock_SetLengthValue',
             'Servo_DeclarationBlock_SetTransform',
             'Servo_DeclarationBlock_SetBackdropFilter',
             'Servo_DeclarationBlock_SetColorScheme']
    records = []
    for name in names:
        anchor = 'fn ' + name + '('
        assert glue.count(anchor) == 1
        start = glue.index(anchor)
        ts = reader['tokens'](glue[start:])
        opening = next(i for i, t in enumerate(ts) if t[0] == '{')
        ending = reader['pair'](ts, opening)
        body = glue[start:start + ts[ending][2]]
        calls = body.count('set_property_to_declarations(')
        assert calls == 1
        if name == 'set_property_to_declarations':
            kind = 'fresh plan and callback seam'
            assert 'let mut updates = Default::default();' in body
        elif name in ('set_property', 'Servo_DeclarationBlock_SetPropertyTypedValue'):
            kind = 'parsed source'
            assert 'SourcePropertyDeclaration::default()' in body
            assert 'parse_property_into(' in body
        else:
            kind = 'singleton source'
            assert body.count('SourcePropertyDeclaration::with_one(') == 1
        records.append({'name': name, 'kind': kind, 'source_start': start,
                        'body': body, 'sha256': hashlib.sha256(body.encode()).hexdigest()})
    assert glue.count('set_property_to_declarations(') == len(records)
    return {'ordinary_shorthands': 94, 'maximum_expansion': maximum,
            'metadata_order_group_and_uniqueness_match': True,
            'direct_callers': 8, 'parsed_callers': 2, 'singleton_callers': 6,
            'functions': records}


if __name__ == '__main__':
    print(json.dumps(inspect(), indent=2))
