import hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'development-build/dictionary-stream-language'
inputs_path=ROOT/'seeds/stream-lean-input.txt'
if not inputs_path.exists():inputs_path=ROOT/'evidence/stream-lean-input.txt'
inputs=inputs_path.read_text()
dictionary=ROOT/'imports/dictionary-stream-v1/source/providers/intl/locales/en-US/hyphenation/hyph_en_US.hyf'
expected=ROOT/'seeds/language-dictionary-results-v1.json'
if not expected.exists():expected=ROOT/'evidence/language-dictionary-results-v1.json'
pins=json.loads(expected.read_text())
assert hashlib.sha256(inputs_path.read_bytes()).hexdigest()==pins['inputs_sha256']
assert hashlib.sha256(dictionary.read_bytes()).hexdigest()==pins['dictionary_sha256']
assert len(inputs.splitlines())==pins['cases']==1284
records=[]
for variant in ['original','candidate']:
 for flavor in ['legacy','stream']:
  result=subprocess.run([str(OUT/(flavor+'-'+variant)),str(dictionary)],input=inputs,text=True,capture_output=True,timeout=120,env=dict(os.environ,UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'))
  (OUT/(flavor+'-'+variant+'.stdout')).write_text(result.stdout)
  (OUT/(flavor+'-'+variant+'.stderr')).write_text(result.stderr)
  digest=hashlib.sha256(result.stdout.encode()).hexdigest()
  records.append({'variant':variant,'provider':flavor,'exit':result.returncode,'stdout_sha256':digest})
  assert result.returncode==0 and not result.stderr,(flavor,variant,result.stderr)
  prior=next(x for x in pins['runs']if x['variant']==variant and x['provider']==flavor)
  assert digest==prior['stdout_sha256'],(flavor,variant)
 assert (OUT/('legacy-'+variant+'.stdout')).read_bytes()==(OUT/('stream-'+variant+'.stdout')).read_bytes()
receipt={'cases':1284,'input_sha256':pins['inputs_sha256'],'runs':records,'all_bytes_equal':True,'scope':'Fixed native provider replacement preservation, not independent normative correctness or full proof acceptance'}
(OUT/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
