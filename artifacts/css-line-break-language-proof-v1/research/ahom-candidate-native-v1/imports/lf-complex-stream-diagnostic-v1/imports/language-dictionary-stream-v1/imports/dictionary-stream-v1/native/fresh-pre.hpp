namespace gfx {
enum class ShapedTextFlags:uint32_t {TEXT_INCOMING_ARABICCHAR=1,TEXT_ENABLE_SPACING=2,TEXT_USE_MATH_SCRIPT=4,TEXT_ENABLE_HYPHEN_BREAKS=8,TEXT_IS_RTL=16,TEXT_TRAILING_ARABICCHAR=32,TEXT_OPTIMIZE_SPEED=64,TEXT_NEED_BOUNDING_BOX=128,TEXT_IS_8BIT=256};
inline ShapedTextFlags operator|(ShapedTextFlags a,ShapedTextFlags b){return ShapedTextFlags(uint32_t(a)|uint32_t(b));}
inline ShapedTextFlags&operator|=(ShapedTextFlags&a,ShapedTextFlags b){return a=a|b;}
inline uint32_t operator&(ShapedTextFlags a,ShapedTextFlags b){return uint32_t(a)&uint32_t(b);}
}
enum class StyleTextAlign{Start,Justify};
enum class StyleTextSecurity{None,Disc};
enum class StyleMathVariant{None,Normal,Bold};
struct TransformStyle{int value=0;TransformStyle(int v=0):value(v){}operator int()const{return value;}bool IsNone()const{return value==0;}bool operator==(const TransformStyle&)const=default;};
struct nsPresContext{int AppUnitsPerDevPixel()const{return 60;}};
struct nsIContent{bool IsMathMLElement(void*)const{return false;}};
namespace nsGkAtoms{inline void*mtext=nullptr;}
struct BidiLevel{bool rtl=false;bool IsRTL()const{return rtl;}};
struct nsStyleText;struct nsStyleFont;
constexpr uint64_t NS_FRAME_IS_IN_SINGLE_CHAR_MI=1,TEXT_IS_IN_TOKEN_MATHML=2,NS_FRAME_MATHML_SCRIPT_DESCENDANT=4;
using nscoord=int;
using StyleTextAlignLast=StyleTextAlign;
