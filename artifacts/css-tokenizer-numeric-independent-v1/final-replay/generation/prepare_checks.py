from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent
for n,h in json.loads((R/'DRAFT-PINS.json').read_text()).items(): assert hashlib.sha256((R/'draft-inputs'/n).read_bytes()).hexdigest()==h
s=(R/'draft-inputs/numeric-comparison.rs').read_text().split('fn reference(number:')[0]
s=s.replace('    assert!(p.is_eof() || p.next_byte_unchecked().is_ascii_whitespace() || p.next_byte_unchecked() == b\';\');','')
# Preserve exact numeric bodies, add a no-allocation benchmark entry.
needle='    pub(super) fn run(input: &str) -> super::Observed {'
extra='''    #[inline(never)]
    pub(super) fn bench(input: &str) -> u32 {
        let mut p = Parser { input, position: 0 };
        let t = consume_numeric(&mut p);
        let bits = match t { Number { value, .. } | Dimension { value, .. } => value.to_bits(), Percentage { unit_value, .. } => unit_value.to_bits() };
        bits ^ p.position as u32
    }
'''
assert s.count(needle)==2
s=s.replace(needle,extra+needle)
for n in ['numeric-before.rs','numeric-candidate.rs']: assert (R/'draft-inputs'/n).read_text() in s
main=r'''
fn main() {
 let cases: &[(&str,&[&str])] = &[
 ("integers", &["0;","1;","-12;","2147483647;","12px;","100%;"]),
 ("fractions", &[".5;","0.25;","-123.456;","1.5em;","99.9%;","1.00001;"]),
 ("exponents", &["1e3;","-1e-3;","2.5e+4px;","3.4e38;","1.2e-38%;","1E2;"]),
 ];
 let loops=400_000;
 for (label,inputs) in cases {
  for x in *inputs { assert_eq!(before::bench(x),candidate::bench(x)); }
  for round in 0..9 {
   for k in 0..2 {
    let which=(round+k)%2;
    let now=std::time::Instant::now();let mut checksum=0u32;
    for _ in 0..loops { for input in *inputs {
      let input=std::hint::black_box(*input);
      checksum=checksum.wrapping_add(if which==0 {before::bench(input)} else {candidate::bench(input)});
    }}
    std::hint::black_box(checksum);
    println!("{} {} {} {} {}",label,round,which,now.elapsed().as_nanos(),checksum);
   }
  }
 }
}
'''
(R/'benchmark.rs').write_text(s+main)
checks=r'''
fn main() {
 let mut cases=0;
 for n in [0,307,308,309,323,324,400] {
  for sign in ["", "-", "+"] {
   for base in [format!("{}5e-{}", "0".repeat(n), 0), format!("0.{}5e{}", "0".repeat(n), n), format!("5{}e-{}", "0".repeat(n), n+1), format!("0.{}0e9999", "0".repeat(n))] {
    let number=format!("{sign}{base}");
    let expected=number.parse::<f64>().unwrap();
    for (suffix,unit,kind,extra) in [(";tail","",0,0),("%tail","",1,1),("px;tail","px",2,2),("e+;tail","e",2,1),("e-;tail","e-",2,2),(".;tail","",0,0)] {
     let input=format!("{number}{suffix}");
     let result=candidate::run(&input);
     let original=before::run(&input);
     assert_eq!((result.kind,&*result.unit,result.consumed,result.sign,result.integer),(kind,unit,number.len()+extra,!sign.is_empty(),None),"{input}");
     assert_eq!((result.kind,&result.unit,result.consumed,result.sign,result.integer),(original.kind,&original.unit,original.consumed,original.sign,original.integer));
     let value=if kind==1 {expected/100.} else {expected};
     assert_eq!(result.bits,(value as f32).to_bits(),"{input}");
     cases+=1;
    }
   }
  }
 }
 println!("PASS {cases} independent signed/zero/compensation/suffix checks");
}
'''
(R/'challenge.rs').write_text(s+checks)
