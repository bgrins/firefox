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
pub enum Integer { Literal(i32), Contextual }
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

mod specified { pub use crate::Integer; }
