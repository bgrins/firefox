let step = step.abs();

                // TODO(emilio): Seems like at least a few of these
                // special-cases could be removed if we do the math in a
                // particular order.
                if step.is_zero() {
                    value = f32::NAN;
                } else if value.is_infinite() {
                    if step.is_infinite() {
                        value = f32::NAN
                    }
                } else if step.is_infinite() {
                    value = match strategy {
                        RoundingStrategy::Nearest | RoundingStrategy::ToZero => {
                            if value.is_sign_negative() { -0.0 } else { 0.0 }
                        },
                        RoundingStrategy::Up => {
                            if !value.is_sign_negative() && !value.is_zero() {
                                f32::INFINITY
                            } else if !value.is_sign_negative() && value.is_zero() {
                                value
                            } else {
                                -0.0
                            }
                        },
                        RoundingStrategy::Down => {
                            if value.is_sign_negative() && !value.is_zero() {
                                -f32::INFINITY
                            } else if value.is_sign_negative() && value.is_zero() {
                                value
                            } else {
                                0.0
                            }
                        },
                    };
                } else {
                    let div = value / step;
                    let lower_bound = div.floor() * step;
                    let upper_bound = div.ceil() * step;

                    value = match strategy {
                        RoundingStrategy::Nearest => {
                            // In case of a tie, use the upper bound
                            if value - lower_bound < upper_bound - value {
                                lower_bound
                            } else {
                                upper_bound
                            }
                        },
                        RoundingStrategy::Up => upper_bound,
                        RoundingStrategy::Down => lower_bound,
                        RoundingStrategy::ToZero => {
                            // In case of a tie, use the upper bound
                            if lower_bound.abs() < upper_bound.abs() {
                                lower_bound
                            } else {
                                upper_bound
                            }
                        },
                    }
                }

                