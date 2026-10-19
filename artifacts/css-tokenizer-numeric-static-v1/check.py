import argparse,hashlib,json,pathlib,tempfile,subprocess,shutil,decimal
R=pathlib.Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--run-rust',action='store_true');p.add_argument('--output',type=pathlib.Path);a=p.parse_args()
f=json.loads((R/'FREEZE.json').read_text());assert H(R/'INPUTS.json')==f['inputs_sha256']
for n,h in json.loads((R/'INPUTS.json').read_text()).items():assert H(R/n)==h,n
s=(R/'source/third_party/rust/cssparser/src/tokenizer.rs').read_text()
def segment(start,end):
 a=s.index(start);b=s.index(end,a);return s[a:b]
parts=[segment('fn byte_to_decimal_digit','\nfn consume_numeric'),segment('fn consume_numeric','\n#[inline]'),segment('fn is_ident_start(','\nfn consume_ident_like')]
expected=(R/'facade-prefix.rs').read_text()+'\n'.join(parts)+(R/'facade-main.rs').read_text()
assert expected==(R/'numeric-witness.rs').read_text()
assert parts[1]==(R/'consume_numeric.rs').read_text()
indexed=(R/'searchfox/source-0.txt').read_text();start=indexed.index('fn consume_numeric');end=indexed.index('\n#[inline]',start);assert indexed[start:end]==parts[1]
rows=json.loads((R/'DECIMAL-REFERENCE.json').read_text())
for row in rows:
 value=decimal.Decimal(row['input'][:-2] if row['unit']=='px' else row['input'])
 assert value==decimal.Decimal(row['exact_decimal'])
 if row['case']<5:assert value==decimal.Decimal('0.5')
 if row['case'] in [7,8]:assert value==17
record=json.loads((R/'RUST-WITNESS.json').read_text());assert record['source_sha256']==H(R/'numeric-witness.rs')
assert all(x['exit']==0 for x in record['commands'])
output=record['commands'][-1]['stdout'];lines=output.splitlines();assert len(lines)==9
for i,marker in enumerate(['value: 0.5','value: 0.5','value: inf','value: NaN','value: NaN','value: NaN','value: inf','value: inf','value: 17.0']):assert marker in lines[i]
html=(R/'numeric-compensated-exponent.html').read_text();js=html.split('<script>')[1].split('</script>')[0]
with tempfile.TemporaryDirectory(prefix='numeric-js-check-') as td:
 q=pathlib.Path(td)/'probe.js';q.write_text(js);subprocess.run(['node','--check',str(q)],check=True)
if a.run_rust:
 assert a.output and not a.output.exists();a.output.mkdir(parents=True)
 rustc=shutil.which('rustc');assert rustc
 commands=[]
 for cmd in [[rustc,'--version','--verbose'],[rustc,'--edition=2021','-O',str(R/'numeric-witness.rs'),'-o',str(a.output.resolve()/'numeric-witness')],[str(a.output.resolve()/'numeric-witness')]]:
  c=subprocess.run(cmd,capture_output=True,text=True);commands.append({'cmd':cmd,'exit':c.returncode,'stdout':c.stdout,'stderr':c.stderr});assert c.returncode==0,c.stderr
 assert commands[-1]['stdout']==output
 (a.output/'RESULT.json').write_text(json.dumps(commands,indent=2)+'\n')
print(json.dumps({'status':'PASS','native_extracted_cases':9,'finite_nonzero_payload_counterexamples':4,'zero_payload_nan_control':1,'browser':'UNEXECUTED','proposal':'numeric lexical and Dimension unit admission; numerical fidelity remains refuted/open'}))
