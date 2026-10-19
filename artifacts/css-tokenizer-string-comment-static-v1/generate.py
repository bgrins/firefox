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
type CowRcStr<'a> = std::borrow::Cow<'a,str>;
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
for name in ['check_for_source_map','consume_comment','consume_string','consume_quoted_string','byte_to_hex_digit','consume_hex_digits','consume_escape_and_write','consume_escape','from_utf8_release_unchecked']:header+=extract(s,name)
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
 for body in ['abc','a\\\nb','a\\\r\nb','\\0','\\000000','\\D800','\\10ffff','\\110000','\\61 b','\\000061b','\\61\r\nb','é𐀀\\61 x','x\0y','\\𐀀x','/*not a comment*/','\\\\','\\"',"\\'",'a\n; color:green']:
  strings.extend([quote+body,quote+body+quote+';tail'])
comments=[]
for size in range(5):
 for chars in itertools.product(['*','/','a','\n'],repeat=size):comments.append('/*'+''.join(chars))
comments+=['/**/tail','/*a\r\né𐀀\0*/tail','/*# sourceMappingURL=a.map */','/*@ sourceURL=b.css\r\n*/','/* outer /* inner */tail','/*\\*/tail','/*é𐀀']
cases=[]
for raw in strings:
 bad,value,pos=reference_string(raw);line,col=location(raw,pos);cases.append(dict(kind='string',raw=raw,bad=bad,value=value,position=pos,line=line,column=col))
for raw in comments:
 end=raw.find('*/',2);value=raw[2:] if end<0 else raw[2:end];pos=len(raw.encode()) if end<0 else len(raw[:end+2].encode());line,col=location(raw,pos);cases.append(dict(kind='comment',raw=raw,value=value,position=pos,line=line,column=col))
def lit(s):
 return '"'+''.join('\\' + c if c in ['"','\\'] else '\\u{'+format(ord(c),'x')+'}' if ord(c)<32 else c for c in s)+'"'

main='''
fn main(){
let cases:[(bool,&str,bool,&str,usize,u32,u32);'''+str(len(cases))+']=[\n'
for c in cases:main+='('+','.join([str(c['kind']=='string').lower(),lit(c['raw']),str(c.get('bad',False)).lower(),lit(c['value']),str(c['position']),str(c['line']),str(c['column'])])+'),\n'
main+=''' ];
for (id,(string,input,bad,value,pos,line,column)) in cases.into_iter().enumerate(){
let mut p=Parser{input,state:ParserState{position:0,current_line_start_position:0,line_number_and_block_type:0},source_map_url:None,source_url:None};
if string {let token=consume_string(&mut p,input.starts_with('\''));match token {QuotedString(v)=>{assert!(!bad,"case {id}");assert_eq!(&*v,value,"case {id}");},BadString(v)=>{assert!(bad,"case {id}");assert_eq!(&*v,value,"case {id}");}}}
else {assert_eq!(consume_comment(&mut p),value,"case {id}");}
assert_eq!(p.state.position,pos,"position case {id}");let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(line,column),"location case {id}");
assert!(input.is_char_boundary(p.state.position));
}
println!("PASS strings='''+str(len(strings))+' comments='+str(len(comments))+' total='+str(len(cases))+'''");
}
'''
# Rust apostrophe char is emitted explicitly to avoid Python string escaping ambiguity.
main=main.replace("input.starts_with(''')", "input.starts_with('\\'')")
(R/'consumer-witness.rs').write_text(header+main)
(R/'CASES.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n')
(R/'EXTRACTIONS.json').write_text(json.dumps(bindings,indent=2)+'\n')
print(len(strings),len(comments),len(bindings))
