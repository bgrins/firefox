int main(){
 std::string line;while(std::getline(std::cin,line)){
  std::istringstream input(line);std::string id,op;input>>id;nsHyphenationManager manager;std::vector<std::unique_ptr<nsIURI>>uris;loads.clear();prefReads.clear();Preferences::values.clear();
  while(input>>op){
   if(op=="P"){std::string locale,path;int valid;input>>locale>>path>>valid;uris.push_back(std::make_unique<nsIURI>(path,bool(valid)));manager.mPatternFiles.InsertOrUpdate(NS_Atomize(locale),RefPtr(uris.back().get()));}
   else if(op=="A"){std::string alias,target;input>>alias>>target;manager.mHyphAliases.InsertOrUpdate(NS_Atomize(alias),RefPtr(NS_Atomize(target)));}
   else if(op=="C"){std::string locale;int value;input>>locale>>value;Preferences::values["intl.hyphenate-capitalized."+locale]=value;}
   else if(op=="G"){std::string locale;input>>locale;RefPtr<nsHyphenator>result=manager.GetHyphenator(NS_Atomize(locale));std::cout<<id<<" GET "<<locale<<" "<<(result?result->uri->path:"-")<<" "<<(result?result->capitalized:false)<<"\n";}
   else if(op=="M"){manager.mHyphenators.Clear();}
   else if(op=="L"){std::string path;input>>path;RefPtr<nsAtom>locale=LocaleAtomFromPath(path);std::cout<<id<<" LOCALE "<<(locale?locale->value:"-")<<"\n";}
   else return 2;
  }
  std::cout<<id<<" LOADS";for(auto&s:loads)std::cout<<" "<<s;
  std::cout<<" PREFS";for(auto&s:prefReads)std::cout<<" "<<s;
  std::cout<<" CACHE";for(auto&[key,value]:manager.mHyphenators.values)std::cout<<" "<<key;
  std::cout<<" PATTERNS";for(auto&[key,value]:manager.mPatternFiles.values)std::cout<<" "<<key;std::cout<<"\n";
 }
}
