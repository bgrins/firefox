from pathlib import Path
import copy
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def reject_duplicates(pairs):
    out = {}
    for key, value in pairs:
        assert key not in out, ('duplicate key', key)
        out[key] = value
    return out


def read(path):
    return json.loads(path.read_text(), object_pairs_hook=reject_duplicates)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def validate(ledger, locks, shape):
    assert ledger['schema_version'] == 1
    assert ledger['universe_complete'] is False
    assert ledger['source_accounting_complete'] is False
    rows = ledger['requirements']
    assert len({r['id'] for r in rows}) == len(rows)
    assert [r['id'] for r in rows] == list(shape)
    lock_by_id = {s['id']: s for s in locks}
    assert len(lock_by_id) == len(locks)
    for source in locks:
        rel = Path(source['path'])
        assert not rel.is_absolute() and '..' not in rel.parts
        path = ROOT / rel
        assert path.is_file() and not path.is_symlink()
        data = path.read_bytes()
        assert len(data) == source['bytes'] and sha(data) == source['sha256']
    for row in rows:
        for key, value in shape[row['id']].items():
            assert row[key] == value, (row['id'], key)
        data = (ROOT / lock_by_id[row['source']]['path']).read_bytes()
        span = row['source_span']
        assert type(span['start']) is int and type(span['end']) is int
        assert 0 <= span['start'] < span['end'] <= len(data)
        body = data[span['start']:span['end']]
        assert sha(body) == span['sha256']
        anchor = row['anchor'].encode()
        assert any(a in body.split(b'>', 1)[0] for a in (b'id="' + anchor + b'"', b'id=' + anchor))
        assert row['dependencies'] and len({d['id'] for d in row['dependencies']}) == len(row['dependencies'])
        assert all(d['status'] == 'open' for d in row['dependencies'])
        assert row['semantic_closed'] is False
        assert all(row[k] == 'unbound' for k in ('model_coverage', 'proof_coverage', 'engine_conformance'))
        assert row['source_accounting'] == 'selected section only; remaining obligations unclassified'
        assert row['interpretation'] == 'candidate-not-independently-reviewed'
    return True


def main():
    ledger = read(ROOT / 'sample-ledger.json')
    locks = read(ROOT / 'source-lock.json')
    shape = read(ROOT / 'reviewed-shape.json')
    validate(ledger, locks, shape)
    changes = {
        'delete-residual': lambda x: x['requirements'].pop(0),
        'permission-to-must': lambda x: x['requirements'][3].update(modality='required-algorithm'),
        'drop-role-guard': lambda x: x['requirements'][-1].update(applicability='all HTML UAs'),
        'forget-choice-persistence': lambda x: x['requirements'][5].update(choice_scope='fresh choice each call'),
        'erase-dependencies': lambda x: x['requirements'][7].update(dependencies=[]),
        'claim-semantic-closure': lambda x: x['requirements'][1].update(semantic_closed=True),
        'claim-native-coverage': lambda x: x['requirements'][1].update(engine_conformance='proved'),
        'claim-source-completeness': lambda x: x.update(source_accounting_complete=True),
        'duplicate-row': lambda x: x['requirements'].append(copy.deepcopy(x['requirements'][0])),
        'shift-byte-span': lambda x: x['requirements'][0]['source_span'].update(start=0),
    }
    rejected = []
    for name, mutate in changes.items():
        other = copy.deepcopy(ledger)
        mutate(other)
        try:
            validate(other, locks, shape)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError(('accepted corruption', name))
    print(json.dumps(dict(status='pass', sources=len(locks), sample_rows=len(ledger['requirements']),
                          rejected_corruptions=rejected, semantic_validation=False,
                          complete_normative_inventory=False), indent=2))


if __name__ == '__main__':
    main()
