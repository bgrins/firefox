#![allow(dead_code, unused_variables)]
mod specified {
    pub enum Color {
        System(()), LightDark(()), ColorFunction(Box<Function>), ColorMix(Box<Mix>),
        ContrastColor(Box<Color>), CurrentColor, Absolute(()), InheritFromBodyQuirk,
    }
    pub struct Function(pub Option<Box<Color>>);
    impl Function { pub fn origin_color(&self) -> Option<&Color> { self.0.as_deref() } }
    pub struct Mix { pub items: Vec<Item> }
    pub struct Item { pub color: Color }
    pub type Image = crate::values::generics::image::Image;
}
mod values { pub mod generics { pub mod image {
    use crate::specified::Color;
    pub enum GradientItem<C, T> { SimpleColorStop(C), ComplexColorStop { color: C, position: T }, InterpolationHint(T) }
    pub enum Gradient {
        Linear { items: Vec<GradientItem<Color, ()>> },
        Radial { items: Vec<GradientItem<Color, ()>> },
        Conic { items: Vec<GradientItem<Color, u8>> },
    }
    pub enum Image {
        LightDark(()), Image(Box<Color>), Gradient(Box<Gradient>), CrossFade(Box<Fade>),
        ImageSet(Box<Set>), None, Url(()), Element(()), MozSymbolicIcon(()),
        #[cfg(feature = "servo")] PaintWorklet(()),
    }
    pub struct Fade { pub elements: Vec<FadeItem> }
    pub struct FadeItem { pub image: CrossFadeImage }
    pub enum CrossFadeImage { Image(Image), Color(Color) }
    pub struct Set { pub items: Vec<SetItem> }
    pub struct SetItem { pub image: Image }
}}}
pub enum GenericValueComponent {
    Color(specified::Color), Image(specified::Image), TransformList(List<GenericValueComponent>),
    Length(()), Number(()), Percentage(()), LengthPercentage(()), Url(()), Integer(()),
    Angle(()), Time(()), Resolution(()), TransformFunction(()), CustomIdent(()), String(()),
}
pub type SpecifiedValueComponent = GenericValueComponent;
pub struct List<T> { pub components: Vec<T> }
pub enum ValueInner<T> { Component(T), List(List<T>), Universal(()) }
pub struct SpecifiedValue { pub v: ValueInner<SpecifiedValueComponent> }
