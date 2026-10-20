import hashlib
import itertools
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent


def database(data):
    db = sqlite3.connect(':memory:')
    db.row_factory = sqlite3.Row
    db.executescript((ROOT / 'schema.sql').read_text())
    tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for table, rows in data.items():
        assert table in tables
        columns = {r[1] for r in db.execute('PRAGMA table_info(' + table + ')')}
        for row in rows:
            assert set(row) <= columns
            fields = ','.join(row)
            db.execute(f'INSERT INTO {table} ({fields}) VALUES ({",".join("?" for _ in row)})', tuple(row.values()))
    assert not list(db.execute('PRAGMA foreign_key_check'))
    return db


def records(db, table):
    return [dict(r) for r in db.execute('SELECT * FROM ' + table)]


def digest(db, req):
    sources = [dict(r) for r in db.execute('''SELECT u.*, d.sha256 FROM requirement_source s
        JOIN source_unit u ON u.id=s.unit_id JOIN document d ON d.id=u.document_id
        WHERE s.requirement_id=? ORDER BY u.id''', (req['id'],))]
    interface = [dict(r) for r in db.execute('SELECT * FROM semantic_interface WHERE id=?', (req['interface_id'],))]
    return hashlib.sha256(json.dumps([req, sources, interface], sort_keys=True).encode()).hexdigest()


def guard_atoms(expr):
    assert isinstance(expr, dict)
    op = expr['op']
    if op in ('true', 'false'):
        assert set(expr) == {'op'}
        return set()
    if op == 'atom':
        assert set(expr) == {'op', 'id'} and isinstance(expr['id'], str)
        return {expr['id']}
    if op == 'not':
        assert set(expr) == {'op', 'arg'}
        return guard_atoms(expr['arg'])
    assert op in ('all', 'any') and set(expr) == {'op', 'args'} and isinstance(expr['args'], list)
    return set().union(*(guard_atoms(x) for x in expr['args']))


def evaluate(expr, env):
    op = expr['op']
    if op in ('true', 'false'): return op == 'true'
    if op == 'atom': return env[expr['id']]
    if op == 'not': return not evaluate(expr['arg'], env)
    return (all if op == 'all' else any)(evaluate(x, env) for x in expr['args'])


def satisfiable(expr):
    atoms = sorted(guard_atoms(expr))
    assert len(atoms) <= 10, 'demo guard bound; production needs a certificate-backed solver'
    return any(evaluate(expr, dict(zip(atoms, values))) for values in itertools.product([False, True], repeat=len(atoms)))


def gate(db, profile_id, level='model', whole=True):
    errors = []
    profile = dict(db.execute('SELECT * FROM profile WHERE id=?', (profile_id,)).fetchone())
    if whole and profile['scope'] != 'normative-universe': errors.append('not-a-whole-CSS-profile')
    for key in ['universe_review', 'source_partition_review', 'interaction_review']:
        if profile[key] != 'accepted': errors.append('open-' + key)
    for entry in records(db, 'catalog_entry'):
        if not entry['reviewed'] or entry['disposition'] == 'unresolved' or (entry['disposition'] in ('target', 'dependency') and entry['document_id'] is None):
            errors.append('catalog:' + entry['id'])
        if entry['disposition'] in ('target', 'dependency') and entry['document_id'] is not None and not db.execute('SELECT 1 FROM profile_document WHERE profile_id=? AND document_id=?', (profile_id, entry['document_id'])).fetchone():
            errors.append('unselected-catalog-document:' + entry['id'])
    for unit in records(db, 'source_unit'):
        if not unit['reviewed'] or unit['normative_context'] == 'unresolved' or unit['disposition'] == 'unclassified': errors.append('unit:' + unit['id'])
        if unit['disposition'] in ('obligation', 'definition') and not db.execute('SELECT 1 FROM requirement_source WHERE unit_id=?', (unit['id'],)).fetchone():
            errors.append('unmapped-unit:' + unit['id'])
    requirements = {r['id']: r for r in records(db, 'requirement')}
    interfaces = {r['id']: r for r in records(db, 'semantic_interface')}
    predicates = {r['id']: r for r in records(db, 'predicate')}
    targets = {r['requirement_id']: r for r in records(db, 'target') if r['profile_id'] == profile_id}
    if not any(t['disposition'] == 'active' for t in targets.values()): errors.append('empty-active-targets')
    edges = records(db, 'dependency')
    for row in records(db, 'replacement'):
        if row['profile_id'] != profile_id: continue
        covered, residual = json.loads(row['covered_guard_json']), json.loads(row['residual_guard_json'])
        guard_atoms(covered); guard_atoms(residual)
        if row['partition_review'] != 'accepted': errors.append('replacement-review:' + row['old_id'])
        if satisfiable(residual) and (row['residual_id'] is None or targets.get(row['residual_id'], {}).get('disposition') != 'active'):
            errors.append('lost-residual:' + row['old_id'])
        if targets.get(row['new_id'], {}).get('disposition') != 'active': errors.append('inactive-replacement:' + row['old_id'])
    levels = ['model', 'executable', 'native'][:['model', 'executable', 'native'].index(level) + 1]
    done, visiting = set(), set()

    def visit(ident):
        if ident in visiting:
            errors.append('cycle-needs-composition-certificate:' + ident)
            return
        if ident in done: return
        visiting.add(ident)
        req = requirements[ident]
        if req['interpretation'] != 'accepted': errors.append('interpretation:' + ident)
        guard = json.loads(req['guard_json'])
        for atom in guard_atoms(guard):
            if predicates.get(atom, {}).get('state') != 'accepted': errors.append('predicate:' + atom)
        if not satisfiable(guard): errors.append('false-domain:' + ident)
        interface = interfaces.get(req['interface_id'])
        if not interface or interface['state'] != 'accepted': errors.append('interface:' + ident)
        contract = json.loads(req['contract_json'])
        for selected in levels:
            row = db.execute('SELECT * FROM binding WHERE profile_id=? AND requirement_id=? AND level=?', (profile_id, ident, selected)).fetchone()
            if not row or row['status'] != 'accepted':
                errors.append('binding:' + selected + ':' + ident)
                continue
            if row['requirement_revision'] != req['revision'] or row['contract_digest'] != digest(db, req) or not interface or row['interface_revision'] != interface['revision']:
                errors.append('stale-binding:' + ident)
            if row['observation_ref'] != contract.get('observation'): errors.append('wrong-observation:' + ident)
        for edge in edges:
            if edge['source_id'] == ident: visit(edge['target_id'])
        choices = records(db, 'choice_contract')
        if req['modality'] == 'may' and not any(c['requirement_id'] == ident for c in choices):
            errors.append('missing-choice-contract:' + ident)
        for choice in choices:
            if choice['requirement_id'] == ident:
                if not json.loads(choice['constraint_refs_json']): errors.append('unconstrained-choice:' + ident)
                visit(choice['consistency_obligation']); visit(choice['nonempty_obligation'])
        for transition in records(db, 'transition_contract'):
            if transition['requirement_id'] == ident:
                if not json.loads(transition['trigger_refs_json']): errors.append('missing-triggers:' + ident)
                visit(transition['readiness_obligation'])
        visiting.remove(ident); done.add(ident)

    for ident, target in targets.items():
        if target['disposition'] == 'active': visit(ident)
        elif target['disposition'] == 'replaced' and not db.execute('SELECT 1 FROM replacement WHERE profile_id=? AND old_id=?', (profile_id, ident)).fetchone():
            errors.append('unexplained-replacement:' + ident)
        elif target['disposition'] == 'not-applicable':
            errors.append('nonapplicability-needs-certificate:' + ident)
    return sorted(set(errors))


