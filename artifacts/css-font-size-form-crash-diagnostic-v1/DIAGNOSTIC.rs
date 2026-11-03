        fn write_metric_diagnostic(
            &self,
            out: &mut impl std::io::Write,
            result: VisitResult,
            progress: Option<&MetricActionProgress>,
        ) {
            let _ = writeln!(
                out,
                "CSS_METRIC_PENDING result={result:?} root={:?} reply={:?} count={} stack={:?} frames={} nodes={}",
                self.frame_root,
                self.frame_reply,
                self.count,
                self.stack.iter().take(16).collect::<Vec<_>>(),
                self.frames.len(),
                self.var_info.len()
            );
            let progress_name = match progress {
                None => "not-driven",
                Some(MetricActionProgress::Published(_)) => "published",
                Some(MetricActionProgress::AlreadyComplete) => "already-complete",
                Some(MetricActionProgress::GeneratedPrerequisite(_)) => "generated-prerequisite",
                Some(MetricActionProgress::References(_, _)) => "references",
                Some(MetricActionProgress::Invalidated) => "invalidated",
                Some(MetricActionProgress::Unsupported) => "unsupported",
                Some(MetricActionProgress::WrongAction) => "wrong-action",
            };
            let _ = writeln!(out, "CSS_METRIC_PENDING progress={progress_name}");
            match progress {
                Some(MetricActionProgress::References(id, value)) => {
                    let _ = writeln!(
                        out,
                        "CSS_METRIC_PENDING progress_property={id:?} value={:p}",
                        value.as_ref() as *const _
                    );
                },
                Some(MetricActionProgress::GeneratedPrerequisite(id)) => {
                    let _ = writeln!(
                        out,
                        "CSS_METRIC_PENDING prerequisite={:?}",
                        id.to_longhand()
                    );
                },
                _ => {},
            }
            if let Some(action) = &self.metric_action {
                let _ = writeln!(
                    out,
                    "CSS_METRIC_PENDING action={:p} root={:?} owner={:?} index={} target={:?}",
                    action.identity.as_ref() as *const _,
                    action.root,
                    action.owner,
                    action.index,
                    action.prerequisite
                );
            }
            for id in PrioritaryPropertyId::each() {
                let _ = writeln!(
                    out,
                    "CSS_METRIC_PENDING priority={:?} cascade_complete={} ledger_complete={} claimed={} active={} dynamic={} ensured={}",
                    id.to_longhand(),
                    self.cascade.completed_prioritary.contains(id),
                    self.priority_completion.complete.contains(id),
                    self.priority_completion.claimed.contains(id),
                    self.priority_completion.active.contains(id),
                    priority_has_dynamic_declarations(self.decls, id),
                    self.cascade.ensured_prioritary.contains(id)
                );
                for dependency in id.dependencies().iter() {
                    let _ = writeln!(
                        out,
                        "CSS_METRIC_PENDING dependency={:?}->{:?} ensured={} cascade_complete={} ledger_complete={}",
                        id.to_longhand(),
                        dependency.to_longhand(),
                        self.cascade.ensured_prioritary.contains(dependency),
                        self.cascade.completed_prioritary.contains(dependency),
                        self.priority_completion.complete.contains(dependency)
                    );
                }
            }
            for frame in self.frames.iter().rev().take(16) {
                let phase = match frame.phase {
                    FramePhase::References => "references",
                    FramePhase::Prepare => "prepare",
                    FramePhase::Units => "units",
                    FramePhase::PrioritySize => "priority-size",
                    FramePhase::PriorityReferences => "priority-references",
                    FramePhase::LateDefault => "late-default",
                    FramePhase::Close => "close",
                    FramePhase::Publish => "publish",
                };
                let _ = writeln!(
                    out,
                    "CSS_METRIC_PENDING frame={:?} index={} lowlink={} phase={phase} flags={} unit_cursor={} priority_cursor={} waiting={:?}",
                    frame.var,
                    frame.index,
                    frame.lowlink,
                    frame.value_non_custom_refs.bits(),
                    frame.unit_cursor,
                    frame.priority_cursor,
                    frame.waiting.as_ref().map(|(target, _)| target)
                );
            }
            for (index, node) in self.var_info.iter().enumerate().take(16) {
                let _ = writeln!(
                    out,
                    "CSS_METRIC_PENDING node={index} var={:?} lowlink={} readiness={:?}",
                    node.var,
                    node.lowlink,
                    node.publication.readiness()
                );
            }
            if let VisitResult::ComputationPending(index) | VisitResult::SemanticOpen(index) =
                result
            {
                if let Some(node) = self.var_info.get(index) {
                    let _ = writeln!(
                        out,
                        "CSS_METRIC_PENDING pending_node={index} var={:?} lowlink={} readiness={:?}",
                        node.var,
                        node.lowlink,
                        node.publication.readiness()
                    );
                }
            }
            if let Some(state) = &self.metric_references {
                let _ = writeln!(
                    out,
                    "CSS_METRIC_PENDING references action={:p} property={:?} value={:p} depth={} floor={} complete={} flags_current={} cursor={:?} queued={} waiting={:?} reply_target={:?}",
                    state.action.identity.as_ref() as *const _,
                    state.longhand,
                    state.value.as_ref() as *const _,
                    state.depth,
                    state.semantic_floor,
                    state.complete,
                    state.flags == self.computed_context.included_cascade_flags,
                    state.walk.current.as_ref().map(|(_, cursor)| *cursor),
                    state.walk.queued.len(),
                    state.walk.waiting,
                    state.reply.as_ref().map(|(target, _)| target)
                );
            }
            let _ = writeln!(
                out,
                "CSS_METRIC_PENDING facet={} size_node={:?} deferred={} finished_root={:?} size_preparation={}",
                self.priority_completion.computed_size.is_some(),
                self.size_node,
                self.deferred_size.is_some(),
                self.finished_root,
                self.size_preparation.is_some()
            );
            if let Some(certificate) = &self.priority_completion.computed_size {
                let _ = writeln!(
                    out,
                    "CSS_METRIC_PENDING facet_same_session={} facet_flags_valid={}",
                    std::ptr::eq(certificate.identity.as_ref(), self.size_identity.as_ref()),
                    certificate.valid_flags(self.computed_context.included_cascade_flags)
                );
            }
            if let Some(frame) = &self.deferred_size {
                let _ = writeln!(
                    out,
                    "CSS_METRIC_PENDING deferred_var={:?} index={} lowlink={} waiting={:?}",
                    frame.var,
                    frame.index,
                    frame.lowlink,
                    frame.waiting.as_ref().map(|(target, _)| target)
                );
            }
            if let Some(states) = &self.size_preparation {
                for state in [&states.size, &states.text_scale] {
                    let _ = writeln!(
                        out,
                        "CSS_METRIC_PENDING size_selection={:?} cursor={:?} complete={} waiting={} retained={} flags_current={}",
                        state.longhand,
                        state.cursor,
                        state.complete,
                        state.waiting.is_some(),
                        state.prepared.len(),
                        state.flags == self.computed_context.included_cascade_flags
                    );
                }
            }
        }

