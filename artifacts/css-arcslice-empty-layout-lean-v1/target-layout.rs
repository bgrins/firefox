use std::mem::{align_of, size_of};
use std::sync::atomic::AtomicUsize;

fn main() {
    let layouts = [
        ("usize", size_of::<usize>(), align_of::<usize>()),
        ("u64", size_of::<u64>(), align_of::<u64>()),
        ("AtomicUsize", size_of::<AtomicUsize>(), align_of::<AtomicUsize>()),
    ];
    for (name, size, alignment) in layouts {
        assert_eq!((size, alignment), (8, 8));
        println!("{name}: size={size}, alignment={alignment}");
    }
}
