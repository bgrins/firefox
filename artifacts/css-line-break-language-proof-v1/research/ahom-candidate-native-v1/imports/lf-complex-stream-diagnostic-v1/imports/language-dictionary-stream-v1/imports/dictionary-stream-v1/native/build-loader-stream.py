import hashlib,json,runpy,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
helper=runpy.run_path(str(ROOT/'native/extract-full.py'));full=helper['full']
OUT=ROOT/'development-build/loader-stream';OUT.mkdir(exist_ok=True,parents=True)
adaptations=[]
def replace(text,old,new,label):
 assert text.count(old)==1,(label,text.count(old))
 adaptations.append({'label':label,'before':old,'after':new})
 return text.replace(old,new)
base=(ROOT/'native/manager-facade.hpp').read_text()
strings=base[base.index('struct String{'):base.index('template<class T>struct already_AddRefed')]
strings=strings.replace('size_t Length()const', 'operator const std::string&()const{return value;}void Insert(const char*s,size_t i){value.insert(i,s);}void Append(uint32_t c){value.push_back(char(c));}const char*BeginReading()const{return value.data();}uint8_t operator[](size_t i)const{return uint8_t(value.at(i));}size_t Length()const')
tables=base[base.index('template<class T>RefPtr<T>*getter_AddRefs'):base.index('struct nsIURI{')]
loader=(ROOT/'native/loader-facade.hpp').read_text();a=loader.index('template<class T>struct Span{');b=loader.index('template<class...T>struct Overload',a);loader=loader[:a]+loader[b:]
loader=loader.replace('uri.p','uri.get()')
for line in ['#define MOZ_ASSERT(...) ((void)0)','#define MOZ_ASSERT_UNREACHABLE(...) ((void)0)','#define NS_ASSERTION(...) ((void)0)','#define NS_FAILED(value) ((value)!=0)','#define NS_SUCCEEDED(value) ((value)==0)']:
 loader=loader.replace(line,'')
cpp=ROOT/'source/providers/intl/hyphenation/glue/nsHyphenator.cpp';header=cpp.with_suffix('.h')
klass=full(header,'class nsHyphenator {',True).replace(' private:',' public:').replace(' public:',' public:\n nsIURI*uri;',1)
manager=base[base.index('struct nsHyphenationManager{'):].replace(' Table<nsHyphenator>', ' static nsHyphenationManager*Instance(){static nsHyphenationManager manager;return &manager;}\n Table<nsHyphenator>',1)
parts=[tables,loader,full(header,'namespace std {'),klass,manager,full(cpp,'namespace std {')]
for marker in ['static const uint8_t* GetItemPtrFromJarURI(', 'static ipc::ReadOnlySharedMemoryMapping GetHyphDictFromParent(', 'static ipc::ReadOnlySharedMemoryHandle CopyToShmem(', 'static ipc::ReadOnlySharedMemoryHandle LoadFromURI(', 'nsHyphenator::nsHyphenator(', 'bool nsHyphenator::IsValid()', 'ipc::ReadOnlySharedMemoryHandle nsHyphenator::CloneHandle()']:
 body=full(cpp,marker)
 if marker=='nsHyphenator::nsHyphenator(':body=replace(body,'mHyphenateCapitalized(aHyphenateCapitalized) {','mHyphenateCapitalized(aHyphenateCapitalized) {\n uri=aURI;loads.push_back(aURI->path);','constructor ghost trace')
 parts.append(body)
