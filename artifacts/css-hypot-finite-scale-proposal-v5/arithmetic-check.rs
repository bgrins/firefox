fn before(values: &[f32]) -> f32 {
    let mut value = values[0].powi(2);
    for child in values.iter().skip(1) {
        value += child.powi(2);
    }
    value.sqrt()
}

fn hypot(a: f32, b: f32) -> f32 {
    let a = a as f64;
    let b = b as f64;
    (a * a + b * b).sqrt() as f32
}

fn after(values: &[f32]) -> f32 {
    let mut value = values[0].abs();
    for child in values.iter().skip(1) {
        value = hypot(value, *child);
    }
    value
}

fn main() {
    let large = f32::from_bits(0x5f800000);
    let tiny = f32::from_bits(0x17800000);
    let den_large = f32::from_bits(0x60000000);
    let den_tiny = f32::from_bits(0x18000000);
    for (name, value, denominator, old) in [
        ("large", large, den_large, f32::INFINITY),
        ("tiny", tiny, den_tiny, 0.0),
    ] {
        for values in [vec![value], vec![value, 0.0], vec![0.0, value], vec![-value, 0.0]] {
            let baseline = before(&values) / denominator;
            let candidate = after(&values) / denominator;
            assert_eq!(baseline.to_bits(), old.to_bits());
            assert_eq!(candidate.to_bits(), 0.5f32.to_bits());
            println!("{name} {values:?}: before={:08x}, after={:08x}", baseline.to_bits(), candidate.to_bits());
        }
    }
    let controls: Vec<(&str, Vec<f32>, f32)> = vec![
        ("ordinary", vec![3.0, 4.0], 5.0),
        ("three", vec![2.0, 3.0, 6.0], 7.0),
        ("four large", vec![large; 4], 2.0 * large),
        ("four tiny", vec![tiny; 4], 2.0 * tiny),
        ("positive zero", vec![0.0], 0.0),
        ("negative zero", vec![-0.0], 0.0),
        ("zero pair", vec![-0.0, -0.0], 0.0),
        ("zero mixed", vec![0.0, -0.0], 0.0),
        ("minimum subnormal", vec![f32::from_bits(1), 0.0], f32::from_bits(1)),
        ("positive infinity", vec![f32::INFINITY, 1.0], f32::INFINITY),
        ("negative infinity", vec![f32::NEG_INFINITY, 1.0], f32::INFINITY),
        ("infinity pair", vec![f32::NEG_INFINITY, f32::INFINITY], f32::INFINITY),
        ("true result overflow", vec![f32::MAX, f32::MAX], f32::INFINITY),
    ];
    for (name, values, expected) in controls {
        let actual = after(&values);
        assert_eq!(actual.to_bits(), expected.to_bits(), "{name}");
        println!("control {name}: {:08x}", actual.to_bits());
    }
    for values in [vec![f32::NAN], vec![f32::NAN, f32::INFINITY],
                   vec![f32::INFINITY, f32::NAN], vec![1.0, f32::NAN],
                   vec![f32::MAX, f32::MAX, f32::NAN]] {
        assert!(after(&values).is_nan());
        assert!(before(&values).is_nan());
        println!("NaN precedence {values:?}: PASS");
    }
    println!("PASS: 8 finite-extreme witnesses, 13 controls, 5 NaN cases; extracted arithmetic only");
}
