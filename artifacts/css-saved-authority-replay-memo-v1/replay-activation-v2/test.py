import argparse
import configparser
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import urllib.parse

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('memo_under_test', HERE / 'memo.py')
memo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memo)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
positive, negative = [], []


def rejects(name, action):
    try:
        action()
    except (memo.Rejected, AssertionError, OSError):
        negative.append(name)
    else:
        raise AssertionError(name)


with tempfile.TemporaryDirectory(prefix='saved-authority-memo-fixture-', dir='/private/tmp') as directory:
    root = Path(directory)
    raw = root / 'raw.json'; raw.write_text('{"value": 7}')
    manifest = root / 'FILES.json'; manifest.write_text(json.dumps({'raw.json': sha(raw)}))
    observations = root / 'observations'; observations.mkdir()
    text = root / 'text.txt'; text.write_bytes('é\r\nnext\rline\n'.encode())

    def leaf():
        pins = json.loads(manifest.read_text())
        assert sha(raw) == pins['raw.json']
        assert raw.is_file() and not raw.is_symlink() and raw.stat().st_size > 0
        assert not list(observations.glob('*-wpt-*'))
        assert not (observations / 'original-build').exists()
        assert not (observations / 'candidate-OUTCOMES.json').exists()
        return json.loads(raw.read_bytes())

    def fresh():
        return memo.Session(root, {}, {'policy': {'head': 'fixture'}, 'receipt': {'ok': True}}, [root])

    s = fresh()
    def duplicate():
        a = s.call('leaf', {}, [], {}, leaf)
        assert a == s.call('leaf', {}, [], {}, leaf)
        return a
    with s:
        assert s.call('parent', {}, [], {}, duplicate) == {'value': 7}
        assert s.call('parent', {}, [], {}, duplicate) == {'value': 7}
        assert s.calls == {'parent': 1, 'leaf': 1} and s.hits == {'leaf': 1, 'parent': 1}
        result = s.call('parent', {}, [], {}, duplicate); result['value'] = 99
        assert s.call('parent', {}, [], {}, duplicate)['value'] == 7
        assert s.call('text', {}, [], {}, lambda:text.read_text()) == 'é\nnext\nline\n'
    positive.extend(['duplicate branch once', 'transitive hit', 'deep copy', 'UTF8 universal newlines'])
    raw.write_text('{"value": 8}')
    with s:
        rejects('raw changed unchanged manifest', lambda: s.call('parent', {}, [], {}, duplicate))
    raw.write_text('{"value": 7}')

    def primed():
        session = fresh()
        with session:
            assert session.call('leaf', {}, [], {}, leaf)['value'] == 7
        return session

    for name, path, directory in [
        ('glob matching directory', observations/'new-wpt-page', True),
        ('previously absent directory', observations/'original-build', True),
        ('previously absent receipt', observations/'candidate-OUTCOMES.json', False),
    ]:
        session = primed()
        if directory: path.mkdir()
        else: path.write_text('{}')
        with session:
            rejects(name, lambda: session.call('leaf', {}, [], {}, leaf))
        if directory: path.rmdir()
        else: path.unlink()
    session = primed(); retained = root/'retained.json'; raw.rename(retained); raw.write_bytes(retained.read_bytes())
    with session:
        rejects('same bytes changed inode', lambda: session.call('leaf', {}, [], {}, leaf))
    raw.unlink(); retained.rename(raw)
    session = primed(); raw.rename(retained); raw.symlink_to(retained)
    with session:
        rejects('changed symlink', lambda: session.call('leaf', {}, [], {}, leaf))
    raw.unlink(); retained.rename(raw)
    calls=[]
    def argument(value): calls.append(value['nested']['value']); return value
    session=fresh();arg={'nested':{'value':1}}
    with session:
        assert session.call('argument',{},[arg],{},argument)==arg
        arg['nested']['value']=2
        assert session.call('argument',{},[arg],{},argument)==arg and calls==[1,2]
    positive.append('complete mutable arguments distinguish keys')
    scope={'policy':{'head':'before'}}
    scoped=memo.Session(root,{},scope,[root])
    with scoped:
        assert scoped.call('scope',{},[],{},lambda:scope['policy']['head'])=='before'
        scope['policy']['head']='after'
        assert scoped.call('scope',{},[],{},lambda:scope['policy']['head'])=='after'
        assert scoped.calls['scope']==2
    positive.append('mutable outer policy distinguishes keys')
    calls=[]
    def fail(): calls.append(1); raise AssertionError('fixture failure')
    with session:
        rejects('failure first',lambda:session.call('fail',{},[],{},fail))
        rejects('failure repeated',lambda:session.call('fail',{},[],{},fail))
        assert calls==[1,1] and not session.executing
        rejects('direct open denied',lambda:session.call('open',{},[],{},lambda:open(raw).read()))
        rejects('process denied',lambda:session.call('process',{},[],{},lambda:memo.subprocess.run(['true'])))
    positive.append('failed evaluations never cached')
    helper=root/'helper.py';bindings=root/'BINDINGS.json';imported=root/'imported.json'
    imported.write_text('{"value":7}');bindings.write_text('{"scope":"fixture"}')
    helper.write_text("from pathlib import Path\nimport argparse\nimport configparser\nimport json\nimport urllib.parse\nassert urllib.parse.urlsplit('https://example.test/a').path=='/a'\nassert argparse.Namespace(value=7).value==7\nassert configparser.ConfigParser().sections()==[]\nbinding={'scope':'fixture'}\nloaded=json.loads((Path(__file__).parent/'imported.json').read_text())\ndef validate_refresh(receipt):\n    assert receipt['ok']\n    return loaded\n")
    registry={'helper.py':{'sha256':sha(helper),'function':'validate_refresh','bindings_path':'BINDINGS.json','bindings_sha256':sha(bindings)}}
    session=memo.Session(root,registry,{'policy':'fixture'},[root])
    def module(name):
        spec=importlib.util.spec_from_file_location(name,helper)
        result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
    with session:
        a,b=module('fresh_one'),module('fresh_two')
        assert a.validate_refresh({'ok':True})==b.validate_refresh({'ok':True})=={'value':7}
        assert sum(session.calls.values())==1 and sum(session.hits.values())==1
        rejects('changed receipt argument',lambda:b.validate_refresh({'ok':False}))
        b.binding['scope']='changed';assert b.validate_refresh({'ok':True})=={'value':7}
        assert sum(session.calls.values())==3
    positive.extend(['fresh loaders share source cache','binding value distinguishes key'])
    positive.append('audited preloaded stdlib used inside import frame')
    imported.write_text('{"value":8}')
    with session:
        rejects('changed import-time input',lambda:a.validate_refresh({'ok':True}))
    helper.write_text(helper.read_text()+'\nchanged=True\n')
    with session:
        rejects('changed imported code',lambda:module('changed_code'))
    bindings.write_text('{"scope":"changed"}')
    with session:
        rejects('changed binding file',lambda:a.validate_refresh({'ok':True}))
    # A child hit must contribute its import-time dependencies to a new parent.
    helper.write_text(helper.read_text().replace('\nchanged=True\n',''))
    imported.write_text('{"value":7}');bindings.write_text('{"scope":"fixture"}')
    registry['helper.py']['sha256']=sha(helper)
    registry['helper.py']['bindings_sha256']=sha(bindings)
    stale_session=memo.Session(root,registry,{'policy':'fixture'},[root])
    imported.write_text('{"value":8}')
    with stale_session:
        stale=module('stale_globals')
    imported.write_text('{"value":7}')
    with stale_session:
        current=module('current_globals')
        assert current.validate_refresh({'ok':True})=={'value':7}
        rejects('fresh module stale import seed on hit',lambda:stale.validate_refresh({'ok':True}))
    child_session=memo.Session(root,registry,{'policy':'fixture'},[root])
    with child_session:
        child=module('import_child')
        child.validate_refresh({'ok':True})
        assert child_session.call('new-parent',{},[],{},lambda:child.validate_refresh({'ok':True}))=={'value':7}
        assert sum(child_session.hits.values())==1
    imported.write_text('{"value":9}')
    with child_session:
        rejects('parent inherits child-hit import ledger',lambda:child_session.call('new-parent',{},[],{},lambda:child.validate_refresh({'ok':True})))
    positive.append('child-hit ledger merged into new parent')
    imported.write_text('{"value":7}')
    bytecode=root/'unused.pyc';bytecode.write_bytes(b'not Python source')
    with child_session:
        loader=importlib.machinery.SourceFileLoader('unsupported',str(helper))
        rejects('bytecode loader access rejected in cached call',lambda:child_session.call('bytecode',{},[],{},lambda:loader.get_data(str(bytecode))))
        rejects('nested recording sessions rejected',lambda:fresh().__enter__())
    # Outside recorded functions the session must not suppress live guard behavior.
    with fresh():
        with open(raw) as handle: assert json.load(handle)=={'value':7}
    positive.append('outer uncached I/O preserved')
    scratch=str(root)
assert not Path(scratch).exists()
print(json.dumps({'positive':positive,'negative':negative,'scratch_removed':True,'scratch':scratch,
                  'source_sha256':sha(HERE/'memo.py'),'real_saved_replay':False,
                  'historical_modules_changed':False},indent=2))
