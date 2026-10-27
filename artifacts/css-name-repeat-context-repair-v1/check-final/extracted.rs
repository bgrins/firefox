#![allow(dead_code)]
type OwnedSlice<T> = Vec<T>;
struct Context { count: i32 }
trait ToComputedValue {
    type ComputedValue;
    fn to_computed_value(&self, context: &Context) -> Self::ComputedValue;
    fn from_computed_value(value: &Self::ComputedValue) -> Self;
}
impl<T: ToComputedValue> ToComputedValue for Vec<T> {
    type ComputedValue = Vec<T::ComputedValue>;
    fn to_computed_value(&self, context: &Context) -> Self::ComputedValue {
        self.iter().map(|v| v.to_computed_value(context)).collect()
    }
    fn from_computed_value(value: &Self::ComputedValue) -> Self {
        value.iter().map(T::from_computed_value).collect()
    }
}
#[derive(Clone, Debug, PartialEq)]
enum Integer { Literal(i32), Contextual }
impl ToComputedValue for Integer {
    type ComputedValue = i32;
    fn to_computed_value(&self, context: &Context) -> i32 {
        match self { Self::Literal(v) => *v, Self::Contextual => context.count.max(1) }
    }
    fn from_computed_value(value: &i32) -> Self { Self::Literal(*value) }
}
#[derive(Clone, Debug, PartialEq)]
enum RepeatCount<I> { Number(I), AutoFill, AutoFit }
#[derive(Clone, Debug, PartialEq)]
struct NameRepeat<I> { count: RepeatCount<I>, line_names: Vec<Vec<String>> }
#[derive(Clone, Debug, PartialEq)]
enum LineNameListValue<I> { LineNames(Vec<String>), Repeat(NameRepeat<I>) }
impl<I: ToComputedValue> ToComputedValue for LineNameListValue<I> {
    type ComputedValue = LineNameListValue<I::ComputedValue>;
    fn to_computed_value(&self, c: &Context) -> Self::ComputedValue {
        match self {
            Self::LineNames(v) => LineNameListValue::LineNames(v.clone()),
            Self::Repeat(r) => LineNameListValue::Repeat(NameRepeat {
                count: match &r.count { RepeatCount::Number(i) => RepeatCount::Number(i.to_computed_value(c)), RepeatCount::AutoFill => RepeatCount::AutoFill, RepeatCount::AutoFit => RepeatCount::AutoFit },
                line_names: r.line_names.clone(),
            }),
        }
    }
    fn from_computed_value(v: &Self::ComputedValue) -> Self {
        match v {
            LineNameListValue::LineNames(n) => Self::LineNames(n.clone()),
            LineNameListValue::Repeat(r) => Self::Repeat(NameRepeat {
                count: match &r.count { RepeatCount::Number(i) => RepeatCount::Number(I::from_computed_value(i)), RepeatCount::AutoFill => RepeatCount::AutoFill, RepeatCount::AutoFit => RepeatCount::AutoFit },
                line_names: r.line_names.clone(),
            }),
        }
    }
}
#[derive(Clone, Debug, PartialEq)]
struct LineNameList<I> { expanded_line_names_length: usize, line_names: OwnedSlice<LineNameListValue<I>> }
impl LineNameListValue<i32> {
    fn line_names_length(&self) -> usize {
        match self {
            Self::LineNames(..) => 1,
            Self::Repeat(r) => match r.count {
                RepeatCount::Number(count) => {
                    debug_assert!(count >= 1);
                    r.line_names.len().saturating_mul(count as usize)
                },
                _ => 0,
            },
        }
    }
}

impl<I> ToComputedValue for LineNameList<I>
where
    I: ToComputedValue<ComputedValue = i32>,
{
    type ComputedValue = LineNameList<i32>;

    fn to_computed_value(&self, context: &Context) -> Self::ComputedValue {
        let line_names = self.line_names.to_computed_value(context);
        let expanded_line_names_length = line_names.iter().fold(0usize, |length, value| {
            length.saturating_add(value.line_names_length())
        });
        LineNameList {
            expanded_line_names_length,
            line_names,
        }
    }

    fn from_computed_value(computed: &Self::ComputedValue) -> Self {
        Self {
            expanded_line_names_length: 0,
            line_names: ToComputedValue::from_computed_value(&computed.line_names),
        }
    }
}

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
                checked += 1;
            }
        }
    }
    println!("PASS {checked} context/cache/inverse cases; host usize bits {}", usize::BITS);
}
