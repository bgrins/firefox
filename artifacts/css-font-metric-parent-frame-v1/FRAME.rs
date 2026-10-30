#[derive(Clone, Copy)]
enum FramePhase {
    References,
    Prepare,
    Units,
    PrioritySize,
    PriorityReferences,
    LateDefault,
    Close,
    Publish,
}

#[derive(Clone, Copy)]
enum LinkPurpose {
    Reference,
    Unit,
    PrioritySize,
    LateDefault,
}

struct TraversalFrame {
    var: VarType,
    index: usize,
    lowlink: usize,
    self_ref: bool,
    registered: bool,
    selected_dependency_eligible: bool,
    value_non_custom_refs: ReferenceFlags,
    value: Option<Arc<ComputedPropertyValue>>,
    prepared_custom: Option<PreparedCustomValue>,
    phase: FramePhase,
    walk: Option<ReferenceWalk>,
    unit_links: SmallVec<[SingleNonCustomReference; 3]>,
    unit_cursor: usize,
    priority_cursor: usize,
    waiting: Option<(VarType, LinkPurpose)>,
    reference_reply: Option<(VarType, ReferenceReadiness)>,
}

enum FrameStep {
    Link(VarType),
    Complete(VisitResult),
    Pending,
}

impl TraversalFrame {
    fn link(&mut self, target: VarType, purpose: LinkPurpose) -> FrameStep {
        assert!(self.waiting.is_none());
        self.waiting = Some((target.clone(), purpose));
        FrameStep::Link(target)
    }

    fn receive(&mut self, target: VarType, result: VisitResult, context: &Context) -> bool {
        let Some((waiting, purpose)) = self.waiting.as_ref() else {
            return false;
        };
        if *waiting != target || matches!(result, VisitResult::ComputationPending(_)) {
            return false;
        }
        if let VisitResult::SemanticOpen(next_index) = result {
            let next = &context.var_info[next_index];
            assert!(matches!(
                next.publication.readiness(),
                NodeReadiness::SemanticOpen
            ));
            if next_index > self.index {
                self.lowlink = cmp::min(self.lowlink, next.lowlink);
            } else if next_index == self.index {
                self.self_ref = true;
            } else if next.var.is_some() {
                self.lowlink = cmp::min(self.lowlink, next_index);
            }
        }
        match purpose {
            LinkPurpose::Reference => {
                assert!(self.reference_reply.is_none());
                self.reference_reply = Some((
                    target,
                    match result {
                        VisitResult::SemanticOpen(_) => ReferenceReadiness::SemanticOpen,
                        VisitResult::Complete => ReferenceReadiness::Ready,
                        VisitResult::CycleSettled => ReferenceReadiness::SemanticCycle,
                        VisitResult::ComputationPending(_) => unreachable!(),
                    },
                ));
            },
            LinkPurpose::Unit => self.unit_cursor += 1,
            LinkPurpose::PrioritySize | LinkPurpose::LateDefault => {},
        }
        self.waiting = None;
        true
    }

