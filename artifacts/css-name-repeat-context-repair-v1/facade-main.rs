fn main() {
    let mut checked = 0;
    for count in [-8, 0, 1, 2, 3, 17, i32::MAX] {
        for groups in [1, 2, 3, 7] {
            for stale in [0, 1, usize::MAX] {
                let source = LineNameList {
                    expanded_line_names_length: stale,
                    line_names: vec![
                        LineNameListValue::LineNames(vec![]),
                        LineNameListValue::Repeat(NameRepeat { count: RepeatCount::Number(Integer::Contextual), line_names: vec![vec![]; groups] }),
                        LineNameListValue::Repeat(NameRepeat { count: RepeatCount::AutoFill, line_names: vec![vec![]] }),
                        LineNameListValue::LineNames(vec!["tail".into()]),
                    ],
                };
                let actual = source.to_computed_value(&Context { count });
                let exact = 2u128 + groups as u128 * count.max(1) as u128;
                assert_eq!(actual.expanded_line_names_length, exact.min(usize::MAX as u128) as usize);
                let inverse = LineNameList::<Integer>::from_computed_value(&actual);
                assert_eq!(inverse.expanded_line_names_length, 0);
                assert_eq!(inverse.to_computed_value(&Context { count: 999 }), actual);
                assert_eq!(actual.to_computed_value(&Context { count: 999 }), actual);
                assert_eq!(LineNameList::<i32>::from_computed_value(&actual), actual);
                checked += 1;
            }
        }
    }
    println!("PASS {checked} context/cache/inverse cases; host usize bits {}", usize::BITS);
}
