import json
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
helper=runpy.run_path(str(ROOT/'native/extract-full.py'))
source=ROOT/'source/providers/intl/hyphenation/glue/nsHyphenationManager.cpp'
functions='\n'.join(helper['full'](source,name) for name in ['already_AddRefed<nsHyphenator> nsHyphenationManager::GetHyphenator(', 'static already_AddRefed<nsAtom> LocaleAtomFromPath('])
OUT=ROOT/'development-build/full'
(OUT/'manager.cpp').write_text((ROOT/'native/manager-facade.hpp').read_text()+'\n'+functions+'\n'+(ROOT/'native/manager-runner.cpp').read_text())
(OUT/'manager-extraction.json').write_text(json.dumps(helper['records'],indent=2)+'\n')