    fn step(
        &mut self,
        references: &NonCustomPropertyReferences,
        context: &mut Context,
        attribute_tracker: &mut AttributeTracker,
        publication_ready: &mut impl FnMut(&VarType) -> bool,
    ) -> FrameStep {
        assert!(self.waiting.is_none());
        loop {
            match self.phase {
                FramePhase::References => {
                    let value = self.value.as_ref().unwrap();
                    let name = match &self.var {
                        VarType::Custom(name) | VarType::Attr(name, _) => name,
                        VarType::NonCustom(_) => unreachable!(),
                    };
                    let walk = self
                        .walk
                        .get_or_insert_with(|| ReferenceWalk::new(&value.references));
                    match walk.resume(
                        &value.url_data,
                        Some(PropertyIdRef::from(name)),
                        context,
                        attribute_tracker,
                        self.reference_reply.take(),
                    ) {
                        ReferenceWalkStep::Link(target) => {
                            return self.link(target, LinkPurpose::Reference);
                        },
                        ReferenceWalkStep::WrongReply => {
                            unreachable!("Frame owns its reference reply")
                        },
                        ReferenceWalkStep::Complete => {},
                    }
                    self.value_non_custom_refs |= walk.flags;
                    self.walk = None;
                    self.phase = FramePhase::Prepare;
                },
                FramePhase::Prepare => {
                    if let VarType::Custom(ref name) = self.var {
                        if self.selected_dependency_eligible {
                            let may_compute_color = self
                                .value_non_custom_refs
                                .intersects(ReferenceFlags::COLOR_SCHEME);
                            self.value_non_custom_refs
                                .remove(ReferenceFlags::COLOR_SCHEME);
                            if self.registered
                                && may_compute_color
                                && self.lowlink == self.index
                                && !self.self_ref
                                && context.stack.last() == Some(&self.index)
                            {
                                let prepared = prepare_custom_value(
                                    name,
                                    self.value.as_ref().unwrap(),
                                    context.stylist,
                                    context.computed_context,
                                    attribute_tracker,
                                );
                                if prepared.depends_on_color_scheme() {
                                    self.value_non_custom_refs |= ReferenceFlags::COLOR_SCHEME;
                                }
                                self.prepared_custom = Some(prepared);
                            }
                        }
                    }
                    if self.registered && !self.value_non_custom_refs.is_empty() {
                        self.value_non_custom_refs.for_each_non_custom(
                            context.computed_context.is_root_element(),
                            |reference| self.unit_links.push(reference),
                        );
                    }
                    self.phase = FramePhase::Units;
                },
                FramePhase::Units => {
                    if let Some(reference) = self.unit_links.get(self.unit_cursor) {
                        return self.link(VarType::NonCustom(*reference), LinkPurpose::Unit);
                    }
                    self.phase = FramePhase::LateDefault;
                },
                FramePhase::PrioritySize => {
                    self.phase = FramePhase::PriorityReferences;
                    if self.var == VarType::NonCustom(SingleNonCustomReference::LhUnits) {
                        return self.link(
                            VarType::NonCustom(SingleNonCustomReference::FontUnits),
                            LinkPurpose::PrioritySize,
                        );
                    }
                },
                FramePhase::PriorityReferences => {
                    let VarType::NonCustom(reference) = self.var else {
                        unreachable!()
                    };
                    let entry = references[reference]
                        .as_ref()
                        .and_then(|values| values.get(self.priority_cursor));
                    let Some((longhand, value)) = entry else {
                        self.phase = FramePhase::LateDefault;
                        continue;
                    };
                    let walk = self.walk.get_or_insert_with(|| {
                        ReferenceWalk::new(&value.variable_value.references)
                    });
                    match walk.resume(
                        &value.variable_value.url_data,
                        Some(value.substitution_property_id(*longhand)),
                        context,
                        attribute_tracker,
                        self.reference_reply.take(),
                    ) {
                        ReferenceWalkStep::Link(target) => {
                            return self.link(target, LinkPurpose::Reference);
                        },
                        ReferenceWalkStep::WrongReply => {
                            unreachable!("Frame owns its reference reply")
                        },
                        ReferenceWalkStep::Complete => {},
                    }
                    self.walk = None;
                    self.priority_cursor += 1;
                },
                FramePhase::LateDefault => {
                    self.phase = FramePhase::Close;
                    if let VarType::Custom(ref name) = self.var {
                        let cyclic = self.self_ref
                            || self.lowlink < self.index
                            || context.stack.last() != Some(&self.index);
                        if self.registered
                            && self.selected_dependency_eligible
                            && cyclic
                            && !self
                                .value_non_custom_refs
                                .intersects(ReferenceFlags::COLOR_SCHEME)
                            && invalid_custom_value_depends_on_color_scheme(
                                name,
                                context.stylist,
                                context.computed_context,
                            )
                        {
                            return self.link(
                                VarType::NonCustom(SingleNonCustomReference::ColorScheme),
                                LinkPurpose::LateDefault,
                            );
                        }
                    }
                },
                FramePhase::Close => {
                    context.var_info[self.index].lowlink = self.lowlink;
                    if self.lowlink != self.index {
                        return FrameStep::Complete(VisitResult::SemanticOpen(self.index));
                    }
                    let mut in_loop = self.self_ref;
                    let mut members = SmallVec::<[usize; 5]>::new();
                    loop {
                        let index = context.stack.pop().expect("Frame's SCC remains owned");
                        let var = context.var_info[index].var.take().expect("Node pops once");
                        if index != self.index {
                            in_loop = true;
                        }
                        if in_loop {
                            context.var_info[index].publication.begin_cycle();
                            members.push(index);
                            context.handle_loop(&var);
                        }
                        if index == self.index {
                            assert_eq!(var, self.var);
                            break;
                        }
                    }
                    if in_loop {
                        for index in members {
                            context.var_info[index].publication.settle_cycle();
                        }
                        return FrameStep::Complete(VisitResult::CycleSettled);
                    }
                    let publication = match &self.var {
                        VarType::Custom(name) | VarType::Attr(name, _) => {
                            if let Some(prepared) = self.prepared_custom.take() {
                                ClosedValue::Prepared(name.clone(), prepared)
                            } else {
                                ClosedValue::Substitute(
                                    self.var.clone(),
                                    self.value.take().unwrap(),
                                )
                            }
                        },
                        VarType::NonCustom(reference) => {
                            ClosedValue::Prioritary(reference.to_prioritary_id())
                        },
                    };
                    context.var_info[self.index].publication.close(publication);
                    self.phase = FramePhase::Publish;
                },
                FramePhase::Publish => {
                    if !publication_ready(&self.var) {
                        return FrameStep::Pending;
                    }
                    context.publish_closed(self.index, attribute_tracker);
                    return FrameStep::Complete(VisitResult::Complete);
                },
            }
        }
    }
}
