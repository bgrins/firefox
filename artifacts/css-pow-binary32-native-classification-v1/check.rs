use std::hint::black_box;

fn main() {
    let mut count = 0u64;
    for bits in 0..=u32::MAX {
        let value = black_box(f32::from_bits(bits));
        let magnitude = bits & 0x7fff_ffff;
        assert_eq!(value.is_nan(), magnitude > 0x7f80_0000, "NaN at {bits:08x}");
        assert_eq!(value.is_infinite(), magnitude == 0x7f80_0000, "infinity at {bits:08x}");
        assert_eq!(value.abs() == 1.0, magnitude == 0x3f80_0000, "unit at {bits:08x}");
        count += 1;
    }
    assert_eq!(count, 1u64 << 32);
    println!("All {count} binary32 encodings matched all three native predicates");
}
