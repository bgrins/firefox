from pathlib import Path
import json,re,itertools,hashlib
R=Path(__file__).resolve().parent
s=(R/'source/third_party/rust/cssparser/src/tokenizer.rs').read_text();st=(R/'source/third_party/rust/cssparser/src/parser.rs').read_text();bindings=[]
assert 'const BLOCK_TYPE_BITS: u32 = 2;' in st
for field in ['position: usize', 'current_line_start_position: u32', 'line_number_and_block_type: u32']:assert field in st
def extract(source,name,method=False):
 pattern=r'^'+('    ' if method else '')+r'(?:pub(?:\([^)]*\))? )?(?:unsafe )?fn '+name+r'[<(]'
 m=re.search(pattern,source,re.M);assert m,name
 end=source.index('\n'+('    ' if method else '')+'}',m.start())+len('\n'+('    ' if method else '')+'}')
 value=source[m.start():end]
 bindings.append(dict(name=name,method=method,source='parser.rs' if source is st else 'tokenizer.rs',start=m.start(),end=end,sha256=hashlib.sha256(value.encode()).hexdigest()))
 return value+'\n'
header='''#![allow(dead_code)]
use std::ops::Range;
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
for name in ['position','slice_from','slice','next_byte','is_eof','has_at_least','advance','next_byte_unchecked','byte_at','consume_4byte_intro','consume_continuation_byte','consume_newline']:header+=extract(s,name,True)
header+='}\n'
for name in ['check_for_source_map','consume_comment']:header+=extract(s,name)

def location(prefix):
 line=3;column=1;i=0
 while i<len(prefix):
  c=prefix[i];i+=1
  if c=='\r' and i<len(prefix) and prefix[i]=='\n':i+=1
  if c in '\r\n\f':line+=1;column=1
  else:column+=len(c.encode('utf-16-le'))//2
 return line,column

def update(body,urls):
 result=list(urls)
 for idx,key in enumerate(['sourceMappingURL','sourceURL']):
  m=re.match(r'^[#@] '+key+r'=([^ \t\n\r\f]*)',body)
  if m:result[idx]=m.group(1)
 return result

def reference(comments):
 raw='seed'+''.join(comments);cursor=4;urls=['initial.map','initial.css'];steps=[]
 for supplied in comments:
  assert raw[cursor:cursor+2]=='/*'
  end=raw.find('*/',cursor+2);body=raw[cursor+2:] if end<0 else raw[cursor+2:end]
  start=cursor;cursor=len(raw) if end<0 else end+2;urls=update(body,urls)
  line,col=location(raw[:cursor])
  steps.append(dict(body=body,start=len(raw[:start].encode()),position=len(raw[:cursor].encode()),line=line,column=col,urls=list(urls)))
 assert cursor==len(raw)
 return dict(input=raw,steps=steps)

histories=[]
for size in range(5):
 for chars in itertools.product(['*','/','a','\n'],repeat=size):
  body=''.join(chars)
  if '*/' not in body:histories.append(['/*'+body])
for marker in ['#','@']:
 for key in ['sourceURL','sourceMappingURL']:
  for value in ['', 'x.css','é𐀀.map','a\0b']:
   for delimiter in ['', ' ', '\t','\n','\r\n','\f']:
    histories.append(['/*'+marker+' '+key+'='+value+delimiter+'*/'])
for body in ['#sourceURL=no','#  sourceURL=no',' # sourceURL=no','# SourceURL=no','# sourceURLX=no','@ sourceMappingURL','x# sourceURL=no','é𐀀\0','outer /* inner']:
 histories.append(['/*'+body+'*/'])
histories.extend([
 ['/*# sourceURL=a*/','/*# sourceMappingURL=m*/','/**/','/*@ sourceURL=*/','/*@ sourceMappingURL=é𐀀\fignored*/'],
 ['/*# sourceMappingURL=old*/','/*# sourceMappingURL=new'],
 ['/*# sourceURL=old*/','/*@ sourceURL='],
 ['/*é𐀀\r\n*/','/*\0\r*/','/*\n\f*/','/*# sourceURL=final*/'],
 ['/* outer /* inner */','/*# sourceURL=nested-boundary*/'],
])
cases=[reference(h) for h in histories]

def lit(s):
 return '"'+''.join('\\'+c if c in ['"','\\'] else '\\u{'+format(ord(c),'x')+'}' if ord(c)<32 else c for c in s)+'"'
def option(s):return 'None' if s is None else 'Some('+lit(s)+')'
main='\nfn main(){\n'
for i,c in enumerate(cases):
 main+=' { let input='+lit(c['input'])+';\nlet mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};\n'
 for j,v in enumerate(c['steps']):
  tag=f'history {i} step {j}'
  main+='let body=consume_comment(&mut p);\n'
  main+=f'assert_eq!(body,{lit(v["body"])},"body {tag}");\n'
  main+=f'assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,{v["start"]+2},"slice {tag}");\n'
  main+=f'assert_eq!(p.state.position,{v["position"]},"position {tag}");\n'
  main+=f'let loc=p.state.source_location();assert_eq!((loc.line,loc.column),({v["line"]},{v["column"]}),"location {tag}");\n'
  main+=f'assert_eq!((p.source_map_url,p.source_url),({option(v["urls"][0])},{option(v["urls"][1])}),"URLs {tag}");\n'
  main+='assert!(input.is_char_boundary(p.state.position));\n'
 main+=' }\n'
main+='\nfor block in 0..4 {\n let mut state=ParserState{position:0,current_line_start_position:0,line_number_and_block_type:0xfffffff8+block};\n state.advance_line_number(1);\n assert_eq!(state.line_number(),(1u32<<30)-1);\n assert_eq!(state.line_number_and_block_type&3,block);\n std::panic::set_hook(Box::new(|_|{}));\n let overflow=std::panic::catch_unwind(std::panic::AssertUnwindSafe(||state.advance_line_number(1)));\n if cfg!(debug_assertions){assert!(overflow.is_err());}\n else{assert!(overflow.is_ok());assert_eq!(state.line_number(),0);assert_eq!(state.line_number_and_block_type&3,block);}\n}\nlet mut p=Parser{input:"𐀀",state:ParserState{position:0,current_line_start_position:0,line_number_and_block_type:0},source_map_url:None,source_url:None};\np.consume_4byte_intro();assert_eq!(p.state.current_line_start_position,u32::MAX);\nassert_eq!(p.state.source_location().column,3);\nfor _ in 0..3{p.consume_continuation_byte();assert_eq!(p.state.source_location().column,3);}\nassert_eq!(p.state.position,4);\nlet state=ParserState{position:(1usize<<32)+5,current_line_start_position:0,line_number_and_block_type:0};\nassert_eq!(state.source_location().column,6);\n'
main+=f'println!("PASS histories={len(cases)} comment_calls={sum(len(c["steps"]) for c in cases)} raw_slices_positions_locations_and_both_URLs");\n}}\n'
(R/'observer-witness.rs').write_text(header+main)
(R/'CASES.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n')
(R/'EXTRACTIONS.json').write_text(json.dumps(bindings,indent=2)+'\n')
print(len(cases),sum(len(c['steps']) for c in cases),len(bindings))
