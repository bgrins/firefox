#![allow(dead_code)]
#[derive(Clone, Debug)]
struct Payload { n: f64, reject: bool }
#[derive(Clone, Debug)]
struct ValueInner<T>(T);
#[derive(Clone, Debug)]
struct Value<T> { v: ValueInner<T>, url_data: u32, attr_tainted: bool }
trait Animate: Sized { fn animate(&self, other: &Self, procedure: Procedure) -> Result<Self, ()>; }
impl Animate for Payload {
 fn animate(&self, other: &Self, procedure: Procedure) -> Result<Self, ()> {
  if self.reject || other.reject { return Err(()); }
  let (a,b) = procedure.weights();
  Ok(Self { n: self.n*a + other.n*b, reject: false })
 }
}
impl<T: Animate> Animate for ValueInner<T> {
 fn animate(&self, other: &Self, p: Procedure) -> Result<Self, ()> { Ok(Self(self.0.animate(&other.0,p)?)) }
}
impl<Component: Animate> Animate for Value<Component> {
    fn animate(&self, other: &Self, procedure: Procedure) -> Result<Self, ()> {
        let v = self.v.animate(&other.v, procedure)?;
        Ok(Value {
            v,
            url_data: self.url_data.clone(),
            attr_tainted: self.attr_tainted || other.attr_tainted,
        })
    }
}
#[derive(Clone, Copy, Debug)]
pub enum Procedure {
    /// <https://drafts.csswg.org/web-animations/#animation-interpolation>
    Interpolate { progress: f64 },
    /// <https://drafts.csswg.org/web-animations/#animation-addition>
    Add,
    /// <https://drafts.csswg.org/web-animations/#animation-accumulation>
    Accumulate { count: u64 },
}
impl Procedure {
    /// Returns this procedure as a pair of weights.
    ///
    /// This is useful for animations that don't animate differently
    /// depending on the used procedure.
    #[inline]
    pub fn weights(self) -> (f64, f64) {
        match self {
            Procedure::Interpolate { progress } => (1. - progress, progress),
            Procedure::Add => (1., 1.),
            Procedure::Accumulate { count } => (count as f64, 1.),
        }
    }
}
impl<T> Animate for Option<T>
where
    T: Animate,
{
    #[inline]
    fn animate(&self, other: &Self, procedure: Procedure) -> Result<Self, ()> {
        match (self.as_ref(), other.as_ref()) {
            (Some(this), Some(other)) => Ok(Some(this.animate(other, procedure)?)),
            (None, None) => Ok(None),
            _ => Err(()),
        }
    }
}
fn value(n: f64, reject: bool, taint: bool, url: u32) -> Value<Payload> {
 Value { v: ValueInner(Payload { n, reject }), url_data: url, attr_tainted: taint }
}
fn main() {
 let procedures = [Procedure::Interpolate { progress: 0.25 }, Procedure::Add, Procedure::Accumulate { count: 2 }];
 let mut id = 0;
 for (p, procedure) in procedures.into_iter().enumerate() {
  for mode in 0..3 {
   for a in [false, true] {
    for b in [false, true] {
     let left = value(12., mode == 1, a, 17);
     let right = value(8., mode == 2, b, 29);
     match left.animate(&right, procedure) {
      Ok(v) => println!("{id}|{p}|{mode}|{a}|{b}|ok|{}|{}|{}", v.v.0.n, v.url_data, v.attr_tainted),
      Err(()) => println!("{id}|{p}|{mode}|{a}|{b}|error|-|-|-"),
     }
     id += 1;
    }
   }
  }
  let v = value(8., false, true, 29);
  let absent: Option<Value<Payload>> = None;
  let result = absent.animate(&absent, procedure);
  println!("{id}|{p}|none-none|{}", matches!(result, Ok(None))); id += 1;
  println!("{id}|{p}|some-none|{}", Some(v.clone()).animate(&absent, procedure).is_err()); id += 1;
  println!("{id}|{p}|none-some|{}", absent.animate(&Some(v), procedure).is_err()); id += 1;
 }
}