managerSource=ROOT/'source/providers/intl/hyphenation/glue/nsHyphenationManager.cpp'
method=full(managerSource,'already_AddRefed<nsHyphenator> nsHyphenationManager::GetHyphenator(')
method=replace(method,'nsAtom* aLocale) {','nsAtom* aLocale) {\n static unsigned depth=0;if(depth==0&&!currentCaseIdentity().empty())std::cout<<currentCaseIdentity()<<" LOOKUP "<<(aLocale?aLocale->value:"<null>")<<"\\n";depth++;auto depthExit=mozilla::MakeScopeExit([&]{depth--;});','outer lookup event')
parts.append(method)
provider='\n'.join(parts)
for flavor in ['original','candidate','standalone']:
 text=(ROOT/f'development-build/full/stream-{flavor}.cpp').read_text()
 text=replace(text,'template<class T> using Span=std::span<T>;','template<class T>struct Span:std::span<T>{using std::span<T>::span;bool IsEmpty()const{return this->empty();}};',flavor+' span facade')
 old='template<class T> class RefPtr{T* p=nullptr;public:RefPtr()=default;RefPtr(T* x):p(x){}operator T*()const{return p;}T* operator->()const{return p;}T* get()const{return p;}RefPtr& operator=(T*x){p=x;return *this;}};'
 new='template<class T>class already_AddRefed;template<class T> class RefPtr{T* p=nullptr;public:RefPtr()=default;RefPtr(T* x):p(x){}RefPtr(already_AddRefed<T> x):p(x.take()){}operator T*()const{return p;}T* operator->()const{return p;}T* get()const{return p;}already_AddRefed<T>forget(){auto old=p;p=nullptr;return already_AddRefed<T>(old);}RefPtr& operator=(T*x){p=x;return *this;}};'
 text=replace(text,old,new,flavor+' manager RefPtr adapter')
 text=replace(text,'explicit already_AddRefed(T* value):p(value){}','already_AddRefed(std::nullptr_t):p(nullptr){}explicit already_AddRefed(T* value):p(value){}',flavor+' null result adapter')
 text=replace(text,'inline std::string nsAtomCString(nsAtom* p){return p->value;}','#include <map>\n'+strings,flavor+' common string adapter')
 text=replace(text,'struct nsAutoCString{std::string s;void Append(uint32_t c){s.push_back(char(c));}size_t Length()const{return s.size();}const char* BeginReading()const{return s.data();}uint8_t operator[](size_t i)const{return uint8_t(s.at(i));}};','',flavor+' old string removed')
 a=text.index('struct HyphDic{};');b=text.index('using mozilla::Span;using mozilla::fallible;',a)
 adaptations.append({'label':flavor+' dictionary provider replacement','removed_sha256':hashlib.sha256(text[a:b].encode()).hexdigest(),'new_sha256':hashlib.sha256(provider.encode()).hexdigest()})
 text=text[:a]+provider+'\n'+text[b:]
 old='std::ifstream dict(argv[1],std::ios::binary);gHyphenator.mDict.bytes.assign(std::istreambuf_iterator<char>(dict),{});\n if(!mapped_hyph_is_valid_hyphenator(gHyphenator.mDict.bytes.data(),gHyphenator.mDict.bytes.size()))return 3;'
 new='std::ifstream dict(argv[1],std::ios::binary);gDictionaryBytes.assign(std::istreambuf_iterator<char>(dict),{});if(!mapped_hyph_is_valid_hyphenator(gDictionaryBytes.data(),gDictionaryBytes.size()))return 3;nsIURI dictionaryURI("hyph_en_US.hyf",true);auto manager=nsHyphenationManager::Instance();manager->mPatternFiles.InsertOrUpdate(NS_Atomize("en-US"),RefPtr(&dictionaryURI));manager->mPatternFiles.InsertOrUpdate(NS_Atomize("en"),RefPtr(&dictionaryURI));RefPtr<nsHyphenator> dictionary=manager->GetHyphenator(NS_Atomize("en-US"));if(!dictionary)return 5;auto&gHyphenator=*dictionary.get();'
 text=replace(text,old,new,flavor+' actual dictionary setup')
 (OUT/f'stream-{flavor}.cpp').write_text(text)
(OUT/'EXTRACTION.json').write_text(json.dumps({'records':helper['records'],'adaptations':adaptations,'boundaries':['resource discovery replaced by explicit en/en-US fixture pattern registration','existing non-owning RefPtr/atom/string/table and native URI/jar/IPC adapters retained','actual full constructor and Hyphenate/HyphenateWord composed; no universal native provider refinement']},indent=2)+'\n')
TOOL=Path('/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr');SDK=Path('/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk');bridge=ROOT/'provider-bridge-v1';prior=ROOT/'development-build/full'
flags=[TOOL/'bin/clang++','-std=c++20','-isysroot',SDK,'-isystem',SDK/'usr/include/c++/v1','-O1','-g','-fsanitize=undefined','-I',prior,'-I',ROOT/'native','-I',bridge/'development-build/provider','-I',bridge/'provider-crates/icu_capi/bindings/cpp','-I',bridge/'source/providers/intl/icu/source/common','-I',bridge/'native/hyphen-producer-input','-I',bridge/'native']
libs=[prior/'provider.o',prior/'locale.o',ROOT/'development-build/icu/debug/liblanguage_break_provider.a',ROOT/'development-build/rust/libmapped_hyph.a','-licucore','-framework','CoreFoundation','-framework','Security']
commands=[]
for flavor in ['original','candidate','standalone']:
 command=list(map(str,[*flags,OUT/f'stream-{flavor}.cpp',*libs,'-o',OUT/f'stream-{flavor}']))
 result=subprocess.run(command,capture_output=True,text=True,timeout=120);(OUT/f'build-{flavor}.log').write_text(result.stdout+result.stderr)
 commands.append({'args':command,'exit':result.returncode});(OUT/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n');print(flavor,result.returncode,flush=True)
 if result.returncode:raise SystemExit(result.returncode)
