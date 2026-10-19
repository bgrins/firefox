#include <cstdint>
#include <cstdio>
extern "C" {void u_getVersion(uint8_t*); int32_t uscript_getScript(int32_t,int32_t*); int32_t uloc_addLikelySubtags(const char*,char*,int32_t,int32_t*);}
int main(){uint8_t v[4];u_getVersion(v);int32_t e=0;char b[256];auto n=uloc_addLikelySubtags("ja",b,256,&e);std::printf("%u.%u.%u.%u %s %d %d script=%d\n",v[0],v[1],v[2],v[3],b,n,e,uscript_getScript(0x0e01,&e));}
