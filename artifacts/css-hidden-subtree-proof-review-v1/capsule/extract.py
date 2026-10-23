import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent

def unit(text, signature):
    if text.count(signature) != 1:
        raise ValueError('Nonunique signature: ' + signature)
    start = text.index(signature)
    brace = text.index('{', start)
    depth, mode, i = 0, 'code', brace
    while i < len(text):
        c, pair = text[i], text[i:i + 2]
        if mode == 'line':
            if c == '\n': mode = 'code'
        elif mode == 'block':
            if pair == '*/': mode, i = 'code', i + 1
        elif mode in ('"', "'"):
            if c == '\\': i += 1
            elif c == mode: mode = 'code'
        elif pair == '//': mode, i = 'line', i + 1
        elif pair == '/*': mode, i = 'block', i + 1
        elif c in ('"', "'"): mode = c
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1] + (';' if text[i + 1:i + 2] == ';' else '')
        i += 1
    raise ValueError('Unclosed source unit')

ROLES = [
 ('producer', 'native-pres-shell.cpp', 'void PresShell::FrameNeedsReflow('),
 ('mark', 'native-frame.cpp', 'void nsIFrame::MarkSubtreeDirty()'),
 ('principal', 'native-frame.cpp', 'void nsIFrame::MarkPrincipalChildrenDirty()'),
 ('hides', 'native-frame.cpp', 'bool nsIFrame::HidesContentForLayout() const'),
 ('hidden_parent', 'native-frame.cpp', 'bool nsIFrame::IsHiddenByContentVisibilityOfInFlowParentForLayout() const'),
 ('update', 'native-pres-shell.cpp', 'void PresShell::UpdateHiddenContentInForcedLayout('),
 ('ensure', 'native-pres-shell.cpp', 'void PresShell::EnsureReflowIfFrameHasHiddenContent('),
 ('forcing', 'native-pres-shell.cpp', 'bool PresShell::IsForcingLayoutForHiddenContent('),
 ('flush', 'native-pres-shell.cpp', 'bool PresShell::ReflowForHiddenContentIfNeeded()'),
 ('candidate_caller', 'candidate.cpp', 'std::tuple<nscoord, nsReflowStatus> nsFlexContainerFrame::ReflowChildren('),
 ('original_caller', 'original.cpp', 'std::tuple<nscoord, nsReflowStatus> nsFlexContainerFrame::ReflowChildren('),
]

def extract():
 values, bindings = {}, []
 for name, file, signature in ROLES:
  path = ROOT / 'input' / file
  value = unit(path.read_text(), signature)
  values[name] = value
  bindings.append({'name': name, 'source': file, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'signature': signature, 'unit_sha256': hashlib.sha256(value.encode()).hexdigest(), 'kind': 'complete unit; caller is binding-only'})
 root_mark = 'subtreeRoot->AddStateBits(aBitToAdd);'
 if values['producer'].count(root_mark) != 1: raise ValueError('root mark identity')
 bindings.append({'name': 'producer_root_mark', 'unit_sha256': hashlib.sha256(root_mark.encode()).hexdigest(), 'kind': 'exact statement; aBitToAdd specialized to IS_DIRTY'})
 values['producer_walk'] = unit(values['producer'], 'if (frameAncestorAndDescendantISizesDirty || dirty)')
 bindings.append({'name': 'producer_walk', 'unit_sha256': hashlib.sha256(values['producer_walk'].encode()).hexdigest(), 'kind': 'exact conditional descendant walk, specialized dirty=true and intrinsic=None'})
 for role in ('candidate', 'original'):
  value = unit(values[role + '_caller'], 'if (HidesContentForLayout())')
  values[role + '_guard'] = value
  bindings.append({'name': role + '_guard', 'unit_sha256': hashlib.sha256(value.encode()).hexdigest(), 'kind': 'exact initial guard, remaining caller not executed'})
 return values, bindings

def generate(mutant='none'):
 values, _ = extract()
 if mutant == 'omit_mark':
  values['candidate_guard'] = values['candidate_guard'].replace('MarkPrincipalChildrenDirty();', '(void)0;')
 elif mutant == 'root_bit_only':
  values['principal'] = values['principal'].replace('childFrame->MarkSubtreeDirty();', 'childFrame->AddStateBits(NS_FRAME_IS_DIRTY);')
 elif mutant == 'has_dirty_children_prunes':
  values['mark'] = values['mark'].replace('HasAnyStateBits(NS_FRAME_IS_DIRTY)', 'HasAnyStateBits(NS_FRAME_IS_DIRTY | NS_FRAME_HAS_DIRTY_CHILDREN)')
 elif mutant == 'principal_lists_only':
  values['mark'] = values['mark'].replace('ChildLists()', 'PrincipalOnly()')
 elif mutant == 'ignore_table_barrier':
  values['mark'] = values['mark'].replace(' || f->IsTableColGroupFrame()', '')
 elif mutant == 'ignore_dirty_barrier':
  values['mark'] = values['mark'].replace('HasAnyStateBits(NS_FRAME_IS_DIRTY)', 'HasAnyStateBits(0)')
 elif mutant == 'force_clean_query':
  values['update'] = values['update'].replace('!aFrame || !aFrame->IsSubtreeDirty()', '!aFrame')
 elif mutant != 'none': raise ValueError(mutant)
 return '\n'.join([(ROOT/'facade-prefix.cpp').read_text()] + [values[n] for n in ('mark','principal','hides','hidden_parent','update','ensure','forcing','flush')] + ['void ProduceDirty(nsIFrame* subtreeRoot) { const bool frameAncestorAndDescendantISizesDirty = false; const bool dirty = true; const uint32_t aBitToAdd = NS_FRAME_IS_DIRTY; AutoTArray<nsIFrame*, 4> subtrees; subtreeRoot->AddStateBits(aBitToAdd);\n' + values['producer_walk'] + '\n}', 'Result CandidateFlex::HiddenGuard() {\n' + values['candidate_guard'] + '\nreturn {1, {}};\n}'] + [(ROOT/'facade-main.cpp').read_text()])

if __name__ == '__main__':
 print(json.dumps(extract()[1], indent=2, sort_keys=True))
