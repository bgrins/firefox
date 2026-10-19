#include <cstdint>
#include <fstream>
#include <vector>
extern "C" void* mapped_hyph_compile_buffer(const uint8_t*,uint32_t,bool);
extern "C" uint32_t mapped_hyph_compiled_data_size(const void*);
extern "C" const uint8_t* mapped_hyph_compiled_data_ptr(const void*);
extern "C" void mapped_hyph_free_compiled_data(void*);
int main(int argc,char**argv){
 if(argc!=3)return 2;
 std::ifstream in(argv[1],std::ios::binary);std::vector<uint8_t> bytes(std::istreambuf_iterator<char>(in),{});
 void* data=mapped_hyph_compile_buffer(bytes.data(),bytes.size(),false);if(!data)return 3;
 std::ofstream out(argv[2],std::ios::binary);out.write(reinterpret_cast<const char*>(mapped_hyph_compiled_data_ptr(data)),mapped_hyph_compiled_data_size(data));mapped_hyph_free_compiled_data(data);return out?0:4;
}
