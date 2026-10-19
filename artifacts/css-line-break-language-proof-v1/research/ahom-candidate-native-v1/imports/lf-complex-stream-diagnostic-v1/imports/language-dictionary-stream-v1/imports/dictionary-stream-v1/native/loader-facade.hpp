#include <cstring>
#include <functional>
#include <variant>
#include <type_traits>
#define MOZ_ASSERT(...) ((void)0)
#define MOZ_ASSERT_UNREACHABLE(...) ((void)0)
#define NS_ASSERTION(...) ((void)0)
#define NS_INLINE_DECL_REFCOUNTING(...) 
#define NS_FAILED(value) ((value)!=0)
#define NS_SUCCEEDED(value) ((value)==0)
using nsresult=int;
struct HyphDic;
struct CompiledData;
extern "C" {
const HyphDic* mapped_hyph_load_dictionary(const char*);
void mapped_hyph_free_dictionary(HyphDic*);
const CompiledData* mapped_hyph_compile_buffer(const uint8_t*,uint32_t,bool);
const CompiledData* mapped_hyph_compile_file(const char*,bool);
void mapped_hyph_free_compiled_data(CompiledData*);
uint32_t mapped_hyph_compiled_data_size(const CompiledData*);
const uint8_t* mapped_hyph_compiled_data_ptr(const CompiledData*);
bool mapped_hyph_is_valid_hyphenator(const uint8_t*,uint32_t);
}
namespace mozilla {
template<class T> using UniquePtr=std::unique_ptr<T>;
template<class T> auto MakeUnique(size_t count){return std::make_unique<T>(count);}
template<class T>struct Span{
 T* pointer=nullptr;size_t length=0;
 Span()=default;Span(T*p,size_t n):pointer(p),length(n){}
 bool IsEmpty()const{return !length;}T*data()const{return pointer;}size_t size()const{return length;}
};
template<class...T>struct Overload:T...{using T::operator()...;};
template<class...T>Overload(T...)->Overload<T...>;
template<class...T>struct Variant{
 std::variant<T...>data;
 template<class V>Variant(V&&v):data(std::forward<V>(v)){}
 template<class V>Variant&operator=(V&&v){data=std::forward<V>(v);return *this;}
 template<class V,class...A>void emplace(A&&...a){data.template emplace<V>(std::forward<A>(a)...);}
 template<class V>bool is(){return std::holds_alternative<V>(data);}
 template<class V>V&as(){return std::get<V>(data);}
 template<class...F>auto match(F&&...f){return std::visit(Overload{std::forward<F>(f)...},data);}
};
template<class T>T&&AsVariant(T&&v){return std::forward<T>(v);}
namespace ipc {
struct ReadOnlySharedMemoryMapping;
struct ReadOnlySharedMemoryHandle{
 std::shared_ptr<std::vector<uint8_t>>bytes;
 ReadOnlySharedMemoryHandle()=default;ReadOnlySharedMemoryHandle(std::nullptr_t){}
 explicit ReadOnlySharedMemoryHandle(std::shared_ptr<std::vector<uint8_t>>v):bytes(std::move(v)){}
 bool IsValid()const{return bool(bytes);}explicit operator bool()const{return IsValid();}
 ReadOnlySharedMemoryMapping Map();ReadOnlySharedMemoryHandle Clone(){return ReadOnlySharedMemoryHandle(bytes);}
};
struct ReadOnlySharedMemoryMapping{
 std::shared_ptr<std::vector<uint8_t>>bytes;
 ReadOnlySharedMemoryMapping()=default;ReadOnlySharedMemoryMapping(std::nullptr_t){}
 explicit ReadOnlySharedMemoryMapping(std::shared_ptr<std::vector<uint8_t>>v):bytes(std::move(v)){}
 bool IsValid()const{return bool(bytes);}explicit operator bool()const{return IsValid();}
 void*Address(){return bytes?bytes->data():nullptr;}
 template<class T>T*DataAs(){return reinterpret_cast<T*>(Address());}
 size_t Size(){return bytes?bytes->size():0;}
 ReadOnlySharedMemoryHandle Freeze(){return ReadOnlySharedMemoryHandle(bytes);}
};
inline ReadOnlySharedMemoryMapping ReadOnlySharedMemoryHandle::Map(){return ReadOnlySharedMemoryMapping(bytes);}
namespace shared_memory {inline ReadOnlySharedMemoryHandle CreateFreezable(size_t n){return ReadOnlySharedMemoryHandle(std::make_shared<std::vector<uint8_t>>(n));}}
}
}
static bool gParent=true;
bool XRE_IsParentProcess(){return gParent;}
static std::vector<uint8_t>gDictionaryBytes;
struct nsIURI;
struct nsZipArchive;
struct nsIFile{nsZipArchive*archive=nullptr;};
struct nsIJARURI{nsIURI*owner=nullptr;nsresult GetJARFile(RefPtr<nsIURI>*out);nsresult GetJAREntry(String&out);};
struct nsIFileURL{nsIURI*owner=nullptr;nsresult GetFile(RefPtr<nsIFile>*out);};
struct nsZipItem{nsIURI*owner=nullptr;uint16_t Compression();uint32_t Size();};
struct nsZipArchive{nsIURI*owner=nullptr;nsZipItem item;nsZipItem*GetItem(const String&);const uint8_t*GetData(nsZipItem*);};
struct nsIURI{
 std::string path;bool valid;std::vector<uint8_t>data;bool jarAvailable=true;uint16_t compression=0;
 nsIJARURI jar{this};nsIFileURL fileURL{this};nsZipArchive archive{this,{this}};nsIFile file{&archive};
 nsIURI(std::string p,bool v):path(std::move(p)),valid(v),data(v?gDictionaryBytes:std::vector<uint8_t>(4)){}
 nsresult GetFilePath(String&out){out.value=path;return 0;}nsresult GetSpec(String&out){out.value=path;return 0;}
 bool SchemeIs(const char*scheme){return !jarAvailable&&std::string(scheme)=="file";}
 String GetSpecOrDefault(){return path;}
};
nsresult nsIJARURI::GetJARFile(RefPtr<nsIURI>*out){*out=owner;return 0;}
nsresult nsIJARURI::GetJAREntry(String&out){out.value=owner->path;return 0;}
nsresult nsIFileURL::GetFile(RefPtr<nsIFile>*out){*out=&owner->file;return 0;}
uint16_t nsZipItem::Compression(){return owner->compression;}
uint32_t nsZipItem::Size(){return owner->data.size();}
nsZipItem*nsZipArchive::GetItem(const String&){return &item;}
const uint8_t*nsZipArchive::GetData(nsZipItem*){return owner->data.data();}
struct QueryInterface{
 nsIURI*uri;
 template<class T>operator RefPtr<T>()const{
  if constexpr(std::is_same_v<T,nsIJARURI>)return uri&&uri->jarAvailable?&uri->jar:nullptr;
  if constexpr(std::is_same_v<T,nsIFileURL>)return uri?&uri->fileURL:nullptr;
  return nullptr;
 }
};
QueryInterface do_QueryInterface(nsIURI*uri){return {uri};}
QueryInterface do_QueryInterface(RefPtr<nsIURI>uri){return {uri.p};}
namespace mozilla {namespace Omnijar {inline nsZipArchive*GetReader(nsIFile*file){return file?file->archive:nullptr;}}}
struct nsIInputStream{
 nsIURI*uri;size_t position=0;
 nsresult Available(uint64_t*out){*out=uri->data.size()-position;return 0;}
 nsresult Read(char*out,uint32_t count,uint32_t*read){*read=std::min<size_t>(count,uri->data.size()-position);memcpy(out,uri->data.data()+position,*read);position+=*read;return 0;}
};
struct nsIChannel{nsIInputStream stream;nsresult Open(RefPtr<nsIInputStream>*out){*out=&stream;return 0;}};
struct nsContentUtils{static void*GetSystemPrincipal(){return nullptr;}};
struct nsILoadInfo{static constexpr int SEC_ALLOW_CROSS_ORIGIN_SEC_CONTEXT_IS_NULL=0;};
struct nsIContentPolicy{static constexpr int TYPE_OTHER=0;};
static std::vector<std::unique_ptr<nsIChannel>>gChannels;
nsresult NS_NewChannel(RefPtr<nsIChannel>*out,nsIURI*uri,void*,int,int){gChannels.push_back(std::make_unique<nsIChannel>(nsIChannel{{uri,0}}));*out=gChannels.back().get();return 0;}
void NS_UnescapeURL(String&text){
 std::string decoded;
 for(size_t i=0;i<text.value.size();++i){
  auto digit=[](char c)->int{if(c>='0'&&c<='9')return c-'0';if(c>='A'&&c<='F')return c-'A'+10;if(c>='a'&&c<='f')return c-'a'+10;return -1;};
  if(text.value[i]=='%'&&i+2<text.value.size()&&digit(text.value[i+1])>=0&&digit(text.value[i+2])>=0){decoded+=char(16*digit(text.value[i+1])+digit(text.value[i+2]));i+=2;}else decoded+=text.value[i];
 }
 text.value=decoded;
}
namespace mozilla::dom {struct ContentChild{
 static ContentChild*GetSingleton(){static ContentChild child;return &child;}
 bool SendGetHyphDict(nsIURI*,ipc::ReadOnlySharedMemoryHandle*out){*out=nullptr;return false;}
};}
using namespace mozilla;
