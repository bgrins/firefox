#include <cstdio>
struct Matrix { double entries[6]{1,0,0,1,17,23}; };
struct Params {
  const Matrix& matrix;
  explicit Params(const Matrix& value [[clang::lifetimebound]]):matrix(value){}
};
__attribute__((noinline)) double consume(const Params& p){return p.matrix.entries[4];}
int main(){
#ifdef DANGLING
  Params params{Matrix()};
#else
  Matrix owner;
  Params params{owner};
#endif
  std::printf("%g\n",consume(params));
}
