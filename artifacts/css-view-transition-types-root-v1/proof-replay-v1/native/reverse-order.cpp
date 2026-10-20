#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <unordered_set>
#include <vector>
#define MOZ_ASSERT(x) assert(x)
using nsAString = std::u16string;
using char16ptr_t = const char16_t*;
struct nsAtom {
  nsAString text;
  uint32_t mLength;
  unsigned id;
  const char16_t* GetUTF16String() const { return text.data(); }
  bool Equals(char16ptr_t aString, uint32_t aLength) const {
    return mLength == aLength &&
           memcmp(GetUTF16String(), aString, mLength * sizeof(char16_t)) == 0;
  }
};
template<class T> struct RefPtr {
  std::shared_ptr<T> owner;
  RefPtr(std::shared_ptr<T> p) : owner(std::move(p)) {}
  operator T*() const { return owner.get(); }
  T* operator->() const { return owner.get(); }
  bool operator==(const RefPtr& other) const { return owner == other.owner; }
};
template<class T> RefPtr(std::shared_ptr<T>) -> RefPtr<T>;
std::vector<nsAString> alphabet = {u"a",u"b",u"A",u"absent",u"",u"none",u"-ua-test",nsAString({0}),nsAString({0xd800}),nsAString({0xdc00}),nsAString({0x61,0x301}),nsAString({0xe1})};
std::vector<std::weak_ptr<nsAtom>> atoms(alphabet.size());
RefPtr<nsAtom> NS_AtomizeMainThread(const nsAString& text) {
  auto it=std::find(alphabet.begin(),alphabet.end(),text); assert(it!=alphabet.end());
  unsigned id=it-alphabet.begin();
  auto p=atoms[id].lock();
  if (!p) { p=std::make_shared<nsAtom>(nsAtom{text,static_cast<uint32_t>(text.size()),id}); atoms[id]=p; }
  assert(p->Equals(text.data(), text.size()));
  return RefPtr<nsAtom>(p);
}
template<class T> struct nsTArray : std::vector<T> {
  using std::vector<T>::vector;
  void SetCapacity(size_t n) { this->reserve(n); }
  size_t Length() const { return this->size(); }
  bool IsEmpty() const { return this->empty(); }
  void AppendElement(T p) { this->push_back(std::move(p)); }
  template<class U> bool Contains(const U& p) const {
    return std::find(this->begin(),this->end(),p)!=this->end();
  }
  template<class U> bool RemoveElement(const U& p) {
    auto it=std::find(this->begin(),this->end(),p);
    if (it==this->end()) return false;
    this->erase(it); return true;
  }
  void Clear() { this->clear(); }
};
template<class T> struct nsTHashSet {
  using KeyType=T;using EntryType=T;
  struct Hash { size_t operator()(T) const { return 0; } };
  std::unordered_set<T,Hash> values;
  size_t Count() const { return values.size(); }
  EntryType* PutEntry(KeyType p) { values.insert(p); return nullptr; }
  [[nodiscard]] bool EnsureInserted(KeyType aKey,
                                    EntryType** aEntry = nullptr) {
    auto oldCount = Count();
    EntryType* entry = PutEntry(aKey);
    if (aEntry) {
      *aEntry = entry;
    }
    return oldCount != Count();
  }
};
struct ErrorResult { bool Failed() const { return false; } };
ErrorResult& IgnoreErrors() { static ErrorResult e; return e; }
struct ViewTransitionUpdateCallback {};
struct ViewTransitionTypeSet;
struct Document;
using TypeList=nsTArray<RefPtr<nsAtom>>;
struct ViewTransition {
  Document* mDocument;
  ViewTransitionUpdateCallback* mUpdateCallback;
  TypeList mTypeList;
  ViewTransitionTypeSet* mTypes=nullptr;
  ViewTransition(Document&,ViewTransitionUpdateCallback*,TypeList&&);
  ~ViewTransition();
  TypeList& GetTypeList() { return mTypeList; }
  const TypeList& GetTypeList() const { return mTypeList; }
  ViewTransitionTypeSet* Types();
};
struct ViewTransitionTypeSet {
  ViewTransition* mTransition;
  std::vector<nsAString> backing;
  explicit ViewTransitionTypeSet(ViewTransition& t):mTransition(&t){}
  ViewTransitionTypeSet* Add(const nsAString&,ErrorResult&);
  void Clear(ErrorResult&);
  bool Delete(const nsAString&,ErrorResult&);
};
ViewTransition::~ViewTransition(){delete mTypes;}
namespace ViewTransitionTypeSet_Binding::SetlikeHelpers {
  bool Has(ViewTransitionTypeSet* s,const nsAString& x,ErrorResult&) {
    return std::find(s->backing.begin(),s->backing.end(),x)!=s->backing.end();
  }
  void Add(ViewTransitionTypeSet* s,const nsAString& x,ErrorResult& e) {
    if (!Has(s,x,e)) s->backing.push_back(x);
  }
  bool Delete(ViewTransitionTypeSet* s,const nsAString& x,ErrorResult&) {
    auto i=std::find(s->backing.begin(),s->backing.end(),x);
    if(i==s->backing.end())return false;
    s->backing.erase(i);return true;
  }
  void Clear(ViewTransitionTypeSet* s,ErrorResult&){s->backing.clear();}
}
namespace SetlikeHelpers=ViewTransitionTypeSet_Binding::SetlikeHelpers;
char16_t asciiLower(char16_t x){return x>=u'A'&&x<=u'Z'?x+32:x;}
struct nsDependentAtomString:nsAString {
  explicit nsDependentAtomString(nsAtom* p):nsAString(p->text){}
  bool LowerCaseEqualsASCII(const char* text)const{
    if(size()!=strlen(text))return false;
    for(size_t i=0;i<size();i++)if(asciiLower(at(i))!=text[i])return false;
    return true;
  }
};
nsAString operator""_ns(const char16_t* text,size_t length){return nsAString(text,length);}
constexpr int nsASCIICaseInsensitiveStringComparator=0;
bool StringBeginsWith(const nsAString& text,const nsAString& beginning,int){
  if(text.size()<beginning.size())return false;
  for(size_t i=0;i<beginning.size();i++)if(asciiLower(text[i])!=asciiLower(beginning[i]))return false;
  return true;
}
ViewTransition::ViewTransition(Document& aDoc,
                               ViewTransitionUpdateCallback* aCb,
                               TypeList&& aTypeList)
    : mDocument(&aDoc), mUpdateCallback(aCb), mTypeList(std::move(aTypeList)) {}
