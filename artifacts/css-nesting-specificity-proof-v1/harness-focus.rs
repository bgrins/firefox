use super::*;
use super::tests::{DummyParser, DummySelectorImpl};
use cssparser::ToCss;
use std::io::Write;
use std::hint::black_box;
use std::time::Instant;

fn parse_text(text: &str, nested: bool) -> SelectorList<DummySelectorImpl> {
    SelectorList::parse(&DummyParser::default(), &mut CssParser::new(text), if nested { ParseRelative::ForNesting } else { ParseRelative::No }).unwrap()
}

#[test]
fn nesting_capsule() {
    let input = std::env::var("NESTING_INPUT").unwrap();
    let output = std::env::var("NESTING_OUTPUT").unwrap();
    let mut file = std::fs::File::create(output).unwrap();
    for line in std::fs::read_to_string(input).unwrap().lines() {
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), 3);
        let parent = parse_text(fields[1], false);
        let child = parse_text(fields[2], !fields[0].ends_with("no-parent"));
        let result = child.replace_parent_selector(&parent);
        assert_eq!(result.slice().len(), 1);
        let selector = &result.slice()[0];
        writeln!(file, "{}\t{}\t{}\t{}", fields[0], selector.specificity(), selector.flags().bits(), result.to_css_string()).unwrap();
    }
    let Ok(output) = std::env::var("NESTING_BENCH") else { return };
    let mut file = std::fs::File::create(output).unwrap();
    writeln!(file, "parents,ampersands,shape,sample,iterations,nanoseconds").unwrap();
    for p in [1, 10, 100, 1000] {
        let parent_text = (0..p).map(|i| format!("#p{}", i)).collect::<Vec<_>>().join(", ");
        let parent = parse_text(&parent_text, false);
        for a in [1, 10, 100] {
            for shape in ["direct", "is", "no-parent"] {
                if let Ok(focus) = std::env::var("NESTING_FOCUS") {
                    if focus != format!("{p},{a},{shape}") { continue; }
                }
                let atom = match shape { "direct" => "&", "is" => ":is(&, .x)", _ => ".x" };
                let child = parse_text(&atom.repeat(a), shape != "no-parent");
                let run = |count| {
                    let start = Instant::now();
                    for _ in 0..count {
                        let result = black_box(&child).replace_parent_selector(black_box(&parent));
                        black_box(result);
                    }
                    start.elapsed().as_nanos()
                };
                let mut iterations = 1u64;
                while run(iterations) < 20_000_000 && iterations < 1_048_576 { iterations *= 2; }
                for sample in 0..7 {
                    let elapsed = run(iterations);
                    writeln!(file, "{},{},{},{},{},{}", p, a, shape, sample, iterations, elapsed).unwrap();
                }
            }
        }
    }
}
