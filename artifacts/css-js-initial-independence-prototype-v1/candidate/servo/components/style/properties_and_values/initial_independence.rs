/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use super::{SpecifiedValue, SpecifiedValueComponent, ValueInner};
use crate::values::generics::{Optional, image as gi, transform as gt};
use crate::values::specified::length::LengthUnit;
use crate::values::specified::{
    self as s,
    calc::{CalcNode, CalcNumeric},
};

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub(crate) struct InitialIndependenceAudit {
    pub(crate) element_context: bool,
    pub(crate) unresolved: bool,
}

impl InitialIndependenceAudit {
    fn merge(self, other: Self) -> Self {
        Self {
            element_context: self.element_context || other.element_context,
            unresolved: self.unresolved || other.unresolved,
        }
    }
}

const FREE: InitialIndependenceAudit = InitialIndependenceAudit {
    element_context: false,
    unresolved: false,
};
const CONTEXT: InitialIndependenceAudit = InitialIndependenceAudit {
    element_context: true,
    unresolved: false,
};
const UNKNOWN: InitialIndependenceAudit = InitialIndependenceAudit {
    element_context: false,
    unresolved: true,
};

fn all(values: impl IntoIterator<Item = InitialIndependenceAudit>) -> InitialIndependenceAudit {
    values
        .into_iter()
        .fold(FREE, InitialIndependenceAudit::merge)
}

fn length_unit(unit: LengthUnit) -> InitialIndependenceAudit {
    use LengthUnit::*;
    match unit {
        Px | In | Cm | Mm | Q | Pt | Pc | Vw | Svw | Lvw | Dvw | Vh | Svh | Lvh | Dvh | Vmin
        | Svmin | Lvmin | Dvmin | Vmax | Svmax | Lvmax | Dvmax => FREE,
        Em | Ex | Rex | Ch | Rch | Cap | Rcap | Ic | Ric | Rem | Lh | Rlh | Vi | Svi | Lvi
        | Dvi | Vb | Svb | Lvb | Dvb | Cqw | Cqh | Cqi | Cqb | Cqmin | Cqmax
        | ServoCharacterWidth => CONTEXT,
    }
}

fn calc(value: Option<&CalcNumeric>) -> InitialIndependenceAudit {
    value.map_or(FREE, |v| node(&v.node))
}

fn node(value: &CalcNode) -> InitialIndependenceAudit {
    use CalcNode::*;
    match value {
        Leaf(leaf) => match leaf {
            s::calc::Leaf::Length(value) => length_unit(value.length_unit()),
            s::calc::Leaf::Number(_)
            | s::calc::Leaf::Angle(_)
            | s::calc::Leaf::Time(_)
            | s::calc::Leaf::Resolution(_)
            | s::calc::Leaf::Percentage(_) => FREE,
            s::calc::Leaf::TreeCountingFunction(_) => CONTEXT,
            s::calc::Leaf::ColorComponent(_) | s::calc::Leaf::RandomKey(_) => UNKNOWN,
        },
        Negate(v) | Invert(v) | Sin(v) | Cos(v) | Tan(v) | Asin(v) | Acos(v) | Atan(v)
        | Sqrt(v) | Exp(v) | Abs(v) | Sign(v) => node(v),
        Sum(v) | Product(v) | MinMax(v, _) | Hypot(v) => all(v.iter().map(node)),
        Clamp { min, center, max } => all([node(min), node(center), node(max)]),
        Round { value, step, .. }
        | ModRem {
            dividend: value,
            divisor: step,
            ..
        }
        | Atan2(value, step)
        | Pow(value, step) => node(value).merge(node(step)),
        Log(value, base) => node(value).merge(match base {
            Optional::Some(base) => node(base),
            Optional::None => FREE,
        }),
        Progress {
            value, start, end, ..
        } => all([node(value), node(start), node(end)]),
        Random(_) => UNKNOWN,
        Anchor(_) | AnchorSize(_) => CONTEXT,
    }
}

fn lp(value: &s::LengthPercentage) -> InitialIndependenceAudit {
    match value {
        s::LengthPercentage::Length(value) => length_unit(value.length_unit()),
        s::LengthPercentage::Percentage(_) => FREE,
        s::LengthPercentage::Calc(value) => node(&value.node),
    }
}

