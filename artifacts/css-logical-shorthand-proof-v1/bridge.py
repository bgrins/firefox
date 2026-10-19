import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent


def inventory(read=lambda name: (BASE / name).read_text()):
    def variants(text, name):
        section = text.split('pub enum ' + name + ' {', 1)[1].split('}', 1)[0]
        rows = re.findall(r'/// ([^\n]+)\n\s+(\w+) = (\d+),', section)
        if [int(i) for _, _, i in rows] != list(range(len(rows))):
            raise RuntimeError('Invalid enum coverage')
        return rows
    longs = variants(read('generated-longhands.rs'), 'LonghandId')
    shorts = variants(read('generated-shorthands.rs'), 'ShorthandId')
    if len(longs) != 431 or len(shorts) != 95:
        raise RuntimeError('Changed property inventory')
    map_text = read('generated-shorthands.rs').split('static MAP:', 1)[1].split('NonCustomPropertyIterator {', 1)[0]
    maps = re.findall(r'&\[\s*((?:LonghandId::\w+,\s*)*)\]', map_text)
    if len(maps) != len(shorts):
        raise RuntimeError('Incomplete shorthand map')
    words_text = read('generated-logical.rs').split('from_storage([', 1)[1].split('])', 1)[0]
    words = [int(x.strip(), 16) for x in words_text.split(',')]
    if len(words) != (len(longs) + 31) // 32:
        raise RuntimeError('Invalid logical bitset length')
    logical = {name: bool(words[int(i) // 32] & (1 << (int(i) % 32))) for _, name, i in longs}
    orders_text = read('generated-idl.rs').split('= [', 1)[1].split('];', 1)[0]
    orders = [int(x) for x in re.findall(r'\d+', orders_text)]
    if sorted(orders) != list(range(len(shorts))):
        raise RuntimeError('Invalid IDL permutation')
    def idl(css):
        parts = css.split('-')
        return parts[0] + ''.join(x[:1].upper() + x[1:] for x in parts[1:])
    idl_names = [idl(css) for css, _, _ in shorts]
    if orders != [sorted(idl_names).index(x) for x in idl_names]:
        raise RuntimeError('IDL order disagrees with independent codepoint conversion')
    rows = []
    for (css, name, index), members, order in zip(shorts, maps, orders):
        names = re.findall(r'LonghandId::(\w+)', members)
        if not names or len(names) != len(set(names)) or any(n not in logical for n in names):
            raise RuntimeError('Invalid component list')
        flags = [logical[n] for n in names]
        rows.append({'name': name, 'css': css, 'members': names, 'flags': flags, 'idl': idl_names[int(index)], 'order': order})
    mixed = [x['name'] for x in rows if any(x['flags']) and not all(x['flags'])]
    if mixed != ['All'] or sum(all(x['flags']) for x in rows) != 26:
        raise RuntimeError('Changed logical classification inventory')
    if len(rows[-1]['members']) != 406 or rows[-1]['name'] != 'All':
        raise RuntimeError('Changed all shorthand')
    return {'longhands': [{'name': name, 'css': css, 'logical': logical[name]} for css, name, _ in longs], 'shorthands': rows}


def generate(native, data):
    longs = data['longhands']
    shorts = data['shorthands']
    lookup = {row['name']: i for i, row in enumerate(longs)}
    flags = ','.join(str(x['logical']).lower() for x in longs)
    arrays = ',\n'.join('&[' + ','.join('LonghandId(' + str(lookup[n]) + ')' for n in x['members']) + ']' for x in shorts)
    orders = ','.join(str(x['order']) for x in shorts)
    names = ','.join(json.dumps(x['idl']) for x in shorts)
    return '''use std::cmp;
#[derive(Clone,Copy)] struct LonghandId(usize);
impl LonghandId { fn is_logical(self)->bool { LOGICAL[self.0] } }
#[derive(Clone,Copy)] struct ShorthandId(usize);
impl ShorthandId {
 fn longhands(self)->impl Iterator<Item=LonghandId> { MEMBERS[self.0].iter().copied() }
 fn idl_name_sort_order(self)->u32 { ORDERS[self.0] }
}
#[derive(Clone,Copy)] enum NonCustom { Long(LonghandId), Short(ShorthandId) }
impl NonCustom { fn longhand_or_shorthand(self)->Result<LonghandId,ShorthandId> {
 match self {Self::Long(x)=>Ok(x),Self::Short(x)=>Err(x)}
}}
#[derive(Clone,Copy)] enum PropertyId { NonCustom(NonCustom), Custom(()) }
impl PropertyId { fn as_shorthand(self)->Option<ShorthandId> {
 match self {Self::NonCustom(NonCustom::Short(x))=>Some(x),_=>None}
}}
''' + f'const LOGICAL: [bool; {len(longs)}] = [{flags}];\nconst MEMBERS: [&[LonghandId]; {len(shorts)}] = [{arrays}];\nconst ORDERS: [u32; {len(shorts)}] = [{orders}];\nconst NAMES: [&str; {len(shorts)}] = [{names}];\n' + native + '''
fn spec(a:PropertyId,b:PropertyId)->cmp::Ordering {
 use PropertyId::*;
 use NonCustom::*;
 match (a,b) {
  (Custom(_),Custom(_))=>cmp::Ordering::Equal,
  (Custom(_),_)=>cmp::Ordering::Less,
  (_,Custom(_))=>cmp::Ordering::Greater,
  (NonCustom(Long(a)),NonCustom(Long(b)))=>LOGICAL[a.0].cmp(&LOGICAL[b.0]),
  (NonCustom(Long(_)),NonCustom(Short(_)))=>cmp::Ordering::Less,
  (NonCustom(Short(_)),NonCustom(Long(_)))=>cmp::Ordering::Greater,
  (NonCustom(Short(a)),NonCustom(Short(b)))=> {
   let aa=MEMBERS[a.0]; let bb=MEMBERS[b.0];
   if aa.len()!=bb.len() { return aa.len().cmp(&bb.len()); }
   let a_physical=aa.iter().any(|x| !LOGICAL[x.0]);
   let b_physical=bb.iter().any(|x| !LOGICAL[x.0]);
   if a_physical!=b_physical { return b_physical.cmp(&a_physical); }
   NAMES[a.0].cmp(NAMES[b.0])
  }
 }
}
fn main() {
 let mut all=vec![PropertyId::Custom(())];
 all.extend((0..LOGICAL.len()).map(|i|PropertyId::NonCustom(NonCustom::Long(LonghandId(i)))));
 all.extend((0..MEMBERS.len()).map(|i|PropertyId::NonCustom(NonCustom::Short(ShorthandId(i)))));
 let mut checks=0usize;
 for (i,a) in all.iter().enumerate() { for (j,b) in all.iter().enumerate() {
  assert_eq!(compare_property_priority(a,b),spec(*a,*b),"pair {i} {j}"); checks+=1;
 }}
 println!("{} properties, {} ordered pairs",all.len(),checks);
}
'''

if __name__ == '__main__':
    data = inventory()
    (BASE / 'inventory-v1.json').write_text(json.dumps(data, indent=2) + '\n')
    (BASE / 'bridge.rs').write_text(generate((BASE / 'native-candidate.rs').read_text(), data))
