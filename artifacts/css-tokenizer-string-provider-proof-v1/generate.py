from pathlib import Path
import json,re,itertools,hashlib
R=Path(__file__).resolve().parent
s=(R/'source/third_party/rust/cssparser/src/tokenizer.rs').read_text();st=(R/'source/third_party/rust/cssparser/src/parser.rs').read_text();bindings=[]
def extract(source,name,method=False):
 pattern=r'^'+('    ' if method else '')+r'(?:pub(?:\([^)]*\))? )?(?:unsafe )?fn '+name+r'[<(]'
 m=re.search(pattern,source,re.M);assert m,name
 end=source.index('\n'+('    ' if method else '')+'}',m.start())+len('\n'+('    ' if method else '')+'}')
 value=source[m.start():end]
 bindings.append(dict(name=name,method=method,source='parser.rs' if source is st else 'tokenizer.rs',start=m.start(),end=end,sha256=hashlib.sha256(value.encode()).hexdigest()))
 return value+'\n'
header='''#![allow(dead_code)]
use std::ops::Range;
mod cow_rc_str {
include!("source/third_party/rust/cssparser/src/cow_rc_str.rs");
pub fn is_shared(value: &CowRcStr<'_>) -> bool { value.borrowed_len_or_max == usize::MAX }
}
use cow_rc_str::CowRcStr;
macro_rules! match_byte { ($value:expr, $($arms:tt)*) => { match $value { $($arms)* } }; }
#[derive(Clone,Copy)] struct SourcePosition(usize);
struct SourceLocation {line:u32,column:u32}
struct ParserState {position:usize,current_line_start_position:u32,line_number_and_block_type:u32}
impl ParserState {
const BLOCK_TYPE_BITS:u32=2;
'''
for name in ['position','source_location','line_number','advance_line_number']:header+=extract(st,name,True)
header+='''}
struct Parser<'a> {input:&'a str,state:ParserState,source_map_url:Option<&'a str>,source_url:Option<&'a str>}
impl<'a> Parser<'a> {
'''
for name in ['position','slice_from','slice','next_byte','is_eof','has_at_least','advance','next_byte_unchecked','byte_at','consume_4byte_intro','consume_continuation_byte','next_char','consume_newline','consume_char']:header+=extract(s,name,True)
header+='''}
#[derive(Debug)] enum Token<'a> {QuotedString(CowRcStr<'a>),BadString(CowRcStr<'a>)}
use Token::*;
'''
for name in ['consume_string','consume_quoted_string','byte_to_hex_digit','consume_hex_digits','consume_escape_and_write','consume_escape','from_utf8_release_unchecked']:header+=extract(s,name)
def preprocessed(text):
 result=[];i=0;byte=0
 while i<len(text):
  c=text[i];start=byte;byte+=len(c.encode());i+=1
  if c=='\r' and i<len(text) and text[i]=='\n':byte+=1;i+=1
  if c in '\r\f':c='\n'
  if c=='\0':c='\ufffd'
  result.append((c,start,byte))
 return result

def reference_string(raw):
 cp=preprocessed(raw);quote=cp[0][0];i=1;out=''
 while i<len(cp):
  c,a,b=cp[i];i+=1
  if c==quote:return False,out,b
  if c=='\n':return True,out,a
  if c!='\\':out+=c;continue
  if i==len(cp):continue
  c=cp[i][0]
  if c=='\n':i+=1;continue
  if c in '0123456789abcdefABCDEF':
   digits=''
   while i<len(cp) and len(digits)<6 and cp[i][0] in '0123456789abcdefABCDEF':digits+=cp[i][0];i+=1
   v=int(digits,16);out+=chr(v) if 0<v<=0x10ffff and not 0xd800<=v<=0xdfff else '\ufffd'
   if i<len(cp) and cp[i][0] in ' \t\n':i+=1
  else:out+=c;i+=1
 return False,out,len(raw.encode())
