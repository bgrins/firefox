from pathlib import Path
import hashlib,json,re
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
RECORD=BASE/'SOURCE-v1.json'
SNIPPETS={
 'same-space': 'if source.color_space == self.color_space {\n            return;\n        }',
 'rgb-domain': 'if source.color_space.is_rgb_or_xyz_like() && self.color_space.is_rgb_or_xyz_like() {',
 'carry-union': 'self.flags |= source.flags & (F::C0_IS_NONE | F::C1_IS_NONE | F::C2_IS_NONE);',
 'mix-conversion': 'let mut converted = color.to_color_space(color_space);\n    converted.carry_forward_analogous_missing_components(color);\n    converted',
 'outcome-none': '(true, true) => Self::None,',
 'outcome-right': '(true, false) => Self::UseRight,',
 'outcome-left': '(false, true) => Self::UseLeft,',
 'outcome-mix': '(false, false) => Self::Mix,',
}
MOD_SNIPPETS={
 'c0': 'const C0_IS_NONE = 1 << 0;',
 'c1': 'const C1_IS_NONE = 1 << 1;',
 'c2': 'const C2_IS_NONE = 1 << 2;',
 'alpha': 'const ALPHA_IS_NONE = 1 << 3;',
 'conversion-alpha': 'nan_to_missing!(result.2),\n            self.alpha(),',
 'rgb-family': '''Self::Srgb
            | Self::SrgbLinear
            | Self::DisplayP3
            | Self::DisplayP3Linear
            | Self::A98Rgb
            | Self::ProphotoRgb
            | Self::Rec2020
            | Self::XyzD50
            | Self::XyzD65 => true,''',
}
SPACES=['Srgb','Hsl','Hwb','Lab','Lch','Oklab','Oklch','SrgbLinear','DisplayP3','DisplayP3Linear','A98Rgb','ProphotoRgb','Rec2020','XyzD50','XyzD65']
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def record():return json.loads(RECORD.read_text())
def inputs(require_worktree=True):
 result=[RECORD,BASE/'SPEC-v1.json',BASE/'interpolation-missing.html']
 for path,entry in record()['files'].items():
  result += [BASE/entry['old_snapshot'],BASE/entry['current_snapshot']]
  if require_worktree:result.append(ROOT/path)
 return result

def shape(source,module):
 for group,text in [(SNIPPETS,source),(MOD_SNIPPETS,module)]:
  for name,snippet in group.items():
   if text.count(snippet)!=1:raise RuntimeError('Source shape: '+name)
 start=source.index(SNIPPETS['rgb-domain']);end=source.index('\n        }',start)
 if source[start:end] != SNIPPETS['rgb-domain']+'\n            '+SNIPPETS['carry-union']+'\n            return;':
  raise RuntimeError('RGB branch changed')
 enum=module.split('pub enum ColorSpace {',1)[1].split('\n}',1)[0]
 found=re.findall(r'^    ([A-Za-z0-9]+)(?: = 0)?,',enum,re.M)
 if found!=SPACES:raise RuntimeError('Color space inventory')

def lineage(source,module,old_source,old_module):
 insertion='            '+SNIPPETS['carry-union']+'\n'
 if source.count(insertion)!=1 or source.replace(insertion,'',1)!=old_source:
  raise RuntimeError('Unexpected native patch delta')
 if module!=old_module:raise RuntimeError('Unexpected conversion module change')

def run(require_worktree=True):
 r=record()
 if sha(BASE/'SPEC-v1.json')!=r['spec_record_sha256']:raise RuntimeError('Spec provenance drift')
 spec=json.loads((BASE/'SPEC-v1.json').read_text())
 if sha(BASE/'interpolation-missing.html')!=spec['section_sha256']:raise RuntimeError('Spec subsection drift')
 for path,entry in r['files'].items():
  pairs=[(BASE/entry['current_snapshot'],entry['current_sha256']),(BASE/entry['old_snapshot'],entry['old_sha256'])]
  if require_worktree:pairs.append((ROOT/path,entry['current_sha256']))
  for p,h in pairs:
   if sha(p)!=h:raise RuntimeError('Source drift '+str(p))
 source=(BASE/'current-mix.rs').read_text();module=(BASE/'current-mod.rs').read_text()
 shape(source,module)
 old_source=(BASE/'old-mix.rs').read_text();old_module=(BASE/'old-mod.rs').read_text()
 lineage(source,module,old_source,old_module);rejected=[]
 for name,src,mod in [('foreign-mix-delta',source+'\n',module),('foreign-conversion-delta',source,module+'\n')]:
  try:lineage(src,mod,old_source,old_module)
  except RuntimeError:rejected.append(name)
  else:raise RuntimeError('Accepted unrelated native delta')
 for group,text,which in [(SNIPPETS,source,0),(MOD_SNIPPETS,module,1)]:
  for name,snippet in group.items():
   texts=[source,module];texts[which]=text.replace(snippet,'',1)
   try:shape(*texts)
   except RuntimeError:rejected.append(name)
   else:raise RuntimeError('Accepted source mutation '+name)
 return r,rejected
