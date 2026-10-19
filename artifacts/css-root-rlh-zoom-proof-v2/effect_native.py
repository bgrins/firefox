import json
import os
from pathlib import Path
import subprocess
import sys
import effect_cases
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / 'baseline'))
import cases
import extract

VARIANTS = [('original', 'original', 0), ('candidate', 'candidate', 0),
    ('drop-relative', 'candidate', 1), ('drop-normal', 'candidate', 2), ('clear-incoming', 'candidate', 3)]

def replace_once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)

def driver():
    runner = (BASE / 'baseline/native/runner.rs').read_text()
    runner = replace_once(runner, 'builder.flags.set(0);', 'builder.flags.set(u(&t,21));')
    old = 'for_non_inherited_property:true,rule_cache_conditions:RefCell::new(Conditions::default())};\n                let font_base='
    new = 'for_non_inherited_property:true,rule_cache_conditions:RefCell::new(Conditions{font:if u(&t,22)!=0{Some(n(&t,23))}else{None},lh:if u(&t,24)!=0{Some(n(&t,25))}else{None}})};\n                let font_base='
    runner = replace_once(runner, old, new)
    runner = replace_once(runner, '\\"flags\\":{},\\"font_dependency', '\\"flags\\":{},\\"font_present\\":{},\\"lh_present\\":{},\\"font_dependency')
    runner = replace_once(runner, 'builder.flags.get(),cond.font.map', 'builder.flags.get(),cond.font.is_some(),cond.lh.is_some(),cond.font.map')
    return runner

def run(out):
    out.mkdir(parents=True, exist_ok=False)
    events = effect_cases.generate()
    protocol = effect_cases.protocol(events, cases.protocol)
    (out / 'events.json').write_text(json.dumps(events, indent=2) + '\n')
    (out / 'input.txt').write_text(protocol)
    commands = []
    for name, source, mutation in VARIANTS:
        folder = out / name
        extract.generate(folder, source)
        raw = (folder / 'style.inc').read_text()
        marker = 'context\n            .builder\n            .add_flags(ComputedValueFlags::USES_FONT_OR_WM_RELATIVE_UNITS);'
        if mutation == 1:
            raw = replace_once(raw, marker, 'context.builder.add_flags(0);')
        elif mutation == 2:
            raw = replace_once(raw, 'self.add_flags(flag);', 'self.add_flags(0);')
        elif mutation == 3:
            raw = replace_once(raw, marker, 'context.builder.flags.set(0);\n        ' + marker)
        (folder / 'style.inc').write_text(raw)
        style = (BASE / 'baseline/native/style.rs').read_text()
        source_path = BASE / 'baseline/source/servo/components/style/properties/properties.mako.rs'
        helper = extract.body(source_path.read_text(), 'pub fn add_flags(')
        adapted = helper.replace('flag: ComputedValueFlags', 'flag: u32').replace('self.flags()', 'self.flags.get()')
        style = replace_once(style, 'fn add_flags(&self,f:u32){self.flags.set(self.flags.get()|f)}', adapted)
        (folder / 'builder-effect-extraction.json').write_text(json.dumps(dict(
            path='baseline/source/servo/components/style/properties/properties.mako.rs',
            marker='pub fn add_flags(', text=helper, adapted=adapted,
            adaptations=['Symbolic three-flag u32 encoding replaces generated bitflags type',
                         'Actual getter self.flags() inlined to self.flags.get()']), indent=2) + '\n')
        (folder / 'style.rs').write_text(style)
        (folder / 'runner.rs').write_text(driver())
        cpp = folder / 'provider.o'
        binary = folder / 'native'
        env = dict(os.environ, RLH_EXTRACTED=str((folder / 'style.inc').resolve()), RLH_MUTANT='0')
        for command in [
            ['clang++', '-std=c++17', '-O0', '-I', str(folder), '-c', str(BASE / 'baseline/native/provider.cpp'), '-o', str(cpp)],
            ['rustc', '--edition=2021', str(folder / 'style.rs'), '-C', 'link-arg=' + str(cpp.resolve()), '-C', 'link-arg=-lc++', '-o', str(binary)],
        ]:
            result = subprocess.run(command, env=env, text=True, capture_output=True)
            commands.append(dict(command=command, variant=name, exit=result.returncode, stdout=result.stdout, stderr=result.stderr))
            (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
            assert result.returncode == 0, result.stderr
        result = subprocess.run([str(binary)], input=protocol, text=True, capture_output=True)
        (folder / 'raw.jsonl').write_text(result.stdout)
        (folder / 'stderr.txt').write_text(result.stderr)
        assert result.returncode == 0, result.stderr
    return events
