from pathlib import Path
import difflib
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PARENT = ROOT / 'artifacts/css-root-font-cancellation-selective-handoff-fix-v1'
SAVED = ROOT / 'artifacts/css-root-font-simultaneous-startup-source-review-v1/source'
REV = 'e86b64866cdc5e2260ba9be08c45756fd96e21bb'
roles = json.loads((PARENT / 'SOURCE-ROLES.json').read_text())['roles']
paths = list(roles) + ['servo/components/style/matching.rs', 'servo/components/style/values/specified/length.rs', 'layout/style/GeckoBindings.cpp', 'dom/animation/KeyframeEffect.cpp']
texts = {}
edits = []
for path in paths:
    base = (PARENT / 'base' / path if path in roles else SAVED / path).read_bytes()
    parent = (PARENT / 'candidate' / path).read_bytes() if path in roles else base
    assert base == subprocess.check_output(['git', 'show', f'{REV}:{path}'], cwd=ROOT)
    if path in roles:
        assert hashlib.sha256(parent).hexdigest() == roles[path]['candidate_sha256']
    for name, data in [('base', base), ('parent', parent)]:
        dest = HERE / name / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    texts[path] = parent.decode()

def replace(path, old, new):
    assert texts[path].count(old) == 1, (path, old, texts[path].count(old))
    texts[path] = texts[path].replace(old, new)
    edits.append({'path': path, 'old': old, 'new': new})

def rust(indent, message, args):
    arguments = ',\n'.join(indent + '        ' + arg for arg in args.split(', '))
    return f'{indent}if std::env::var_os("MOZ_ROOT_FONT_STARTUP_TRACE").is_some() {{\n{indent}    eprintln!(\n{indent}        "RFST {message} thread={{:?}}",\n{arguments},\n{indent}        std::thread::current().id()\n{indent}    );\n{indent}}}\n'

p = 'servo/components/style/matching.rs'
replace(p, 'use crate::dom::TElement;\n#[cfg(feature = "servo")]\nuse crate::dom::TNode;', 'use crate::dom::{TElement, TNode};')
old = '        if context.shared.traversal_flags.for_animation_only() && old_values.is_some() {\n'
replace(p, old, old + rust('            ', 'skip-existing-animation node={:#x} flags={:?}', 'self.as_node().opaque().0, context.shared.traversal_flags'))
old = '        if !tasks.is_empty() {\n'
replace(p, old, rust('        ', 'tasks node={:#x} flags={:?} mask={:#x}', 'self.as_node().opaque().0, context.shared.traversal_flags, tasks.bits()') + old)
old = '                device.set_root_font_size(new_primary_style.effective_zoom.unzoom(size.px()));'
replace(p, old, '                let root_size = new_primary_style.effective_zoom.unzoom(size.px());\n                device.set_root_font_size(root_size);\n' + rust('                ', 'root-published node={:#x} flags={:?} px={} old_computed_px={:?} device={:p}', 'self.as_node().opaque().0, context.shared.traversal_flags, root_size, old_font_size.map(|size| size.computed_size().px()), device').rstrip())
old = "        // Don't accumulate damage if we're in the final animation traversal.\n"
replace(p, old, rust('        ', 'finish node={:#x} flags={:?} hint={:?}', 'self.as_node().opaque().0, context.shared.traversal_flags, child_restyle_hint') + old)

p = 'servo/components/style/traversal.rs'
old = '    let restyle_kind = data.restyle_kind(context.shared, has_animations);\n'
replace(p, old, old + rust('    ', 'restyle node={:#x} flags={:?} hint={:?} kind={:?} admitted_animation={}', 'element.as_node().opaque().0, flags, data.hint, restyle_kind, has_animations'))

p = 'servo/components/style/gecko/traversal.rs'
old = '            if self.shared.traversal_flags.for_animation_only()\n'
replace(p, old, rust('            ', 'returned node={:#x} flags={:?} hint={:?}', 'el.as_node().opaque().0, self.shared.traversal_flags, child_hint') + old)
old = '                self.normal_descendant_restyle.store(true, Ordering::Relaxed);\n'
replace(p, old, old + rust('                ', 'signal node={:#x} flags={:?}', 'el.as_node().opaque().0, self.shared.traversal_flags'))

