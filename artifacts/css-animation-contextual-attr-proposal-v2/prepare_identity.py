from pathlib import Path
import difflib
p=Path(__file__).parent
files=['servo/components/style/custom_properties.rs','servo/components/style/properties/cascade.rs']
old={n:(p/'candidate'/n).read_text() for n in files}
s=old[files[0]]
s=s.replace('''#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct AttrUseKey''','''#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct AttrInvocation {
    owner: usize,
    occurrence: usize,
    ancestors: Vec<usize>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct AttrUseKey''',1)
s=s.replace('    pub guard_identity: usize,','    pub guard_identity: usize,\n    invocation: Option<AttrInvocation>,',1)
s=s.replace('            guard_identity,\n        }','            guard_identity,\n            invocation: None,\n        }',1)
needle='    pub fn property_id(&self) -> Option<PropertyIdRef> {'
s=s.replace(needle,'''    fn same_prepared_use(&self, other: &Self) -> bool {
        self.invocation.is_some()
            && self.invocation == other.invocation
            && self.name == other.name && self.namespace == other.namespace
            && self.property == other.property
            && self.suppress_animation_taint_sink == other.suppress_animation_taint_sink
            && self.url_data == other.url_data
    }

'''+needle,1)
s=s.replace('    pub prepared_only: bool,','    pub prepared_owner: Option<usize>,',1).replace('        self.prepared_only = false;','        self.prepared_owner = None;',1)
a=s.index('    pub fn key(');b=s.index('    pub fn suspend(',a)
s=s[:a]+'''    fn invocation_key(
        &self, owner: usize, occurrence: usize, name: &Name, namespace: &Namespace,
        property: Option<PropertyIdRef>, suppress: bool, url_data: &UrlExtraData,
    ) -> AttrUseKey {
        let mut key = AttrUseKey::new(name, namespace, property, suppress, url_data, self.uses.len());
        key.invocation = Some(AttrInvocation { owner, occurrence, ancestors: self.active.clone() });
        key
    }

    pub fn admit(
        &mut self, owner: usize, occurrence: usize, name: &Name, namespace: &Namespace,
        property: Option<PropertyIdRef>, suppress: bool, url_data: &UrlExtraData,
        input: Option<Arc<VariableValue>>,
    ) -> usize {
        let key = self.invocation_key(owner, occurrence, name, namespace, property, suppress, url_data);
        if let Some(index) = self.uses.iter().position(|request| request.key.same_prepared_use(&key)) {
            return index;
        }
        self.request(key, input)
    }

    fn prepared_request(
        &self, owner: usize, occurrence: usize, name: &Name, namespace: &Namespace,
        property: Option<PropertyIdRef>, suppress: bool, url_data: &UrlExtraData,
    ) -> Option<usize> {
        let key = self.invocation_key(owner, occurrence, name, namespace, property, suppress, url_data);
        self.uses.iter().position(|request| request.key.same_prepared_use(&key))
    }

'''+s[b:]
# Named owner ensures final evaluation consumes only this graph node's prepared occurrence.
s=s.replace('    request: usize,\n    stylist: &Stylist,','    request: usize,\n    owner: usize,\n    stylist: &Stylist,',1)
s=s.replace('    let previous = attribute_tracker.attr_resolution.prepared_only;\n    attribute_tracker.attr_resolution.prepared_only = true;','    let previous = attribute_tracker.attr_resolution.prepared_owner;\n    attribute_tracker.attr_resolution.prepared_owner = Some(owner);',1)
s=s.replace('    attribute_tracker.attr_resolution.prepared_only = previous;','    attribute_tracker.attr_resolution.prepared_owner = previous;',1)
a=s.index('    let key = attribute_tracker.attr_resolution.key(',s.index('fn substitute_typed_attribute('))
b=s.index('    attribute_tracker.attr_resolution.uses[request].custom_depth',a)
s=s[:a]+'''    let request = if let Some(owner) = attribute_tracker.attr_resolution.prepared_owner {
        attribute_tracker.attr_resolution.prepared_request(
            owner, reference as *const SubstitutionFunctionReference as usize,
            &reference.name, namespace, property_id, suppress_animation_taint_sink, url_data,
        ).expect("Final attribute occurrence must match dependency preparation")
    } else {
        let key = AttrUseKey::new(
            &reference.name, namespace, property_id, suppress_animation_taint_sink,
            url_data, attribute_tracker.attr_resolution.uses.len(),
        );
        attribute_tracker.attr_resolution.request(key, Some(Arc::clone(&input)))
    };
'''+s[b:]
s=s.replace('!attribute_tracker.attr_resolution.prepared_only','attribute_tracker.attr_resolution.prepared_owner.is_none()')
assert 'prepared_only' not in s
(p/'candidate'/files[0]).write_text(s)
s=old[files[1]]
a=s.index('                let key = attribute_tracker.attr_resolution.key(');b=s.index('                attr_request = Some(request);',a)
s=s[:a]+'''                let request = attribute_tracker.attr_resolution.admit(
                    index, next as *const crate::custom_properties::SubstitutionFunctionReference as usize,
                    &next.name, namespace, property_id, suppress_animation_taint_sink, url_data, input,
                );
'''+s[b:]
s=s.replace('let previous = attribute_tracker.attr_resolution.prepared_only;','let previous = attribute_tracker.attr_resolution.prepared_owner;')
s=s.replace('attribute_tracker.attr_resolution.prepared_only = true;','attribute_tracker.attr_resolution.prepared_owner = Some(index);')
s=s.replace('attribute_tracker.attr_resolution.prepared_only = previous;','attribute_tracker.attr_resolution.prepared_owner = previous;')
s=s.replace('finish_prepared_attribute(request, context.stylist,','finish_prepared_attribute(request, index, context.stylist,',1)
needle='''        traverse(
            var,
            references_from_non_custom_properties,
            &mut context,
            attr_tracker,
        );
    };'''
assert needle in s
s=s.replace(needle,'''        attr_tracker.attr_resolution.reset();
'''+needle.replace('''        );
    };''','''        );
        assert!(context.cascade.resolution.stack.is_empty());
        attr_tracker.attr_resolution.reset();
    };'''),1)
assert 'prepared_only' not in s
(p/'candidate'/files[1]).write_text(s)
(p/'IDENTITY-DELTA.patch').write_text(''.join(''.join(difflib.unified_diff(old[n].splitlines(True),(p/'candidate'/n).read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n)) for n in files))
