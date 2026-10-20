from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parent
rows=[]
def bind(file,signature,scope=''):
 text=(r/file).read_text();start=text.index(signature,text.index(scope) if scope else 0);i=text.index('{',start);depth=0;j=i
 while j<len(text):
  if text.startswith('//',j):j=text.find('\n',j);continue
  if text.startswith('/*',j):j=text.index('*/',j+2)+2;continue
  if text[j]=='"':
   j+=1
   while j<len(text):
    if text[j]=='\\':j+=2;continue
    if text[j]=='"':j+=1;break
    j+=1
   continue
  if text[j]=='{':depth+=1
  if text[j]=='}':
   depth-=1
   if depth==0:j+=1;break
  j+=1
 assert depth==0
 body=text[start:j]
 rows.append(dict(file=file,signature=signature,scope=scope,start_byte=len(text[:start].encode()),end_byte=len(text[:j].encode()),body=body,sha256=hashlib.sha256(body.encode()).hexdigest()))
cpp='dom/animation/KeyframeEffect.cpp'
for kind in ('original','candidate'):
 for name in ('UpdateProperties','EnsureBaseStyles'):
  bind('source/'+kind+'/'+cpp,'void KeyframeEffect::'+name+'(')
for name in ('EnsureBaseStyle','ComposeStyleRule','RequestRestyle'):
 bind('source/candidate/'+cpp,'void KeyframeEffect::'+name+'(')
bind('source/context/layout/style/StyleAnimationValue.cpp','bool AnimationValue::operator==(')
glue='source/context/servo/ports/geckolib/glue.rs'
for sig in ('pub extern "C" fn Servo_AnimationValue_IsAttrTainted(', 'pub extern "C" fn Servo_AnimationValue_DeepEqual(', 'pub extern "C" fn Servo_AnimationCompose(', 'fn composite_endpoint('):bind(glue,sig)
bind('source/context/servo/components/style/properties_and_values/value.rs','pub fn is_attr_tainted(', 'impl CustomAnimatedValue')
bind('source/context/dom/animation/EffectCompositor.cpp','void EffectCompositor::RequestRestyle(')
(r/'SOURCE-BINDINGS.json').write_text(json.dumps(rows,indent=2)+'\n')
print(len(rows))
