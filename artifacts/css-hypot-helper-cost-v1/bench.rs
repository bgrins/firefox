use std::hint::black_box;
use std::time::Instant;
#[inline(never)] fn old(a:f32,b:f32)->f32 {(a*a+b*b).sqrt()}
#[inline(never)] fn library(a:f32,b:f32)->f32 {if a.is_nan()||b.is_nan(){return f32::NAN;} (a as f64).hypot(b as f64) as f32}
#[inline(never)] fn wide(a:f32,b:f32)->f32 {let a=a as f64;let b=b as f64;(a*a+b*b).sqrt() as f32}
fn main(){
 for round in 0..7 {
  for (name,f) in [("old",old as fn(f32,f32)->f32),("library",library),("wide",wide)] {
   let start=Instant::now();let mut sum=0.0f64;
   for i in 0..1000000 {let a=black_box((i%97+1)as f32);let b=black_box((i%83+1)as f32);sum+=black_box(f(a,b))as f64;}
   println!("{} {} {} {}",round,name,start.elapsed().as_nanos(),black_box(sum));
  }
 }
 for (a,b) in [(f32::NAN,f32::INFINITY),(f32::INFINITY,f32::NAN),(-0.0,-0.0),(f32::from_bits(1),0.0),(f32::MAX,f32::MAX)] {
  let x=library(a,b);let y=wide(a,b);assert!(x.to_bits()==y.to_bits() || (x.is_nan()&&y.is_nan()));
 }
}
