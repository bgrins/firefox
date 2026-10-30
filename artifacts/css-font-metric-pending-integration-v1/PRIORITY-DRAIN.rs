#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum ComputationStatus {
    Ready,
    Pending,
}

#[derive(Default)]
struct PriorityCompletion {
    active: PrioritaryPropertyIdSet,
    complete: PrioritaryPropertyIdSet,
    claimed: PrioritaryPropertyIdSet,
}

impl PriorityCompletion {
    fn ensure_ordinary(
        &mut self,
        id: PrioritaryPropertyId,
        apply: &mut impl FnMut(PrioritaryPropertyId) -> ComputationStatus,
    ) -> ComputationStatus {
        if self.complete.contains(id) {
            return ComputationStatus::Ready;
        }
        if self.active.contains(id) || self.claimed.contains(id) {
            return ComputationStatus::Pending;
        }
        self.active.insert(id);
        for dependency in id.dependencies().iter() {
            if self.ensure_ordinary(dependency, apply) == ComputationStatus::Pending {
                self.suspend(id);
                return ComputationStatus::Pending;
            }
        }
        if apply(id) == ComputationStatus::Pending {
            self.suspend(id);
            return ComputationStatus::Pending;
        }
        self.finish(id);
        ComputationStatus::Ready
    }

    fn finish(&mut self, id: PrioritaryPropertyId) {
        assert!(self.active.contains(id));
        self.active.remove(id);
        self.complete.insert(id);
    }

    fn suspend(&mut self, id: PrioritaryPropertyId) {
        self.active.remove(id);
    }
}

struct MetricDrain<'a, 'b> {
    declarations: &'a Declarations<'b>,
    continuations: Vec<(PrioritaryPropertyId, MetricPreparation<'a, 'b>)>,
    complete: PrioritaryPropertyIdSet,
    requested: PrioritaryPropertyIdSet,
    cursor: usize,
}

enum MetricDrainStep {
    Prerequisite(PrioritaryPropertyId),
    References(LonghandId, Arc<UnparsedValue>),
    Published(PrioritaryPropertyId),
    Complete,
    Invalidated(PrioritaryPropertyId),
    WrongReply,
}

impl<'a, 'b> MetricDrain<'a, 'b> {
    fn new(declarations: &'a Declarations<'b>) -> Self {
        Self {
            declarations,
            continuations: Vec::new(),
            complete: PrioritaryPropertyIdSet::default(),
            requested: PrioritaryPropertyIdSet::default(),
            cursor: 0,
        }
    }

    fn request(
        &mut self,
        id: PrioritaryPropertyId,
        completion: &mut PriorityCompletion,
    ) -> Result<(), PrioritaryPropertyId> {
        if self.requested.contains(id) {
            return Ok(());
        }
        if completion.claimed.contains(id) || completion.active.contains(id) {
            return Err(id);
        }
        self.requested.insert(id);
        if completion.complete.contains(id) {
            self.complete.insert(id);
        } else {
            completion.claimed.insert(id);
        }
        Ok(())
    }

    fn poll(
        &mut self,
        cascade: &mut Cascade,
        context: &mut computed::Context,
        cache: &mut ShorthandsWithPropertyReferencesCache,
        attribute_tracker: &mut AttributeTracker,
        completion: &mut PriorityCompletion,
        mut reference: Option<(LonghandId, Arc<UnparsedValue>)>,
    ) -> MetricDrainStep {
        if let Some((longhand, value)) = reference.as_ref() {
            let valid = self.continuations.iter().any(|(id, state)| {
                id.to_longhand() == *longhand
                    && state
                        .waiting
                        .as_ref()
                        .is_some_and(|waiting| std::ptr::eq(waiting.as_ref(), value.as_ref()))
            });
            if !valid {
                return MetricDrainStep::WrongReply;
            }
        }
        let requested: Vec<_> = self.requested.iter().collect();
        for offset in 0..requested.len() {
            let position = (self.cursor + offset) % requested.len();
            let id = requested[position];
            if reference
                .as_ref()
                .is_some_and(|(longhand, _)| *longhand != id.to_longhand())
            {
                continue;
            }
            if self.complete.contains(id) {
                continue;
            }
            self.cursor = (position + 1) % requested.len();
            for dependency in id.dependencies().iter() {
                if !completion.complete.contains(dependency) {
                    if reference.is_some() {
                        return MetricDrainStep::Invalidated(id);
                    }
                    return MetricDrainStep::Prerequisite(dependency);
                }
            }
            let index = match self
                .continuations
                .iter()
                .position(|(candidate, _)| *candidate == id)
            {
                Some(index) => index,
                None => {
                    self.continuations.push((
                        id,
                        cascade.begin_metric_preparation(context, self.declarations, id),
                    ));
                    self.continuations.len() - 1
                },
            };
            let state = &mut self.continuations[index].1;
            let resolved = match reference.take() {
                Some((longhand, value)) if longhand == id.to_longhand() => Some(value),
                Some(_) => return MetricDrainStep::Invalidated(id),
                None => None,
            };
            match cascade.resume_metric_preparation(
                context,
                cache,
                attribute_tracker,
                state,
                &completion.complete,
                resolved,
            ) {
                MetricPreparationStep::Prerequisites(dependencies) => {
                    let dependency = dependencies
                        .iter()
                        .find(|dependency| !completion.complete.contains(*dependency))
                        .unwrap();
                    return MetricDrainStep::Prerequisite(dependency);
                },
                MetricPreparationStep::References(longhand, value) => {
                    return MetricDrainStep::References(longhand, value);
                },
                MetricPreparationStep::Invalidated => return MetricDrainStep::Invalidated(id),
                MetricPreparationStep::Complete => {},
            }
            let (_, state) = self.continuations.remove(index);
            if let Err(state) = cascade.publish_prepared_metric(
                context,
                cache,
                attribute_tracker,
                state,
                &completion.complete,
            ) {
                self.continuations.push((id, state));
                return MetricDrainStep::Invalidated(id);
            }
            self.complete.insert(id);
            completion.complete.insert(id);
            completion.claimed.remove(id);
            return MetricDrainStep::Published(id);
        }
        if reference.is_some() {
            return MetricDrainStep::WrongReply;
        }
        MetricDrainStep::Complete
    }
}
