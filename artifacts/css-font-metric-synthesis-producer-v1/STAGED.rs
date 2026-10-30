struct PreparedMetricDeclaration {
    declaration: PropertyDeclaration,
    priority: CascadePriority,
}

struct MetricPreparation<'a, 'b> {
    longhand: LonghandId,
    declarations: &'a Declarations<'b>,
    cursor: Option<usize>,
    flags: RuleCascadeFlags,
    initial_revert: Option<(CascadePriority, RevertKind)>,
    revert: Option<(CascadePriority, RevertKind)>,
    waiting: Option<Arc<UnparsedValue>>,
    prepared: SmallVec<[PreparedMetricDeclaration; 2]>,
    complete: bool,
}

enum MetricPreparationStep {
    Prerequisites(&'static PrioritaryPropertyIdSet),
    References(LonghandId, Arc<UnparsedValue>),
    Complete,
    Invalidated,
}

impl MetricPreparation<'_, '_> {
    fn retain(&mut self, declaration: PropertyDeclaration, priority: CascadePriority) {
        debug_assert!(!matches!(
            declaration,
            PropertyDeclaration::WithVariables(..)
        ));
        let revert = declaration
            .get_css_wide_keyword()
            .and_then(|keyword| keyword.revert_kind());
        self.prepared.push(PreparedMetricDeclaration {
            declaration,
            priority,
        });
        if let Some(revert) = revert {
            self.revert = Some((priority, revert));
            self.advance();
        } else {
            self.complete = true;
        }
    }

    fn advance(&mut self) {
        let index = self
            .cursor
            .expect("advancing an exhausted declaration cursor");
        if PrioritaryPropertyId::from_longhand(self.longhand).is_none() {
            self.cursor = next_font_declaration(self.declarations, self.longhand, index + 1);
            return;
        }
        let next = self.declarations.longhand_declarations[index].next_index;
        self.cursor = (next != 0).then_some(next as usize);
    }
}

impl Cascade<'_> {
    fn begin_metric_preparation<'a, 'b>(
        &self,
        context: &computed::Context,
        declarations: &'a Declarations<'b>,
        id: PrioritaryPropertyId,
    ) -> MetricPreparation<'a, 'b> {
        use PrioritaryPropertyId::*;
        assert!(matches!(
            id,
            FontWeight
                | FontWidth
                | FontStyle
                | FontSizeAdjust
                | Direction
                | WritingMode
                | TextOrientation
        ));
        self.begin_font_preparation(context, declarations, id.to_longhand())
    }

    fn begin_font_preparation<'a, 'b>(
        &self,
        context: &computed::Context,
        declarations: &'a Declarations<'b>,
        longhand: LonghandId,
    ) -> MetricPreparation<'a, 'b> {
        let cursor = if let Some(id) = PrioritaryPropertyId::from_longhand(longhand) {
            let index = declarations.prioritary_positions[id as usize].most_important;
            (index != DeclarationIndex::MAX).then_some(index as usize)
        } else {
            assert!(is_synthesis_longhand(longhand));
            next_font_declaration(declarations, longhand, 0)
        };
        let initial_revert = self.reverted.longhands.get(&longhand).copied();
        MetricPreparation {
            longhand,
            declarations,
            cursor,
            flags: context.included_cascade_flags,
            initial_revert,
            revert: initial_revert,
            waiting: None,
            prepared: SmallVec::new(),
            complete: false,
        }
    }

    // `completed` is supplied by the readiness scheduler, not the existing early-set ensured bit.
    fn resume_metric_preparation(
        &self,
        context: &mut computed::Context,
        cache: &mut ShorthandsWithPropertyReferencesCache,
        attribute_tracker: &mut AttributeTracker,
        state: &mut MetricPreparation,
        completed: &PrioritaryPropertyIdSet,
        mut resolved_reference: Option<Arc<UnparsedValue>>,
    ) -> MetricPreparationStep {
        let longhand = state.longhand;
        let priority = PrioritaryPropertyId::from_longhand(longhand);
        if priority.is_some_and(|id| self.ensured_prioritary.contains(id))
            || state.flags != context.included_cascade_flags
            || self.seen.longhands.contains(longhand)
            || self.reverted.longhands.get(&longhand).copied() != state.initial_revert
        {
            return MetricPreparationStep::Invalidated;
        }
        if let Some(id) = priority {
            let prerequisites = id.dependencies();
            if !completed.contains_all(prerequisites) {
                return MetricPreparationStep::Prerequisites(prerequisites);
            }
        }
        loop {
            if state.complete {
                return MetricPreparationStep::Complete;
            }
            let Some(index) = state.cursor else {
                state.complete = true;
                continue;
            };
            let entry = state.declarations.longhand_declarations[index];
            if let Some(value) = state.waiting.as_ref() {
                let Some(resolved) = resolved_reference.take() else {
                    return MetricPreparationStep::References(longhand, value.clone());
                };
                if !std::ptr::eq(value.as_ref(), resolved.as_ref()) {
                    return MetricPreparationStep::Invalidated;
                }
                let declaration = self
                    .substitute_variables_if_needed(context, cache, entry.decl, attribute_tracker)
                    .into_owned();
                state.waiting = None;
                resolved_reference = None;
                state.retain(declaration, entry.priority);
                continue;
            }
            if !(entry.priority.flags() - state.flags).is_empty()
                || state.revert.is_some_and(|(priority, kind)| {
                    !priority.allows_when_reverted(&entry.priority, kind)
                })
            {
                state.advance();
                continue;
            }
            if let PropertyDeclaration::WithVariables(value) = entry.decl {
                state.waiting = Some(value.value.clone());
                resolved_reference = None;
                continue;
            }
            state.retain(entry.decl.clone(), entry.priority);
        }
    }

    fn publish_prepared_metric<'a, 'b>(
        &mut self,
        context: &mut computed::Context,
        cache: &mut ShorthandsWithPropertyReferencesCache,
        attribute_tracker: &mut AttributeTracker,
        state: MetricPreparation<'a, 'b>,
        completed: &PrioritaryPropertyIdSet,
    ) -> Result<(), MetricPreparation<'a, 'b>> {
        let longhand = state.longhand;
        let priority = PrioritaryPropertyId::from_longhand(longhand);
        if priority.is_some_and(|id| self.ensured_prioritary.contains(id))
            || !state.complete
            || state.waiting.is_some()
            || priority.is_some_and(|id| !completed.contains_all(id.dependencies()))
            || state.flags != context.included_cascade_flags
            || self.seen.longhands.contains(longhand)
            || self.reverted.longhands.get(&longhand).copied() != state.initial_revert
        {
            return Err(state);
        }
        for entry in state.prepared {
            self.apply_one_longhand(
                context,
                longhand,
                &entry.declaration,
                entry.priority,
                cache,
                attribute_tracker,
            );
        }
        if let Some(id) = priority {
            if self.seen.longhands.contains(longhand) {
                self.did_apply_prioritary_property(context, id);
            }
            self.ensured_prioritary.insert(id);
        }
        Ok(())
    }
}

