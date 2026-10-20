import argparse
import collections
import hashlib
import json
from pathlib import Path
import random
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
M = 1073741823
I = 2147483647


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, obj):
    p.write_text(json.dumps(obj, indent=2) + '\n')


def authenticate(root):
    rows = json.loads((root / 'FILES.json').read_text())
    wanted = {'FILES.json'} | {r['path'] for r in rows}
    assert len(wanted) == len(rows) + 1, 'duplicate input'
    assert wanted == set(json.loads((HERE/'INPUT-ROSTER.json').read_text())), 'canonical input roster'
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    directories = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_dir()}
    expected_dirs = {str(p) for name in wanted for p in Path(name).parents if str(p) != '.'}
    assert actual == wanted and directories == expected_dirs, 'closed input roster'
    assert not any(p.is_symlink() for p in root.rglob('*')), 'symlink'
    for row in rows:
        p = root / row['path']
        assert p.stat().st_size == row['size'] and digest(p) == row['sha256'], 'input digest'


def body(text):
    start = 'void FlexLine::ComputeCrossSizeAndBaseline('
    end = '\nnscoord FlexLine::ExtractBaselineOffset('
    assert text.count(start) == text.count(end) == 1
    return text[text.index(start):text.index(end)].rstrip() + '\n'


def semantic(items):
    groups = [[-M, -M], [-M, -M]]
    ordinary = 0
    for outer, distance, align, group, autos in items:
        if align < 2 and autos == 0:
            assert -I-1 <= outer-distance <= I
            groups[group][0] = max(groups[group][0], distance)
            groups[group][1] = max(groups[group][1], outer-distance)
        else:
            ordinary = max(ordinary, outer)
    sums = [sum(g) for g in groups]
    raw = max(*sums, ordinary)
    return [groups[0][0], groups[1][1], min(M, raw)], raw, all(-I-1 <= s <= I for s in sums)


def corpus():
    cases = [[]]
    values = [-I-1, -I, -M-1, -M, -1, 0, 1, M-1, M, M+1, I-1, I]
    for outer in values:
        for distance in values:
            for align, group, autos in [(0,0,0),(1,1,0),(0,1,0),(1,0,0),(0,0,1),(2,0,0)]:
                if align >= 2 or autos or -I-1 <= outer-distance <= I:
                    cases.append([[outer,distance,align,group,autos]])
    for n in [1, 6000, 700000000, 714000000, 720000000, 840000000, 1020000000, M]:
        for group in [0,1]:
            for align in [0,1]:
                for autos in [0,1]:
                    cases.append([[n,-n,align,group,autos],[n,n,align,group,autos]])
    rng = random.Random(872641)
    for _ in range(500):
        items = []
        for _ in range(rng.randrange(1,9)):
            outer, distance = rng.choice(values), rng.choice(values)
            align, group, autos = rng.randrange(3), rng.randrange(2), rng.randrange(2)
            if align < 2 and not autos and not -I-1 <= outer-distance <= I:
                continue
            items.append([outer,distance,align,group,autos])
        cases.append(items)
    return cases


