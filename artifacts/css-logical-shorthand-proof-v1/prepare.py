import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
GENERATED = 'objdir-full.noindex/aarch64-apple-darwin/release/build/style-7fa586137f1e787d/out/properties.rs'

def block(text, marker):
    if text.count(marker) != 1:
        raise RuntimeError('Ambiguous marker ' + marker)
    start = text.index(marker)
    brace = text.index('{', start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]


def extract(text, kind):
    if kind == 'native':
        a = text.index('#[derive(Clone, Copy, Eq, Ord, PartialEq, PartialOrd)]')
        return text[a:text.index('\n/// A helper function to animate', a)]
    if kind == 'shorthands':
        return block(text, 'pub enum ShorthandId {') + '\n\n' + block(text, 'pub fn longhands(self)')
    if kind == 'glue':
        a = text.index('struct PrioritizedPropertyIter')
        z = text.index('\n#[unsafe(no_mangle)]', text.index('pub extern "C" fn Servo_GetComputedKeyframeValues', a))
        return text[a:z]
    if kind == 'iterator':
        return block(text, 'impl<Item> Iterator for NonCustomPropertyIterator<Item>') + '\n\n' + block(text, 'pub fn is_logical(self) -> bool')
    if kind == 'template':
        return block(text, 'pub fn longhands(self)') + '\n\n' + block(text, 'pub fn idl_name_sort_order(self)')
    markers = {'longhands': 'pub enum LonghandId {', 'logical': 'pub(super) fn logical()', 'idl': 'pub fn idl_name_sort_order(self)'}
    return block(text, markers[kind])


def main():
    records = []
    requests = [(GENERATED, kind, 'generated-' + kind + '.rs') for kind in ['shorthands', 'longhands', 'logical', 'idl']]
    requests += [('servo/components/style/values/animated/mod.rs', 'native', 'native-candidate.rs'),
                 ('artifacts/css-logical-shorthand-fix-v1/pre-fix-animated.rs', 'native', 'native-before.rs'),
                 ('servo/ports/geckolib/glue.rs', 'glue', 'native-glue.rs'),
                 ('servo/components/style/properties/mod.rs', 'iterator', 'native-iterator.rs'),
                 ('servo/components/style/properties/properties.mako.rs', 'template', 'native-template.rs')]
    for name, kind, dest in requests:
        raw = (ROOT / name).read_bytes()
        fragment = extract(raw.decode(), kind)
        (BASE / dest).write_text(fragment)
        records.append({'source': name, 'source_sha256': hashlib.sha256(raw).hexdigest(), 'kind': kind, 'snapshot': dest, 'sha256': hashlib.sha256(fragment.encode()).hexdigest()})
    (BASE / 'SOURCE-v1.json').write_text(json.dumps(records, indent=2) + '\n')

if __name__ == '__main__':
    main()
