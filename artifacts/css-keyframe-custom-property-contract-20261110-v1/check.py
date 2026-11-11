import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for name,digest in pins['files'].items():
        p=HERE/'source'/name
        assert sha(p)==digest
        assert p.read_bytes()==subprocess.check_output(['git','-c','core.fsmonitor=false','show',pins['revision']+':'+name],cwd=HERE)
    primary=json.loads((HERE/'PRIMARY.json').read_text())
    for name,row in primary.items():
        p=HERE/'primary'/(name+'.html')
        assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
    for file,spec in [('css-processing.json','css-animations-2'),('computed-keyframes.json','web-animations-1'),('value-context.json','web-animations-1'),('keyframe-interface.json','web-animations-1'),('variables.json','css-variables-1')]:
        value=json.loads((HERE/file).read_text())
        assert value['sha']=='hash:'+primary[spec]['sha256']
    syntax=json.loads((HERE/'SYNTAX.json').read_text())
    assert syntax['exit']==0 and syntax['execution'] is False
    assert sha(HERE/'proposal/custom-keyframe-value-observations.html')==syntax['fixture_sha256']
    for n,digest in json.loads((HERE/'FILES.json').read_text()).items():
        assert sha(HERE/n)==digest
    print(json.dumps({'status':'PASS','native_test_source_pins':len(pins['files']),'fresh_primary_pages':len(primary),'indexed_sections_matching_primary':5,'JavaScript_syntax_pass':True,'browser_build_or_live_execution':False},indent=2))


if __name__=='__main__':
    main()
