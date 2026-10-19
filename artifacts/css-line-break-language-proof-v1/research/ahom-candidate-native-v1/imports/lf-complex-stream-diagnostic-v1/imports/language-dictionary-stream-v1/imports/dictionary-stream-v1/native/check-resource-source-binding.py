import hashlib,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PINS={'source/providers/intl/hyphenation/glue/nsHyphenator.cpp': '4a158c0a65fb328f64fe1f0bfe1c4666e0d59c5f31a30cec69562a8226899145', 'source/providers/intl/hyphenation/glue/nsHyphenator.h': '60ea055cc010ff0f86dda72c26461ffebd183f59063d17d994ac20371758a4d2', 'native/extract-full.py': 'b70e5480ae6cd926ae88cfca50abaf53cc4b6549c6ba9c7e780f9f7936a0060f'}
for name,digest in PINS.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
helper=runpy.run_path(str(ROOT/'native/extract-full.py'))
source=ROOT/'source/providers/intl/hyphenation/glue/nsHyphenator.cpp'
markers=['static const uint8_t* GetItemPtrFromJarURI(',
'static ipc::ReadOnlySharedMemoryMapping GetHyphDictFromParent(',
'static ipc::ReadOnlySharedMemoryHandle CopyToShmem(',
'static ipc::ReadOnlySharedMemoryHandle LoadFromURI(',
'nsHyphenator::nsHyphenator(',
'bool nsHyphenator::IsValid()',
'ipc::ReadOnlySharedMemoryHandle nsHyphenator::CloneHandle()']
bodies={marker:helper['full'](source,marker) for marker in markers}
bodies['class nsHyphenator']=helper['full'](ROOT/'source/providers/intl/hyphenation/glue/nsHyphenator.h','class nsHyphenator {',True)
constructor=bodies[markers[4]]
for phrase in ['if (!precompiled && !XRE_IsParentProcess())','GetHyphDictFromParent(aURI)','GetItemPtrFromJarURI(jar, &length)','mapped_hyph_is_valid_hyphenator(ptr, length)','LoadFromURI(aURI, precompiled)','mapped_hyph_load_dictionary(path.get())','mapped_hyph_compile_file(path.get(), false)']:assert phrase in constructor,phrase
assert 'SendGetHyphDict(aURI, &handle)' in bodies[markers[1]]
assert 'mDict.is<ipc::ReadOnlySharedMemoryHandle>()' in bodies[markers[6]]
OUT=ROOT/'development-build/resource-binding';OUT.mkdir(parents=True,exist_ok=True)
(OUT/'DEFINITIONS.json').write_text(json.dumps(bodies,indent=2)+'\n')
(OUT/'RESULT.json').write_text(json.dumps({'records':helper['records'],'status':'eight complete additional loader/storage definitions retained as static evidence; no native constructor execution or parent/child identity proof claimed'},indent=2)+'\n')
print(len(helper['records']),'complete static definitions')
