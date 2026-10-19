impl Animate for Display {
    #[inline]
    fn animate(&self, other: &Self, procedure: Procedure) -> Result<Self, ()> {
        match procedure {
            Procedure::Interpolate { progress } => {
                if !crate::pref!("layout.css.display-animations.enabled") {
                    return animate_discrete(self, other, procedure)
                };
                let (this_weight, other_weight) = procedure.weights();
                match (*self, *other) {
                    (_, Display::None) => Ok(if this_weight > 0.0 { *self } else { *other }),
                    (Display::None, _) => Ok(if other_weight > 0.0 { *other } else { *self }),
                    _ => Ok(if progress >= 0.5 { *other } else { *self }),
                }
            },
            _ => Err(()),
        }
    }
}