ViewTransitionTypeSet* ViewTransition::Types() {
  if (!mTypes) {
    mTypes = new ViewTransitionTypeSet(*this);
    for (const auto& type : mTypeList) {
      ViewTransitionTypeSet_Binding::SetlikeHelpers::Add(
          mTypes, nsDependentAtomString(type), IgnoreErrors());
    }
  }
  return mTypes;
}
ViewTransitionTypeSet* ViewTransitionTypeSet::Add(const nsAString& aValue,
                                                  ErrorResult& aRv) {
  if (SetlikeHelpers::Has(this, aValue, aRv) || aRv.Failed()) {
    return this;
  }
  SetlikeHelpers::Add(this, aValue, aRv);
  if (aRv.Failed()) {
    return this;
  }
  RefPtr atom = NS_AtomizeMainThread(aValue);
  MOZ_ASSERT(!mTransition->GetTypeList().Contains(atom));
  mTransition->GetTypeList().AppendElement(std::move(atom));
  return this;
}
bool ViewTransitionTypeSet::Delete(const nsAString& aValue, ErrorResult& aRv) {
  if (!SetlikeHelpers::Delete(this, aValue, aRv) || aRv.Failed()) {
    return false;
  }
  RefPtr atom = NS_AtomizeMainThread(aValue);
  MOZ_ASSERT(mTransition->GetTypeList().Contains(atom));
  mTransition->GetTypeList().RemoveElement(atom);
  return true;
}
void ViewTransitionTypeSet::Clear(ErrorResult& aRv) {
  SetlikeHelpers::Clear(this, aRv);
  if (aRv.Failed()) {
    return;
  }
  mTransition->GetTypeList().Clear();
}
struct NullableTypes {
  nsTArray<nsAString> values;
  bool null=false;
  bool IsNull() const{return null;}
  const nsTArray<nsAString>& Value() const{return values;}
};
struct Options { NullableTypes mTypes; std::shared_ptr<ViewTransitionUpdateCallback> mUpdate; };
struct Arguments {
  Options options;
  ViewTransitionUpdateCallback callback;
  bool isCallback=false;
  bool IsViewTransitionUpdateCallback() const{return isCallback;}
  bool IsStartViewTransitionOptions() const{return !isCallback;}
  ViewTransitionUpdateCallback& GetAsViewTransitionUpdateCallback(){return callback;}
  const Options& GetAsStartViewTransitionOptions()const{return options;}
};
TypeList initialize(Arguments& aOptions) {
  nsTArray<RefPtr<nsAtom>> types;
  ViewTransitionUpdateCallback* cb = nullptr;
  if (aOptions.IsViewTransitionUpdateCallback()) {
    cb = &aOptions.GetAsViewTransitionUpdateCallback();
  } else {
    MOZ_ASSERT(aOptions.IsStartViewTransitionOptions());
    const auto& options = aOptions.GetAsStartViewTransitionOptions();
    cb = options.mUpdate.get();
    if (!options.mTypes.IsNull()) {
      const auto& optionsTypes = options.mTypes.Value();
      types.SetCapacity(optionsTypes.Length());
      nsTHashSet<nsAtom*> seenTypes;
      for (const auto& type : optionsTypes) {
        RefPtr<nsAtom> atom = NS_AtomizeMainThread(type);
        if (seenTypes.EnsureInserted(atom)) {
          types.insert(types.begin(), std::move(atom));
        }
      }
    }
  }

  return types;
}
std::string nativeIDs(const TypeList& xs){std::string s;for(auto&x:xs){if(!s.empty())s+=",";s+=std::to_string(x->id);}return s;}
std::string publicIDs(const std::vector<nsAString>& xs){std::string s;for(auto&x:xs){if(!s.empty())s+=",";s+=std::to_string(std::find(alphabet.begin(),alphabet.end(),x)-alphabet.begin());}return s;}
struct Document { ViewTransition* transition=nullptr; const ViewTransition* GetActiveViewTransition()const{return transition;} };
namespace mozilla::dom {using Document=::Document;}
struct StyleCustomIdent { RefPtr<nsAtom> atom; nsAtom* AsAtom()const{return atom;} };
static bool IsValidViewTransitionType(nsAtom* aName) {
  nsDependentAtomString str(aName);
  return !StringBeginsWith(str, u"-ua-"_ns,
                           nsASCIICaseInsensitiveStringComparator) &&
         !str.LowerCaseEqualsASCII("none");
}
bool Gecko_HasActiveViewTransitionTypes(
    const mozilla::dom::Document* aDoc,
    const nsTArray<StyleCustomIdent>* aNames) {
  MOZ_ASSERT(aDoc);
  MOZ_ASSERT(aNames);
  const ViewTransition* vt = aDoc->GetActiveViewTransition();
  if (!vt) {
    return false;
  }
  const auto& typeList = vt->GetTypeList();
  if (typeList.IsEmpty()) {
    return false;
  }
  for (const auto& name : *aNames) {
    if (typeList.Contains(name.AsAtom())) {
      // NOTE(emilio): This IsValidViewTransitionType() check is not in the spec
      // and is rather weird, but matches other browsers for now, see:
      // https://github.com/w3c/csswg-drafts/issues/13141
      if (IsValidViewTransitionType(name.AsAtom())) {
        return true;
      }
    }
  }
  return false;
}
int main(){
  std::string line;
  while(std::getline(std::cin,line)){
    std::istringstream in(line);unsigned id,kind,n,count;in>>id>>kind>>n;
    Arguments args;args.isCallback=kind==2;args.options.mTypes.null=kind==1;
    for(unsigned i=0,x;i<n;i++){in>>x;args.options.mTypes.values.push_back(alphabet.at(x));}
    Document doc; ViewTransition transition(doc,nullptr,initialize(args));doc.transition=&transition;
    auto* types=transition.Types();ErrorResult error;
    std::cout<<id<<"|"<<nativeIDs(transition.GetTypeList())<<"|"<<publicIDs(types->backing);
    in>>count;
    for(unsigned i=0,x,op;i<count;i++){
      in>>op>>x;int reply=-1;
      if(op==0){auto* identity=types->Add(alphabet.at(x),error);assert(identity==types);reply=2;}
      if(op==1)reply=types->Delete(alphabet.at(x),error)?1:0;
      if(op==2)types->Clear(error);
      if(op==3){assert(transition.Types()==types);reply=3;}
      std::cout<<"|"<<nativeIDs(transition.GetTypeList())<<"|"<<publicIDs(types->backing)<<"|"<<reply<<"|";
      for(unsigned query=0;query<alphabet.size();query++){
        nsTArray<StyleCustomIdent> names;names.push_back({NS_AtomizeMainThread(alphabet[query])});
        std::cout<<(Gecko_HasActiveViewTransitionTypes(&doc,&names)?'1':'0');
      }
    }
    std::cout<<"\n";
  }
}
