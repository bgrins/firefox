import hashlib
import json
from pathlib import PurePosixPath

BASE = 'e86b64866cdc5e2260ba9be08c45756fd96e21bb'
FONT = '334937d9ef8537e95cb80b29295797bc78f44252'
FONT_RESEARCH = '2701dc46ac5920adf3505885c67936287e1b037f'
POST_FONT_RESEARCH = 'cb5bb52e3a1645f8eaf5db40cf727c4da36cac8b'
ROLE = 'servo/components/style/custom_properties.rs'
PREIMAGE = 'bb13b61a82f6736c7c4488fc6b58c4ed99cc9a6a4d2d427d3e60530010fe6ccd'
digest = lambda body: hashlib.sha256(body).hexdigest()


def authenticated(root, record):
    assert record is not None and set(record) == {'path', 'sha256'}
    assert record['path'].startswith('artifacts/') and '..' not in record['path'].split('/')
    path = root / record['path']
    assert path.is_file() and not path.is_symlink()
    body = path.read_bytes()
    assert digest(body) == record['sha256']
    return json.loads(body)


def require_research(receipt, head):
    assert receipt['head'] == head and receipt['committed'] is True
    assert receipt['signature_verified'] is True and receipt['accepted_fix_increment'] == 0
    assert receipt['native_working_diff_preserved'] is True


def require_native(receipt, stage, parent):
    assert set(receipt) == {'stage', 'commit', 'parent', 'signature_verified', 'files',
                            'epoch_sha256', 'accepted', 'accepted_fix_increment', 'app_rebuilt'}
    assert receipt['stage'] == stage['stage'] and receipt['parent'] == parent
    assert receipt['signature_verified'] is True and receipt['accepted'] is False
    assert receipt['accepted_fix_increment'] == 0 and receipt['app_rebuilt'] is False
    assert receipt['files'] == sorted(stage['files'])
    assert len(receipt['commit']) == 40 and set(receipt['commit']) <= set('0123456789abcdef')
    assert len(receipt['epoch_sha256']) == 64 and set(receipt['epoch_sha256']) <= set('0123456789abcdef')
    assert receipt['commit'] != parent


def signature(git, allowed_signers, revision):
    git('-c', 'gpg.ssh.allowedSignersFile=' + allowed_signers, 'verify-commit', revision)


def artifact_interval(git, allowed_signers, start, end):
    assert start != end
    assert not git('merge-base', '--is-ancestor', start, end)
    commits = git('rev-list', '--parents', start + '..' + end).decode().splitlines()
    assert commits and commits[0].split()[0] == end
    expected = end
    for row in commits:
        fields = row.split()
        assert len(fields) == 2 and fields[0] == expected
        revision, parent = fields
        assert all(path.startswith('artifacts/') for path in git('diff', '--name-only', parent, revision).decode().splitlines())
        expected = parent
    assert expected == start
    signature(git, allowed_signers, end)


def native_history(git, allowed_signers, receipt, stage):
    commit, parent = receipt['commit'], receipt['parent']
    assert git('rev-list', '--parents', '-n', '1', commit).decode().split() == [commit, parent]
    signature(git, allowed_signers, commit)
    assert sorted(git('diff', '--name-only', parent, commit).decode().splitlines()) == sorted(stage['files'])
    for path, record in stage['files'].items():
        assert digest(git('show', commit + ':' + path)) == record['sha256']
        if path in stage['head_preimages']:
            assert digest(git('show', parent + ':' + path)) == stage['head_preimages'][path]
        else:
            assert not git('ls-tree', parent, '--', path)


