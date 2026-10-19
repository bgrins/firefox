template<class T>void runTransform(std::istream&in,int compression,int incoming,nsAtom*lang,size_t n){
 std::vector<T> input(n),output(n+1);for(auto&c:input){unsigned value;in>>value;c=T(value);}
 gfxSkipChars skip;uint8_t context=incoming;nsTextFrameUtils::Flags flags{};
 auto end=nsTextFrameUtils::TransformText(input.data(),n,output.data(),nsTextFrameUtils::CompressionMode(compression),&context,&skip,&flags,lang);
 std::cout<<"OUT";for(auto p=output.data();p!=end;++p)std::cout<<" "<<unsigned(*p);
 std::cout<<" SKIP ";gfxSkipCharsIterator it(skip);for(size_t i=0;i<n;i++,it.AdvanceOriginal(1))std::cout<<it.IsOriginalCharSkipped();
 std::cout<<" CONTEXT "<<unsigned(context)<<" FLAGS "<<unsigned(flags)<<" COUNT "<<skip.GetOriginalCharCount()<<" KEPT "<<it.GetSkippedOffset()<<"\n";
}
int main(){std::string line;while(std::getline(std::cin,line)){std::istringstream in(line);std::string id,language;int width,compression,incoming;size_t n;in>>id>>width>>compression>>incoming>>language>>n;nsAtom atom{language};std::cout<<id<<" ";if(width==8)runTransform<uint8_t>(in,compression,incoming,language=="-"?nullptr:&atom,n);else runTransform<char16_t>(in,compression,incoming,language=="-"?nullptr:&atom,n);}}
