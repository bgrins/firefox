#![allow(dead_code)]
mod width32 {
    #[derive(Clone, Copy)] struct Integer(i32);
    impl Integer { fn resolve(&self) -> Option<i32> { Some(self.0) } }
    #[derive(Clone, Copy)] enum RepeatCount { Number(Integer), AutoFill }
    struct Length(u32);
    impl Length { fn len(&self) -> u32 { self.0 } }
    struct Repeat { line_names: Length, count: RepeatCount }
    enum LineNameListValue { LineNames(()), Repeat(Repeat) }
    impl LineNameListValue { pub fn line_names_length(&self) -> u32 {
        match *self {
            Self::LineNames(..) => 1,
            Self::Repeat(ref r) => {
                match r.count {
                    // Note: RepeatCount is always >= 1. Unresolvable calc
                    // expressions were rejected at parse-time.
                    RepeatCount::Number(ref v) => {
                        r.line_names
                            .len()
                            .saturating_mul(v.resolve().unwrap() as u32)
                    },
                    _ => 0,
                }
            },
        }
    } }
    pub fn cache(terms: &[(u8,u64,i32)]) -> u64 {
        let mut expanded_line_names_length = 0u32;
        for &(kind, groups, count) in terms {
            assert!(groups <= u32::MAX as u64);
            let value = match kind {
                0 => LineNameListValue::LineNames(()),
                1 => LineNameListValue::Repeat(Repeat { line_names: Length(groups as u32), count: RepeatCount::Number(Integer(count)) }),
                2 => LineNameListValue::Repeat(Repeat { line_names: Length(groups as u32), count: RepeatCount::AutoFill }),
                _ => panic!("invalid kind"),
            };
            expanded_line_names_length =
                expanded_line_names_length.saturating_add(value.line_names_length());
        }
        expanded_line_names_length as u64
    }
}

mod width64 {
    #[derive(Clone, Copy)] struct Integer(i32);
    impl Integer { fn resolve(&self) -> Option<i32> { Some(self.0) } }
    #[derive(Clone, Copy)] enum RepeatCount { Number(Integer), AutoFill }
    struct Length(u64);
    impl Length { fn len(&self) -> u64 { self.0 } }
    struct Repeat { line_names: Length, count: RepeatCount }
    enum LineNameListValue { LineNames(()), Repeat(Repeat) }
    impl LineNameListValue { pub fn line_names_length(&self) -> u64 {
        match *self {
            Self::LineNames(..) => 1,
            Self::Repeat(ref r) => {
                match r.count {
                    // Note: RepeatCount is always >= 1. Unresolvable calc
                    // expressions were rejected at parse-time.
                    RepeatCount::Number(ref v) => {
                        r.line_names
                            .len()
                            .saturating_mul(v.resolve().unwrap() as u64)
                    },
                    _ => 0,
                }
            },
        }
    } }
    pub fn cache(terms: &[(u8,u64,i32)]) -> u64 {
        let mut expanded_line_names_length = 0u64;
        for &(kind, groups, count) in terms {
            assert!(groups <= u64::MAX as u64);
            let value = match kind {
                0 => LineNameListValue::LineNames(()),
                1 => LineNameListValue::Repeat(Repeat { line_names: Length(groups as u64), count: RepeatCount::Number(Integer(count)) }),
                2 => LineNameListValue::Repeat(Repeat { line_names: Length(groups as u64), count: RepeatCount::AutoFill }),
                _ => panic!("invalid kind"),
            };
            expanded_line_names_length =
                expanded_line_names_length.saturating_add(value.line_names_length());
        }
        expanded_line_names_length as u64
    }
}

mod host {
    #[derive(Clone, Copy)] struct Integer(i32);
    impl Integer { fn resolve(&self) -> Option<i32> { Some(self.0) } }
    #[derive(Clone, Copy)] enum RepeatCount { Number(Integer), AutoFill }
    struct Length(usize);
    impl Length { fn len(&self) -> usize { self.0 } }
    struct Repeat { line_names: Length, count: RepeatCount }
    enum LineNameListValue { LineNames(()), Repeat(Repeat) }
    impl LineNameListValue { pub fn line_names_length(&self) -> usize {
        match *self {
            Self::LineNames(..) => 1,
            Self::Repeat(ref r) => {
                match r.count {
                    // Note: RepeatCount is always >= 1. Unresolvable calc
                    // expressions were rejected at parse-time.
                    RepeatCount::Number(ref v) => {
                        r.line_names
                            .len()
                            .saturating_mul(v.resolve().unwrap() as usize)
                    },
                    _ => 0,
                }
            },
        }
    } }
    pub fn cache(terms: &[(u8,u64,i32)]) -> u64 {
        let mut expanded_line_names_length = 0usize;
        for &(kind, groups, count) in terms {
            assert!(groups <= usize::MAX as u64);
            let value = match kind {
                0 => LineNameListValue::LineNames(()),
                1 => LineNameListValue::Repeat(Repeat { line_names: Length(groups as usize), count: RepeatCount::Number(Integer(count)) }),
                2 => LineNameListValue::Repeat(Repeat { line_names: Length(groups as usize), count: RepeatCount::AutoFill }),
                _ => panic!("invalid kind"),
            };
            expanded_line_names_length =
                expanded_line_names_length.saturating_add(value.line_names_length());
        }
        expanded_line_names_length as u64
    }
}
use std::io::{self, BufRead};
fn main() {
    println!("host_bits {}", usize::BITS);
    for line in io::stdin().lock().lines() {
        let line = line.unwrap();
        let mut fields = line.split_whitespace();
        let id = fields.next().unwrap();
        let mode = fields.next().unwrap();
        let n: usize = fields.next().unwrap().parse().unwrap();
        let mut terms = Vec::new();
        for _ in 0..n {
            terms.push((fields.next().unwrap().parse().unwrap(), fields.next().unwrap().parse().unwrap(), fields.next().unwrap().parse().unwrap()));
        }
        assert!(fields.next().is_none());
        let result = match mode { "width32" => width32::cache(&terms), "width64" => width64::cache(&terms), "host" => host::cache(&terms), _ => panic!("mode") };
        println!("{} {}", id, result);
    }
}
