impl SubstitutionLookup {
    pub(crate) fn read_current(
        &self,
        functions: &ComputedSubstitutionFunctions,
        stylist: &Stylist,
        tracker: &mut AttributeTracker,
    ) -> SubstitutionLookupReply {
        let value = match self.kind {
            SubstitutionLookupKind::RawAttribute => {
                let raw = self.namespace.as_ref().and_then(|namespace| {
                    LocalName::with_name(&self.name, |name| tracker.query(name, namespace))
                });
                SubstitutionLookupValue::Attribute(raw.map(|value| value.to_string()))
            },
            SubstitutionLookupKind::Environment => {
                let device = stylist.device();
                match device.environment().get(&self.name, device, &self.url_data) {
                    Some(value) => SubstitutionLookupValue::Value(value, false),
                    None => SubstitutionLookupValue::Invalid,
                }
            },
            SubstitutionLookupKind::Variable | SubstitutionLookupKind::TypedAttribute => {
                let resolved = if self.kind == SubstitutionLookupKind::Variable {
                    functions.get_var(
                        stylist.get_custom_property_registration(&self.name),
                        &self.name,
                    )
                } else {
                    self.namespace
                        .as_ref()
                        .and_then(|namespace| functions.get_attr(&self.name, namespace))
                };
                match resolved {
                    None => SubstitutionLookupValue::Invalid,
                    Some(value) => {
                        let owned = value.to_variable_value();
                        if self.kind == SubstitutionLookupKind::Variable && owned.has_references() {
                            SubstitutionLookupValue::Expand(owned, value.attr_tainted)
                        } else {
                            SubstitutionLookupValue::Value(owned, value.attr_tainted)
                        }
                    },
                }
            },
        };
        SubstitutionLookupReply {
            identity: self.identity.clone(),
            value,
        }
    }
}
