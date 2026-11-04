use style_traits::arc_slice::ArcSlice;
include!("module.rs");

#[test]
fn variant_identity() {
    let variant = env!("TESTED_VARIANT");
    let name = std::any::type_name::<servo_arc::ThinArc<u64, u64>>();
    let owner = servo_arc::ThinArc::from_header_and_iter(0u64, std::iter::empty::<u64>());
    let view = &*owner;
    let words = std::mem::size_of_val(&view) / std::mem::size_of::<usize>();
    assert_eq!(name.contains("dst_thin::ThinArc"), variant == "dst");
    assert_eq!(words, if variant == "dst" { 2 } else { 1 });
    println!("variant={variant} thin_type={name} header_reference_words={words}");
}