def synthetic():
    db = database({})
    db.execute("INSERT INTO profile VALUES ('test','synthetic-test','v1','[]','accepted','accepted','accepted')")
    db.execute("INSERT INTO semantic_interface VALUES ('I','v1','{}','accepted')")
    for ident in ['A', 'B']:
        db.execute('INSERT INTO requirement VALUES (?,?,?,?,?,?,?,?,?)', (ident, 'v1', 'rule', 'must', 'synthetic', '{"op":"true"}', '{"observation":"synthetic-observer"}', 'I', 'accepted'))
        req = dict(db.execute('SELECT * FROM requirement WHERE id=?', (ident,)).fetchone())
        db.execute('INSERT INTO binding VALUES (?,?,?,?,?,?,?,?,?,?)', ('test', ident, 'model', 'v1', digest(db, req), 'v1', 'synthetic-definition', 'synthetic-observer', 'synthetic-review-attestation', 'accepted'))
    db.execute("INSERT INTO target VALUES ('test','A','active','synthetic test')")
    db.execute("INSERT INTO dependency VALUES ('A','B','provider')")
    return db


def main():
    actual = database(json.loads((ROOT / 'examples.json').read_text()))
    blockers = gate(actual, 'css-inventory-pilot')
    assert blockers
    assert gate(synthetic(), 'test', whole=False) == []
    challenges = {
        'unsupported-provider': "UPDATE binding SET status='unsupported' WHERE requirement_id='B'",
        'stale-interface-revision': "UPDATE semantic_interface SET revision='v2' WHERE id='I'",
        'missing-interface': "UPDATE requirement SET interface_id=NULL WHERE id='B'",
        'observer-mismatch': "UPDATE binding SET observation_ref='pixels-only' WHERE requirement_id='A'",
        'false-domain': "UPDATE requirement SET guard_json='{\"op\":\"false\"}' WHERE id='A'",
        'unfounded-cycle': "INSERT INTO dependency VALUES ('B','A','provider')",
        'unexplained-replacement': "UPDATE target SET disposition='replaced' WHERE requirement_id='A'",
        'unproved-exclusion': "UPDATE target SET disposition='not-applicable' WHERE requirement_id='A'",
        'changed-contract': "UPDATE requirement SET contract_json='{\"observation\":\"different\"}' WHERE id='A'",
    }
    rejected = {}
    for name, sql in challenges.items():
        db = synthetic(); db.execute(sql)
        failures = gate(db, 'test', whole=False)
        assert failures, name
        rejected[name] = failures
    db = synthetic()
    db.execute("UPDATE target SET disposition='replaced' WHERE requirement_id='A'")
    db.execute("INSERT INTO target VALUES ('test','B','active','synthetic replacement')")
    db.execute('INSERT INTO replacement VALUES (?,?,?,?,?,?,?,?)', ('test','A','B','{"op":"false"}','{"op":"true"}',None,'synthetic authority','accepted'))
    failures = gate(db, 'test', whole=False)
    assert 'lost-residual:A' in failures
    rejected['lost-residual'] = failures
    assert gate(synthetic(), 'test', 'native', whole=False)
    print(json.dumps({'sample_blockers': blockers, 'synthetic_positive_structural_gate': True,
                      'rejected_challenges': rejected, 'model_does_not_imply_native': True,
                      'semantic_completion_checked': False}, indent=2))


if __name__ == '__main__': main()
