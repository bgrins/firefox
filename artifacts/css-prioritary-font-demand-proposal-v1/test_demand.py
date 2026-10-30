import hashlib, json, re, subprocess, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RUSTC=Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def extract(path):
    text=path.read_text()
    start=text.index('/// Set of flags to references this custom property makes.')
    end=text.index('/// A map from NonCustomReferenceMap to a T.',start)
    block=text[start:end].replace(', MallocSizeOf, ToShmem','')
    return block.replace('    fn from_unit(', '    pub(crate) fn from_unit(')
base=extract(HERE/'base/servo/components/style/custom_properties.rs')
candidate=extract(HERE/'candidate/servo/components/style/custom_properties.rs')
preamble='use bitflags::bitflags;\ntype CowRcStr = str;\n#[derive(Clone, Copy, Debug, PartialEq, Eq)]\npub enum PrioritaryPropertyId { FontSize, LineHeight, ColorScheme }\nstruct NoCalcLength;\nimpl NoCalcLength {\nconst EM: &\'static str = "em";\nconst EX: &\'static str = "ex";\nconst CAP: &\'static str = "cap";\nconst CH: &\'static str = "ch";\nconst IC: &\'static str = "ic";\nconst LH: &\'static str = "lh";\nconst REM: &\'static str = "rem";\nconst REX: &\'static str = "rex";\nconst RCAP: &\'static str = "rcap";\nconst RCH: &\'static str = "rch";\nconst RIC: &\'static str = "ric";\nconst RLH: &\'static str = "rlh";\n}\n'
body=preamble+'mod base { use super::*;\n'+base+'}\nmod candidate { use super::*;\n'+candidate+'}\n'+(HERE/'DemandTests.rs').read_text()
(HERE/'ExtractedDemand.rs').write_text(body)
commands=[]
def run(args,expect=0):
    r=subprocess.run([str(a) for a in args],capture_output=True,text=True)
    commands.append({'command':[str(a) for a in args],'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    assert r.returncode==expect,commands[-1]
with tempfile.TemporaryDirectory(prefix='css-font-demand-',dir='/private/tmp') as temporary:
    scratch=Path(temporary)
    lib=scratch/'libbitflags.rlib'
    run([RUSTC,'--edition=2021','--crate-name','bitflags','--crate-type','rlib',ROOT/'third_party/rust/bitflags/src/lib.rs','-o',lib])
    source=scratch/'Demand.rs';source.write_text(body);binary=scratch/'demand-tests'
    run([RUSTC,'--edition=2024','--test',source,'--extern','bitflags='+str(lib),'-o',binary])
    run([binary])
    mutants = {
      'metric_collapsed': candidate.replace('SingleNonCustomReference::FontUnits if metrics => FontDependencyDemand::FontMetrics', 'SingleNonCustomReference::FontUnits if metrics => FontDependencyDemand::ComputedSize'),
      'orientation_collapsed': candidate.replace('FontDependencyDemand::OrientedMetrics\n                },', 'FontDependencyDemand::FontMetrics\n                },', 1),
      'root_leak': candidate.replace('(is_root_element && self.intersects(Self::ROOT_FONT_ORIENTATION))', 'self.intersects(Self::ROOT_FONT_ORIENTATION)'),
      'downgrade': candidate.replace('if self >= other { self } else { other }', 'other'),
    }
    for name, mutant in mutants.items():
        assert mutant != candidate, name
        variant = preamble+'mod base { use super::*;\n'+base+'}\nmod candidate { use super::*;\n'+mutant+'}\n'+(HERE/'DemandTests.rs').read_text()
        source.write_text(variant)
        run([RUSTC,'--edition=2024','--test',source,'--extern','bitflags='+str(lib),'-o',binary])
        run([binary],expect=101)
assert not scratch.exists()
result={'commands':commands,'scratch_removed':True,'source_sha256':sha(HERE/'ExtractedDemand.rs'),'rustc_sha256':sha(RUSTC),'native_style_compilation':False,'extraction_changes':['remove MallocSizeOf/ToShmem derives','expose from_unit to test sibling','stub CowRcStr/NoCalcLength/PrioritaryPropertyId imports'],'bitflags_source_sha256':sha(ROOT/'third_party/rust/bitflags/src/lib.rs')}
(HERE/'TEST-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'tests':3,'semantic_flag_root_combinations':8192,'join_triples':64,'rejected_semantic_mutants':4,'scratch_removed':True,'native_style_compilation':False}))
