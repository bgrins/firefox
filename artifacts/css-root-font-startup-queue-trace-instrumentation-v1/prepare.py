from pathlib import Path
import difflib, hashlib, json, subprocess
HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'css-root-font-startup-trace-instrumentation-v1'
REV = 'e86b64866cdc5e2260ba9be08c45756fd96e21bb'
sha = lambda b: hashlib.sha256(b).hexdigest()
old_roles = json.loads((OLD / 'SOURCE-ROLES.json').read_text())['roles']
roles = {}
edits = []
for path in [*old_roles, 'dom/animation/EffectCompositor.cpp', 'layout/style/ServoStyleSet.cpp']:
    base = subprocess.check_output(['git', 'show', REV + ':' + path])
    parent = (OLD / 'candidate' / path).read_bytes() if path in old_roles else base
    if path in old_roles:
        assert sha(base) == old_roles[path]['base_sha256']
        assert sha(parent) == old_roles[path]['candidate_sha256']
    for kind, data in [('base', base), ('parent', parent), ('candidate', parent)]:
        out = HERE / kind / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
    roles[path] = {'base_sha256': sha(base), 'parent_sha256': sha(parent)}
def edit(path, old, new):
    p = HERE / 'candidate' / path
    text = p.read_text()
    assert text.count(old) == 1, (path, old[:120], text.count(old))
    p.write_text(text.replace(old, new))
    edits.append({'path': path, 'old': old, 'new': new})
def log(fmt, args, indent='  '):
    return indent + 'if (std::getenv("MOZ_ROOT_FONT_STARTUP_TRACE")) {\n' + indent + '  std::fprintf(stderr, "RFST ' + fmt + '\\n", ' + args + ');\n' + indent + '}\n'
E = 'dom/animation/EffectCompositor.cpp'
S = 'layout/style/ServoStyleSet.cpp'
for path in [E, S]:
    text = (HERE / 'candidate' / path).read_text()
    first = next(line for line in text.splitlines() if line.startswith('#include '))
    edit(path, first + '\n', first + '\n\n#include <cstdio>\n#include <cstdlib>\n')
node = 'static_cast<const void*>(static_cast<const nsINode*>(aElement))'
pseudo = 'static_cast<unsigned>(aPseudoRequest.mType)'
edit(E, '  bool& restyleEntry = elementsToRestyle.LookupOrInsert(key, false);\n',
     '  bool& restyleEntry = elementsToRestyle.LookupOrInsert(key, false);\n' + log('request compositor=%p target_node=%p pseudo=%u level=%u type=%u posted_before=%d', 'static_cast<void*>(this), ' + node + ', ' + pseudo + ', static_cast<unsigned>(aCascadeLevel), static_cast<unsigned>(aRestyleType), int(restyleEntry)'))
edit(E, '    bool skipRestyle = std::exchange(restyleEntry, true);\n',
     '    bool skipRestyle = std::exchange(restyleEntry, true);\n' + log('request-post compositor=%p target_node=%p pseudo=%u level=%u skip=%d', 'static_cast<void*>(this), ' + node + ', ' + pseudo + ', static_cast<unsigned>(aCascadeLevel), int(skipRestyle)', '    '))
