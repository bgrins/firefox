mod actual_font_hooks {
use super::{LonghandId, Seen};
use crate::values::generics::NonNegative;
#[derive(Clone,Copy,Debug,PartialEq)] enum Scale { All, None }
impl Scale { fn text_zoom_enabled(self)->bool{matches!(self,Self::All)} }
struct Device { zoom:f64 }
impl Device { fn unzoom_text(&self,n:f64)->f64{n/self.zoom} }
struct PlatformFont { size:NonNegative<f64> }
struct KeywordInfo {kw:u8,factor:f64,offset:f64}
struct FontSize {computed_size:NonNegative<f64>,used_size:NonNegative<f64>,keyword_info:KeywordInfo}
struct Font {
 mSize:NonNegative<f64>,mScriptUnconstrainedSize:NonNegative<f64>,mFont:PlatformFont,
 mFontSizeKeyword:u8,mFontSizeFactor:f64,mFontSizeOffset:f64,scale:Scale,
}
impl Font {
 fn new(size:f64,scale:Scale)->Self{Self{mSize:NonNegative(size),mScriptUnconstrainedSize:NonNegative(size),mFont:PlatformFont{size:NonNegative(size)},mFontSizeKeyword:7,mFontSizeFactor:2.,mFontSizeOffset:3.,scale}}
 fn get__x_text_scale(&self)->&Scale{&self.scale}
 __FONT_METHODS__
}
struct StyleBuilder<'a> {device:&'a Device,parent:Font,font:Font}
impl StyleBuilder<'_>{fn get_parent_font(&self)->&Font{&self.parent}fn get_font(&self)->&Font{&self.font}fn mutate_font(&mut self)->&mut Font{&mut self.font}}
struct Cascade {seen:Seen}
impl Cascade { __UNZOOM_HOOK__ }
#[test]fn native_unzoom_and_fresh_setter_preserve_computed_vs_used_fields(){
 for fresh in [0.,20.,30.] {
  let device=Device{zoom:2.};let mut builder=StyleBuilder{device:&device,parent:Font::new(80.,Scale::All),font:Font::new(80.,Scale::None)};
  let mut cascade=Cascade{seen:Seen::default()};cascade.seen.longhands.insert(LonghandId::XTextScale);
  cascade.unzoom_fonts_if_needed(&mut builder);assert_eq!(builder.font.mSize.0,40.);assert_eq!(builder.font.mScriptUnconstrainedSize.0,40.);assert_eq!(builder.font.mFont.size.0,40.);
  builder.font.set_font_size(FontSize{computed_size:NonNegative(fresh),used_size:NonNegative(999.),keyword_info:KeywordInfo{kw:0,factor:1.,offset:0.}});
  assert_eq!(builder.font.mSize.0,fresh);assert_eq!(builder.font.mScriptUnconstrainedSize.0,fresh);assert_eq!(builder.font.mFont.size.0,fresh);assert_eq!(builder.font.mFontSizeKeyword,0);assert_eq!(builder.font.mFontSizeOffset,0.);
  if fresh>0. {cascade.unzoom_fonts_if_needed(&mut builder);assert_ne!(builder.font.mSize.0,fresh);}
 }
}
#[test]fn native_unzoom_same_parent_policy_is_noop(){
 let device=Device{zoom:2.};let mut builder=StyleBuilder{device:&device,parent:Font::new(80.,Scale::All),font:Font::new(80.,Scale::All)};let mut cascade=Cascade{seen:Seen::default()};cascade.seen.longhands.insert(LonghandId::XTextScale);cascade.unzoom_fonts_if_needed(&mut builder);assert_eq!(builder.font.mSize.0,80.);
}
}
