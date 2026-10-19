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

/// The strategy used in `round()`
#[derive(
    Clone,
    Copy,
    Debug,
    Deserialize,
    MallocSizeOf,
    PartialEq,
    Serialize,
    ToAnimatedZero,
    ToResolvedValue,
    ToShmem,
)]
#[repr(u8)]
pub enum RoundingStrategy {
    /// `round(nearest, a, b)`
    /// round a to the nearest multiple of b
    Nearest,
    /// `round(up, a, b)`
    /// round a up to the nearest multiple of b
    Up,
    /// `round(down, a, b)`
    /// round a down to the nearest multiple of b
    Down,
    /// `round(to-zero, a, b)`
    /// round a to the nearest multiple of b that is towards zero
    ToZero,
}

/// The clamping mode used in `progress()`
#[derive(
    Clone,
    Copy,
    Debug,
    Deserialize,
    MallocSizeOf,
    Parse,
    PartialEq,
    Serialize,
    ToAnimatedZero,
    ToCss,
    ToResolvedValue,
    ToShmem,
)]
#[repr(u8)]
pub enum ProgressClampingMode {
    /// `progress(value, start, end)`
    /// Progress result is clamped to the range [0, 1}.
    #[css(skip)]
    Clamp,
    /// `progress(no-clamp value, start, end)`
    /// Progress result can be any number.
    NoClamp,
}

