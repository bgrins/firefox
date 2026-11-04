use std::sync::atomic::{AtomicUsize, Ordering};
use style_traits::arc_slice::ArcSlice;

#[repr(align(64))]
struct High([u8; 64]);
struct Zst;
#[repr(align(64))]
struct HighZst;
static ZST_DROPS: AtomicUsize = AtomicUsize::new(0);
static HIGH_ZST_DROPS: AtomicUsize = AtomicUsize::new(0);
impl Drop for Zst {
    fn drop(&mut self) { ZST_DROPS.fetch_add(1, Ordering::Relaxed); }
}
impl Drop for HighZst {
    fn drop(&mut self) { HIGH_ZST_DROPS.fetch_add(1, Ordering::Relaxed); }
}

fn empty<T>(name: &str, iter: bool) {
    assert_eq!(std::mem::size_of::<ArcSlice<T>>(), std::mem::size_of::<usize>());
    let value: ArcSlice<T> = if iter {
        ArcSlice::from_iter(std::iter::empty())
    } else {
        ArcSlice::default()
    };
    let borrowed: &[T] = &value;
    assert_eq!(borrowed.len(), 0);
    assert_eq!(borrowed.as_ptr().addr() % std::mem::align_of::<T>(), 0);
    let cloned = value.clone();
    assert_eq!(borrowed.as_ptr(), cloned.as_ptr());
    assert_eq!(borrowed.len(), 0);
    drop(value);
    assert_eq!(cloned.len(), 0);
    drop(cloned);
    println!("empty {name} {} read-clone-drop passed", if iter { "from_iter" } else { "default" });
}

fn main() {
    let mode = std::env::args().nth(1).unwrap();
    let variant = std::env::args().nth(2).unwrap();
    let type_name = std::any::type_name::<servo_arc::ThinArc<u64, u64>>();
    let owner = servo_arc::ThinArc::from_header_and_iter(0u64, std::iter::empty::<u64>());
    let view = &*owner;
    let words = std::mem::size_of_val(&view) / std::mem::size_of::<usize>();
    assert_eq!(type_name.contains("dst_thin::ThinArc"), variant == "dst");
    assert_eq!(words, if variant == "dst" { 2 } else { 1 });
    println!("variant={variant} thin_type={type_name} header_reference_words={words}");
    drop(owner);
    assert_eq!(cfg!(debug_assertions), mode == "on");
    println!("debug_assertions={}", cfg!(debug_assertions));
    for iter in [false, true] {
        empty::<u64>("u64", iter);
        empty::<High>("align64-sized", iter);
        empty::<Zst>("zst", iter);
        empty::<HighZst>("align64-zst", iter);
    }
    assert_eq!(ZST_DROPS.load(Ordering::Relaxed), 0);
    assert_eq!(HIGH_ZST_DROPS.load(Ordering::Relaxed), 0);
    assert!(std::panic::catch_unwind(|| ArcSlice::from_iter([Zst, Zst, Zst].into_iter())).is_err());
    assert_eq!(ZST_DROPS.load(Ordering::Relaxed), 3);
    assert!(std::panic::catch_unwind(|| ArcSlice::from_iter([HighZst, HighZst, HighZst].into_iter())).is_err());
    assert_eq!(HIGH_ZST_DROPS.load(Ordering::Relaxed), 3);
    println!("eight empty cases and two nonempty ZST refusals passed");
}
