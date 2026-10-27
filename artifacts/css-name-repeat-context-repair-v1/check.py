import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PATHS = ['servo/components/style/values/specified/grid.rs', 'servo/components/style/values/generics/grid.rs']
WPT_PATH = 'testing/web-platform/tests/css/css-grid/subgrid/subgrid-contextual-name-repeat.html'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, cwd, log):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=60)
    log.write_text(result.stdout + result.stderr)
    assert result.returncode == 0, (command, result.returncode, str(log))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve()
    out.mkdir(exist_ok=False)
    for name, digest in json.loads((HERE/'REFERENCES.json').read_text()).items():
        assert sha(ROOT/name) == digest
    generic = (HERE/'candidate'/PATHS[1]).read_text()
    start = generic.index('impl LineNameListValue<i32> {')
    end = generic.index('impl<I: ToCss> ToCss for LineNameList<I>', start)
    extracted = generic[start:end]
    facade = (HERE/'facade-prefix.rs').read_text() + extracted + (HERE/'facade-main.rs').read_text()
    (out/'extracted.rs').write_text(facade)
    with tempfile.TemporaryDirectory(prefix='name-repeat-review-') as temporary:
        scratch = Path(temporary)
        for opt in [0, 2]:
            binary = scratch/f'helper-{opt}'
            run(['rustc','--edition=2024','-C','overflow-checks=yes','-C',f'opt-level={opt}',str(out/'extracted.rs'),'-o',str(binary)], scratch, out/f'compile-{opt}.log')
            run([str(binary)], scratch, out/f'run-{opt}.log')
            binary.unlink()
        for base in ['head90','installed']:
            tree = scratch/base
            tree.mkdir()
            run(['git','init','-q'],tree,out/f'{base}-init.log')
            original = HERE/('head' if base == 'head90' else 'original-installed')
            for name in PATHS:
                path=tree/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((original/name).read_bytes())
            run(['git','apply',str(HERE/f'{base}-standalone.patch')],tree,out/f'{base}-apply.log')
            for name in PATHS:
                assert sha(tree/name)==sha(HERE/'candidate'/name)
            assert sha(tree/WPT_PATH)==sha(HERE/'subgrid-contextual-name-repeat.html')
            run(['git','apply','--reverse',str(HERE/f'{base}-standalone.patch')],tree,out/f'{base}-reverse.log')
            assert not (tree/WPT_PATH).exists()
            for name in PATHS:
                assert sha(tree/name)==sha(original/name)
        body = (HERE/'subgrid-contextual-name-repeat.html').read_text()
        scripts = [s for s in re.findall(r'<script[^>]*>(.*?)</script>',body,re.S) if s.strip()]
        assert len(scripts)==1
        js=scratch/'fixture.js';js.write_text(scripts[0])
        run(['node','--check',str(js)],scratch,out/'syntax.log')
        js.write_text('const names=[]; function test(fn,name){names.push(name);}\n'+scripts[0]+'\nprocess.stdout.write(JSON.stringify(names));')
        result=run(['node',str(js)],scratch,out/'roster.log')
        names=json.loads(result.stdout)
        assert len(names)==len(set(names))==10
        assert names==json.loads((HERE/'ROSTER.json').read_text())
        lint=scratch/'lint';lint.mkdir();run(['git','init','-q'],lint,out/'lint-init.log')
        wpt=ROOT/'testing/web-platform/tests'
        for name in ['.gitignore','lint.ignore']:(lint/name).write_bytes((wpt/name).read_bytes())
        relative=WPT_PATH.removeprefix('testing/web-platform/tests/')
        destination=lint/relative;destination.parent.mkdir(parents=True);destination.write_text(body)
        result=run([str(wpt/'_venv3/bin/python3'),'-I','-B',str(ROOT/'artifacts/css-round-parse-negative-zero-repair-v2/check.py'),'--lint-worker',str(lint),relative],lint,out/'lint.log')
        assert result.stdout==result.stderr==''
    assert 'n.resolve().is_none()' not in (HERE/'candidate'/PATHS[0]).read_text()
    report={'status':'ARTIFACT_CHECK_PASS','native_paths':2,'wpt_paths':1,'wpt_cases':10,
            'patch_roundtrips':['HEAD90','installed123124_reference'],
            'helper_exact_cache_and_conversion_bodies':True,'helper_context_and_owned_slice_are_typed_facades':True,
            'helper_overflow_checks':True,'helper_optimization_levels':[0,2],
            'full_gecko_compile':False,'browser_executed':False,'scratch_removed':True}
    (out/'CHECK.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__ == '__main__':
    main()