def location(raw,pos):
 prefix=raw.encode()[:pos].decode();line=0;column=1
 for c,a,b in preprocessed(prefix):
  if c=='\n':line+=1;column=1
  else:column+=len(c.encode('utf-16-le'))//2
 return line,column
strings=[]
alphabet=['a','"',"'",'\\','\n','\r','\f','\0','é','𐀀']
for quote in ['"',"'"]:
 for size in range(3):
  for chars in itertools.product(alphabet,repeat=size):strings.append(quote+''.join(chars))
 for body in ['abc','a\\\nb','a\\\r\nb','\\0','\\000000','\\D800','\\10ffff','\\110000','\\61 b','\\000061b','\\61\r\nb','é𐀀\\61 x','x\0y','\\𐀀x','/*# sourceURL=not-a-directive*/','\\\\','\\"',"\\'",'a\n; color:green']:
  strings.extend([quote+body,quote+body+quote+';tail'])
 for pre in ['', 'é𐀀', '\0', '\\61 ']:
  for escape in ['\\','\\\0','\\é','\\𐀀','\\\n','\\\r','\\\r\n','\\\f','\\1','\\f','\\ff','\\fff','\\ffff','\\10000','\\ffffff','\\000061b','\\61\r\n','\\61\t','\\61\f','\\61  ','\\00000','\\DFFF','\\110000']:
   for ending in ['',quote+'tail','\n']:
    strings.append(quote+pre+escape+ending)
strings=list(dict.fromkeys(strings));cases=[]
for raw in strings:
 bad,value,pos=reference_string(raw);line,col=location('seed'+raw,4+pos)
 scanned=raw.encode()[1:pos].decode()
 allocated='\\' in scanned or '\0' in scanned
 cases.append(dict(raw=raw,bad=bad,value=value,position=4+pos,line=3+line,column=col,allocated=allocated,remainder=raw.encode()[pos:].decode()))

def lit(s):
 return '"'+''.join('\\'+c if c in ['"','\\'] else '\\u{'+format(ord(c),'x')+'}' if ord(c)<32 else c for c in s)+'"'
main='''
fn main(){
let cases:[(&str,bool,&str,usize,u32,u32,bool,&str);'''+str(len(cases))+']=[\n'
for c in cases:main+='('+','.join([lit(c['raw']),str(c['bad']).lower(),lit(c['value']),str(c['position']),str(c['line']),str(c['column']),str(c['allocated']).lower(),lit(c['remainder'])])+'),\n'
main+=''' ];
for (id,(raw,bad,value,pos,line,column,allocated,remainder)) in cases.into_iter().enumerate(){
let storage=format!("seed{}",raw);let input=&*storage;
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let token=consume_string(&mut p,raw.starts_with('\''));
let v=match token{QuotedString(v)=>{assert!(!bad,"kind {id}");v},BadString(v)=>{assert!(bad,"kind {id}");v}};
assert_eq!(&*v,value,"payload {id}");
let cloned=v.clone();assert_eq!(&*cloned,value,"provider clone {id}");drop(cloned);
assert_eq!(cow_rc_str::is_shared(&v),allocated,"storage {id}");
if !allocated{assert_eq!(v.as_ptr() as usize-input.as_ptr() as usize,5,"borrowed slice {id}");}
assert!(std::str::from_utf8(v.as_bytes()).is_ok(),"output UTF8 {id}");
assert_eq!(p.state.position,pos,"position {id}");
assert_eq!(&input[pos..],remainder,"reconsume/suffix {id}");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(line,column),"location {id}");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URL observers {id}");
assert!(input.is_char_boundary(pos));
}
println!("PASS strings='''+str(len(cases))+''' payload_storage_raw_slice_endpoint_suffix_UTF8_location_URLs");
}
'''
main=main.replace("raw.starts_with(''')", "raw.starts_with('\\'')")
(R/'string-witness.rs').write_text(header+main)
(R/'CASES.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n')
(R/'EXTRACTIONS.json').write_text(json.dumps(bindings,indent=2)+'\n')
print(len(cases),len(bindings))
