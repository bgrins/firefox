#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    freeze = json.loads((ROOT / 'FREEZE.json').read_text())
    assert digest(ROOT / 'MANIFEST.json') == freeze['manifest_sha256']
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
    for name, expected in manifest.items():
        path = ROOT / name
        assert path.resolve().is_relative_to(ROOT.resolve()), name
        assert digest(path) == expected, name
    design = json.loads((ROOT / 'design/INPUTS.json').read_text())
    for name, expected in design.items():
        assert digest(ROOT / 'design' / name) == expected, name
    parser = (ROOT / 'source/third_party/rust/cssparser/src/parser.rs').read_text()
    tokenizer = (ROOT / 'source/third_party/rust/cssparser/src/tokenizer.rs').read_text()
    proposal = (ROOT / 'scanner-proposal.rs').read_text()
    assert 'const REASONABLE_NESTED_BLOCK_LIMIT: u8 = 75;' in parser
    assert 'let mut stack = SmallVec::<[BlockType; 16]>::new();' in parser
    assert 'pub(crate) fn next_unchecked' in tokenizer
    assert 'pub fn byte_index(&self) -> usize' in tokenizer
    assert proposal.count('Parser::new(css)') == 1
    assert proposal.count('next_including_whitespace_and_comments()') == 1
    assert 'parse_nested_block' not in proposal
    assert 'css = &css[consumed..];' in proposal
    assert 'SubstitutionFunctionKind::from_ident(name).is_ok()' in proposal
    cases = json.loads((ROOT / 'CASES.json').read_text())
    assert cases['status'].startswith('UNEXECUTED')
    print(json.dumps({'authenticated_files': len(manifest), 'design_inputs': len(design),
                      'static_structure_checks': 'PASS', 'native_execution': False,
                      'formal_proof': False, 'proposed_cases_executed': False}, indent=2))


if __name__ == '__main__':
    main()
