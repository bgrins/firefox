from pathlib import Path
import difflib
import hashlib
import json
import shutil

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'css-root-font-startup-queue-trace-instrumentation-v1'
ROLE = 'layout/style/ServoStyleSet.cpp'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(PARENT / 'FILES.json') == 'a433f9535e2ab68f9b1defb462b13acfbce9746f9a2b7f1877192a812ef38f1a'
roles = json.loads((PARENT / 'SOURCE-ROLES.json').read_text())
for path, pins in roles['roles'].items():
    for kind, old_kind in [('base', 'base'), ('parent', 'candidate'), ('candidate', 'candidate')]:
        source = PARENT / old_kind / path
        assert sha(source) == pins[old_kind + '_sha256']
        dest = HERE / kind / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)

addition = '''  constexpr unsigned kMaxAdditionalAnimationPasses = 16;
  unsigned additionalAnimationPasses = 0;
  for (; additionalAnimationPasses < kMaxAdditionalAnimationPasses;
       ++additionalAnimationPasses) {
    const bool selected =
        GetPresContext()->EffectCompositor()->PreTraverse(aFlags);
    if (std::getenv("MOZ_ROOT_FONT_STARTUP_TRACE")) {
      std::fprintf(stderr,
                   "RFST drain-select set=%p extra=%u selected=%d\\n",
                   static_cast<void*>(this), additionalAnimationPasses + 1,
                   int(selected));
    }
    if (!selected) {
      break;
    }
    DocumentStyleRootIterator iter(mDocument->GetServoRestyleRoot());
    while (Element* root = iter.GetNextStyleRoot()) {
      if (std::getenv("MOZ_ROOT_FONT_STARTUP_TRACE")) {
        std::fprintf(stderr,
                     "RFST drain-subtree set=%p extra=%u root_node=%p\\n",
                     static_cast<void*>(this), additionalAnimationPasses + 1,
                     static_cast<const void*>(static_cast<const nsINode*>(root)));
      }
      AutoPrepareTraversal guard(this);
      postTraversalRequired |=
          Servo_TraverseSubtree(root, mRawData.get(), &snapshots, aFlags) ||
          root->HasAnyOfFlags(Element::kAllServoDescendantBits |
                              NODE_NEEDS_FRAME);
    }
    if (std::getenv("MOZ_ROOT_FONT_STARTUP_TRACE")) {
      std::fprintf(stderr,
                   "RFST drain-pass-end set=%p extra=%u post_required=%d\\n",
                   static_cast<void*>(this), additionalAnimationPasses + 1,
                   int(postTraversalRequired));
    }
  }
  if (std::getenv("MOZ_ROOT_FONT_STARTUP_TRACE")) {
    std::fprintf(stderr,
                 "RFST drain-exit set=%p completed=%u cap_reached=%d "
                 "pending_any=%d\\n",
                 static_cast<void*>(this), additionalAnimationPasses,
                 int(additionalAnimationPasses == kMaxAdditionalAnimationPasses),
                 int(GetPresContext()->EffectCompositor()->HasPendingStyleUpdates()));
  }

'''
source = HERE / 'candidate' / ROLE
old = source.read_text()
needle = '  if (std::getenv("MOZ_ROOT_FONT_STARTUP_TRACE")) {\n    std::fprintf(stderr, "RFST document-exit set=%p post_required=%d\\n", static_cast<void*>(this), int(postTraversalRequired));\n'
assert old.count(needle) == 1
source.write_text(old.replace(needle, addition + needle))
(HERE / 'ADDITION.cpp').write_text(addition)
new_roles = {'revision': roles['revision'], 'parent': str(PARENT.relative_to(HERE.parent.parent)), 'roles': {}}
for path in roles['roles']:
    new_roles['roles'][path] = {kind + '_sha256': sha(HERE / kind / path) for kind in ['base', 'parent', 'candidate']}
(HERE / 'SOURCE-ROLES.json').write_text(json.dumps(new_roles, indent=2) + '\n')
for origin, filename in [('base', 'native.patch'), ('parent', 'PARENT-DELTA.patch')]:
    parts = []
    for path in roles['roles']:
        parts.extend(difflib.unified_diff((HERE / origin / path).read_text().splitlines(True), (HERE / 'candidate' / path).read_text().splitlines(True), fromfile='a/' + path, tofile='b/' + path))
    (HERE / filename).write_text(''.join(parts))
refs = {str(PARENT / n): {'sha256': sha(PARENT / n)} for n in ['FILES.json', 'SOURCE-ROLES.json', 'SOURCE-CONTEXT.json']}
(HERE / 'REFERENCES.json').write_text(json.dumps(refs, indent=2) + '\n')
print(json.dumps(new_roles['roles'][ROLE], indent=2))
