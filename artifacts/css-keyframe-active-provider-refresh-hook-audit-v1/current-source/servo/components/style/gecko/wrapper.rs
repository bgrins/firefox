    fn update_animations(
        &self,
        before_change_style: Option<Arc<ComputedValues>>,
        tasks: UpdateAnimationsTasks,
    ) {
        // We have to update animations even if the element has no computed
        // style since it means the element is in a display:none subtree, we
        // should destroy all CSS animations in display:none subtree.
        let computed_data = self.borrow_data();
        let computed_values = computed_data.as_ref().map(|d| d.styles.primary());
        let before_change_values = before_change_style
            .as_ref()
            .map_or(ptr::null(), |x| x.as_gecko_computed_style());
        let computed_values_opt = computed_values
            .as_ref()
            .map_or(ptr::null(), |x| x.as_gecko_computed_style());
        unsafe {
            Gecko_UpdateAnimations(
                self.0,
                before_change_values,
                computed_values_opt,
                tasks.bits(),
            );
        }
    }
