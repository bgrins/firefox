#include <algorithm>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <sstream>
#include <string>
#include <vector>
struct nsAtom{std::string value;};
struct String{
 std::string value;String()=default;String(const char*s):value(s){}String(std::string s):value(std::move(s)){}String(nsAtom*a):value(a->value){}
 size_t Length()const{return value.size();}const char*get()const{return value.c_str();}
 void Truncate(size_t n){value.resize(n);}int32_t RFindChar(char c)const{auto i=value.rfind(c);return i==std::string::npos?-1:int32_t(i);}
 void ReplaceLiteral(size_t i,size_t n,const char*s){value.replace(i,n,s);}void Append(String s){value+=s.value;}
 void Cut(size_t i,size_t n){value.erase(i,n);}void ReplaceChar(char a,char b){std::replace(value.begin(),value.end(),a,b);}
};
using nsCString=String;using nsAutoCString=String;using nsAtomCString=String;
String operator""_ns(const char*s,size_t n){return std::string(s,n);}
bool StringEndsWith(const String&s,const String&tail){return s.value.ends_with(tail.value);}
bool StringBeginsWith(const String&s,const String&head){return s.value.starts_with(head.value);}
void ToLowerCase(String&s){for(auto&c:s.value)if(c>='A'&&c<='Z')c+=32;}
static std::map<std::string,std::unique_ptr<nsAtom>> atoms;
nsAtom*NS_Atomize(const String&s){auto&atom=atoms[s.value];if(!atom)atom=std::make_unique<nsAtom>(s.value);return atom.get();}
template<class T>struct already_AddRefed{T*p;already_AddRefed(T*v):p(v){}already_AddRefed(std::nullptr_t):p(nullptr){}T*take(){auto q=p;p=nullptr;return q;}};
template<class T>struct RefPtr{T*p=nullptr;RefPtr()=default;RefPtr(T*v):p(v){}RefPtr(already_AddRefed<T>v):p(v.take()){}operator T*()const{return p;}T*operator->()const{return p;}already_AddRefed<T>forget(){auto q=p;p=nullptr;return q;}RefPtr&operator=(T*v){p=v;return *this;}};
template<class T>RefPtr<T>*getter_AddRefs(RefPtr<T>&p){return &p;}
template<class T>using nsCOMPtr=RefPtr<T>;
template<class T>struct Table{
 std::map<std::string,T*>values;
 T*Get(nsAtom*a){auto i=values.find(a->value);return i==values.end()?nullptr:i->second;}
 void Get(nsAtom*a,RefPtr<T>*out){*out=Get(a);}void InsertOrUpdate(nsAtom*a,RefPtr<T>v){values[a->value]=v;}
 void Remove(nsAtom*a){values.erase(a->value);}void Clear(){values.clear();}
};
static std::vector<std::string>loads,prefReads;
namespace mozilla {struct Preferences{
 static std::map<std::string,bool>values;
 static bool GetBool(const char*key){prefReads.emplace_back(key);return values[key];}
};std::map<std::string,bool>Preferences::values;}
using mozilla::Preferences;
struct nsIURI{std::string path;bool valid;};
struct nsHyphenator{
 nsIURI*uri;bool capitalized;nsHyphenator(nsIURI*u,bool c):uri(u),capitalized(c){loads.push_back(u->path);}
 bool IsValid()const{return uri->valid;}
};
struct nsHyphenationManager{
 Table<nsHyphenator>mHyphenators;Table<nsIURI>mPatternFiles;Table<nsAtom>mHyphAliases;
 already_AddRefed<nsHyphenator>GetHyphenator(nsAtom*);
};
