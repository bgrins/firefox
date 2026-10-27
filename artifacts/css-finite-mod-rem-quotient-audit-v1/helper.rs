#[derive(Clone, Copy)]
enum ModRemOp { Mod, Rem }
impl ModRemOp {
    fn apply(self, dividend: f32, divisor: f32) -> f32 {
        // In mod(A, B) only, if B is infinite and A has opposite sign to B
        // (including an oppositely-signed zero), the result is NaN.
        // https://drafts.csswg.org/css-values/#round-infinities
        if matches!(self, Self::Mod)
            && divisor.is_infinite()
            && dividend.is_sign_negative() != divisor.is_sign_negative()
        {
            return f32::NAN;
        }

        if dividend.is_finite() && divisor.is_infinite() {
            return dividend;
        }

        let (r, same_sign_as) = match self {
            Self::Mod => (dividend - divisor * (dividend / divisor).floor(), divisor),
            Self::Rem => (dividend - divisor * (dividend / divisor).trunc(), dividend),
        };
        if r == 0.0 && same_sign_as.is_sign_negative() {
            -0.0
        } else {
            r
        }
    }
}

fn main() {
    for (a, b) in [(33554432i64, 3i64), (16777216, 3), (17, 3), (33554432, 4), (33554430, 3)] {
        for sa in [1i64, -1] { for sb in [1i64, -1] {
            let a = a * sa; let b = b * sb;
            for (name, op) in [("mod", ModRemOp::Mod), ("rem", ModRemOp::Rem)] {
                let x = a as f32; let y = b as f32;
                let result = op.apply(x, y);
                println!("{} {} {} {:08x} {:08x} {:08x} {:08x}",name,a,b,x.to_bits(),y.to_bits(),result.to_bits(),(x/y).to_bits());
            }
        }}
    }
    for (name, op, a, b) in [
        ("mod_negative_zero", ModRemOp::Mod, 6.0, -3.0),
        ("mod_positive_zero", ModRemOp::Mod, -6.0, 3.0),
        ("rem_negative_zero", ModRemOp::Rem, -6.0, 3.0),
        ("rem_positive_zero", ModRemOp::Rem, 6.0, -3.0),
        ("mod_same_inf", ModRemOp::Mod, 1.0, f32::INFINITY),
        ("mod_opposite_inf", ModRemOp::Mod, -1.0, f32::INFINITY),
        ("rem_positive_inf", ModRemOp::Rem, -1.0, f32::INFINITY),
        ("rem_negative_inf", ModRemOp::Rem, 1.0, f32::NEG_INFINITY),
    ] { println!("guard {} {:08x}", name, op.apply(a, b).to_bits()); }
}
