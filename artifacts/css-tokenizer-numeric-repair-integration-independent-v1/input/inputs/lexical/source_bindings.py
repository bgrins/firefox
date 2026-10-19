import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
reader=R/'inputs/integration/inputs/name/rust_reader.py'
spec=importlib.util.spec_from_file_location('retained_rust_reader',reader);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
records=[]
def full(path,names):
 source=path.read_text();tokens=m.tokens(source)
 for name in names:
  found=[i for i in range(len(tokens)-1) if tokens[i][0]=='fn' and tokens[i+1][0]==name]
  assert len(found)==1,(name,found)
  i=found[0];j=i+2
  while tokens[j][0]!='{':j+=1
  end=m.pair(tokens,j);body=source[tokens[i][1]:tokens[end][2]]
  records.append({'source':str(path.relative_to(R)),'name':name,'byte_start':len(source[:tokens[i][1]].encode()),'byte_end':len(source[:tokens[end][2]].encode()),'sha256':hashlib.sha256(body.encode()).hexdigest(),'body':body})
full(R/'inputs/static/source/third_party/rust/cssparser/src/tokenizer.rs',['next_token_unchecked','byte_to_decimal_digit','consume_numeric','is_ident_start','consume_name','consume_escape','consume_escape_and_write','consume_hex_digits','is_eof','has_at_least','advance','next_byte_unchecked','byte_at'])
full(R/'inputs/static/source/servo/components/style/custom_properties.rs',['from_unit','resolved_token_dependencies','parse_declaration_value_block'])
by={x['name']:x for x in records}
assert by['consume_numeric']['body']+'\n'==(R/'inputs/static/consume_numeric.rs').read_text()
prior=json.loads((R/'inputs/integration/evidence/CURRENT-BINDINGS.json').read_text())
for old in prior:
 if old['name'] in by:assert old['body']==by[old['name']]['body'],old['name']
unit=by['from_unit']['body']
assert unit.count('eq_ignore_ascii_case')==12
assert 'Self::FONT_UNITS | Self::LH_UNITS' in unit
assert 'Self::ROOT_FONT_UNITS | Self::ROOT_LH_UNITS' in unit
scanner=by['resolved_token_dependencies']['body'];decl=by['parse_declaration_value_block']['body']
assert 'Token::Dimension { unit, .. } => flags.insert(ReferenceFlags::from_unit(unit))' in scanner
assert 'if matches!(token, Token::Dimension { .. }) {\n                    references.flags.insert(ReferenceFlags::from_unit(value));\n                }' in decl
assert scanner.count('ReferenceFlags::from_unit')==decl.count('ReferenceFlags::from_unit')==1
assert 'let consumed = input.position().byte_index();' in scanner and 'css = &css[consumed..];' in scanner
expected=json.loads((R/'SOURCE-BINDINGS.json').read_text()) if (R/'SOURCE-BINDINGS.json').exists() else None
if expected is not None:assert records==expected
(a.output).write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps({'status':'PASS','complete_definitions':len(records),'numeric_body':'unchanged original arithmetic','custom_property_functions':'source bindings; only unit classifier and suffix scanner compiled here'}))