anchor = '  if (ServoStyleSet::IsInServoTraversal() || mIsInPreTraverse) {\n'
edit(E, anchor, anchor + log('post-deferred compositor=%p target_node=%p normalized_node=%p pseudo=%u level=%u pretraverse=%d', 'static_cast<void*>(this), ' + node + ', static_cast<const void*>(static_cast<const nsINode*>(element)), ' + pseudo + ', static_cast<unsigned>(aCascadeLevel), int(mIsInPreTraverse)', '    '))
anchor = '  mPresContext->PresShell()->RestyleForAnimation(element, hint);\n'
edit(E, anchor, log('post-shell compositor=%p target_node=%p normalized_node=%p pseudo=%u level=%u', 'static_cast<void*>(this), ' + node + ', static_cast<const void*>(static_cast<const nsINode*>(element)), ' + pseudo + ', static_cast<unsigned>(aCascadeLevel)') + anchor)
anchor = 'bool EffectCompositor::PreTraverseInSubtree(ServoTraversalFlags aFlags,\n                                            Element* aRoot) {\n'
entry = log('pre-enter compositor=%p root_node=%p flags=%u', 'static_cast<void*>(this), static_cast<const void*>(static_cast<const nsINode*>(aRoot)), static_cast<unsigned>(aFlags)')
entry += '  if (std::getenv("MOZ_ROOT_FONT_STARTUP_TRACE")) {\n    for (size_t i = 0; i < kCascadeLevelCount; ++i) {\n      std::fprintf(stderr, "RFST pre-queue compositor=%p level=%zu count=%u\\n", static_cast<void*>(this), i, unsigned(mElementsToRestyle[CascadeLevel(i)].Count()));\n    }\n  }\n'
edit(E, anchor, anchor + entry)
anchor = '      // We need to post restyle hints even if the target is not in EffectSet to\n'
edit(E, anchor, log('pre-selected compositor=%p target_node=%p pseudo=%u level=%u posted=%d', 'static_cast<void*>(this), static_cast<const void*>(static_cast<const nsINode*>(target.mElement)), static_cast<unsigned>(target.mPseudoRequest.mType), static_cast<unsigned>(cascadeLevel), int(iter.Data())', '      ') + anchor)
anchor = '  return foundElementsNeedingRestyle;\n'
exitlog = '  if (std::getenv("MOZ_ROOT_FONT_STARTUP_TRACE")) {\n    for (size_t i = 0; i < kCascadeLevelCount; ++i) {\n      std::fprintf(stderr, "RFST pre-remaining compositor=%p level=%zu count=%u\\n", static_cast<void*>(this), i, unsigned(mElementsToRestyle[CascadeLevel(i)].Count()));\n    }\n  }\n'
exitlog += log('pre-exit compositor=%p found=%d', 'static_cast<void*>(this), int(foundElementsNeedingRestyle)')
edit(E, anchor, exitlog + anchor)
anchor = 'bool ServoStyleSet::StyleDocument(ServoTraversalFlags aFlags) {\n'
edit(S, anchor, anchor + log('document-enter set=%p document=%p flags=%u', 'static_cast<void*>(this), static_cast<void*>(mDocument), static_cast<unsigned>(aFlags)'))
anchor = '  if (!mDocument->GetServoRestyleRoot()) {\n    return false;\n  }\n\n  PreTraverse(aFlags);'
edit(S, anchor, '  if (!mDocument->GetServoRestyleRoot()) {\n' + log('document-no-root set=%p', 'static_cast<void*>(this)', '    ') + '    return false;\n  }\n\n' + log('document-pre set=%p', 'static_cast<void*>(this)') + '  PreTraverse(aFlags);')
anchor = '  // Do the first traversal.\n'
edit(S, anchor, log('document-pass-begin set=%p pass=1', 'static_cast<void*>(this)') + anchor)
anchor = '    AutoPrepareTraversal guard(this);\n\n    postTraversalRequired |=\n'
edit(S, anchor, log('document-subtree set=%p pass=1 root_node=%p', 'static_cast<void*>(this), static_cast<const void*>(static_cast<const nsINode*>(root))', '    ') + anchor)
anchor = '  // If there are still animation restyles needed, trigger a second traversal to\n'
edit(S, anchor, log('document-pass-end set=%p pass=1 post_required=%d', 'static_cast<void*>(this), int(postTraversalRequired)') + anchor)
anchor = '  if (GetPresContext()->EffectCompositor()->PreTraverse(aFlags)) {\n    DocumentStyleRootIterator iter(mDocument->GetServoRestyleRoot());'
edit(S, anchor, log('document-between-pre set=%p', 'static_cast<void*>(this)') + '  if (GetPresContext()->EffectCompositor()->PreTraverse(aFlags)) {\n' + log('document-pass-begin set=%p pass=2', 'static_cast<void*>(this)', '    ') + '    DocumentStyleRootIterator iter(mDocument->GetServoRestyleRoot());')
anchor = '    while (Element* root = iter.GetNextStyleRoot()) {\n      AutoPrepareTraversal guard(this);\n      postTraversalRequired |='
edit(S, anchor, '    while (Element* root = iter.GetNextStyleRoot()) {\n' + log('document-subtree set=%p pass=2 root_node=%p', 'static_cast<void*>(this), static_cast<const void*>(static_cast<const nsINode*>(root))', '      ') + '      AutoPrepareTraversal guard(this);\n      postTraversalRequired |=')
anchor = '  return postTraversalRequired;\n}\n\nvoid ServoStyleSet::StyleNewSubtree'
edit(S, anchor, log('document-exit set=%p post_required=%d', 'static_cast<void*>(this), int(postTraversalRequired)') + anchor)
anchor = '    if (MOZ_UNLIKELY(!root->HasServoData()) && !parent) {\n'
edit(S, anchor, anchor + log('document-new-subtree set=%p pass=1 root_node=%p', 'static_cast<void*>(this), static_cast<const void*>(static_cast<const nsINode*>(root))', '      '))
for path in roles:
    roles[path]['candidate_sha256'] = sha((HERE / 'candidate' / path).read_bytes())
for origin, name in [('base', 'native.patch'), ('parent', 'PARENT-DELTA.patch')]:
    diff = ''.join(''.join(difflib.unified_diff((HERE / origin / p).read_text().splitlines(True), (HERE / 'candidate' / p).read_text().splitlines(True), fromfile='a/' + p, tofile='b/' + p)) for p in roles)
    (HERE / name).write_text(diff)
(HERE / 'SOURCE-ROLES.json').write_text(json.dumps({'revision': REV, 'parent': str(OLD.relative_to(HERE.parent.parent)), 'roles': roles}, indent=2) + '\n')
(HERE / 'EDITS.json').write_text(json.dumps(edits, indent=2) + '\n')
print(json.dumps({'roles': len(roles), 'edits': len(edits)}, indent=2))
