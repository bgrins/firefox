#include "mozilla/ServoStyleConsts.h"
using namespace mozilla;
template<class T> void Compatible() { using S=StyleHeaderSlice<uint64_t,uint64_t>; using D=StyleHeaderSlice<uint64_t,T>; using A=StyleArcInner<S>; using B=StyleArcInner<D>; static_assert(alignof(B)<=alignof(A),"alignment"); static_assert(sizeof(B)<=sizeof(A),"extent"); static_assert(offsetof(A,data)==offsetof(B,data),"base"); static_assert(offsetof(S,header)==offsetof(D,header),"header"); static_assert(offsetof(S,len)==offsetof(D,len),"length"); StyleArcSlice<T> empty; (void)empty.Length(); }
template void Compatible<StyleAtomIdent>();
template void Compatible<StyleCustomIdent>();
template void Compatible<StyleLinkParam>();
template void Compatible<StylePathCommand>();
template void Compatible<StylePiecewiseLinearFunctionEntry>();
template void Compatible<StylePositionTryFallbacksItem>();
template void Compatible<StyleQuotePair>();
template void Compatible<StyleSingleFontFamily>();
template void Compatible<StyleSymbol>();
template void Compatible<StyleSimpleShadow>();
struct alignas(64) High { unsigned char data[64]; }; void Nondefault(const StyleArcSlice<High>& a) { auto b=a; (void)b.AsSpan(); }
void RejectedDefault() { StyleArcSlice<High> value; }
