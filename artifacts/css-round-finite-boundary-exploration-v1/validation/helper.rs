#[derive(Clone, Copy)]
enum RoundingStrategy { Nearest, Up, Down, ToZero }
trait Zero { fn is_zero(self) -> bool; }
impl Zero for f32 { fn is_zero(self) -> bool { self == 0.0 } }
fn old(mut value: f32, step: f32, strategy: RoundingStrategy) -> Result<(f32, ()), ()> {
let ty = ();
                let step = step.abs();

                // TODO(emilio): Seems like at least a few of these
                // special-cases could be removed if we do the math in a
                // particular order.
                if step.is_zero() {
                    value = f32::NAN;
                } else if value.is_infinite() {
                    if step.is_infinite() {
                        value = f32::NAN
                    }
                } else if step.is_infinite() {
                    value = match strategy {
                        RoundingStrategy::Nearest | RoundingStrategy::ToZero => {
                            if value.is_sign_negative() { -0.0 } else { 0.0 }
                        },
                        RoundingStrategy::Up => {
                            if !value.is_sign_negative() && !value.is_zero() {
                                f32::INFINITY
                            } else if !value.is_sign_negative() && value.is_zero() {
                                value
                            } else {
                                -0.0
                            }
                        },
                        RoundingStrategy::Down => {
                            if value.is_sign_negative() && !value.is_zero() {
                                -f32::INFINITY
                            } else if value.is_sign_negative() && value.is_zero() {
                                value
                            } else {
                                0.0
                            }
                        },
                    };
                } else {
                    let div = value / step;
                    let lower_bound = div.floor() * step;
                    let upper_bound = div.ceil() * step;

                    value = match strategy {
                        RoundingStrategy::Nearest => {
                            // In case of a tie, use the upper bound
                            if value - lower_bound < upper_bound - value {
                                lower_bound
                            } else {
                                upper_bound
                            }
                        },
                        RoundingStrategy::Up => upper_bound,
                        RoundingStrategy::Down => lower_bound,
                        RoundingStrategy::ToZero => {
                            // In case of a tie, use the upper bound
                            if lower_bound.abs() < upper_bound.abs() {
                                lower_bound
                            } else {
                                upper_bound
                            }
                        },
                    }
                }

                Ok((value, ty))
}
fn candidate(mut value: f32, step: f32, strategy: RoundingStrategy) -> Result<(f32, ()), ()> {
let ty = ();
                let step = step.abs();

                // TODO(emilio): Seems like at least a few of these
                // special-cases could be removed if we do the math in a
                // particular order.
                if step.is_zero() {
                    value = f32::NAN;
                } else if value.is_infinite() {
                    if step.is_infinite() {
                        value = f32::NAN
                    }
                } else if step.is_infinite() {
                    value = match strategy {
                        RoundingStrategy::Nearest | RoundingStrategy::ToZero => {
                            if value.is_sign_negative() { -0.0 } else { 0.0 }
                        },
                        RoundingStrategy::Up => {
                            if !value.is_sign_negative() && !value.is_zero() {
                                f32::INFINITY
                            } else if !value.is_sign_negative() && value.is_zero() {
                                value
                            } else {
                                -0.0
                            }
                        },
                        RoundingStrategy::Down => {
                            if value.is_sign_negative() && !value.is_zero() {
                                -f32::INFINITY
                            } else if value.is_sign_negative() && value.is_zero() {
                                value
                            } else {
                                0.0
                            }
                        },
                    };
                } else {
                    let remainder = value % step;
                    if remainder.is_zero() {
                        return Ok((value, ty));
                    }
                    let wide_value = f64::from(value);
                    let wide_step = f64::from(step);
                    let toward_zero = (wide_value - f64::from(remainder)).copysign(wide_value);
                    let (lower_bound, upper_bound) = if value.is_sign_negative() {
                        (toward_zero - wide_step, toward_zero)
                    } else {
                        (toward_zero, toward_zero + wide_step)
                    };

                    value = match strategy {
                        RoundingStrategy::Nearest => {
                            // In case of a tie, use the upper bound
                            if wide_value - lower_bound < upper_bound - wide_value {
                                lower_bound
                            } else {
                                upper_bound
                            }
                        },
                        RoundingStrategy::Up => upper_bound,
                        RoundingStrategy::Down => lower_bound,
                        RoundingStrategy::ToZero => {
                            // In case of a tie, use the upper bound
                            if lower_bound.abs() < upper_bound.abs() {
                                lower_bound
                            } else {
                                upper_bound
                            }
                        },
                    } as f32;
                }

                Ok((value, ty))
}
fn main() {
    use std::io::{self, Read, Write};
    let mut input = String::new(); io::stdin().read_to_string(&mut input).unwrap();
    let stdout = io::stdout(); let mut out = io::BufWriter::new(stdout.lock());
    for line in input.lines() {
        let mut words = line.split_whitespace();
        let a = f32::from_bits(u32::from_str_radix(words.next().unwrap(),16).unwrap());
        let b = f32::from_bits(u32::from_str_radix(words.next().unwrap(),16).unwrap());
        write!(out, "{:08x}", (a % b.abs()).to_bits()).unwrap();
        for strategy in [RoundingStrategy::Nearest, RoundingStrategy::Up, RoundingStrategy::Down, RoundingStrategy::ToZero] {
            write!(out, " {:08x}", candidate(a,b,strategy).unwrap().0.to_bits()).unwrap();
        }
        writeln!(out).unwrap();
    }
}
