#[derive(Clone, Copy, Eq, PartialEq)]
enum ReferenceReadiness {
    Ready,
    SemanticCycle,
    ComputationPending,
}

struct ReferenceWalk {
    queued: SmallVec<[References; 5]>,
    current: Option<(References, usize)>,
    waiting: Option<VarType>,
    flags: ReferenceFlags,
}

enum ReferenceWalkStep {
    Link(VarType),
    Complete,
    WrongReply,
}

impl ReferenceWalk {
    fn new(root: &References) -> Self {
        let mut queued = SmallVec::new();
        queued.push(root.clone());
        Self {
            queued,
            current: None,
            waiting: None,
            flags: ReferenceFlags::empty(),
        }
    }

    fn resume(
        &mut self,
        url_data: &UrlExtraData,
        property_id: Option<PropertyIdRef>,
        context: &mut Context,
        attribute_tracker: &mut AttributeTracker,
        mut reply: Option<(VarType, ReferenceReadiness)>,
    ) -> ReferenceWalkStep {
        if let Some((target, readiness)) = reply.as_ref() {
            if self.waiting.as_ref() != Some(target) {
                return ReferenceWalkStep::WrongReply;
            }
            if *readiness == ReferenceReadiness::ComputationPending {
                return ReferenceWalkStep::Link(target.clone());
            }
        }
        loop {
            if self
                .current
                .as_ref()
                .is_some_and(|(refs, next)| *next == refs.refs.len())
            {
                self.current = None;
            }
            if self.current.is_none() {
                let Some(refs) = self.queued.pop() else {
                    return ReferenceWalkStep::Complete;
                };
                self.flags |= refs.flags;
                self.current = Some((refs, 0));
            }
            let (refs, cursor) = self.current.as_mut().unwrap();
            let Some(next) = refs.refs.get(*cursor) else {
                continue;
            };
            if self.waiting.is_none() {
                if next.substitution_kind == SubstitutionFunctionKind::Env {
                    let device = context.stylist.device();
                    if device
                        .environment()
                        .get(&next.name, device, url_data)
                        .is_none()
                    {
                        if let Some(fallback) = &next.fallback {
                            self.queued.push(fallback.references.clone());
                        }
                    }
                    *cursor += 1;
                    continue;
                }
                let target = if next.substitution_kind == SubstitutionFunctionKind::Attr {
                    if !next.is_attr_with_type() {
                        if let Some(fallback) = &next.fallback {
                            if !next
                                .attribute_data
                                .non_type_primary_is_valid(&next.name, attribute_tracker)
                            {
                                self.queued.push(fallback.references.clone());
                            }
                        }
                        *cursor += 1;
                        continue;
                    }
                    let Some(namespace) = next.attribute_data.namespace() else {
                        if let Some(fallback) = &next.fallback {
                            self.queued.push(fallback.references.clone());
                        }
                        *cursor += 1;
                        continue;
                    };
                    if !context.map().contains_attr(&next.name, namespace) {
                        if let Ok(value) = get_attr_value_for_cycle_resolution(
                            &next.name,
                            &next.attribute_data,
                            url_data,
                            attribute_tracker,
                        ) {
                            context.map_mut().insert_attr(&next.name, namespace, value);
                        }
                    }
                    VarType::Attr(next.name.clone(), namespace.clone())
                } else {
                    VarType::Custom(next.name.clone())
                };
                self.waiting = Some(target.clone());
                return ReferenceWalkStep::Link(target);
            }
            let Some((_, readiness)) = reply.take() else {
                return ReferenceWalkStep::Link(self.waiting.as_ref().unwrap().clone());
            };
            debug_assert!(readiness != ReferenceReadiness::ComputationPending);
            let resolved = match next.substitution_kind {
                SubstitutionFunctionKind::Var => {
                    let registration =
                        context.stylist.get_custom_property_registration(&next.name);
                    context.map().get_var(registration, &next.name)
                },
                SubstitutionFunctionKind::Attr => next
                    .attribute_data
                    .namespace()
                    .and_then(|namespace| context.map().get_attr(&next.name, namespace)),
                SubstitutionFunctionKind::Env => unreachable!(),
            };
            let mut primary_valid = false;
            if let Some(resolved) = resolved {
                if let Some(value) = resolved.as_universal() {
                    primary_valid = !value.has_references();
                    self.flags |= value.references.flags;
                } else {
                    primary_valid = true;
                }
                if primary_valid && next.is_attr_with_type() {
                    let value = resolved.to_variable_value();
                    primary_valid = next
                        .attribute_data
                        .parse_typed_value(
                            &mut cssparser::Parser::new(&value.css),
                            url_data,
                            property_id,
                        )
                        .is_ok();
                }
            }
            if !primary_valid {
                if let Some(fallback) = &next.fallback {
                    self.queued.push(fallback.references.clone());
                }
            }
            self.waiting = None;
            *cursor += 1;
        }
    }
}
