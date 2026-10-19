from pathlib import Path
import json
R=Path(__file__).resolve().parent
s=(R/'original/third_party/rust/cssparser/src/tokenizer.rs').read_text()
def segment(start,end):
 a=s.index(start);b=s.index(end,a);return s[a:b]
prefix=(R/'facade-prefix.rs').read_text().replace('#![allow(dead_code)]\n','').replace('#[derive(Debug)]','#[derive(Debug, PartialEq)]')
prefix=prefix.replace('    fn is_eof',"    fn position(&self) -> SourcePosition { SourcePosition(self.position) }\n    fn slice_from(&self, start: SourcePosition) -> &'a str { &self.input[start.0..self.position] }\n    fn is_eof")
helpers=segment('fn byte_to_decimal_digit','\nfn consume_numeric')+segment('fn is_ident_start(','\nfn consume_ident_like')
module='''
#[derive(Debug, PartialEq)]
struct Observed { kind: u8, bits: u32, integer: Option<i32>, sign: bool, unit: String, consumed: usize }
'''
for name,file in [('before','numeric-before.rs'),('candidate','numeric-candidate.rs')]:
 module+='mod '+name+' {\n'+prefix+helpers+(R/file).read_text()+'''
    pub(super) fn run(input: &str) -> super::Observed {
        let mut p = Parser { input, position: 0 };
        let (kind, value, integer, sign, unit) = match consume_numeric(&mut p) {
            Number { value, int_value, has_sign } => (0, value, int_value, has_sign, ""),
            Percentage { unit_value, int_value, has_sign } => (1, unit_value, int_value, has_sign, ""),
            Dimension { value, int_value, has_sign, unit } => (2, value, int_value, has_sign, unit),
        };
        super::Observed { kind, bits: value.to_bits(), integer, sign, unit: unit.to_owned(), consumed: p.position }
    }
}
'''
main='''
fn reference(number: &str, suffix: &str) -> Observed {
    let value: f64 = number.parse().unwrap();
    let integer = if !number.contains(['.', 'e', 'E']) { Some(value.clamp(i32::MIN as f64, i32::MAX as f64) as i32) } else { None };
    let (kind, output, unit) = match suffix { "" => (0, value as f32, ""), "%" => (1, (value / 100.) as f32, ""), s => (2, value as f32, s) };
    Observed { kind, bits: output.to_bits(), integer, sign: number.starts_with(['+', '-']), unit: unit.to_owned(), consumed: number.len() + suffix.len() }
}
fn main() {
    let cases = [
'''
cases=[]
def add(label,numeric,strict=True):
 for sign in ('','-','+'):
  for suffix in ('','%','px','em'):
   cases.append((label,sign+numeric,suffix,strict))
for n in [0,1,20,300,306,307,308,309,310,322,323,324,325,399,1000]:
 add(f'large-compensated-{n}','5'+'0'*n+'e-'+str(n+1))
 add(f'small-compensated-{n}','0.'+'0'*n+'5e'+str(n))
for n in [306,307,308,309,322,323,324,399]:
 add(f'finite-underflow-{n}','0.'+'0'*n+'5e308')
 add(f'subnormal-power-{n}','1'+'0'*300+'e-'+str(n))
for n in ['0','1','17','2147483647','2147483648','2147483649','0000001','0.5','.5','5e-1','1E+2','0e999','1e999','1e-999','0.'+'1'+'0'*500,'9'*1000,'0e'+'9'*1000,'1e-'+'9'*1000]:
 add('syntax-and-range',n)
# Existing short-path f64 arithmetic is not asserted correctly rounded: test preservation separately.
for n in ['0.1','0.29','123.456','1.23456789123456789','3.4028235e38','1.17549435e-38','1.401298464e-45']:
 add('normal-path',n,False)
for label,num,suffix,strict in cases:
 main+='    ('+json.dumps(label)+', '+json.dumps(num)+', '+json.dumps(suffix)+', '+str(strict).lower()+'),\n'
main+='''
    ];
    let mut repaired = 0;
    let mut unchanged = 0;
    for (id, (label, number, suffix, strict)) in cases.iter().enumerate() {
        let input = format!("{number}{suffix};rest");
        let original = before::run(&input);
        let actual = candidate::run(&input);
        let expected = reference(number, suffix);
        assert_eq!((actual.kind, actual.integer, actual.sign, &actual.unit, actual.consumed), (original.kind, original.integer, original.sign, &original.unit, original.consumed), "lexical metadata {id}");
        assert_eq!((actual.kind, actual.integer, actual.sign, &actual.unit, actual.consumed), (expected.kind, expected.integer, expected.sign, &expected.unit, expected.consumed), "independent metadata {id}");
        if *strict { assert_eq!(actual, expected, "reference case {id} {label}"); }
        else { assert_eq!(actual, original, "ordinary path {id}"); }
        if original == actual { unchanged += 1; } else { repaired += 1; }
        if id % 12 == 0 { println!("case={id} label={label} original={:e} candidate={:e} reference={:e}", f32::from_bits(original.bits), f32::from_bits(actual.bits), f32::from_bits(expected.bits)); }
    }
    println!("PASS total={} changed={repaired} unchanged={unchanged}", cases.len());
}
'''
(R/'numeric-comparison.rs').write_text('#![allow(dead_code)]\n'+module+main)
(R/'CASES.json').write_text(json.dumps([dict(label=a,number=b,suffix=c,reference_required=d) for a,b,c,d in cases],indent=2)+'\n')
print(len(cases))
