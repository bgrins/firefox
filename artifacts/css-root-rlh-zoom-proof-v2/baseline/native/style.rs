#![allow(dead_code, non_snake_case, unused_imports)]
use std::cell::{Cell,RefCell};
use std::sync::atomic::{AtomicBool,AtomicU32,Ordering};
use std::ops::Deref;
use std::io::{self,BufRead};
type CSSFloat=f32;
type Length=CSSPixelLength;
thread_local! { static PREPARING:Cell<bool>=Cell::new(false); static PREPARATION:RefCell<Vec<Vec<(u32,u32,u32,u32)>>>=RefCell::new(Vec::new()); static TRACE:RefCell<Vec<(u32,u32,u32,u32)>>=RefCell::new(Vec::new()); }
#[no_mangle]
pub extern "C" fn capsule_trace(kind:u32,owner:u32,a:f32,b:f32) {
    TRACE.with(|t|t.borrow_mut().push((kind,owner,a.to_bits(),b.to_bits())));
}
#[repr(C)] struct RawContext{_opaque:[u8;0]}
#[repr(C)] struct RawElement{_opaque:[u8;0]}
unsafe extern "C" {
    #[link_name="Gecko_CalcLineHeight"] fn native_line_height(lh:*const LineHeight,pc:*const RawContext,vertical:bool,font:*const FontData,element:*const RawElement)->i32;
    fn capsule_context(present:bool)->*const RawContext;
    fn capsule_cssom(length:f32,zoom:f32)->f32;
}
mod bindings {
    use super::*;
    pub unsafe fn Gecko_CalcLineHeight(lh:*const LineHeight,pc:*const RawContext,vertical:bool,font:*const FontData,element:*const RawElement)->i32 {
        let result=unsafe {native_line_height(lh,pc,vertical,font,element)};
        capsule_trace(22,unsafe{(*font).font.owner},result as f32,0.0);
        result
    }
}
#[derive(Clone,Copy,Debug,PartialEq)] struct CSSPixelLength(f32);
impl CSSPixelLength {fn new(x:f32)->Self{Self(x)}}
#[derive(Clone,Copy,Debug)] struct NonNegativeLength(CSSPixelLength);
impl NonNegativeLength {fn new(x:f32)->Self{Self(CSSPixelLength(x))}fn px(self)->f32{self.0.0}}
#[derive(Clone,Copy,Debug,PartialEq)] struct Zoom(f32);
impl Zoom {const ONE:Self=Self(1.0);fn value(self)->f32{self.0}}
const AU_PER_PX:i32=60;
const MAX_AU:Au=Au((1<<30)-1); const MIN_AU:Au=Au(-((1<<30)-1));
#[derive(Clone,Copy)] struct Au(i32);
#[repr(C,u32)] #[derive(Clone,Copy)] enum LineHeight {Length(f32),Number(f32),Normal}
#[repr(C)] #[derive(Clone,Copy)] struct NativeFont {size:f32,owner:u32,em:i32,internal:i32,external:i32}
#[repr(C)] #[derive(Clone,Copy)] struct FontData {lh:LineHeight,font:NativeFont,explicit:u32}
#[derive(Clone)] struct Font(FontData);
impl Deref for Font {type Target=FontData;fn deref(&self)->&FontData{&self.0}}
impl Font {
    fn get_line_height(&self)->&LineHeight{&self.0.lh}
    fn slow_clone_font_size(&self)->FontSize{capsule_trace(1,self.0.font.owner,self.0.font.size,0.0);FontSize{computed_size:NonNegative(CSSPixelLength(self.0.font.size)),used_size:NonNegative(CSSPixelLength(self.0.font.size)),keyword_info:0}}
}
#[derive(Clone,Copy)]struct NonNegative<T>(T);
#[derive(Clone,Copy)] struct FontSize{computed_size:NonNegative<Length>,used_size:NonNegative<Length>,keyword_info:u32}
mod computed {pub type Length=super::CSSPixelLength; pub type FontSize=super::FontSize; pub type NonNegativeLength=super::NonNegativeLength;pub type LineHeight=super::LineHeight;}
mod properties {pub mod style_structs {pub type Font=super::super::Font;}}
mod computed_value_flags {pub struct ComputedValueFlags;impl ComputedValueFlags {
    pub const USES_FONT_OR_WM_RELATIVE_UNITS:u32=1;
    pub const DEPENDS_ON_SELF_FONT_METRICS:u32=2;
    pub const DEPENDS_ON_INHERITED_FONT_METRICS:u32=4;
}}
use computed_value_flags::ComputedValueFlags;
#[derive(Clone,Copy)]struct WritingMode{vertical:bool}
impl WritingMode {fn is_text_vertical(self)->bool{self.vertical}fn is_upright(self)->bool{self.vertical}}
#[derive(Clone,Copy,PartialEq)]enum FontBaseSize{CurrentStyle,InheritedStyle}
#[derive(Clone,Copy,PartialEq)]enum LineHeightBase{CurrentStyle,InheritedStyle}
#[derive(Clone,Copy,Debug,PartialEq)]enum LengthUnit{Em,Lh,Ex,Ch,Cap,Ic,Rex,Rch,Rcap,Ric,Rem,Rlh,Px,ServoCharacterWidth}
impl LengthUnit {fn is_font_relative(self)->bool{!matches!(self,Self::Px|Self::ServoCharacterWidth)}fn is_viewport_percentage(self)->bool{false}fn is_container_relative(self)->bool{false}}
#[derive(Clone,Copy)]enum FontMetricsOrientation{Horizontal,MatchContextPreferHorizontal,MatchContextPreferVertical}
struct QueryFontMetricsFlags(u32);
impl QueryFontMetricsFlags{const NEEDS_CH:Self=Self(1);const NEEDS_IC:Self=Self(2);fn empty()->Self{Self(0)}}
struct FontMetrics{value:f32}
impl FontMetrics {
    fn x_height_or_default(&self,_:CSSPixelLength)->CSSPixelLength{CSSPixelLength(self.value)}
    fn zero_advance_measure_or_default(&self,_:CSSPixelLength,_:bool)->CSSPixelLength{CSSPixelLength(self.value)}
    fn cap_height_or_default(&self)->CSSPixelLength{CSSPixelLength(self.value)}
    fn ic_width_or_default(&self,_:CSSPixelLength)->CSSPixelLength{CSSPixelLength(self.value)}
}
#[derive(Clone)]struct Builder {
    font:Font,parent:Font,is_root_element:bool,effective_zoom:Zoom,effective_zoom_for_inheritance:Zoom,writing_mode:WritingMode,flags:Cell<u32>,owner:u32
}
impl Builder {
    fn get_font(&self)->&Font{capsule_trace(2,self.font.0.font.owner,0.0,0.0);&self.font}
    fn get_parent_font(&self)->&Font{capsule_trace(3,self.parent.0.font.owner,0.0,0.0);&self.parent}
    fn add_flags(&self,f:u32){self.flags.set(self.flags.get()|f)}
}
struct GeckoElement(*const RawElement);
struct Device {root_line_height:AtomicU32,used_root_line_height:AtomicBool,has_pc:bool,root_metrics:f32,owner:u32}
impl Device {
    fn pres_context(&self)->Option<*const RawContext>{if self.has_pc {Some(unsafe{capsule_context(true)})}else{None}}
    fn root_font_size(&self)->CSSPixelLength{capsule_trace(4,self.owner,self.root_metrics,0.0);CSSPixelLength(self.root_metrics)}
    fn root_font_metrics_ex(&self)->CSSPixelLength{self.root_font_size()}
    fn root_font_metrics_ch(&self)->CSSPixelLength{self.root_font_size()}
    fn root_font_metrics_cap(&self)->CSSPixelLength{self.root_font_size()}
    fn root_font_metrics_ic(&self)->CSSPixelLength{self.root_font_size()}
}
#[derive(Default)]struct Conditions{font:Option<f32>,lh:Option<f32>}
impl Conditions {fn set_font_size_dependency(&mut self,v:NonNegative<Length>){self.font=Some(v.0.0)}fn set_line_height_dependency(&mut self,v:NonNegativeLength){self.lh=Some(v.px())}}
struct Context<'a>{builder:&'a Builder,device:&'a Device,default:&'a Builder,in_media_query:bool,for_non_inherited_property:bool,rule_cache_conditions:RefCell<Conditions>}
impl Context<'_> {
    fn style(&self)->&Builder{self.builder}
    fn device(&self)->&Device{self.device}
    fn default_style(&self)->&Builder{self.default}
    fn query_font_metrics(&self,base:FontBaseSize,_:FontMetricsOrientation,flags:QueryFontMetricsFlags)->FontMetrics {
        let f=if base==FontBaseSize::CurrentStyle{self.builder.get_font()}else{self.builder.get_parent_font()};
        capsule_trace(5,f.0.font.owner,flags.0 as f32,0.0);FontMetrics{value:8.0}
    }
    fn maybe_zoom_text(&self,v:CSSPixelLength)->CSSPixelLength{v}
}
struct ResolvedContext<'a>{style:&'a Builder}
struct NoCalcLength {unit:LengthUnit,value:f32}
impl NoCalcLength {
    fn to_px_if_absolute(&self)->Option<f32>{if self.unit==LengthUnit::Px{Some(self.value)}else{None}}
    fn length_unit(&self)->LengthUnit{self.unit}
    fn should_zoom_text(&self)->bool{self.unit==LengthUnit::Px}
    fn viewport_percentage_to_computed_value(&self,_:&Context)->CSSPixelLength{panic!("viewport adapter outside admitted domain")}
    fn container_relative_to_computed_value(&self,_:&Context)->CSSPixelLength{panic!("container adapter outside admitted domain")}
    fn servo_character_width_to_computed_value(&self,_:CSSPixelLength)->CSSPixelLength{panic!("character adapter outside admitted domain")}
}
include!(env!("RLH_EXTRACTED"));
const MUTANT:u32 = match option_env!("RLH_MUTANT") { Some(v) => if v.len()==2 {10} else {(v.as_bytes()[0]-b'0') as u32}, None => 0 };
fn font(owner:u32,size:f32,tag:u32,value:f32)->Font {
    Font(FontData{lh:match tag{0=>LineHeight::Length(value),1=>LineHeight::Number(value),_=>LineHeight::Normal},font:NativeFont{size,owner,em:(size*60.0)as i32,internal:60,external:120},explicit:0})
}
include!("runner.rs");
