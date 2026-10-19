import hashlib,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'source/providers/intl/hyphenation/glue/nsHyphenationManager.cpp'
HELPER=ROOT/'native/extract-full.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='c77b8767420e7bae3d2561653cd6290992ebf373de7d367f73127dc2bf59c61f'
assert hashlib.sha256(HELPER.read_bytes()).hexdigest()=='b70e5480ae6cd926ae88cfca50abaf53cc4b6549c6ba9c7e780f9f7936a0060f'
helper=runpy.run_path(str(HELPER))
markers=[
'already_AddRefed<nsHyphenator> nsHyphenationManager::GetHyphenator(',
'nsHyphenationManager::Observe(',
'nsHyphenationManager::nsHyphenationManager()',
'void nsHyphenationManager::LoadPatternList()',
'static already_AddRefed<nsAtom> LocaleAtomFromPath(',
'void nsHyphenationManager::LoadPatternListFromOmnijar(',
'void nsHyphenationManager::LoadPatternListFromDir(',
'void nsHyphenationManager::LoadAliases()',
'void nsHyphenationManager::ShareHyphDictToProcess(']
bodies={marker:helper['full'](SOURCE,marker) for marker in markers}
get=bodies[markers[0]]
phases=['mHyphenators.Get(aLocale','mPatternFiles.Get(aLocale)','mHyphAliases.Get(aLocale)','mHyphenators.Get(alias','mPatternFiles.Get(alias)','aLocale = alias','StringEndsWith(localeStr','localeStr.RFindChar','if (i > 1)','GetHyphenator(fuzzyLocale)','hyphCapPref.Append','new nsHyphenator(uri','hyph->IsValid()','mHyphenators.InsertOrUpdate','mPatternFiles.Remove(aLocale)']
positions=[get.index(phase) for phase in phases]
assert positions==sorted(positions)
assert 'mHyphenators.Clear()' in bodies[markers[1]]
reload=bodies[markers[3]]
phases=['mPatternFiles.Clear()','mHyphenators.Clear()','Omnijar::GRE','Omnijar::APP','NS_GRE_DIR','NS_XPCOM_CURRENT_PROCESS_DIR','NS_APP_USER_PROFILE_LOCAL_50_DIR']
assert [reload.index(phase) for phase in phases]==sorted(reload.index(phase) for phase in phases)
assert 'ToLowerCase(alias)' in bodies[markers[7]] and 'ToLowerCase(value)' in bodies[markers[7]]
OUT=ROOT/'development-build/manager-binding';OUT.mkdir(parents=True,exist_ok=True)
(OUT/'DEFINITIONS.json').write_text(json.dumps(bodies,indent=2)+'\n')
result={'records':helper['records'],'status':'nine complete source definitions retained; two compiled in manager bridge, seven static bindings; resource discovery/IPC/validity and native string/atom/refcount providers remain open'}
(OUT/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'definitions':len(helper['records']),'status':result['status']}))
