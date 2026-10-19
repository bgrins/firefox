import difflib
import hashlib
import json
from pathlib import Path
BASE=Path(__file__).resolve().parent
PATH='servo/components/style/values/specified/length.rs'
ORIGINAL='0467c54a65866b4566d4b34d72dff1a29cc87ed2506820dfdc5ca0e57845d7e7'
CANDIDATE='aa1e6d7cbac46a713a58646b3c57374c007acd640c187c1b0aa0fce5dfef2302'

def run():
    original=(BASE/'source'/PATH).read_bytes();candidate=(BASE/'candidate'/PATH).read_bytes()
    assert hashlib.sha256(original).hexdigest()==ORIGINAL
    assert hashlib.sha256(candidate).hexdigest()==CANDIDATE
    before=original.decode();after=candidate.decode()
    changes=[x for x in difflib.SequenceMatcher(None,before.splitlines(),after.splitlines()).get_opcodes() if x[0]!='equal']
    assert len(changes)==1,changes
    kind,a,b,c,d=changes[0];old=before.splitlines()[a:b];new=after.splitlines()[c:d]
    assert old==['                let reference_size = reference_size.zoom(context.builder.effective_zoom);']
    assert new==[
      '                let reference_size = if context.builder.is_root_element {',
      '                    reference_size',
      '                } else {',
      '                    reference_size.zoom(context.builder.effective_zoom)',
      '                };']
    browser=json.loads((BASE/'evidence/candidate-v2-inputs.json').read_text())['pins_before']
    checked=[]
    for name,digest in browser.items():
        path=BASE/'source'/name
        if name==PATH:path=BASE/'candidate'/name
        if path.is_file():
            assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
            checked.append(name)
    assert len(checked)>=9
    assert hashlib.sha256((BASE/'evidence/rlh-on-zoomed-root.html').read_bytes()).hexdigest()=='b03a12394ebecee5c772ec1c655a78f303950825ce3828bc787bfa7e29a0c872'
    assert hashlib.sha256((BASE/'SCOPE.md').read_bytes()).hexdigest()=='77ea404c5c870f463858a5dae460cde4ddf5b039816d624b6c80f414dbeaf2c3'
    return {'original':ORIGINAL,'candidate':CANDIDATE,'delta':{'before':old,'after':new},'browserSourceBindings':checked}
