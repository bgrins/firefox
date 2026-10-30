use specified::{Color, Function, Item, Mix};
use values::generics::image::*;
fn component(v: GenericValueComponent) -> bool { SpecifiedValue { v: ValueInner::Component(v) }.depends_on_color_scheme() }
fn color(v: Color) -> bool { component(GenericValueComponent::Color(v)) }
fn image(v: Image) -> bool { component(GenericValueComponent::Image(v)) }
#[test] fn selected_non_color() { assert!(!component(GenericValueComponent::CustomIdent(()))); assert!(!component(GenericValueComponent::String(()))); }
#[test] fn independent_colors() { assert!(!color(Color::Absolute(()))); assert!(!color(Color::CurrentColor)); assert!(!color(Color::InheritFromBodyQuirk)); }
#[test] fn direct_scheme_reads() { assert!(color(Color::System(()))); assert!(color(Color::LightDark(()))); }
#[test] fn relative_origin() { assert!(color(Color::ColorFunction(Box::new(Function(Some(Box::new(Color::System(())))))))); assert!(!color(Color::ColorFunction(Box::new(Function(None))))); }
#[test] fn mix_all_items() { assert!(color(Color::ColorMix(Box::new(Mix { items: vec![Item {color: Color::Absolute(())}, Item {color: Color::System(())}] })))); }
#[test] fn contrast() { assert!(color(Color::ContrastColor(Box::new(Color::LightDark(()))))); }
#[test] fn repeated_components() { assert!(SpecifiedValue { v: ValueInner::List(List { components: vec![GenericValueComponent::Color(Color::Absolute(())), GenericValueComponent::Color(Color::System(()))] }) }.depends_on_color_scheme()); }
#[test] fn universal_tokens() { assert!(!SpecifiedValue { v: ValueInner::Universal(()) }.depends_on_color_scheme()); }
#[test] fn linear_gradient() { assert!(image(Image::Gradient(Box::new(Gradient::Linear {items: vec![GradientItem::InterpolationHint(()), GradientItem::SimpleColorStop(Color::System(()))]})))); }
#[test] fn radial_gradient() { assert!(image(Image::Gradient(Box::new(Gradient::Radial {items: vec![GradientItem::ComplexColorStop {color: Color::LightDark(()), position: ()}]})))); }
#[test] fn conic_gradient() { assert!(image(Image::Gradient(Box::new(Gradient::Conic {items: vec![GradientItem::SimpleColorStop(Color::System(()))]})))); }
#[test] fn crossfade_color() { assert!(image(Image::CrossFade(Box::new(Fade {elements: vec![FadeItem {image: CrossFadeImage::Color(Color::System(()))}]})))); }
#[test] fn crossfade_image() { assert!(image(Image::CrossFade(Box::new(Fade {elements: vec![FadeItem {image: CrossFadeImage::Image(Image::LightDark(()))}]})))); }
#[test] fn image_set_all_candidates() { assert!(image(Image::ImageSet(Box::new(Set {items: vec![SetItem {image: Image::Url(())}, SetItem {image: Image::Image(Box::new(Color::System(())))}]})))); }
#[test] fn image_independence() { assert!(!image(Image::Url(()))); assert!(!image(Image::Image(Box::new(Color::Absolute(()))))); assert!(!image(Image::None)); }
#[test] fn image_light_dark() { assert!(image(Image::LightDark(()))); }
