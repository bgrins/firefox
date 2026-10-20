import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('use python3 -I -S, without optimization')
sys.dont_write_bytecode = True

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import stat

ROOT = Path(__file__).resolve().parent

def require(value, message):
    if not value:
        raise ValueError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result

def read(name):
    return json.loads((ROOT / name).read_text(), object_pairs_hook=unique)

def authenticate(expected):
    for name in ('FILES.json', 'FREEZE.json'):
        require(stat.S_ISREG((ROOT / name).lstat().st_mode), 'nonregular seal')
    require(digest(ROOT / 'FILES.json') == expected, 'external manifest mismatch')
    files = read('FILES.json')
    require(isinstance(files, dict) and files, 'bad manifest')
    directories = set()
    for name, value in files.items():
        require(isinstance(name, str) and isinstance(value, str), 'bad row')
        path = PurePosixPath(name)
        require(str(path) == name and not path.is_absolute() and
                '..' not in path.parts and name not in ('FILES.json', 'FREEZE.json'),
                'unsafe manifest path')
        require(len(value) == 64 and all(c in '0123456789abcdef' for c in value),
                'bad digest')
        directories.update(str(parent) for parent in path.parents if str(parent) != '.')
    found = set()
    def walk(directory):
        for entry in os.scandir(directory):
            path = Path(entry.path)
            relative = path.relative_to(ROOT).as_posix()
            mode = entry.stat(follow_symlinks=False).st_mode
            if stat.S_ISDIR(mode):
                require(relative in directories, 'unexpected directory: ' + relative)
                walk(path)
            else:
                require(stat.S_ISREG(mode), 'nonregular input: ' + relative)
                if relative in ('FILES.json', 'FREEZE.json'):
                    continue
                require(relative in files, 'unexpected file: ' + relative)
                require(digest(path) == files[relative], 'input hash mismatch: ' + relative)
                found.add(relative)
    walk(ROOT)
    require(found == set(files), 'missing input')
    freeze = read('FREEZE.json')
    require(freeze['FILES_sha256'] == expected and
            freeze['check_sha256'] == digest(ROOT / 'check.py'), 'seal mismatch')
    return files

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--files-sha256', required=True)
    args = parser.parse_args()
    files = authenticate(args.files_sha256)
    spec = importlib.util.spec_from_file_location('bound_source_extract', ROOT / 'extract.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    bound = module.bindings()
    require(bound == read('BINDINGS.json') and len(bound) == 51, 'source binding mismatch')
    for row in read('SOURCE-PINS.json'):
        require(digest(ROOT / row['path']) == row['sha256'] and
                (ROOT / row['path']).stat().st_size == row['bytes'], 'source pin mismatch')
    for row in read('SELECTED-TRANSFER.json'):
        left = module.selected((ROOT / row['left']).read_text(), row['anchor'])[2]
        right = module.selected((ROOT / row['right']).read_text(), row['anchor'])[2]
        require(hashlib.sha256(left.encode()).hexdigest() == row['left_sha256'] and
                hashlib.sha256(right.encode()).hexdigest() == row['right_sha256'] and
                (left == right) == row['equal'], 'transfer mismatch')
    def body(anchor):
        matches = [row['text'] for row in bound if row['anchor'] == anchor]
        require(len(matches) == 1, 'ambiguous body')
        return matches[0]
    destroy = body('void nsIFrame::Destroy(DestroyContext& aContext)')
    first = destroy.index('if (IsPrimaryFrame())')
    second = destroy.index('if (IsPrimaryFrame())', first + 1)
    require(destroy.count('if (IsPrimaryFrame())') == 2 and
            destroy.index('SVGObserverUtils::InvalidateDirectRenderingObservers') < first <
            destroy.index('ps->NotifyDestroyingFrame(this)') <
            destroy.index('ps->ClearFrameRefs(this)') < second <
            destroy.index('mContent->SetPrimaryFrame(nullptr)') <
            destroy.index('RemoveAllProperties();') < destroy.index('this->~nsIFrame()'),
            'destruction order changed')
    notify = body('void PresShell::NotifyDestroyingFrame(nsIFrame* aFrame)')
    require(notify.index('RemoveDisplayItemDataForDeletion') <
            notify.index('if (!mIgnoreFrameDestruction)') <
            notify.index('aFrame->RemoveAllProperties()'), 'early cleanup order changed')
    remove = body('void RemoveAll(const nsIFrame* aFrame)')
    require(remove.index('std::move(mProperties)') < remove.index('prop.DestroyValueFor(aFrame)') <
            remove.index('MOZ_ASSERT(mProperties.IsEmpty()'), 'property dispatch changed')
    cancel = body('void ManagedPostRefreshObserver::Cancel()')
    leave = body('void EventStateManager::MaybeLeavePendingLink(bool aWasCanceled)')
    require('action(true)' in cancel and 'if (aWasCanceled ||' in leave and
            leave.index('return;') < leave.index('element->LeaveLink('), 'cancel guard changed')
    require('obs->Cancel()' in body('void nsPresContext::RegisterManagedPostRefreshObserver('),
            'immediate cancel branch missing')
    svg = body('void SVGTextPathObserver::OnRenderingChange()')
    require(all(x in svg for x in ['AnyOuterSVGIsCallingReflowSVG',
            'NS_STATE_SVG_TEXT_IN_REFLOW', 'NS_STATE_SVG_TEXT_CORRESPONDENCE_DIRTY',
            'text->ReflowSVGNonDisplayText()', 'text->ReflowSVG()', 'text->ScheduleReflowSVG()']),
            'SVG dispatch branch changed')
    require(len(read('CALLBACK-ROSTER.json')['rows']) == 26, 'roster changed')
    require(digest(ROOT / 'PREDECESSOR-FILES.json') ==
            '2bd9d96917a87bacaa2c742d8b61b9a60fe511e338d81e481582b22b90291156',
            'predecessor manifest changed')
    require(read('ENTRY.json')['sha256'] == digest(ROOT / 'source/nsIFrame.frozen.cpp'),
            'entry source changed')
    authenticate(args.files_sha256)
    print(json.dumps({'result': 'PASS', 'inputs': len(files), 'bound_definitions': len(bound),
                      'selected_transfers': 12, 'top_level_roster_rows': 26,
                      'scope': 'source identity/order only; semantic/lifetime frontier remains open'}))

if __name__ == '__main__':
    main()
