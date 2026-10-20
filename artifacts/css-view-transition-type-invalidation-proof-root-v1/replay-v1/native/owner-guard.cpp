#include <algorithm>
#include <cassert>
#include <iostream>
#include <memory>
#include <sstream>
#include <vector>
#define MOZ_ASSERT(x) assert(x)
using nsAString = unsigned;
struct Atom { unsigned id; };
template<class T> struct RefPtr : std::shared_ptr<T> {
  RefPtr(std::shared_ptr<T> p) : std::shared_ptr<T>(std::move(p)) {}
};
template<class T> RefPtr(std::shared_ptr<T>) -> RefPtr<T>;
std::shared_ptr<Atom> atoms[2] = {std::make_shared<Atom>(Atom{0}),std::make_shared<Atom>(Atom{1})};
std::shared_ptr<Atom> NS_AtomizeMainThread(unsigned x) { return atoms[x]; }
struct TypeList : std::vector<RefPtr<Atom>> {
  bool Contains(const RefPtr<Atom>& x) const { return std::find(begin(),end(),x)!=end(); }
  void AppendElement(RefPtr<Atom> x) { push_back(std::move(x)); }
  void RemoveElement(RefPtr<Atom> x) { auto i=std::find(begin(),end(),x);if(i!=end())erase(i); }
  bool IsEmpty() const { return empty(); }
  void Clear() { clear(); }
};
struct ErrorResult { unsigned stage; bool failed=false; bool Failed() const { return failed; } };
struct ViewTransition;
struct ViewTransitionTypeSet {
  ViewTransition* mTransition;
  std::vector<unsigned> backing;
  ViewTransitionTypeSet* Add(const nsAString&,ErrorResult&);
  void Clear(ErrorResult&);
  bool Delete(const nsAString&,ErrorResult&);
};
namespace SetlikeHelpers {
  bool Has(ViewTransitionTypeSet* s,unsigned x,ErrorResult& e) {
    if(e.stage==1)e.failed=true;
    return std::find(s->backing.begin(),s->backing.end(),x)!=s->backing.end();
  }
  void Add(ViewTransitionTypeSet* s,unsigned x,ErrorResult& e) {
    if(e.stage==2){e.failed=true;return;}s->backing.push_back(x);
  }
  bool Delete(ViewTransitionTypeSet* s,unsigned x,ErrorResult& e) {
    if(e.stage){e.failed=true;return false;}
    auto i=std::find(s->backing.begin(),s->backing.end(),x);
    if(i==s->backing.end())return false;s->backing.erase(i);return true;
  }
  void Clear(ViewTransitionTypeSet* s,ErrorResult& e) {
    if(e.stage){e.failed=true;return;}s->backing.clear();
  }
}
struct RestyleHint { static RestyleHint RestyleSubtree(){return {};} };
using nsChangeHint=unsigned;
struct Manager {
  bool pending=false;
  unsigned requests=0;
  void PostRestyleEvent(void*,RestyleHint,nsChangeHint change){assert(change==0);pending=true;requests++;}
};
struct nsPresContext { Manager* manager; Manager* RestyleManager(){return manager;} };
struct Document;
struct Element { Document* doc; bool composed=true; Document* GetComposedDoc(){return composed?doc:nullptr;} };
struct Document {
  ViewTransition* active=nullptr;
  Element* root;
  nsPresContext* context;
  unsigned helperCalls=0;
  ViewTransition* GetActiveViewTransition(){helperCalls++;return active;}
  Element* GetRootElement(){return root;}
  nsPresContext* GetPresContext(){return context;}
};
namespace nsLayoutUtils { void PostRestyleEvent(Element*,RestyleHint,nsChangeHint); }
struct ViewTransition {
  Document* mDocument;
  TypeList types;
  TypeList& GetTypeList(){return types;}
  void TypesChanged();
};
void nsLayoutUtils::PostRestyleEvent(Element* aElement,
                                     RestyleHint aRestyleHint,
                                     nsChangeHint aMinChangeHint) {
  if (Document* doc = aElement->GetComposedDoc()) {
    if (nsPresContext* presContext = doc->GetPresContext()) {
      presContext->RestyleManager()->PostRestyleEvent(aElement, aRestyleHint,
                                                      aMinChangeHint);
    }
  }
}
void ViewTransition::TypesChanged() {
  if ((mDocument->GetActiveViewTransition(), false)) {
    return;
  }
  if (Element* root = mDocument->GetRootElement()) {
    nsLayoutUtils::PostRestyleEvent(root, RestyleHint::RestyleSubtree(),
                                    nsChangeHint(0));
  }
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
  mTransition->TypesChanged();
  return this;
}
bool ViewTransitionTypeSet::Delete(const nsAString& aValue, ErrorResult& aRv) {
  if (!SetlikeHelpers::Delete(this, aValue, aRv) || aRv.Failed()) {
    return false;
  }
  RefPtr atom = NS_AtomizeMainThread(aValue);
  MOZ_ASSERT(mTransition->GetTypeList().Contains(atom));
  mTransition->GetTypeList().RemoveElement(atom);
  mTransition->TypesChanged();
  return true;
}
void ViewTransitionTypeSet::Clear(ErrorResult& aRv) {
  SetlikeHelpers::Clear(this, aRv);
  if (aRv.Failed() || mTransition->GetTypeList().IsEmpty()) {
    return;
  }
  mTransition->GetTypeList().Clear();
  mTransition->TypesChanged();
}
unsigned mask(const TypeList& xs){unsigned m=0;for(auto& x:xs)m|=1u<<x->id;return m;}
unsigned expected(unsigned subject,Document& doc){
  bool alpha=doc.active && (mask(doc.active->types)&1);
  bool beta=doc.active && (mask(doc.active->types)&2);
  unsigned bases[]={10,17,20,25,30},selected[]={100,43,80,75,70};
  if(beta && subject<2)return subject==0?200:61;return alpha?selected[subject]:bases[subject];
}
void snapshot(Manager& manager,Document& doc,ViewTransition* ts,unsigned* cache){
  std::cout<<"|"<<mask(ts[0].types)<<","<<mask(ts[1].types)<<","<<doc.helperCalls<<","<<manager.requests<<","<<manager.pending;
  for(unsigned j=0;j<5;j++)std::cout<<","<<cache[j];
}
int main(){
  std::string line;
  while(std::getline(std::cin,line)){
    std::istringstream in(line);unsigned id,owner,root,composed,pres,m0,m1,count;
    in>>id>>owner>>root>>composed>>pres>>m0>>m1>>count;
    Manager manager;nsPresContext context{&manager};Document doc;Element element{&doc,bool(composed)};
    doc.root=root?&element:nullptr;doc.context=pres?&context:nullptr;
    ViewTransition ts[2]={{&doc,{}},{&doc,{}}};doc.active=owner<2?&ts[owner]:nullptr;
    ViewTransitionTypeSet sets[2]={{&ts[0],{}},{&ts[1],{}}};unsigned masks[]={m0,m1};
    for(unsigned t=0;t<2;t++)for(unsigned x=0;x<2;x++)if(masks[t]&(1u<<x)){ts[t].types.AppendElement(RefPtr(atoms[x]));sets[t].backing.push_back(x);}
    unsigned cache[5];for(unsigned j=0;j<5;j++)cache[j]=expected(j,doc);
    std::cout<<id;snapshot(manager,doc,ts,cache);
    for(unsigned k=0;k<count;k++){
      unsigned tag,actor,name,stage;in>>tag>>actor>>name>>stage;
      ErrorResult error{stage};
      if(tag==0)sets[actor].Add(name,error);
      if(tag==1)sets[actor].Delete(name,error);
      if(tag==2)sets[actor].Clear(error);
      if(tag==3){
        if(manager.pending){for(unsigned j=0;j<5;j++)if(name&(1u<<j))cache[j]=expected(j,doc);if(name==31)manager.pending=false;}
      }
      snapshot(manager,doc,ts,cache);
    }
    std::cout<<"\n";
  }
}