fn length(value: &s::Length) -> InitialIndependenceAudit {
    lp(&s::LengthPercentage::from(value.clone()))
}

fn color(value: &s::Color) -> InitialIndependenceAudit {
    use s::Color::*;
    match value {
        CurrentColor | Absolute(_) => FREE,
        System(_) | MozInheritFromBody => CONTEXT,
        LightDark(ld) => {
            let branches = color(&ld.light).merge(color(&ld.dark));
            if branches != FREE {
                return branches;
            }
            match (
                ld.light.to_computed_color(None),
                ld.dark.to_computed_color(None),
            ) {
                (Ok(light), Ok(dark)) if light == dark => FREE,
                (Ok(_), Ok(_)) => CONTEXT,
                _ => UNKNOWN,
            }
        },
        ColorMix(mix) => all(mix.items.iter().map(|item| {
            color(&item.color).merge(match &item.percentage {
                Optional::Some(p) => calc(p.as_calc()),
                Optional::None => FREE,
            })
        })),
        ContrastColor(color_value) => color(color_value),
        ColorFunction(function) => {
            let origin = function.origin_color().map_or(FREE, color);
            if value.to_computed_color(None).is_ok() {
                origin
            } else {
                origin.merge(UNKNOWN)
            }
        },
    }
}

fn position_component<T>(value: &s::position::PositionComponent<T>) -> InitialIndependenceAudit {
    use s::position::PositionComponent::*;
    match value {
        Center => FREE,
        Length(value) => lp(value),
        Side(_, value) => value.as_ref().map_or(FREE, lp),
    }
}

fn position(value: &s::Position) -> InitialIndependenceAudit {
    position_component(&value.horizontal).merge(position_component(&value.vertical))
}

fn stop<T>(
    value: &gi::GradientItem<s::Color, T>,
    dimension: impl Fn(&T) -> InitialIndependenceAudit,
) -> InitialIndependenceAudit {
    match value {
        gi::GradientItem::SimpleColorStop(c) => color(c),
        gi::GradientItem::ComplexColorStop { color: c, position } => {
            color(c).merge(dimension(position))
        },
        gi::GradientItem::InterpolationHint(p) => dimension(p),
    }
}

fn gradient(value: &s::image::Gradient) -> InitialIndependenceAudit {
    match value {
        gi::Gradient::Linear {
            direction, items, ..
        } => {
            let direction = match direction {
                s::image::LineDirection::Angle(a) => calc(a.as_calc()),
                s::image::LineDirection::Horizontal(_)
                | s::image::LineDirection::Vertical(_)
                | s::image::LineDirection::Corner(_, _) => FREE,
            };
            direction.merge(all(items.iter().map(|item| stop(item, lp))))
        },
        gi::Gradient::Radial {
            shape,
            position: p,
            items,
            ..
        } => {
            let shape = match shape {
                gi::EndingShape::Circle(gi::Circle::Radius(r)) => length(&r.0),
                gi::EndingShape::Circle(gi::Circle::Extent(_))
                | gi::EndingShape::Ellipse(gi::Ellipse::Extent(_)) => FREE,
                gi::EndingShape::Ellipse(gi::Ellipse::Radii(x, y)) => lp(&x.0).merge(lp(&y.0)),
            };
            all([
                shape,
                position(p),
                all(items.iter().map(|item| stop(item, lp))),
            ])
        },
        gi::Gradient::Conic {
            angle,
            position: p,
            items,
            ..
        } => all([
            calc(angle.as_calc()),
            position(p),
            all(items.iter().map(|item| {
                stop(item, |value| match value {
                    s::AngleOrPercentage::Angle(a) => calc(a.as_calc()),
                    s::AngleOrPercentage::Percentage(p) => calc(p.as_calc()),
                })
            })),
        ]),
    }
}

