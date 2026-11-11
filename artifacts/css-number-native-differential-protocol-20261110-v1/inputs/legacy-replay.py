import argparse,json,os,re,shutil,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
commands=[]
def run(cmd,cwd,stdin=None,success=True):
 r=subprocess.run(cmd,cwd=cwd,input=stdin,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
 commands.append({'cmd':cmd,'cwd':str(cwd),'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});(out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
 assert (r.returncode==0)==success,commands[-1]
 return r
lex=R/'inputs/lexical';rel=Path('third_party/rust/cssparser/src/tokenizer.rs')
cases=json.loads((lex/'native/CASES.json').read_text())
for variant in ['original','candidate']:
 work=out/(variant+'-source');shutil.copytree(lex,work)
 shutil.copyfile(R/'inputs/repair'/variant/rel,work/'inputs/static/source'/rel)
 if variant=='candidate':
  cs=[{k:v for k,v in c.items() if k!='payload_bits'} for c in cases];(work/'native/CASES.json').write_text(json.dumps(cs)+'\n')
 run([sys.executable,str(work/'native/build.py'),'--output',str(out/variant)],out)
old=(out/'original/OBSERVATIONS.tsv').read_text().splitlines();new=(out/'candidate/OBSERVATIONS.tsv').read_text().splitlines();assert len(old)==len(new)==90
changed=[]
for i,(x,y) in enumerate(zip(old,new)):
 x=x.split('\t');y=y.split('\t');assert x[:6]+x[7:]==y[:6]+y[7:],(i,x,y)
 if x[6]!=y[6]:changed.append({'case':i,'original_f32_bits':x[6],'candidate_f32_bits':y[6]})
assert changed
base=out/'candidate';instrument=out/'instrumented';instrument.mkdir();shutil.copytree(base/'vendor/cssparser',instrument/'cssparser')
source=(instrument/'cssparser/src/tokenizer.rs').read_text()
hook='''    eprintln!("CAPTURE\\t{}\\t{}\\t{}", start_position.byte_index(), parser.position().byte_index(), parser.slice_from(start_position).as_bytes().iter().map(|b| format!("{b:02x}")).collect::<String>());
'''
needle='    // Reparse long numbers as a whole:';assert source.count(needle)==1
instrumented=source.replace(needle,hook+needle,1);(instrument/'cssparser/src/tokenizer.rs').write_text(instrumented)
(instrument/'TRACE-INSERTION.rs').write_text(hook)
rustc=json.loads((lex/'inputs/scanner/scanner/TOOLCHAIN.json').read_text())['rustc']
def compile_crate(folder):
 cmd=[rustc,'--crate-name','cssparser','--crate-type','rlib','--edition','2024','-C','opt-level=1','-L','dependency='+str(base),str(folder/'cssparser/src/lib.rs'),'-o',str(folder/'libcssparser.rlib')]
 for dep in ['dtoa_short','itoa','smallvec']:cmd+=['--extern',dep+'='+str(base/('lib'+dep+'.rlib'))]
 run(cmd,folder)
compile_crate(instrument)
driver='''use cssparser::Parser;
use std::io::{self,BufRead};
fn main() {
 for line in io::stdin().lock().lines() {
  let line=line.unwrap();let (prefix,hex)=line.split_once(':').unwrap();
  let raw:Vec<u8>=(0..hex.len()).step_by(2).map(|i|u8::from_str_radix(&hex[i..i+2],16).unwrap()).collect();
  let css=String::from_utf8(raw).unwrap();
  let before=if prefix=="1" { "\\\"é𐀀\\\" " } else { "" };
  let input=before.to_owned()+&css;
  let mut parser=Parser::new(&input);
  if !before.is_empty() {parser.next_including_whitespace_and_comments().unwrap();parser.next_including_whitespace_and_comments().unwrap();}
  assert_eq!(parser.position().byte_index(),before.len());
  parser.next_including_whitespace_and_comments().unwrap();
 }
}
'''
(instrument/'driver.rs').write_text(driver)
def compile_driver(folder):run([rustc,'--edition','2024','-C','opt-level=1','-L','dependency='+str(base),'--extern','cssparser='+str(folder/'libcssparser.rlib'),str(instrument/'driver.rs'),'-o',str(folder/'capture')],folder)
compile_driver(instrument)
capture=[(False,c['css']) for c in cases if c['model']]
capture += [(True,'.5px'),(True,'1\\65 m'),(True,'5'+'0'*308+'e-309em')]
stdin=''.join(str(int(prefix))+':'+css.encode().hex()+'\n' for prefix,css in capture)
res=run([str(instrument/'capture')],instrument,stdin)
lines=res.stderr.splitlines();assert len(lines)==len(capture)==84
regex=re.compile(rb'[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?')
for (prefix,css),line in zip(capture,lines):
 tag,start,end,raw=line.split('\t');assert tag=='CAPTURE';start=int(start);end=int(end)
 expected=regex.match(css.encode()).group();before='"é𐀀" '.encode() if prefix else b''
 assert raw==expected.hex() and start==len(before) and end==start+len(expected),(css,line,expected)
 assert end<=len(before)+len(css.encode()) and all(c<128 for c in expected)
(out/'CAPTURES.json').write_text(json.dumps([{'prefix':p,'input':s,'trace':l} for (p,s),l in zip(capture,lines)],indent=2)+'\n')
mut=out/'slice-mutant';mut.mkdir();shutil.copytree(instrument/'cssparser',mut/'cssparser')
oldparse='parser.slice_from(start_position).parse::<f64>().unwrap()'
newparse='parser.slice(start_position..SourcePosition(parser.position().byte_index() + 1)).parse::<f64>().unwrap()'
assert instrumented.count(oldparse)==1
(mut/'cssparser/src/tokenizer.rs').write_text(instrumented.replace(oldparse,newparse,1))
compile_crate(mut);compile_driver(mut)
res=run([str(mut/'capture')],mut,'0:'+('1'+'0'*255+'em').encode().hex()+'\n',success=False)
assert 'ParseFloatError' in res.stderr and 'Invalid' in res.stderr
result={'status':'PASS','exact_original_candidate_rows':90,'lexical_projection_unchanged':True,'payload_changes_retained':changed,'captured_slices':84,'nonzero_utf8_start_cases':3,'independent_prefix_oracle':'ASCII numeric grammar regex','extended_into_unit_mutant':'compiled then rejected by actual FromStr','instrumentation':'one removable logging statement; uninstrumented source pair also rebuilt'}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
