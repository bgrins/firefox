impl Context {
    fn receipt_lookup(&mut self, root: &Arc<()>, name: &Name) -> Result<CustomBinding, ReceiptError> {
        let registration = self.stylist.get_custom_property_registration(name);
        self.receipt.lookup_no_node(root, self.computed_context.included_cascade_flags, name, registration)
    }

    fn receipt_bind_node(&mut self, index: usize) -> Result<(), ReceiptError> {
        let info = self.var_info.get(index).ok_or(ReceiptError::WrongNode)?;
        self.receipt.bind_custom_node(index, info)
    }

    fn receipt_publish(&mut self, root: &Arc<()>, index: usize) -> Result<(), ReceiptError> {
        self.receipt.after_indexed_publication(root, self.computed_context.included_cascade_flags, index,
            &self.var_info, &self.computed_context.builder.substitution_functions, &self.stylist)
    }

    fn receipt_reset(&mut self, root: &Arc<()>) -> Result<(), ReceiptError> {
        self.receipt.guard(root, self.computed_context.included_cascade_flags)?;
        self.reset();
        self.receipt.after_retirement(root, self.computed_context.included_cascade_flags)
    }

    fn receipt_dependency_free_applied(&mut self, root: &Arc<()>, name: &Name) -> Result<(), ReceiptError> {
        self.receipt.after_dependency_free_apply(root, self.computed_context.included_cascade_flags, name,
            &self.computed_context.builder.substitution_functions, &self.stylist)
    }
}