fn image(value: &s::Image) -> InitialIndependenceAudit {
    match value {
        gi::Image::None | gi::Image::Url(_) => FREE,
        gi::Image::Gradient(g) => gradient(g),
        #[cfg(feature = "gecko")]
        gi::Image::Element(_) | gi::Image::MozSymbolicIcon(_) => UNKNOWN,
        #[cfg(feature = "servo")]
        gi::Image::PaintWorklet(_) => UNKNOWN,
        gi::Image::CrossFade(fade) => all(fade.elements.iter().map(|item| {
            let amount = match &item.percent {
                Optional::Some(p) => calc(p.as_calc()),
                Optional::None => FREE,
            };
            amount.merge(match &item.image {
                gi::CrossFadeImage::Image(i) => image(i),
                gi::CrossFadeImage::Color(c) => color(c),
            })
        })),
        gi::Image::ImageSet(set) => all(set
            .items
            .iter()
            .map(|item| image(&item.image).merge(calc(item.resolution.as_calc())))),
        gi::Image::LightDark(ld) => {
            let branches = image(&ld.light).merge(image(&ld.dark));
            if matches!((&ld.light, &ld.dark), (gi::Image::None, gi::Image::None)) {
                branches
            } else {
                branches.merge(UNKNOWN)
            }
        },
        gi::Image::Image(c) => color(c),
    }
}

fn transform(value: &s::Transform) -> InitialIndependenceAudit {
    use gt::TransformOperation::*;
    all(value.0.iter().map(|operation| match operation {
        Matrix(m) => all([&m.a, &m.b, &m.c, &m.d, &m.e, &m.f]
            .into_iter()
            .map(|v| calc(v.as_calc()))),
        Matrix3D(m) => all([
            &m.m11, &m.m12, &m.m13, &m.m14, &m.m21, &m.m22, &m.m23, &m.m24, &m.m31, &m.m32, &m.m33,
            &m.m34, &m.m41, &m.m42, &m.m43, &m.m44,
        ]
        .into_iter()
        .map(|v| calc(v.as_calc()))),
        Skew(x, y) => calc(x.as_calc()).merge(calc(y.as_calc())),
        SkewX(a) | SkewY(a) | Rotate(a) | RotateX(a) | RotateY(a) | RotateZ(a) => calc(a.as_calc()),
        Translate(x, y) => lp(x).merge(lp(y)),
        TranslateX(x) | TranslateY(x) => lp(x),
        TranslateZ(z) => length(z),
        Translate3D(x, y, z) => all([lp(x), lp(y), length(z)]),
        Scale(x, y) => calc(x.as_calc()).merge(calc(y.as_calc())),
        ScaleX(n) | ScaleY(n) | ScaleZ(n) => calc(n.as_calc()),
        Scale3D(x, y, z) => all([calc(x.as_calc()), calc(y.as_calc()), calc(z.as_calc())]),
        Rotate3D(x, y, z, a) => all([
            calc(x.as_calc()),
            calc(y.as_calc()),
            calc(z.as_calc()),
            calc(a.as_calc()),
        ]),
        Perspective(gt::PerspectiveFunction::None) => FREE,
        Perspective(gt::PerspectiveFunction::Length(v)) => length(v),
        InterpolateMatrix {
            from_list, to_list, ..
        } => transform(from_list).merge(transform(to_list)),
        AccumulateMatrix {
            from_list,
            to_list,
            count,
        } => all([
            transform(from_list),
            transform(to_list),
            calc(count.as_calc()),
        ]),
    }))
}

fn component(value: &SpecifiedValueComponent) -> InitialIndependenceAudit {
    use SpecifiedValueComponent::*;
    match value {
        Length(v) => length(v),
        LengthPercentage(v) => lp(v),
        Number(v) => calc(v.as_calc()),
        Integer(v) => calc(v.as_calc()),
        Percentage(v) => calc(v.as_calc()),
        Angle(v) => calc(v.as_calc()),
        Time(v) => calc(v.as_calc()),
        Resolution(v) => calc(v.as_calc()),
        Color(v) => color(v),
        Image(v) => image(v),
        TransformFunction(v) => transform(v),
        TransformList(v) => all(v.components.iter().map(component)),
        CustomIdent(_) | String(_) | Url(_) => FREE,
    }
}

pub(super) fn inspect(value: &SpecifiedValue) -> InitialIndependenceAudit {
    match &value.v {
        ValueInner::Component(value) => component(value),
        ValueInner::List(list) => all(list.components.iter().map(component)),
        ValueInner::Universal(_) => UNKNOWN,
    }
}
