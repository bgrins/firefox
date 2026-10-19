import json
import re
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
helper=runpy.run_path(str(ROOT/'native/extract-full.py'))
full=helper['full'];source=ROOT/'source/candidate/layout/generic/nsTextFrame.cpp'
bits=(ROOT/'source/providers/layout/generic/nsFrameStateBits.h').read_text()
constants=[]
for name in ['TEXT_HAS_FONT_INFLATION','TEXT_IN_TEXTRUN_USER_DATA','TEXT_IN_UNINFLATED_TEXTRUN_USER_DATA']:
    bit=re.search(r'FRAME_STATE_BIT\(Text, (\d+), '+name+r'\)',bits)[1]
    constants.append(f'constexpr nsFrameState {name}=uint64_t(1)<<{bit};')
structures=full(source,'struct TextRunMappedFlow {',True)+'\n'+full(source,'struct TextRunUserData {',True)
structures+='\nstruct ComplexTextRunUserData:TextRunUserData{};\nstatic void DestroyUserData(TextRunUserData*p){::operator delete(p);}\nstatic void DestroyComplexUserData(ComplexTextRunUserData*p){::operator delete(p);}\n'
functions='\n'.join(full(source,name)for name in ['static void DestroyTextRunUserData(', 'static TextRunMappedFlow* GetMappedFlows(', 'static nsTextFrame* GetFrameForSimpleFlow(', 'bool nsTextFrame::RemoveTextRun(', 'static bool ClearAllTextRunReferences(', 'static void UnhookTextRunFromFrames(', 'void nsTextFrame::ClearTextRun('])
functions=functions.replace('  MOZ_ASSERT(\n      static_cast<TextRunUserData*>(aTextRun->GetUserData())->mMappedFlows ==\n          flows,\n      "GetMappedFlows should return the same pointer as mMappedFlows.");','')
OUT=ROOT/'development-build/full'
(OUT/'invalidation.cpp').write_text((ROOT/'native/invalidation-facade.hpp').read_text()+'\n'+'\n'.join(constants)+'\n'+structures+'\n'+functions+'\n'+(ROOT/'native/invalidation-runner.cpp').read_text())
(OUT/'invalidation-extraction.json').write_text(json.dumps({'functions':helper['records'],'adaptation':'The DEBUG-only mMappedFlows assertion is elided in this release-layout harness; observer object fields and allocation/refcount APIs are explicit facades.'},indent=2)+'\n')
