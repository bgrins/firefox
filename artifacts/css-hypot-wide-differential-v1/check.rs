fn hypot(a: f32, b: f32) -> f32 {
    let a = a as f64;
    let b = b as f64;
    (a * a + b * b).sqrt() as f32
}
fn main() {
 let fractions=[0u32,1,2,0x3fffff,0x400000,0x7ffffe,0x7fffff];
 let mut tested=0u64;let mut different=0u64;let mut max_ulp=0u32;
 for ea in 0..255u32 {for eb in 0..255u32 {for fa in fractions {for fb in fractions {
  let a=f32::from_bits((ea<<23)|fa|((ea%2)<<31));let b=f32::from_bits((eb<<23)|fb|((eb%2)<<31));
  let value=hypot(a,b);let reference=(a as f64).hypot(b as f64) as f32;
  assert_eq!(value.is_infinite(),reference.is_infinite(),"classification {a:?} {b:?}");
  assert!(!value.is_nan());assert!(!value.is_sign_negative());
  let ulp=value.to_bits().abs_diff(reference.to_bits());assert!(ulp<=1,"ulp {ulp}: {a:?} {b:?}");
  if ulp!=0 {different+=1;if different<=8{println!("difference {a:?} {b:?} {:08x} {:08x}",value.to_bits(),reference.to_bits());}}
  max_ulp=max_ulp.max(ulp);tested+=1;
 }}}}
 println!("tested={tested} differing={different} maximum_ulp={max_ulp}");
}
