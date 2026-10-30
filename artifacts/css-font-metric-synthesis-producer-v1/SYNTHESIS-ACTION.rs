fn perform_synthesis_action(
    &mut self,
    longhand: LonghandId,
    attribute_tracker: &mut AttributeTracker,
) -> MetricActionProgress {
    if !is_synthesis_longhand(longhand) {
        return MetricActionProgress::Unsupported;
    }
    if self.completed_font_inputs.contains(longhand) {
        self.metric_action = None;
        return MetricActionProgress::AlreadyComplete;
    }
    let state = self.font_preparation.get_or_insert_with(|| {
        self.cascade.begin_font_preparation(self.computed_context, self.decls, longhand)
    });
    if state.longhand != longhand {
        return MetricActionProgress::Invalidated;
    }
    match self.cascade.resume_metric_preparation(
        self.computed_context, self.cache, attribute_tracker, state,
        &self.priority_completion.complete, None,
    ) {
        MetricPreparationStep::References(id, value) => return MetricActionProgress::References(id, value),
        MetricPreparationStep::Prerequisites(_) | MetricPreparationStep::Invalidated => return MetricActionProgress::Invalidated,
        MetricPreparationStep::Complete => {},
    }
    let state = self.font_preparation.take().unwrap();
    if let Err(state) = self.cascade.publish_prepared_metric(
        self.computed_context, self.cache, attribute_tracker, state, &self.priority_completion.complete,
    ) {
        self.font_preparation = Some(state);
        return MetricActionProgress::Invalidated;
    }
    self.completed_font_inputs.insert(longhand);
    self.metric_action = None;
    MetricActionProgress::Published(FontTarget::Synthesis(longhand))
}
