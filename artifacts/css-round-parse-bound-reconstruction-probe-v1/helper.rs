use std::ops::{Add, Sub, Rem};
#[derive(Clone,Copy)] enum RoundingStrategy { Nearest, Up, Down, ToZero }
enum SimplificationResult { Simplified }
#[derive(Clone,Copy)] struct Scalar(f32);
impl Scalar {
    fn try_op<O:Fn(f32,f32)->f32>(&self, other:&Self, op:O)->Result<Self,()> { Ok(Self(op(self.0,other.0))) }
    fn is_negative_leaf(&self)->Option<bool> { Some(self.0.is_sign_negative()) }
    fn is_zero_leaf(&self)->Option<bool> { Some(self.0==0.0) }
    fn negate(&mut self) { self.0 = -self.0; }
    fn lt(&self, other:&Self)->bool { self.0 < other.0 }
}
fn simplify(value:&mut Box<Scalar>, step:&mut Box<Scalar>, strategy:RoundingStrategy, result:&mut Scalar)->SimplificationResult {
    macro_rules! value_or_stop { ($value:expr) => {$value.unwrap()}; }
    macro_rules! replace_self_with { ($value:expr) => {*result = (*$value).clone()}; }
                if value_or_stop!(step.is_negative_leaf()) {
                    step.negate();
                }

                let remainder = value_or_stop!(value.try_op(step, Rem::rem));
                if value_or_stop!(remainder.is_zero_leaf()) {
                    replace_self_with!(&mut **value);
                    return SimplificationResult::Simplified;
                }

                let (mut lower_bound, mut upper_bound) = if value_or_stop!(value.is_negative_leaf())
                {
                    // A zero upper bound is specifically negative zero.
                    let upper_bound = value_or_stop!(value.try_op(&remainder, |a, b| {
                        let result = a - b;
                        if result == 0.0 { -0.0 } else { result }
                    }));
                    let lower_bound = value_or_stop!(upper_bound.try_op(step, Sub::sub));

                    (lower_bound, upper_bound)
                } else {
                    let lower_bound = value_or_stop!(value.try_op(&remainder, Sub::sub));
                    let upper_bound = value_or_stop!(lower_bound.try_op(step, Add::add));

                    (lower_bound, upper_bound)
                };

                match strategy {
                    RoundingStrategy::Nearest => {
                        let lower_diff = value_or_stop!(value.try_op(&lower_bound, Sub::sub));
                        let upper_diff = value_or_stop!(upper_bound.try_op(value, Sub::sub));
                        // In case of a tie, use the upper bound
                        if lower_diff.lt(&upper_diff) {
                            replace_self_with!(&mut lower_bound);
                        } else {
                            replace_self_with!(&mut upper_bound);
                        }
                    },
                    RoundingStrategy::Up => {
                        replace_self_with!(&mut upper_bound);
                    },
                    RoundingStrategy::Down => {
                        replace_self_with!(&mut lower_bound);
                    },
                    RoundingStrategy::ToZero => {
                        let mut lower_diff = lower_bound.clone();
                        let mut upper_diff = upper_bound.clone();

                        if value_or_stop!(lower_diff.is_negative_leaf()) {
                            lower_diff.negate();
                        }

                        if value_or_stop!(upper_diff.is_negative_leaf()) {
                            upper_diff.negate();
                        }

                        // In case of a tie, use the upper bound
                        if lower_diff.lt(&upper_diff) {
                            replace_self_with!(&mut lower_bound);
                        } else {
                            replace_self_with!(&mut upper_bound);
                        }
                    },
                };
                SimplificationResult::Simplified
}
fn main() {
    use std::io::{self,Read};
    let mut input=String::new();io::stdin().read_to_string(&mut input).unwrap();
    for line in input.lines() {
        let words:Vec<_>=line.split_whitespace().collect();
        let a=u32::from_str_radix(words[0],16).unwrap();let b=u32::from_str_radix(words[1],16).unwrap();
        for mode in [RoundingStrategy::Nearest,RoundingStrategy::Up,RoundingStrategy::Down,RoundingStrategy::ToZero] {
            let mut result=Scalar(f32::NAN);
            simplify(&mut Box::new(Scalar(f32::from_bits(a))),&mut Box::new(Scalar(f32::from_bits(b))),mode,&mut result);
            println!("{:08x}",result.0.to_bits());
        }
    }
}
