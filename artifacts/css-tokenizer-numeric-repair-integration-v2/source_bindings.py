import argparse,hashlib,importlib.util,json
from pathlib import Path
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
lex=R/'inputs/lexical';repair=R/'inputs/repair';rel=Path('third_party/rust/cssparser/src/tokenizer.rs')
old=(repair/'original'/rel).read_text();new=(repair/'candidate'/rel).read_text()
assert hashlib.sha256(new.encode()).hexdigest()=='5319a01e403cd2a93bfc3dd4c53a7e5ec95129360da58c6f9f76f480ae5e6211'
assert old==(lex/'inputs/static/source'/rel).read_text()
start='    let start_position = parser.position();\n'
block='''
    // Reparse long numbers as a whole: exponents can compensate for intermediate overflow/underflow.
    // Below 256 bytes, finite underflow cannot affect the final f32 payload.
    if parser.position().byte_index() - start_position.byte_index() >= 256 || !value.is_finite() {
        value = parser.slice_from(start_position).parse::<f64>().unwrap();
    }
'''
offset=new.index("fn consume_numeric<'a>")
assert new[offset:].count(start)==new.count(block)==1
assert new[:offset]+new[offset:].replace(start,'',1).replace(block,'',1)==old
reader=lex/'inputs/integration/inputs/name/rust_reader.py'
spec=importlib.util.spec_from_file_location('retained_reader',reader);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ts=m.tokens(new);records=[]
for name in ['consume_numeric','position','byte_index','slice_from','slice','advance','has_at_least','next_byte_unchecked','byte_at','is_ident_start','consume_name']:
 found=[i for i in range(len(ts)-1) if ts[i][0]=='fn' and ts[i+1][0]==name];assert len(found)==1
 i=found[0];j=i+2
 while ts[j][0]!='{':j+=1
 e=m.pair(ts,j);body=new[ts[i][1]:ts[e][2]]
 records.append({'name':name,'body':body,'sha256':hashlib.sha256(body.encode()).hexdigest(),'byte_start':len(new[:ts[i][1]].encode()),'byte_end':len(new[:ts[e][2]].encode())})
num=next(x['body'] for x in records if x['name']=='consume_numeric')
assert num+'\n'==(repair/'numeric-candidate.rs').read_text()
assert num.index(start)<num.index('let (has_sign, sign)')
assert num.index(block)<num.index('let int_value')<num.index("b'%'")<num.index('is_ident_start')
checksum=json.loads((repair/'candidate/third_party/rust/cssparser/.cargo-checksum.json').read_text())
assert checksum['files']['src/tokenizer.rs']==hashlib.sha256(new.encode()).hexdigest()
lib=(repair/'library/rust-1.92.0-dec2flt.rs').read_text()
for line in ["Float  ::= Sign? ( 'inf' | 'infinity' | 'nan' | Number )","Number ::= ( Digit+ |","Digit+ '.' Digit* |","Digit* '.' Digit+ ) Exp?","Exp    ::= 'e' Sign? Digit+","Sign   ::= [+-]","Digit  ::= [0-9]"]:
 assert line in lib,line
assert 'fn from_str(src: &str) -> Result<Self, ParseFloatError> {\n                dec2flt(src)\n            }' in lib
records.append({'name':'documented_FromStr','body':lib,'sha256':hashlib.sha256(lib.encode()).hexdigest(),'implementation_trust':'documented numeric grammar acceptance; dec2flt correctness not proved or rebuilt here'})
if (R/'SOURCE-BINDINGS.json').exists():assert records==json.loads((R/'SOURCE-BINDINGS.json').read_text())
a.output.write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps({'status':'PASS','native_full_definitions':11,'library_source':1,'delta':'start-position capture and borrowed-slice parse assignment only','candidate_sha256':hashlib.sha256(new.encode()).hexdigest()}))