def run(args):
    inputs = HERE / 'inputs'
    authenticate(inputs)
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    tool = json.loads((inputs/'TOOLCHAIN.json').read_text())
    for name in ['lean','clang']:
        assert digest(Path(tool[name])) == tool[name+'_sha256'], 'tool digest'
    records = []
    def command(name, argv, stdin=None):
        p = subprocess.run(argv, input=stdin, text=True, capture_output=True, cwd=out)
        (out/(name+'.stdout')).write_text(p.stdout)
        (out/(name+'.stderr')).write_text(p.stderr)
        records.append({'name':name,'argv':argv,'exit':p.returncode})
        return p
    roles = json.loads((inputs/'SOURCE-ROLES.json').read_text())
    for row in roles:
        assert digest(inputs/row['path']) == row['sha256']
        assert hashlib.sha256(body((inputs/row['path']).read_text()).encode()).hexdigest() == row['selected_body_sha256']
    tested = (inputs/'candidate-nsFlexContainerFrame.cpp').read_text()
    final = (inputs/'formatted-nsFlexContainerFrame.cpp').read_text()
    assert re.sub(r'\s+', '', tested) == re.sub(r'\s+', '', final)
    import difflib
    tested_lines, final_lines = tested.splitlines(keepends=True), final.splitlines(keepends=True)
    changes = [op for op in difflib.SequenceMatcher(None,tested_lines,final_lines,autojunk=False).get_opcodes() if op[0]!='equal']
    assert len(changes)==2 and all(re.sub(r'\s+', '', ''.join(tested_lines[a:b])) == re.sub(r'\s+', '', ''.join(final_lines[c:d])) for _,a,b,c,d in changes)
    save(out/'format-transfer.json',changes)
    package = json.loads((inputs/'PACKAGING.json').read_text())
    patch = inputs/'fix-candidate-v2.patch'
    assert digest(patch)==package['patch_sha256']
    for check in package['checks']:
        tmp=out/('patch-'+check['base'][:12]);tmp.mkdir()
        native=tmp/'layout/generic/nsFlexContainerFrame.cpp';native.parent.mkdir(parents=True)
        baseline=(inputs/('base-'+check['base'][:12]+'.cpp')).read_bytes();native.write_bytes(baseline)
        assert digest(native)==check['before_sha256']
        for reverse in [False,True]:
            proc=command(tmp.name+('-reverse' if reverse else '-apply'),['git','-C',str(tmp),'apply','--unsafe-paths',*(['-R'] if reverse else []),str(patch)])
            assert proc.returncode==0
            if not reverse:
                assert digest(native)==check['after_sha256']
                wpt=tmp/'testing/web-platform/tests/css/css-flexbox/flexbox-baseline-cross-size-overflow.html'
                assert digest(wpt)==package['wpt_sha256']==digest(inputs/'test.html')
            else:
                assert native.read_bytes()==baseline and not wpt.exists()
        shutil.rmtree(tmp)
    for name, source in [('producer',inputs/'Arithmetic.lean'),('challenges',HERE/'Challenges.lean')]:
        proc=command(name,[tool['lean'],str(source)])
        assert proc.returncode==0 and not proc.stderr
        audit=re.findall(r'(?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)',proc.stdout)
        assert len(audit)==(6 if name=='producer' else 5)
        for row in audit:
            assert set(x.strip() for x in row.split(',') if x.strip()) <= {'propext','Classical.choice','Quot.sound'}
    for name, statement in [
        ('false-universal-identity','min (1073741823 : Int) 2100000000 = 2100000000'),
        ('false-earlier-subtract-safe','(2147483647 : Int) - (-1) ≤ 2147483647'),
        ('false-three-lines-safe','(1073741823 : Int) * 3 ≤ 2147483647')]:
        src=out/(name+'.lean');src.write_text('import Std\nexample : '+statement+' := by decide +kernel\n')
        p=command(name,[tool['lean'],str(src)])
        assert p.returncode!=0 and 'error:' in p.stdout
    for name, proof, reject in [('sorry','by sorry','sorryAx'),('native','by native_decide','._native.native_decide.ax_')]:
        src=out/('axiom-'+name+'.lean');src.write_text('import Std\ntheorem injected : (1 : Nat) = 1 := '+proof+'\n#print axioms injected\n')
        p=command('axiom-'+name,[tool['lean'],str(src)])
        assert p.returncode==0 and reject in p.stdout
    cases=corpus();save(out/'corpus.json',cases)
    expected=[semantic(c) for c in cases]
    (out/'expected.json').write_text(json.dumps(expected)+'\n')
    facade=(inputs/'arithmetic-driver.cpp').read_text().split('void FlexLine::ComputeCrossSizeAndBaseline(')[0]
    main='''
int main() {
  int n;
  while (std::cin >> n) {
    FlexLine line;
    for (int i=0;i<n;i++) {
      int32_t o,d; int a,g,u;
      std::cin >> o >> d >> a >> g >> u;
      line.items.push_back({o,d,StyleAlignFlags(a),BaselineSharingGroup(g),unsigned(u)});
    }
    line.ComputeCrossSizeAndBaseline({});
    std::cout << line.mFirstBaselineOffset << ' ' << line.mLastBaselineOffset << ' ' << line.mLineCrossSize << '\\n';
  }
}
'''
    def encoded(rows):
        return ''.join(str(len(c))+' '+' '.join(str(v) for item in c for v in item)+'\n' for c in rows)
    variants={'before':body((inputs/'before-nsFlexContainerFrame.cpp').read_text())}
    variants.update({row['path'].replace('.cpp',''):body((inputs/row['path']).read_text()) for row in roles})
    repaired=variants['candidate-nsFlexContainerFrame']
    mutants={
        'remove-cap':repaired.replace('nscoord_MAX, std::max','2147483647, std::max'),
        'drop-last':repaired.replace('firstBaselineCrossSize, lastBaselineCrossSize,','firstBaselineCrossSize, firstBaselineCrossSize,'),
        'drop-ordinary':repaired.replace('int64_t(largestOuterCrossSize)','int64_t(0)'),
        'auto-margin-inclusion':repaired.replace('item.NumAutoMarginsInCrossAxis() == 0','true'),
        'last-baseline-exclusion':repaired.replace('item.AlignSelf() == StyleAlignFlags::LAST_BASELINE','false'),
    }
    cleanup=[]; native_counts={}; killed={}
    for opt in ['O0','O2']:
        for name, selected in {**variants,**mutants}.items():
            stem=name+'-'+opt;src=out/(stem+'.cpp');binary=out/(stem+'.bin')
            src.write_text(facade+selected+main)
            p=command(stem+'-compile',[tool['clang'],'-std=c++17','-'+opt,'-fsanitize=undefined','-fno-sanitize-recover=all',str(src),'-o',str(binary)])
            assert p.returncode==0
            if name=='before':
                indexes=[i for i,e in enumerate(expected) if e[2]]
                desired=[[expected[i][0][0],expected[i][0][1],expected[i][1]] for i in indexes]
            else:
                indexes=[i for i,c in enumerate(cases) if name!='auto-margin-inclusion' or all(-I-1 <= item[0]-item[1] <= I for item in c)]
                desired=[expected[i][0] for i in indexes]
            p=command(stem+'-run',[str(binary)],encoded([cases[i] for i in indexes]))
            assert p.returncode==0 and not p.stderr
            observed=[list(map(int,line.split())) for line in p.stdout.splitlines()]
            assert len(observed)==len(desired)
            diffs=[indexes[i] for i,(a,b) in enumerate(zip(observed,desired)) if a!=b]
            if name in mutants:
                assert diffs; killed[stem]={'mismatches':len(diffs),'first_case':diffs[0]}
            else:
                assert not diffs;native_counts[stem]=len(observed)
            if name in variants:
                p=command(stem+'-prior-subtraction-overflow',[str(binary)],encoded([[[I,-1,0,0,0]]]))
                assert p.returncode!=0 and 'signed integer overflow' in p.stderr
            if name=='before':
                p=command(stem+'-sum-overflow',[str(binary)],encoded([[[720000000,-720000000,0,0,0],[720000000,720000000,0,0,0]]]))
                assert p.returncode!=0 and 'signed integer overflow' in p.stderr
            cleanup.append({'path':binary.name,'sha256':digest(binary),'size':binary.stat().st_size});binary.unlink()
    guards=[]
    for name in ['extra-cache','resealed-extra-cache','empty-extra-dir','source-byte','role-substitution']:
        tmp=out/('guard-'+name);shutil.copytree(inputs,tmp)
        if name=='extra-cache':(tmp/'extra.olean').write_bytes(b'cache')
        if name=='resealed-extra-cache':
            (tmp/'extra.olean').write_bytes(b'cache')
            rows=json.loads((tmp/'FILES.json').read_text())
            rows.append({'path':'extra.olean','sha256':digest(tmp/'extra.olean'),'size':5})
            save(tmp/'FILES.json',rows)
        if name=='empty-extra-dir':(tmp/'extra').mkdir()
        if name=='source-byte':(tmp/'Arithmetic.lean').write_text('import Std\n')
        if name=='role-substitution':
            (tmp/'candidate-nsFlexContainerFrame.cpp').write_bytes((tmp/'formatted-nsFlexContainerFrame.cpp').read_bytes())
            rows=json.loads((tmp/'FILES.json').read_text())
            for row in rows:
                p=tmp/row['path'];row.update(sha256=digest(p),size=p.stat().st_size)
            save(tmp/'FILES.json',rows)
        try:
            authenticate(tmp)
            role=json.loads((tmp/'SOURCE-ROLES.json').read_text())[0]
            assert digest(tmp/role['path'])==role['sha256'],'role identity'
        except AssertionError as e:
            guards.append({'name':name,'rejected':str(e)})
        else:raise AssertionError('guard accepted')
        shutil.rmtree(tmp)
    assert guards[-1]['rejected']=='role identity'
    save(out/'COMMANDS.json',records);save(out/'CLEANUP.json',cleanup)
    summary={'cases':len(cases),'native':native_counts,'semantic_mutants':killed,'kernel_audits':11,'false_kernel_challenges':3,'axiom_controls':2,'integrity_controls':guards,'scope':'Exact final-operation repair with admitted providers; preexisting earlier overflow retained, not repaired.'}
    save(out/'SUMMARY.json',summary)
    print(json.dumps(summary))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    run(parser.parse_args())
