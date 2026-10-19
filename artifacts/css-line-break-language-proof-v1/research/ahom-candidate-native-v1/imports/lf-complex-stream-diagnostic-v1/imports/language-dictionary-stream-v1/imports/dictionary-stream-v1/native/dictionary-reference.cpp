#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
extern "C" bool mapped_hyph_is_valid_hyphenator(const uint8_t*,uint32_t);
extern "C" int32_t mapped_hyph_find_hyphen_values_raw(const uint8_t*,uint32_t,const char*,uint32_t,uint8_t*,uint32_t);
int main(int argc,char**argv){
 if(argc!=2)return 2;std::ifstream file(argv[1],std::ios::binary);std::vector<uint8_t>dictionary(std::istreambuf_iterator<char>(file),{});
 if(!mapped_hyph_is_valid_hyphenator(dictionary.data(),dictionary.size()))return 3;
 size_t n;while(std::cin>>n){std::string text(n,'\0');for(auto&c:text){unsigned value;std::cin>>value;assert(value<256);c=value;}std::vector<uint8_t>values(n);
  auto status=mapped_hyph_find_hyphen_values_raw(dictionary.data(),dictionary.size(),text.data(),n,values.data(),n);
  std::cout<<status;for(auto value:values)std::cout<<' '<<unsigned(value);std::cout<<'\n';
 }
}
