pub struct AttributeTracker<'a> {
    /// The element that queries for attributes.
    pub context: &'a dyn ElementContext,
    /// The set of attributes we have queried.
    pub references: AttributeReferences,
}

impl<'a> AttributeTracker<'a> {
    /// Construct a new attribute tracker trivially.
    pub fn new(context: &'a dyn ElementContext) -> Self {
        Self {
            context,
            references: None,
        }
    }

    /// Construct a new dummy attribute tracker
    pub fn new_dummy() -> Self {
        Self {
            context: &DummyElementContext {},
            references: None,
        }
    }

    /// Extract the queried references and consume self
    pub fn finalize(self) -> AttributeReferences {
        self.references
    }

    /// Query the value and save the name of the attribtue.
    pub fn query(&mut self, name: &LocalName, namespace: &Namespace) -> Option<String> {
        // We need to save namespaces in case we are thinking of sharing this element's
        // style with another.
        // i.e if elment a has ns1::attr="blue"
        // and element b has ns2::attr="blue"
        // a and b can only share style if ns1 and ns2 resolve to the same namespace.
        self.references
            .get_or_insert_default()
            .entry_ref(name)
            .or_default()
            .push(namespace.clone());
        self.context.get_attr(name, namespace)
    }
}

