    fn process_animations(
        &self,
        context: &mut StyleContext<Self>,
        old_styles: &mut ElementStyles,
        new_styles: &mut ResolvedElementStyles,
        important_rules_changed: bool,
    ) {
        use crate::context::UpdateAnimationsTasks;

        let old_values = &old_styles.primary;
        if context.shared.traversal_flags.for_animation_only() && old_values.is_some() {
            return;
        }

        // Bug 868975: These steps should examine and update the visited styles
        // in addition to the unvisited styles.

        let mut tasks = UpdateAnimationsTasks::empty();

        if old_values.as_deref().map_or_else(
            || {
                new_styles
                    .primary_style()
                    .get_ui()
                    .specifies_timeline_scope()
            },
            |old| {
                !old.get_ui()
                    .timeline_scope_equals(new_styles.primary_style().get_ui())
            },
        ) {
            tasks.insert(UpdateAnimationsTasks::TIMELINE_SCOPES);
        }

        if old_values.as_deref().map_or_else(
            || {
                new_styles
                    .primary_style()
                    .get_ui()
                    .specifies_scroll_timelines()
            },
            |old| {
                !old.get_ui()
                    .scroll_timelines_equals(new_styles.primary_style().get_ui())
            },
        ) {
            tasks.insert(UpdateAnimationsTasks::SCROLL_TIMELINES);
        }

        if old_values.as_deref().map_or_else(
            || {
                new_styles
                    .primary_style()
                    .get_ui()
                    .specifies_view_timelines()
            },
            |old| {
                !old.get_ui()
                    .view_timelines_equals(new_styles.primary_style().get_ui())
            },
        ) {
            tasks.insert(UpdateAnimationsTasks::VIEW_TIMELINES);
        }

        if self.needs_animations_update(
            context,
            old_values.as_deref(),
            new_styles.primary_style(),
            /* pseudo_element = */ None,
        ) {
            tasks.insert(UpdateAnimationsTasks::CSS_ANIMATIONS);
            tasks.insert(UpdateAnimationsTasks::EFFECT_PROPERTIES);
        }

        let before_change_style =
            self.process_transitions(context, old_values.as_ref(), new_styles);
        if before_change_style.is_some() {
            tasks.insert(UpdateAnimationsTasks::CSS_TRANSITIONS);
        }

        if self.has_animations(context.shared) {
            tasks.insert(UpdateAnimationsTasks::EFFECT_PROPERTIES);
            if important_rules_changed {
                tasks.insert(UpdateAnimationsTasks::CASCADE_RESULTS);
            }
            if new_styles
                .primary_style()
                .is_display_property_changed_from_none(old_values.as_deref())
            {
                tasks.insert(UpdateAnimationsTasks::DISPLAY_CHANGED_FROM_NONE);
            }
        }

        if !tasks.is_empty() {
            let task = crate::context::SequentialTask::update_animations(
                *self,
                before_change_style,
                tasks,
            );
            context.thread_local.tasks.push(task);
        }
    }
