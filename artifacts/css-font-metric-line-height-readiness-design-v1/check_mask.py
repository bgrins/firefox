import hashlib, json, subprocess, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'artifacts/css-font-metric-ordinary-ownership-v1/candidate/servo/components/style/custom_properties.rs'
RUSTC=Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=SOURCE.read_text()
a=s.index('/// Set of flags to references this custom property makes.')
b=s.index('/// A map from NonCustomReferenceMap to a T.',a)
block=s[a:b].replace(', MallocSizeOf, ToShmem','')
preamble='use bitflags::bitflags;\ntype CowRcStr = str;\n#[derive(Clone, Copy, Debug, PartialEq, Eq)]\npub enum PrioritaryPropertyId { FontSize, LineHeight, ColorScheme }\nstruct NoCalcLength;\nimpl NoCalcLength {\nconst EM: &\'static str = "em";\nconst EX: &\'static str = "ex";\nconst CAP: &\'static str = "cap";\nconst CH: &\'static str = "ch";\nconst IC: &\'static str = "ic";\nconst LH: &\'static str = "lh";\nconst REM: &\'static str = "rem";\nconst REX: &\'static str = "rex";\nconst RCAP: &\'static str = "rcap";\nconst RCH: &\'static str = "rch";\nconst RIC: &\'static str = "ric";\nconst RLH: &\'static str = "rlh";\n}\n'
tests = r'''
#[test] fn actual_collision() {
 let lh=ReferenceFlags::from_unit("lh");
 let ch=ReferenceFlags::from_unit("ch");
 assert_eq!(lh, lh | ch);
 assert_eq!(lh, ReferenceFlags::FONT_UNITS | ReferenceFlags::LH_UNITS | ReferenceFlags::FONT_METRICS | ReferenceFlags::FONT_ORIENTATION);
 assert_ne!(ReferenceFlags::from_unit("em"), lh);
}
#[test] fn clearing_lh_aggregate_loses_independent_ch() {
 let both=ReferenceFlags::from_unit("lh") | ReferenceFlags::from_unit("ch");
 let narrowed=both & !(ReferenceFlags::FONT_METRICS | ReferenceFlags::FONT_ORIENTATION);
 assert!(!narrowed.contains(ReferenceFlags::from_unit("ch")));
}
'''
body=preamble+block+tests
(HERE/'ExtractedFlags.rs').write_text(body)
commands=[]
def run(args,expected=0):
 r=subprocess.run([str(x) for x in args],text=True,capture_output=True)
 commands.append(dict(command=[str(x) for x in args],exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
 assert r.returncode==expected,commands[-1]
with tempfile.TemporaryDirectory(prefix='css-lh-mask-',dir='/private/tmp') as directory:
 scratch=Path(directory); lib=scratch/'libbitflags.rlib'; source=scratch/'Flags.rs'; binary=scratch/'flags'
 run([RUSTC,'--edition=2021','--crate-name','bitflags','--crate-type','rlib',ROOT/'third_party/rust/bitflags/src/lib.rs','-o',lib])
 variants={'positive':body,
 'false_distinguishable_mask':body.replace('assert_eq!(lh, lh | ch);','assert_ne!(lh, lh | ch);'),
 'false_global_clearing_preserves_ch':body.replace('assert!(!narrowed.contains','assert!(narrowed.contains')}
 for name,text in variants.items():
  source.write_text(text)
  run([RUSTC,'--edition=2024','--test',source,'--extern','bitflags='+str(lib),'-o',binary])
  run([binary],0 if name=='positive' else 101)
assert not scratch.exists()
result={'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'extracted_sha256':sha(HERE/'ExtractedFlags.rs'),'rustc_sha256':sha(RUSTC),'bitflags_sha256':sha(ROOT/'third_party/rust/bitflags/src/lib.rs'),'commands':commands,'positive_tests':2,'rejected_false_controls':2,'scratch_removed':True,'native_build':False,'scope':'Exact provider methods and real vendored bitflags; CowRcStr and unit constants adapted, priority enum stub as in prior demand extraction; no CSS parser/conversion or Lean proof.'}
(HERE/'MASK-CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['positive_tests','rejected_false_controls','scratch_removed','native_build']}))
