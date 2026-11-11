#!/usr/bin/env python3
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    out = parser.parse_args().out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    target = out / 'candidate'
    shutil.copytree(HERE / 'basis', target)
    cpp = target / 'dom/base/nsDOMWindowUtils.cpp'
    text = cpp.read_text()
    anchor = '#include "mozilla/EventStateManager.h"'
    text = text.replace(anchor, '#include "mozilla/EffectCompositor.h"\n#include "mozilla/EffectSet.h"\n' + anchor)
    text = text.replace('#include "mozilla/Logging.h"', '#include "mozilla/JSONStringWriteFuncs.h"\n#include "mozilla/Logging.h"')
    text = text.replace('#include "mozilla/dom/MouseEventBinding.h"', '#include "mozilla/dom/KeyframeEffect.h"\n#include "mozilla/dom/MouseEventBinding.h"')
    anchor = 'NS_IMETHODIMP\nnsDOMWindowUtils::GetUnanimatedComputedStyle('
    assert text.count(anchor) == 1
    cpp.write_text(text.replace(anchor, (HERE / 'driver.cpp').read_text() + '\n' + anchor))
    header = target / 'dom/animation/Animation.h'
    text = header.read_text().replace('class nsCSSPropertyIDSet;', 'class nsCSSPropertyIDSet;\nclass nsDOMWindowUtils;')
    text = text.replace('friend class AsyncFinishNotification;', 'friend class AsyncFinishNotification;\n  friend class ::nsDOMWindowUtils;')
    header.write_text(text)
    idl = target / 'dom/interfaces/base/nsIDOMWindowUtils.idl'
    text = idl.read_text()
    anchor = '  AString getUnanimatedComputedStyle('
    pos = text.index('  /**\n   * Returns the computed style for the specified property')
    declaration = '''  // Temporary diagnostic for request-local missing-pseudo composition.
  AString getMissingPseudoAnimationValuesForTesting(in Element aElement,
                                                    in AString aPseudoElement,
                                                    in AString aProperty,
                                                    in long aFlushType);

'''
    idl.write_text(text[:pos] + declaration + text[pos:])
    manifest = target / 'dom/base/test/mochitest.toml'
    text = manifest.read_text()
    anchor = '["test_domwindowutils.html"]'
    assert text.count(anchor) == 1
    manifest.write_text(text.replace(anchor, '["test_missing_pseudo_animation_query.html"]\nprefs = [\n  "layout.css.scroll-driven-animations.enabled=true",\n  "layout.css.typed-om.enabled=true",\n]\n\n' + anchor))
    test = target / 'dom/base/test/test_missing_pseudo_animation_query.html'
    test.write_bytes((HERE / 'test.html').read_bytes())
    formatting = []
    for name in ['dom/base/nsDOMWindowUtils.cpp', 'dom/animation/Animation.h']:
        path = target / name
        command = ['/Users/bgrins/.mozbuild/clang-tools/clang-tidy/bin/clang-format', '--style=file', '--assume-filename=' + str(ROOT / name)]
        data = subprocess.check_output(command, input=path.read_bytes())
        assert subprocess.check_output(command, input=data) == data
        path.write_bytes(data)
        formatting.append({'command': command, 'sha256': hashlib.sha256(data).hexdigest()})
    (out / 'FORMAT.json').write_text(json.dumps(formatting, indent=2) + '\n')
    patch = []
    for f in sorted(target.rglob('*')):
        if not f.is_file():
            continue
        name = str(f.relative_to(target))
        base = HERE / 'basis' / name
        before = base.read_text() if base.exists() else ''
        after = f.read_text()
        if before != after:
            patch.append('diff --git a/' + name + ' b/' + name + '\n')
            patch.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='a/' + name if base.exists() else '/dev/null', tofile='b/' + name))
    (out / 'driver.patch').write_text(''.join(patch))


if __name__ == '__main__':
    main()
