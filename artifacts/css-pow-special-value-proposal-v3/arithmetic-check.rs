fn pow(a: f32, b: f32) -> f32 {
    if a.is_nan() || b.is_nan() || (a.abs() == 1.0 && b.is_infinite()) {
        return f32::NAN;
    }
    a.powf(b)
}

fn main() {
    let pairs: [(f32, f32); 8] = [
        (1.0, f32::INFINITY), (-1.0, f32::INFINITY),
        (1.0, f32::NEG_INFINITY), (-1.0, f32::NEG_INFINITY),
        (f32::NAN, 0.0), (f32::NAN, -0.0), (1.0, f32::NAN),
        (f32::NAN, f32::NAN),
    ];
    for (a, b) in pairs {
        let a = std::hint::black_box(a);
        let b = std::hint::black_box(b);
        let old = a.powf(b);
        let new = pow(a, b);
        assert!(new.is_nan());
        println!("target a={:08x} b={:08x}: before={:08x} after_nan={}", a.to_bits(), b.to_bits(), old.to_bits(), new.is_nan());
    }
    let controls: [(f32, f32, f32); 21] = [
        (2.0, 3.0, 8.0), (-2.0, 3.0, -8.0), (-2.0, 2.0, 4.0),
        (0.0, 0.0, 1.0), (-0.0, 0.0, 1.0),
        (f32::INFINITY, 0.0, 1.0), (f32::NEG_INFINITY, 0.0, 1.0),
        (-0.0, 3.0, -0.0), (-0.0, 2.0, 0.0),
        (-0.0, -3.0, f32::NEG_INFINITY), (-0.0, -2.0, f32::INFINITY),
        (f32::NEG_INFINITY, 3.0, f32::NEG_INFINITY),
        (f32::NEG_INFINITY, -3.0, -0.0), (f32::NEG_INFINITY, -2.0, 0.0),
        (0.5, f32::INFINITY, 0.0), (0.5, f32::NEG_INFINITY, f32::INFINITY),
        (-0.5, f32::INFINITY, 0.0), (-0.5, f32::NEG_INFINITY, f32::INFINITY),
        (2.0, f32::INFINITY, f32::INFINITY), (2.0, f32::NEG_INFINITY, 0.0),
        (1.0, -0.0, 1.0),
    ];
    for (a, b, expected) in controls {
        let actual = pow(std::hint::black_box(a), std::hint::black_box(b));
        assert_eq!(actual.to_bits(), expected.to_bits(), "{a:?}^{b:?}");
        println!("control a={:08x} b={:08x}: {:08x}", a.to_bits(), b.to_bits(), actual.to_bits());
    }
    let values = [f32::NEG_INFINITY, -2.0, -1.0, -0.5, -0.0, 0.0, 0.5, 1.0, 2.0, f32::INFINITY, f32::NAN];
    let exponents = [f32::NEG_INFINITY, -3.0, -2.0, -0.5, -0.0, 0.0, 0.5, 2.0, 3.0, f32::INFINITY, f32::NAN];
    let mut delegated = 0;
    let mut guarded = 0;
    for a in values {
        for b in exponents {
            let a = std::hint::black_box(a);
            let b = std::hint::black_box(b);
            let actual = pow(a, b);
            if a.is_nan() || b.is_nan() || (a.abs() == 1.0 && b.is_infinite()) {
                assert!(actual.is_nan());
                guarded += 1;
            } else {
                let expected = a.powf(b);
                assert!(actual.to_bits() == expected.to_bits() || actual.is_nan() && expected.is_nan());
                delegated += 1;
            }
        }
    }
    assert_eq!(guarded + delegated, 121);
    assert!(!f32::NAN.powf(0.0).is_nan(), "NaN guard omission must be detectable");
    assert!(!1.0f32.powf(f32::INFINITY).is_nan(), "unit/infinite guard omission must be detectable");
    assert_eq!(pow(1.0, 2.0), 1.0, "guard must not reject ordinary unit bases");
    assert_eq!(pow(2.0, f32::INFINITY), f32::INFINITY, "guard must not reject every infinite exponent");
    println!("PASS: 8 target pairs, 21 explicit bit controls, {guarded} guarded and {delegated} delegated class pairs, 4 mutation discriminators; scalar helper only");
}
