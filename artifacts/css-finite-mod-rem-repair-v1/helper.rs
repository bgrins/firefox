mod old {
#[derive(Clone, Copy)]
pub enum ModRemOp { Mod, Rem }
impl ModRemOp {
    pub fn apply(self, dividend: f32, divisor: f32) -> f32 {
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
}
mod candidate {
#[derive(Clone, Copy)]
pub enum ModRemOp { Mod, Rem }
impl ModRemOp {
    pub fn apply(self, dividend: f32, divisor: f32) -> f32 {
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

        let mut r = dividend % divisor;
        let same_sign_as = match self {
            Self::Mod => {
                if r != 0.0 && r.is_sign_negative() != divisor.is_sign_negative() {
                    r += divisor;
                }
                divisor
            },
            Self::Rem => dividend,
        };
        if r == 0.0 {
            r.copysign(same_sign_as)
        } else {
            r
        }
    }
}
}
fn main() {
let values: &[u32] = &[0, 1, 2, 3, 8388607, 8388608, 8388609, 855638016, 864026624, 1051372203, 1056964608, 1065353216, 1073741824, 1077936128, 1082130432, 1099431936, 1266679808, 1275068415, 1275068416, 1275068417, 2139095039, 2139095040, 2143289344, 2147483648, 2147483649, 2147483650, 2147483651, 2155872255, 2155872256, 2155872257, 3003121664, 3011510272, 3198855851, 3204448256, 3212836864, 3221225472, 3225419776, 3229614080, 3246915584, 3414163456, 3422552063, 3422552064, 3422552065, 4286578687, 4286578688, 4290772992];
for &a in values { for &b in values {
let aa = std::hint::black_box(f32::from_bits(a));
let bb = std::hint::black_box(f32::from_bits(b));
for is_mod in [true, false] {
let old = if is_mod { old::ModRemOp::Mod } else { old::ModRemOp::Rem };
let new = if is_mod { candidate::ModRemOp::Mod } else { candidate::ModRemOp::Rem };
println!("{} {:08x} {:08x} {:08x} {:08x}", if is_mod { "mod" } else { "rem" }, a,b,old.apply(aa,bb).to_bits(),new.apply(aa,bb).to_bits());
}
}}
}
