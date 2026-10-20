import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('use -I -S without optimization')
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib, json
ROOT=Path(__file__).resolve().parent

def body(file, marker):
    raw=(ROOT/'source'/file).read_text()
    if raw.count(marker)!=1:raise RuntimeError('nonunique marker: '+marker)
    start=raw.index(marker);opening=raw.index('{',start)
    depth=0;i=opening;state='code'
    while i<len(raw):
        c=raw[i];n=raw[i:i+2]
        if state=='line':
            if c=='\n':state='code'
        elif state=='comment':
            if n=='*/':state='code';i+=1
        elif state in ('"',"'"):
            if c=='\\':i+=1
            elif c==state:state='code'
        elif n=='//':state='line';i+=1
        elif n=='/*':state='comment';i+=1
        elif c in ('"',"'"):state=c
        elif c=='{':depth+=1
        elif c=='}':
            depth-=1
            if depth==0:
                text=raw[start:i+1]
                return dict(source='source/'+file,marker=marker,offset=len(raw[:start].encode()),bytes=len(text.encode()),sha256=hashlib.sha256(text.encode()).hexdigest(),complete_text=text)
        i+=1
    raise RuntimeError('unclosed body: '+marker)

SPECS=[
('add','candidate-dom__view-transitions__ViewTransitionTypeSet.cpp','ViewTransitionTypeSet* ViewTransitionTypeSet::Add('),
('clear','candidate-dom__view-transitions__ViewTransitionTypeSet.cpp','void ViewTransitionTypeSet::Clear('),
('delete','candidate-dom__view-transitions__ViewTransitionTypeSet.cpp','bool ViewTransitionTypeSet::Delete('),
('changed','candidate-dom__view-transitions__ViewTransition.cpp','void ViewTransition::TypesChanged()'),
('post','PostRestyleEvent.cpp.txt','void nsLayoutUtils::PostRestyleEvent('),
('original_add','original-dom__view-transitions__ViewTransitionTypeSet.cpp','ViewTransitionTypeSet* ViewTransitionTypeSet::Add('),
('original_clear','original-dom__view-transitions__ViewTransitionTypeSet.cpp','void ViewTransitionTypeSet::Clear('),
('original_delete','original-dom__view-transitions__ViewTransitionTypeSet.cpp','bool ViewTransitionTypeSet::Delete('),
('restyle_dispatch','original-layout__style__RestyleManager.cpp','void RestyleManager::PostRestyleEvent('),
('state_snapshot','original-layout__style__RestyleManager.cpp','void RestyleManager::ElementStateChanged('),
('generated_helpers','generated-ViewTransitionBinding.cpp','namespace SetlikeHelpers {')]

def bindings():
    rows=[]
    for name,file,marker in SPECS:
        row=body(file,marker);row['name']=name;rows.append(row)
    return rows
if __name__=='__main__':
    print(json.dumps(bindings(),indent=2))
