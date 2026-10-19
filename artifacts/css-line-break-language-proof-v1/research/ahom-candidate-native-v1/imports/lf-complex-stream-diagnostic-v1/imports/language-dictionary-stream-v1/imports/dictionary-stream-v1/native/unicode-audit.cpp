#include "transform-native.hpp"
int main(){
 UVersionInfo version;u_getVersion(version);
 uint32_t widthChanges=0,invalidLower=0,nonIdentity=0;
 for(uint32_t cp=0;cp<=0x10ffff;cp++){
  auto lower=ToLowerCase(cp);assert(lower==uint32_t(u_tolower(cp)));
  if((cp<=0xffff)!=(lower<=0xffff)){std::cout<<"WIDTH "<<cp<<" "<<lower<<"\n";widthChanges++;}
  invalidLower+=lower>0x10ffff;nonIdentity+=lower!=cp;
 }
 std::cout<<"ICU "<<unsigned(version[0])<<"."<<unsigned(version[1])<<"."<<unsigned(version[2])<<"."<<unsigned(version[3])<<" CODEPOINTS 1114112 WIDTH_CHANGES "<<widthChanges<<" INVALID "<<invalidLower<<" LOWER_CHANGED "<<nonIdentity<<"\n";
 return widthChanges||invalidLower;
}
