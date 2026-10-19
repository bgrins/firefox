#include <map>
static std::string traceCase;
extern "C" void language_trace(const char* event) { std::cout << traceCase << " EVENT " << event << "\n"; }
struct CaptureSink : nsILineBreakSink {
 std::shared_ptr<nsTransformedTextRun> run; BreakSink real; unsigned owner; size_t instance = 0;
 std::vector<uint8_t> breaks, caps;size_t base;std::vector<std::string> calls;
 CaptureSink(size_t n,size_t offset,unsigned id,std::shared_ptr<nsTransformedTextRun> textRun):run(textRun),real(run.get(),nullptr,offset),owner(id),breaks(n),caps(n),base(offset){run->SetLength(std::max(size_t(run->GetLength()),n+offset));}
 void SetBreaks(uint32_t start,uint32_t n,uint8_t* input)override{
  assert(start<=breaks.size()&&n<=breaks.size()-start);
  real.SetBreaks(start,n,input);
  calls.push_back("B:"+std::to_string(start)+":"+std::to_string(n));
  std::cout<<traceCase<<" CALLBACK B "<<owner<<' '<<base<<' '<<start<<' '<<n;for(size_t i=0;i<n;i++)std::cout<<' '<<unsigned(input[i]);std::cout<<"\n";
  std::cout<<traceCase<<" CALLBACK_ID B "<<instance<<' '<<owner<<' '<<base<<' '<<start<<' '<<n;for(size_t i=0;i<n;i++)std::cout<<' '<<unsigned(input[i]);std::cout<<"\n";
  for(size_t i=0;i<n;i++)breaks[start+i]=input[i];
 }
 void SetCapitalization(uint32_t start,uint32_t n,bool* input)override{
  assert(start<=caps.size()&&n<=caps.size()-start);
  real.SetCapitalization(start,n,input);
  calls.push_back("C:"+std::to_string(start)+":"+std::to_string(n));
  std::cout<<traceCase<<" CALLBACK C "<<owner<<' '<<base<<' '<<start<<' '<<n;for(size_t i=0;i<n;i++)std::cout<<' '<<unsigned(input[i]);std::cout<<"\n";
  std::cout<<traceCase<<" CALLBACK_ID C "<<instance<<' '<<owner<<' '<<base<<' '<<start<<' '<<n;for(size_t i=0;i<n;i++)std::cout<<' '<<unsigned(input[i]);std::cout<<"\n";
  for(size_t i=0;i<n;i++)caps[start+i]=input[i];
 }
};
static void dump_state(const std::string& id,const nsLineBreaker& b) {
 std::cout<<id<<" STATE "<<b.mScriptIsChineseOrJapanese<<' '<<b.mCurrentWordContainsMixedLang<<' '<<b.mCurrentWordMightBeBreakable<<' '<<b.mAfterBreakableSpace<<' '<<b.mBreakHere<<' '<<unsigned(b.mWordBreak)<<' '<<unsigned(b.mLineBreak)<<' '<<b.mWordContinuation<<" LANG "<<(b.mCurrentWordLanguage?b.mCurrentWordLanguage->value:"<null>")<<" WORD";
 for(auto c:b.mCurrentWord) std::cout<<' '<<unsigned(c);
 std::cout<<" ITEMS";for(auto& item:b.mTextItems){auto sink=static_cast<CaptureSink*>(item.mSink);std::cout<<' '<<(sink?std::to_string(sink->owner)+"@"+std::to_string(sink->base):"null")<<':'<<item.mSinkOffset<<':'<<item.mLength<<':'<<item.mFlags;}
 std::cout<<"\n";
 std::cout << id << " ITEM_IDS";for(auto& item:b.mTextItems){auto sink=static_cast<CaptureSink*>(item.mSink);std::cout << ' ' << (sink?std::to_string(sink->instance):"null");}std::cout << "\n";
}
int main(int argc,char**argv){
 if(argc!=2)return 2;
 std::ifstream dict(argv[1],std::ios::binary);gHyphenator.mDict.bytes.assign(std::istreambuf_iterator<char>(dict),{});
 if(!mapped_hyph_is_valid_hyphenator(gHyphenator.mDict.bytes.data(),gHyphenator.mDict.bytes.size()))return 3;
 nsAtom atoms[]={{"en-US"},{"en"},{"xx"},{"ja"},{"zh"},{"de"},{"bad_tag"},{""},{"ja-Jpan"},{"ja-jpan"},{"und-Hans"},{"zh-Hant"},{"invalid--tag"},{"th"},{"und-Hrkt"}};
 std::string line;
 while(std::getline(std::cin,line)){
  std::istringstream in(line);std::string id;in>>id;traceCase=id;
  nsLineBreaker breaker;std::vector<std::unique_ptr<CaptureSink>> sinks;std::vector<int> errors;size_t base=0;bool trailing=false;char op;std::map<unsigned,std::shared_ptr<nsTransformedTextRun>> runs;unsigned nextOwner=0;int requestedOwner=-1;size_t requestedOffset=0;
  unsigned operation=0;
  while(in>>op){
   std::cout<<id<<" OP "<<operation++<<' '<<op<<"\n";
   if(op=='P'){in>>requestedOwner>>requestedOffset;}
   else if(op=='S'){unsigned w,p,s;in>>w>>p>>s;breaker.SetHyphenateLimitChars(w,p,s);}
   else if(op=='A'){
    int encoding,flags,language,hasSink;size_t n;in>>encoding>>flags>>language>>hasSink>>n;
    std::vector<char16_t> u(n);std::vector<uint8_t>b(n);for(size_t i=0;i<n;i++){unsigned x;in>>x;u[i]=x;b[i]=x;}
    unsigned owner=requestedOwner<0?nextOwner++:unsigned(requestedOwner);size_t offset=requestedOwner<0?base:requestedOffset;auto& run=runs[owner];if(!run)run=std::make_shared<nsTransformedTextRun>();auto sink=std::make_unique<CaptureSink>(n,offset,owner,run);base+=n;requestedOwner=-1;
    sink->instance=sinks.size();auto ptr=hasSink?sink.get():nullptr;sinks.push_back(std::move(sink));
    assert(n>0);nsAtom*lang=language<0?nullptr:&atoms[language];
    errors.push_back(encoding==8?breaker.AppendText(lang,b.data(),n,flags,ptr):breaker.AppendText(lang,u.data(),n,flags,ptr));
   }else if(op=='W'){unsigned flags;in>>flags;errors.push_back(breaker.AppendInvisibleWhitespace(flags));}
   else if(op=='B'){int mode;in>>mode;breaker.SetWordBreak(mozilla::intl::WordBreakRule(mode));}
   else if(op=='T'){int mode;in>>mode;breaker.SetStrictness(mozilla::intl::LineBreakRule(mode));}
   else if(op=='C'){bool continuation;in>>continuation;breaker.SetWordContinuation(continuation);}
   else if(op=='R'){errors.push_back(breaker.Reset(&trailing));}
   else if(op=='F'){in>>gFailAt;gAllocations=0;}
   else if(op=='D'){
    size_t n;in>>n;std::u16string word;for(size_t i=0;i<n;i++){unsigned x;in>>x;word.push_back(x);}
    nsTArray<bool> mask;auto result=gHyphenator.Hyphenate(nsAString(word.data(),word.data()+word.size()),mask);
    std::cout<<id<<" DICT "<<result<<" ";for(size_t i=0;i<mask.Length();i++)std::cout<<(mask[i]?'1':'0');std::cout<<"\n";
   }else return 4;
   dump_state(id,breaker);
  }
  gFailAt=-1;errors.push_back(breaker.Reset(&trailing));dump_state(id,breaker);
  std::cout<<id<<" BREAKS ";for(auto&sink:sinks)for(auto x:sink->breaks)std::cout<<unsigned(x);
  std::cout<<" GLYPHS ";for(auto&sink:sinks)for(size_t i=0;i<sink->breaks.size();++i)std::cout<<unsigned(sink->run->glyphs[sink->base+i].CanBreakBefore());
  std::cout<<" CAPS ";for(auto&sink:sinks)for(auto x:sink->caps)std::cout<<unsigned(x);
  std::cout<<" ERR ";for(auto x:errors)std::cout<<x;std::cout<<" TRAIL "<<trailing<<" CALLS";
  for(auto&sink:sinks)for(auto&call:sink->calls)std::cout<<" "<<sink->base<<":"<<call;
  std::cout<<"\n";
 }
 traceCase="shutdown";for(auto& action:shutdownActions) action();for(auto& atom:atoms) assert(atom.refs==1);

}
