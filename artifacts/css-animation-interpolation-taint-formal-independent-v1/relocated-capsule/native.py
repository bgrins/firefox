import argparse
import hashlib
import json
from pathlib import Path


def item(text, anchor):
    start = text.index(anchor)
    body = text.index("{", start)
    depth = 0
    for i in range(body, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise AssertionError(anchor)


def generate(root, variant):
    source = (root / "source" / ("value.original.rs" if variant == "omission" else "value.candidate.rs")).read_text()
    animated = (root / "source/animated.rs").read_text()
    selected = [item(source, "impl<Component: Animate> Animate for Value<Component>"),
                item(animated, "pub enum Procedure"),
                item(animated, "impl Procedure {"),
                item(animated, "impl<T> Animate for Option<T>\n")]
    header = '''#![allow(dead_code)]
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
'''
    return header + selected[0] + '\n#[derive(Clone, Copy, Debug)]\n' + '\n'.join(selected[1:]) + '\n' + (root / 'Driver.rs').read_text(), [dict(anchor=x.split('{',1)[0].strip(), sha256=hashlib.sha256(x.encode()).hexdigest(), body=x) for x in selected]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("variant", choices=["candidate", "omission"])
    parser.add_argument("output")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    code, bindings = generate(root, args.variant)
    Path(args.output).write_text(code)
    Path(args.output + '.bindings.json').write_text(json.dumps(bindings, indent=2) + '\n')
