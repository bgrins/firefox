fn pending_metric_action(&self) -> Option<MetricAction> {
    self.metric_action.clone()
}

fn perform_metric_action(
    &mut self,
    action: &MetricAction,
    attribute_tracker: &mut AttributeTracker,
) -> MetricActionProgress {
    let Some(current) = &self.metric_action else {
        return MetricActionProgress::WrongAction;
    };
    if !std::ptr::eq(current.identity.as_ref(), action.identity.as_ref())
        || current.root != action.root
        || current.owner != action.owner
        || current.index != action.index
        || current.prerequisite != action.prerequisite
        || self.frame_root.as_ref() != Some(&action.root)
        || !self.frames.last().is_some_and(|frame| frame.index == action.index && frame.var == action.owner && matches!(frame.phase, FramePhase::Publish))
        || !matches!(self.var_info[action.index].publication, NodePublication::Pending(_))
    {
        return MetricActionProgress::WrongAction;
    }
    use PrioritaryPropertyId::*;
    if !matches!(action.prerequisite, FontWeight | FontWidth | FontStyle | FontSizeAdjust | Direction | WritingMode | TextOrientation) {
        return MetricActionProgress::Unsupported;
    }
    if self.priority_completion.complete.contains(action.prerequisite) {
        self.metric_action = None;
        return MetricActionProgress::AlreadyComplete;
    }
    if self.metric_drain.request(action.prerequisite, &mut self.priority_completion).is_err() {
        return MetricActionProgress::Invalidated;
    }
    match self.metric_drain.poll(
        self.cascade,
        self.computed_context,
        self.cache,
        attribute_tracker,
        &mut self.priority_completion,
        None,
    ) {
        MetricDrainStep::Published(id) => {
            if id == action.prerequisite {
                assert!(self.priority_completion.complete.contains(id));
                self.metric_action = None;
            }
            MetricActionProgress::Published(id)
        },
        MetricDrainStep::Prerequisite(id) => MetricActionProgress::GeneratedPrerequisite(id),
        MetricDrainStep::References(id, value) => MetricActionProgress::References(id, value),
        MetricDrainStep::Invalidated(_) | MetricDrainStep::WrongReply | MetricDrainStep::Complete => MetricActionProgress::Invalidated,
    }
}
