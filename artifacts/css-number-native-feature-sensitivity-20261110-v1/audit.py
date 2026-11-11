import hashlib
import json
from pathlib import Path

HOST = 'aarch64-apple-darwin'
FEATURES = {'default', 'fast_match_byte', 'fast_match_color'}


def metadata(value, workspace, packages):
    names, ids = {}, {}
    for package in value['packages']:
        name = package['name']
        if name in names:
            raise ValueError('Duplicate resolved crate name')
        names[name] = package
        ids[package['id']] = name
        if name == 'css-number-feature-gate':
            if package['version'] != '0.1.0' or package['source'] is not None:
                raise ValueError('Wrong experiment root')
            expected = workspace / 'Cargo.toml'
        else:
            if name not in packages:
                raise ValueError('Unpinned resolved dependency: ' + name)
            record = packages[name]
            if package['version'] != record['version'] or package['source'] != record.get('source'):
                raise ValueError('Resolved source/version changed: ' + name)
            expected = workspace / 'vendor' / name / 'Cargo.toml'
        if Path(package['manifest_path']).resolve() != expected.resolve():
            raise ValueError('Dependency escaped isolated workspace')
    if not {'cssparser', 'cssparser-macros', 'phf', 'css-number-feature-gate'} <= set(names):
        raise ValueError('Default dispatch dependencies absent')
    features = {}
    for node in value['resolve']['nodes']:
        name = ids[node['id']]
        flags = node['features']
        if type(flags) is not list or any(type(flag) is not str for flag in flags) or len(set(flags)) != len(flags):
            raise ValueError('Malformed feature list')
        features[name] = sorted(flags)
    if set(features['cssparser']) != FEATURES:
        raise ValueError('Wrong cssparser dispatch features')
    return features


def vendor(workspace, records, tokenizer, checksum):
    overrides = {'vendor/cssparser/src/tokenizer.rs': tokenizer,
                 'vendor/cssparser/.cargo-checksum.json': checksum}
    for record in records:
        name = record['destination']
        expected = hashlib.sha256(overrides[name]).hexdigest() if name in overrides else record['sha256']
        if hashlib.sha256((workspace / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Materialized source drift: ' + name)
