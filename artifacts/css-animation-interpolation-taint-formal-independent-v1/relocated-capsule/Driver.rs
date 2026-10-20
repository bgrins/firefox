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
