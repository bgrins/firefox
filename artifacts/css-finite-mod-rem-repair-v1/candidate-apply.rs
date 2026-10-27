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
