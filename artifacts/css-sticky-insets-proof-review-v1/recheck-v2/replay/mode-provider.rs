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
 const VERTICAL:Self=Self(1 << 0);
const INLINE_REVERSED:Self=Self(1 << 1);
const VERTICAL_LR:Self=Self(1 << 2);
const LINE_INVERTED:Self=Self(1 << 3);
const RTL:Self=Self(1 << 4);
const VERTICAL_SIDEWAYS:Self=Self(1 << 5);
const TEXT_SIDEWAYS:Self=Self(1 << 6);
const UPRIGHT:Self=Self(1 << 7);
const WRITING_MODE_HORIZONTAL_TB:Self=Self(0);
const WRITING_MODE_VERTICAL_RL:Self=Self(WritingMode::VERTICAL.bits());
const WRITING_MODE_VERTICAL_LR:Self=Self(WritingMode::VERTICAL.bits() |
                                         WritingMode::VERTICAL_LR.bits() |
                                         WritingMode::LINE_INVERTED.bits());
const WRITING_MODE_SIDEWAYS_RL:Self=Self(WritingMode::VERTICAL.bits() |
                                         WritingMode::VERTICAL_SIDEWAYS.bits());
const WRITING_MODE_SIDEWAYS_LR:Self=Self(WritingMode::VERTICAL.bits() |
                                         WritingMode::VERTICAL_LR.bits() |
                                         WritingMode::VERTICAL_SIDEWAYS.bits());
 pub fn new(inheritedbox_style: &style_structs::InheritedBox) -> Self {
        use crate::properties::longhands::direction::computed_value::T as Direction;

        let mut flags = WritingMode::empty();

        let direction = *inheritedbox_style.get_direction();
        let writing_mode = *inheritedbox_style.get_writing_mode();

        match direction {
            Direction::Ltr => {},
            Direction::Rtl => {
                flags.insert(WritingMode::RTL);
            },
        }

        match writing_mode {
            WritingModeProperty::HorizontalTb => {
                if direction == Direction::Rtl {
                    flags.insert(WritingMode::INLINE_REVERSED);
                }
            },
            WritingModeProperty::VerticalRl => {
                flags.insert(WritingMode::WRITING_MODE_VERTICAL_RL);
                if direction == Direction::Rtl {
                    flags.insert(WritingMode::INLINE_REVERSED);
                }
            },
            WritingModeProperty::VerticalLr => {
                flags.insert(WritingMode::WRITING_MODE_VERTICAL_LR);
                if direction == Direction::Rtl {
                    flags.insert(WritingMode::INLINE_REVERSED);
                }
            },
            #[cfg(feature = "gecko")]
            WritingModeProperty::SidewaysRl => {
                flags.insert(WritingMode::WRITING_MODE_SIDEWAYS_RL);
                if direction == Direction::Rtl {
                    flags.insert(WritingMode::INLINE_REVERSED);
                }
            },
            #[cfg(feature = "gecko")]
            WritingModeProperty::SidewaysLr => {
                flags.insert(WritingMode::WRITING_MODE_SIDEWAYS_LR);
                if direction == Direction::Ltr {
                    flags.insert(WritingMode::INLINE_REVERSED);
                }
            },
        }

        #[cfg(feature = "gecko")]
        {
            use crate::properties::longhands::text_orientation::computed_value::T as TextOrientation;

            // text-orientation only has an effect for vertical-rl and
            // vertical-lr values of writing-mode.
            match writing_mode {
                WritingModeProperty::VerticalRl | WritingModeProperty::VerticalLr => {
                    match *inheritedbox_style.get_text_orientation() {
                        TextOrientation::Mixed => {},
                        TextOrientation::Upright => {
                            flags.insert(WritingMode::UPRIGHT);

                            // https://drafts.csswg.org/css-writing-modes-3/#valdef-text-orientation-upright:
                            //
                            // > This value causes the used value of direction
                            // > to be ltr, and for the purposes of bidi
                            // > reordering, causes all characters to be treated
                            // > as strong LTR.
                            flags.remove(WritingMode::RTL);
                            flags.remove(WritingMode::INLINE_REVERSED);
                        },
                        TextOrientation::Sideways => {
                            flags.insert(WritingMode::TEXT_SIDEWAYS);
                        },
                    }
                },
                _ => {},
            }
        }

        flags
    }
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
