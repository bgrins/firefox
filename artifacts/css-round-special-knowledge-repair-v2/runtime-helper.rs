#[derive(Clone, Copy)] enum RoundingStrategy { Nearest, Up, Down, ToZero }
trait Zero { fn is_zero(&self) -> bool; }
impl Zero for f32 { fn is_zero(&self) -> bool { *self == 0.0 } }
fn extracted(strategy: RoundingStrategy, mut value: f32, step: f32) -> f32 {
let step = step.abs();

                // TODO(emilio): Seems like at least a few of these
                // special-cases could be removed if we do the math in a
                // particular order.
                if value.is_nan() || step.is_nan() || step.is_zero() {
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

                value
}
fn main() {
 let values = [f32::NEG_INFINITY, -1.0, -0.0, 0.0, 1.0, f32::INFINITY, f32::NAN];
 for (s, strategy) in [RoundingStrategy::Nearest,RoundingStrategy::Up,RoundingStrategy::Down,RoundingStrategy::ToZero].into_iter().enumerate() {
  for (i,a) in values.into_iter().enumerate() { for (j,b) in values.into_iter().enumerate() {
   println!("{s} {i} {j} {:08x}", extracted(strategy,a,b).to_bits());
  }}
 }
}
