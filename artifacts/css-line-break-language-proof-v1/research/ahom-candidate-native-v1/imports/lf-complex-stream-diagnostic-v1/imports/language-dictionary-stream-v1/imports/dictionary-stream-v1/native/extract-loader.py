import hashlib,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PINS={"source/providers/intl/hyphenation/glue/nsHyphenator.cpp":"4a158c0a65fb328f64fe1f0bfe1c4666e0d59c5f31a30cec69562a8226899145","source/providers/intl/hyphenation/glue/nsHyphenator.h":"60ea055cc010ff0f86dda72c26461ffebd183f59063d17d994ac20371758a4d2","source/providers/intl/hyphenation/glue/nsHyphenationManager.cpp":"c77b8767420e7bae3d2561653cd6290992ebf373de7d367f73127dc2bf59c61f","native/extract-full.py":"b70e5480ae6cd926ae88cfca50abaf53cc4b6549c6ba9c7e780f9f7936a0060f"}
for name,digest in PINS.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
helper=runpy.run_path(str(ROOT/'native/extract-full.py'));full=helper['full']
cpp=ROOT/'source/providers/intl/hyphenation/glue/nsHyphenator.cpp';header=cpp.with_suffix('.h')
base=(ROOT/'native/manager-facade.hpp').read_text();prefix=base[:base.index('struct nsIURI{')]
prefix=prefix.replace('void Cut(size_t i,size_t n)', 'void Insert(const char*s,size_t i){value.insert(i,s);}void Cut(size_t i,size_t n)')
manager=base[base.index('struct nsHyphenationManager{'):]
klass=full(header,'class nsHyphenator {',True).replace(' private:',' public:').replace(' public:', ' public:\n nsIURI* uri;',1)
parts=[prefix,(ROOT/'native/loader-facade.hpp').read_text(),'class nsAString;template<class T>class nsTArray;',full(header,'namespace std {'),klass,manager,full(cpp,'namespace std {')]
for marker in ['static const uint8_t* GetItemPtrFromJarURI(', 'static ipc::ReadOnlySharedMemoryMapping GetHyphDictFromParent(', 'static ipc::ReadOnlySharedMemoryHandle CopyToShmem(', 'static ipc::ReadOnlySharedMemoryHandle LoadFromURI(', 'nsHyphenator::nsHyphenator(', 'bool nsHyphenator::IsValid()', 'ipc::ReadOnlySharedMemoryHandle nsHyphenator::CloneHandle()']:
 body=full(cpp,marker)
 if marker=='nsHyphenator::nsHyphenator(':
  old='mHyphenateCapitalized(aHyphenateCapitalized) {';assert body.count(old)==1
  body=body.replace(old,old+'\n uri=aURI;loads.push_back(aURI->path);')
 parts.append(body)
source=ROOT/'source/providers/intl/hyphenation/glue/nsHyphenationManager.cpp'
for marker in ['already_AddRefed<nsHyphenator> nsHyphenationManager::GetHyphenator(', 'static already_AddRefed<nsAtom> LocaleAtomFromPath(']:parts.append(full(source,marker))
runner=(ROOT/'native/manager-runner.cpp').read_text().replace('int main(){','int main(int argc,char**argv){\n if(argc!=2)return 3;std::ifstream dict(argv[1],std::ios::binary);gDictionaryBytes.assign(std::istreambuf_iterator<char>(dict),{});if(!mapped_hyph_is_valid_hyphenator(gDictionaryBytes.data(),gDictionaryBytes.size()))return 4;').replace('result->capitalized','result->mHyphenateCapitalized')
runner=runner.replace('std::cout<<id<<" GET "', 'if(result){assert(result->mDict.is<Span<const uint8_t>>());auto&span=result->mDict.as<Span<const uint8_t>>();assert(span.data()==result->uri->data.data());assert(span.size()==result->uri->data.size());}std::cout<<id<<" GET "')
parts.append(runner)
out=ROOT/'development-build/loader';out.mkdir(exist_ok=True,parents=True)
(out/'manager-loader.cpp').write_text('\n'.join(parts))
(out/'EXTRACTION.json').write_text(json.dumps({'records':helper['records'],'instrumentation':['class private exposed; ghost URI field added','constructor records URI/load attempt before native body','runner initializes actual dictionary bytes and reads native capitalized member'],'provider_limits':['XPCOM strings/refcount/URI/jar/stream/shared-memory facades','child IPC deliberately unavailable','fixed manager inputs exercise uncompressed jar resources only; other branches compiled without runtime claim']},indent=2)+'\n')
print(len(helper['records']),'complete extraction records')
