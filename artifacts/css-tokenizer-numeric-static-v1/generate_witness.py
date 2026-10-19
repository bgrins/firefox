from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'source/third_party/rust/cssparser/src/tokenizer.rs').read_text()
def segment(start,end):
 a=s.index(start);b=s.index(end,a);return s[a:b]
parts=[segment('fn byte_to_decimal_digit','\nfn consume_numeric'),segment('fn consume_numeric','\n#[inline]'),segment('fn is_ident_start(','\nfn consume_ident_like')]
output=(R/'facade-prefix.rs').read_text()+'\n'.join(parts)+(R/'facade-main.rs').read_text()
(R/'numeric-witness.rs').write_text(output)
