from pathlib import Path
import re
from generate import ROOT
import importlib.util

def rust_source():
    spec=importlib.util.spec_from_file_location('source_extract',ROOT/'source_extract.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    rows={r['name']:r['body'] for r in m.selected('combined')}
    source=(ROOT/'providers/servo__components__style__logical_geometry.rs').read_text()
    region=source[source.index('bitflags!('):source.index('impl WritingMode {')]
    constants=re.findall(r'const ([A-Z_]+) = ([^;]+);',region)
    if len(constants)!=13:raise RuntimeError(('constant roster',len(constants)))
    constants='\n'.join('const '+name+':Self=Self('+body+');' for name,body in constants)
    template=(ROOT/'native/mode_provider.rs').read_text()
    return template.replace('@@CONSTANTS@@',constants).replace('@@CONSTRUCTOR@@',rows['provider_mode'])
