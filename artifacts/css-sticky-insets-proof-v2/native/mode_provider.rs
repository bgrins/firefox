#![allow(dead_code)]
#[derive(Clone,Copy,PartialEq)]
pub enum WritingModeProperty { HorizontalTb, VerticalRl, VerticalLr, SidewaysRl, SidewaysLr }
#[derive(Clone,Copy,PartialEq)]
pub enum Direction { Ltr, Rtl }
#[derive(Clone,Copy)]
pub enum TextOrientation { Mixed, Upright, Sideways }
mod properties {pub mod longhands {
 pub mod direction {pub mod computed_value {pub type T=crate::Direction;}}
 pub mod text_orientation {pub mod computed_value {pub type T=crate::TextOrientation;}}
}}
mod style_structs {
 pub struct InheritedBox(pub crate::Direction,pub crate::WritingModeProperty,pub crate::TextOrientation);
 impl InheritedBox {
  pub fn get_direction(&self)->&crate::Direction {&self.0}
  pub fn get_writing_mode(&self)->&crate::WritingModeProperty {&self.1}
  pub fn get_text_orientation(&self)->&crate::TextOrientation {&self.2}
 }
}
#[derive(Clone,Copy)]
struct WritingMode(u8);
impl WritingMode {
 const fn bits(self)->u8 {self.0}
 fn empty()->Self {Self(0)}
 fn insert(&mut self,value:Self){self.0|=value.0;}
 fn remove(&mut self,value:Self){self.0&=!value.0;}
 @@CONSTANTS@@
 @@CONSTRUCTOR@@
}
fn main(){
 for (m,mode) in [WritingModeProperty::HorizontalTb,WritingModeProperty::VerticalRl,WritingModeProperty::VerticalLr,WritingModeProperty::SidewaysRl,WritingModeProperty::SidewaysLr].into_iter().enumerate(){
  for (d,direction) in [Direction::Ltr,Direction::Rtl].into_iter().enumerate(){
   for (o,orientation) in [TextOrientation::Mixed,TextOrientation::Upright,TextOrientation::Sideways].into_iter().enumerate(){
    let flags=WritingMode::new(&style_structs::InheritedBox(direction,mode,orientation));
    println!("[{}, {}, {}, {}]",m,d,o,flags.bits());
   }
  }
 }
}