def verify(root, git, allowed_signers, binding, tested_head, research, head):
    assert binding and set(binding) == {'tested_head', 'font_receipt', 'font_research', 'font_stages',
                                       'post_font_research', 'cancellation_research', 'cancellation_stages',
                                       'cancellation_receipt', 'cancellation_installation', 'cancellation_delivery'}
    assert all(binding.values()), 'pending actual cancellation publication'
    assert binding['tested_head'] == tested_head == BASE
    font = authenticated(root, binding['font_receipt'])
    font_research = authenticated(root, binding['font_research'])
    post_font_research = authenticated(root, binding['post_font_research'])
    cancel_research = authenticated(root, binding['cancellation_research'])
    cancellation = authenticated(root, binding['cancellation_receipt'])
    font_stage, = authenticated(root, binding['font_stages'])['stages']
    cancel_stage, = authenticated(root, binding['cancellation_stages'])['stages']
    assert font_stage['stage'] == 'font-units' and len(font_stage['files']) == 3
    assert cancel_stage['stage'] == 'selective-cancellation' and len(cancel_stage['files']) == 5
    assert ROLE not in font_stage['files'] and ROLE not in cancel_stage['files']
    require_research(font_research, FONT_RESEARCH)
    assert font_research['parent'] == BASE
    require_native(font, font_stage, FONT_RESEARCH)
    assert font['commit'] == FONT
    require_research(post_font_research, POST_FONT_RESEARCH)
    assert post_font_research['parent'] == FONT
    require_research(cancel_research, cancel_research['head'])
    assert cancel_research['parent'] == POST_FONT_RESEARCH
    require_native(cancellation, cancel_stage, cancel_research['head'])
    assert git('rev-list', '--parents', '-n', '1', FONT_RESEARCH).decode().split() == [FONT_RESEARCH, BASE]
    assert git('rev-list', '--parents', '-n', '1', POST_FONT_RESEARCH).decode().split() == [POST_FONT_RESEARCH, FONT]
    assert git('rev-list', '--parents', '-n', '1', cancel_research['head']).decode().split() == [cancel_research['head'], POST_FONT_RESEARCH]
    artifact_interval(git, allowed_signers, BASE, FONT_RESEARCH)
    native_history(git, allowed_signers, font, font_stage)
    artifact_interval(git, allowed_signers, FONT, POST_FONT_RESEARCH)
    artifact_interval(git, allowed_signers, POST_FONT_RESEARCH, cancel_research['head'])
    native_history(git, allowed_signers, cancellation, cancel_stage)
    installed = authenticated(root, binding['cancellation_installation'])
    delivery = authenticated(root, binding['cancellation_delivery'])
    runtime = PurePosixPath(binding['cancellation_receipt']['path']).parent
    assert PurePosixPath(binding['cancellation_installation']['path']) == runtime / 'INSTALL-RESULT.json'
    assert PurePosixPath(binding['cancellation_delivery']['path']) == runtime / 'delivery/DELIVERY.json'
    assert installed['stage'] == cancel_stage['stage'] and installed['installed'] is True
    assert installed['accepted'] is False and installed['app_rebuilt'] is False
    assert installed['files'] == sorted(cancel_stage['files'])
    assert installed['new_tests_created'] == sorted(cancel_stage['create_tests'])
    assert installed['existing_tests_adopted_without_write'] == []
    assert delivery['installation_manifest'] == installed['manifest_sha256']
    tests = {path: record['sha256'] for path, record in cancel_stage['files'].items() if path in cancel_stage['create_tests']}
    assert delivery['files'] == tests
    assert delivery['registered_urls'] == sorted('/' + path.removeprefix('testing/web-platform/tests/') for path in tests)
    assert delivery['lint_exit'] == delivery['lint_errors'] == 0
    assert delivery['manifest_entries_verified'] is True and delivery['browser_executed'] is False
    assert delivery['evidence'] and delivery['manifest_command']
    for path, pin in delivery['evidence'].items():
        assert digest((root / path).read_bytes()) == pin
    require_research(research, head)
    assert git('rev-list', '--parents', '-n', '1', head).decode().split() == [head, research['parent']]
    artifact_interval(git, allowed_signers, cancellation['commit'], head)
    assert digest(git('show', cancellation['commit'] + ':' + ROLE)) == PREIMAGE
    assert digest(git('show', head + ':' + ROLE)) == PREIMAGE
    return cancellation['commit']
