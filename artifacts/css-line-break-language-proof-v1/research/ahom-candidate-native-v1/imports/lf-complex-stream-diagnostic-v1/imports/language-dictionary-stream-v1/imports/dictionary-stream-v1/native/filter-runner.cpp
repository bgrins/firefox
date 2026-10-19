static std::string traceCase;
extern "C" void language_trace(const char* event){std::cout<<traceCase<<" EVENT "<<event<<"\n";}
int main(){
 std::string line;
 while(std::getline(std::cin,line)){
  std::istringstream in(line);std::string id;unsigned w,p,s,n;in>>id>>w>>p>>s>>n;traceCase=id;
  std::u16string text;for(unsigned i=0;i<n;i++){unsigned c;in>>c;text.push_back(c);}
  MaskFixtureProvider provider;for(unsigned i=0;i<n;i++){unsigned x;in>>x;provider.mask.push_back(x);}
  std::vector<uint8_t> before;for(unsigned i=0;i<n;i++){unsigned x;in>>x;before.push_back(x);}
  assert(in);FilterHarness harness;harness.FindHyphenationPoints(&provider,text.data(),text.data()+text.size(),before.data(),{uint8_t(w),uint8_t(p),uint8_t(s)});
  std::cout<<id<<" FILTER ";for(auto x:before)std::cout<<unsigned(x);std::cout<<" CATEGORIES";
  for(auto c:text)std::cout<<' '<<int(mozilla::intl::UnicodeProperties::CharType(c));
  std::cout<<" SCALARS";
  for(size_t i=0;i<text.size();i++){uint32_t c=text[i];if(i+1<text.size()&&mozilla::IsSurrogatePair(c,text[i+1]))c=mozilla::SurrogateToUCS4(c,text[++i]);std::cout<<' '<<c<<':'<<int(mozilla::intl::UnicodeProperties::CharType(c));}
  std::cout<<"\n";
 }
 for(auto& action:shutdownActions)action();
}
