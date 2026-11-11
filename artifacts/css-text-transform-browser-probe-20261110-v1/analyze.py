import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROPERTY = 'text-transform'


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_text(), object_pairs_hook=strict_object)


def exact(obj, keys):
    if type(obj) is not dict or set(obj) != set(keys.split()):
        raise ValueError('wrong object fields')


def support(row):
    exact(row, 'value error')
    if row['error'] is None:
        if type(row['value']) is not bool:
            raise ValueError('supports result must be Boolean')
    elif type(row['error']) is not str or row['value'] is not None:
        raise ValueError('malformed supports exception')


def declaration(row):
    exact(row, 'before present serialized priority properties cssText error')
    if row['error'] is not None:
        if type(row['error']) is not str or any(row[key] is not None for key in row if key != 'error'):
            raise ValueError('malformed style exception')
        return
    if type(row['present']) is not bool:
        raise ValueError('style presence must be Boolean')
    if any(type(row[key]) is not str for key in ('before', 'serialized', 'priority', 'cssText')):
        raise ValueError('style fields must be strings')
    if type(row['properties']) is not list or any(type(x) is not str for x in row['properties']):
        raise ValueError('declaration names must be strings')


def consistent(row):
    return row['error'] is None and row['priority'] == '' and (
        row['properties'] == [PROPERTY] and row['present'] and row['serialized'] != '' or
        row['properties'] == [] and not row['present'] and row['serialized'] == '')


def analyze(result):
    corpus = read(ROOT / 'corpus.json')
    exact(result, 'schema protocol inputSha256 oracleSha256 modelManifestSha256 capturedAt browser controls rows')
    if type(result['schema']) is not int or result['schema'] != 1 or result['protocol'] != 'css-text-transform-normalized-v1':
        raise ValueError('unknown capture schema')
    for key, expected in [('inputSha256', hashlib.sha256((ROOT / 'corpus.json').read_bytes()).hexdigest()),
                          ('oracleSha256', corpus['oracleSha256']), ('modelManifestSha256', corpus['modelManifestSha256'])]:
        if result[key] != expected:
            raise ValueError('wrong input identity: ' + key)
    if type(result['capturedAt']) is not str or not result['capturedAt']:
        raise ValueError('missing capture time')
    exact(result['browser'], 'userAgent platform appVersion suppliedBuildLabel href')
    if any(type(x) is not str for x in result['browser'].values()) or not result['browser']['userAgent']:
        raise ValueError('missing browser metadata')
    if type(result['controls']) is not list or len(result['controls']) != 4:
        raise ValueError('wrong setup inventory')
    setup_failures = []
    for row, value, expected in zip(result['controls'], ['none', 'uppercase', 'probe-invalid-token', ''], [True, True, False, False]):
        exact(row, 'value supports fresh seeded')
        if row['value'] != value:
            raise ValueError('setup order/input changed')
        support(row['supports'])
        declaration(row['fresh'])
        declaration(row['seeded'])
        good = row['supports']['error'] is None and row['supports']['value'] is expected
        good = good and consistent(row['fresh']) and row['fresh']['before'] == '' and row['fresh']['present'] is expected
        good = good and consistent(row['seeded']) and row['seeded']['before'] != ''
        if value == '':
            good = good and row['seeded']['present'] is False
        elif expected:
            good = good and row['seeded']['present'] is True
        else:
            good = good and row['seeded']['present'] is True and row['seeded']['serialized'] == row['seeded']['before']
        if not good:
            setup_failures.append(value)
    if type(result['rows']) is not list or len(result['rows']) != len(corpus['rows']):
        raise ValueError('missing/extra corpus rows')
    differences = []
    for row, expected in zip(result['rows'], corpus['rows']):
        exact(row, 'id value supports style removal')
        if type(row['id']) is not int or row['id'] != expected['id'] or row['value'] != expected['value']:
            raise ValueError('corpus identity/order changed')
        support(row['supports'])
        declaration(row['style'])
        reasons = []
        if row['supports']['error'] is not None or row['supports']['value'] is not expected['expected']:
            reasons.append('CSS.supports')
        if not consistent(row['style']) or row['style']['before'] != '' or row['style']['present'] is not expected['expected']:
            reasons.append('CSSStyleDeclaration')
        if expected['value'] == '':
            if row['removal'] is None:
                raise ValueError('missing empty-removal observation')
            declaration(row['removal'])
            if not consistent(row['removal']) or row['removal']['before'] == '' or row['removal']['present'] is not False:
                reasons.append('empty-removal')
        elif row['removal'] is not None:
            raise ValueError('unexpected removal observation')
        if reasons:
            differences.append(dict(id=row['id'], value=row['value'], expected=expected['expected'], reasons=reasons,
                                    supports=row['supports'], style=row['style'], removal=row['removal']))
    return dict(status='SETUP_FAILED' if setup_failures else 'MISMATCH' if differences else 'MATCH',
                rows=len(result['rows']), expectedAccepted=38, setupFailures=setup_failures, differences=differences,
                browser=result['browser'], capturedAt=result['capturedAt'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('capture', type=Path)
    args = parser.parse_args()
    try:
        result = analyze(read(args.capture))
    except (ValueError, KeyError, TypeError) as error:
        print(json.dumps(dict(status='INVALID_CAPTURE', reason=str(error))))
        raise SystemExit(2)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['status'] == 'MATCH' else 1)


if __name__ == '__main__':
    main()