p = 'servo/ports/geckolib/glue.rs'
old = '    if !token.should_traverse() {\n'
replace(p, old, '    let should_traverse = token.should_traverse();\n' + rust('    ', 'entry node={:#x} flags={:?} should={}', 'element.as_node().opaque().0, traversal_flags, should_traverse') + '    if !should_traverse {\n')
old = '    if traversal.needs_normal_descendant_restyle() {\n'
replace(p, old, '    let normal_descendant_restyle = traversal.needs_normal_descendant_restyle();\n' + rust('    ', 'joined node={:#x} flags={:?} signal={}', 'root.as_node().opaque().0, traversal_flags, normal_descendant_restyle') + '    if normal_descendant_restyle {\n')
old = '            has_styled_child = true;\n'
replace(p, old, old + rust('            ', 'seed root={:#x} child={:#x} hint={:?}', 'root.as_node().opaque().0, child.as_node().opaque().0, child_data.hint'))
old = '            unsafe { root.set_dirty_descendants() };\n'
replace(p, old, old + rust('            ', 'normal-dirty node={:#x}', 'root.as_node().opaque().0'))
old = '                    seen.insert(property);\n\n                    animation_values.push'
new = '                    seen.insert(property);\n\n                    if std::env::var_os("MOZ_ROOT_FONT_STARTUP_TRACE").is_some() {\n                        if let Some(AnimationValue::FontSize(size)) = value.as_ref() {\n                            eprintln!(\n                                "RFST converted-font node={:#x} keyframe={} px={} thread={:?}",\n                                element.as_node().opaque().0,\n                                index,\n                                size.px(),\n                                std::thread::current().id()\n                            );\n                        }\n                    }\n\n                    animation_values.push'
replace(p, old, new)

p = 'servo/components/style/values/specified/length.rs'
old = '                (reference_size, length)\n            },\n            LengthUnit::Rlh =>'
replace(p, old, rust('                ', 'rem-basis root_context={} media={} reference_px={} factor={} device={:p}', 'context.builder.is_root_element, context.in_media_query, reference_size.px(), length, context.device()') + old)

def cpp(message, args, indent='  '):
    arguments = ',\n'.join(indent + '               ' + arg for arg in args.split(', '))
    return f'{indent}if (std::getenv("MOZ_ROOT_FONT_STARTUP_TRACE")) {{\n{indent}  std::fprintf(stderr, "RFST {message}\\n",\n{arguments});\n{indent}}}\n'

p = 'layout/style/GeckoBindings.cpp'
replace(p, '#include "mozilla/GeckoBindings.h"', '#include "mozilla/GeckoBindings.h"\n\n#include <cstdio>\n#include <cstdlib>')
old = '      AnimationUtils::GetElementPseudoPair(aElement);\n\n  // Handle timeline scopes first, because our own scroll/view-linked animations\n'
replace(p, old, '      AnimationUtils::GetElementPseudoPair(aElement);\n' + cpp('delivery input_node=%p target_node=%p pseudo=%u mask=%u style=%p', 'static_cast<const void*>(static_cast<const nsINode*>(aElement)), static_cast<const void*>(static_cast<const nsINode*>(element)), unsigned(pseudoRequest.mType), unsigned(aTasks), static_cast<const void*>(aComputedData)') + '\n  // Handle timeline scopes first, because our own scroll/view-linked animations\n')
old = '  if (aTasks & UpdateAnimationsTasks::EffectProperties) {\n'
replace(p, old, old + cpp('effect-properties target_node=%p pseudo=%u style=%p', 'static_cast<const void*>(static_cast<const nsINode*>(element)), unsigned(pseudoRequest.mType), static_cast<const void*>(aComputedData)', '    '))

p = 'dom/animation/KeyframeEffect.cpp'
replace(p, '#include "mozilla/dom/KeyframeEffect.h"', '#include "mozilla/dom/KeyframeEffect.h"\n\n#include <cstdio>\n#include <cstdlib>')
old = '  bool referencesAttributes = false;\n  nsTArray<AnimationProperty> properties = BuildProperties('
replace(p, old, cpp('build-properties effect=%p target_node=%p pseudo=%u style=%p', 'static_cast<const void*>(this), static_cast<const void*>(static_cast<const nsINode*>(mTarget.mElement.get())), unsigned(mTarget.mPseudoRequest.mType), static_cast<const void*>(aStyle)') + old)
old = '  mReferencesAttributes = referencesAttributes;\n\n  if (!propertiesChanged) {'
replace(p, old, '  mReferencesAttributes = referencesAttributes;\n\n' + cpp('built-properties effect=%p changed=%u base_changed=%u count=%zu', 'static_cast<const void*>(this), unsigned(propertiesChanged), unsigned(baseStylesChanged), size_t(properties.Length())') + '  if (!propertiesChanged) {')

for path, text in texts.items():
    dest = HERE / 'candidate' / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text)
for source, name in [('parent', 'INSTRUMENTATION.patch'), ('base', 'native.patch')]:
    patch = ''
    for path in paths:
        patch += ''.join(difflib.unified_diff((HERE / source / path).read_text().splitlines(True), texts[path].splitlines(True), fromfile='a/' + path, tofile='b/' + path))
    (HERE / name).write_text(patch)
(HERE / 'EDITS.json').write_text(json.dumps(edits, indent=2) + '\n')
(HERE / 'SOURCE-ROLES.json').write_text(json.dumps({'revision': REV, 'parent': str(PARENT.relative_to(ROOT)), 'roles': {p: {k + '_sha256': hashlib.sha256((HERE / k / p).read_bytes()).hexdigest() for k in ['base', 'parent', 'candidate']} for p in paths}}, indent=2) + '\n')
print(json.dumps({'roles': len(paths), 'replacements': len(edits)}))
