import argparse
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import importlib.util

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("source_importer", Path(__file__).with_name("importer.py"))
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)

HERE = Path(__file__).resolve().parent


def rejected(fn, message):
    try:
        fn()
    except ValueError as error:
        if message not in str(error):
            raise AssertionError((message, str(error)))
        return str(error)
    raise AssertionError('mutation was accepted')


def check(output):
    lock = json.loads((HERE / 'sources.lock.json').read_text())
    assert len(lock['documents']) == 3 and all(d['status'] == 'acquired' for d in lock['documents'])
    summaries = importer.run(HERE / 'sources.lock.json', output)
    controls = {}
    for document in lock['documents']:
        name = document['id']
        raw = (HERE / document['path']).read_bytes()
        actual = gzip.decompress((output / (name + '.json.gz')).read_bytes())
        expected = gzip.decompress((HERE / 'inventory' / (name + '.json.gz')).read_bytes())
        assert actual == expected, name
        ledger = json.loads(actual)
        assert ledger['candidate'] is not None
        assert not any(x['kind'] == 'duplicate-source-id' for x in ledger['frontier'])
        controls[name + ':stale-source'] = rejected(lambda: importer.validate(document, raw + b' ', ledger), 'stale source')
        bad = deepcopy(ledger)
        bad['units'].pop()
        controls[name + ':missing-last-unit'] = rejected(lambda: importer.validate(document, raw, bad), 'unaccounted source suffix')
        bad = deepcopy(ledger)
        bad['units'][1]['identity'] = bad['units'][0]['identity']
        controls[name + ':duplicate-identity'] = rejected(lambda: importer.validate(document, raw, bad), 'duplicate identity')
        bad = deepcopy(ledger)
        bad['units'][1]['start'] += 1
        controls[name + ':byte-gap'] = rejected(lambda: importer.validate(document, raw, bad), 'missing/overlapping unit')
    fixture = '<!doctype html>\n<p id="anchor" title="a>b">é&#x10000;&amp;<!--note--></p><script>if(a<b)x++;</script>tail'
    raw = fixture.encode()
    doc = dict(id='fixture',sha256=importer.digest(raw),bytes=len(raw),final_url='https://example.invalid/',anchor='anchor')
    ledger = importer.inventory(doc, raw)
    assert b''.join(raw[u['start']:u['end']] for u in ledger['units']) == raw
    accent = next(u for u in ledger['units'] if raw[u['start']:u['end']] == 'é'.encode())
    assert accent['start'] == raw.index('é'.encode()) and accent['end'] == accent['start'] + 2
    assert any(raw[u['start']:u['end']] == b'<p id="anchor" title="a>b">' for u in ledger['units'])
    assert any(raw[u['start']:u['end']] == b'if(a<b)x++;' for u in ledger['units'])
    missing = importer.inventory(doc | {'anchor':'missing'}, raw)
    assert missing['candidate'] is None
    assert any(x['kind'] == 'target-anchor' for x in missing['frontier'])
    with tempfile.TemporaryDirectory(prefix='source-ledger-control-') as temporary:
        temp = Path(temporary)
        (temp / 'fixture.html').write_bytes(raw + b' ')
        (temp / 'lock.json').write_text(json.dumps({'documents':[doc | {'status':'acquired','path':'fixture.html'}]}))
        controls['stale-input:no-output'] = rejected(lambda: importer.run(temp / 'lock.json', temp / 'out'), 'stale source')
        assert not (temp / 'out').exists()
        (temp / 'lock.json').write_text(json.dumps({'documents':[doc, doc]}))
        controls['duplicate-document:no-output'] = rejected(lambda: importer.run(temp / 'lock.json', temp / 'out'), 'duplicate document identity')
        assert not (temp / 'out').exists()
    document = lock['documents'][0]
    raw = (HERE / document['path']).read_bytes()
    old = b'must place at least some content'
    new = b'may place at least some content'
    assert raw.count(old) == 1
    edited = raw.replace(old, new)
    prior = json.loads(gzip.decompress((HERE / 'inventory/fragmentation.json.gz').read_bytes()))
    controls['semantic-edit:old-lock'] = rejected(lambda: importer.inventory(document, edited), 'stale source')
    updated = document | dict(sha256=importer.digest(edited), bytes=len(edited))
    controls['semantic-edit:old-ledger'] = rejected(lambda: importer.validate(updated, edited, prior), 'wrong source binding')
    following = importer.inventory(updated, edited)
    assert set(u['identity'] for u in prior['units']).isdisjoint(u['identity'] for u in following['units'])
    edit = dict(status='synthetic source edit, not a CSSWG revision',old=old.decode(),new=new.decode(),
                source_byte=raw.index(old),old_sha256=document['sha256'],new_sha256=updated['sha256'],
                old_candidate=prior['candidate'],new_candidate=following['candidate'],
                effect='old lock and old ledger rejected; reimport creates new source identities, interpretation remains proposed')
    (output / 'EDIT-INVALIDATION.json').write_bytes(importer.canonical(edit))
    result = dict(status='PASS',python=sys.version,documents=summaries,controls=controls,
                  positive_fixture='UTF8 positions, entity references, quoted >, comments, raw script and full reconstruction',
                  scope='source accounting and source-bound invalidation only, not DOM or normative semantics')
    (output / 'RESULT.json').write_bytes(importer.canonical(result))
    print(json.dumps({'status':'PASS','documents':len(summaries),'controls':len(controls),'bytes':sum(d['bytes'] for d in summaries)},indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    check(args.output)
