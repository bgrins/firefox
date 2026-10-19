--- base/servo/components/style/properties/cascade.rs
+++ head/servo/components/style/properties/cascade.rs
@@ -4,7 +4,7 @@
 
 //! The main cascading algorithm of the style system.
 
-use crate::FxHashMap;
+use crate::{FxHashMap, Namespace};
 use crate::applicable_declarations::{CascadePriority, RevertKind};
 use crate::color::AbsoluteColor;
 use crate::computed_value_flags::ComputedValueFlags;
@@ -21,8 +21,8 @@
 use crate::properties::{
     CASCADE_PROPERTY, CSSWideKeyword, ComputedValues, DeclarationImportanceIterator, LonghandId,
     LonghandIdSet, PrioritaryPropertyId, PrioritaryPropertyIdSet, PropertyDeclaration,
-    PropertyDeclarationId, PropertyFlags, ShorthandsWithPropertyReferencesCache, StyleBuilder,
-    property_counts,
+    PropertyDeclarationId, PropertyFlags, PropertyIdRef, ShorthandsWithPropertyReferencesCache,
+    StyleBuilder, property_counts,
 };
 use crate::properties::{CustomDeclaration, CustomDeclarationValue, UnparsedValue};
 use crate::properties_and_values::rule::Descriptors as PropertyDescriptors;
@@ -707,7 +707,7 @@
     /// The boolean means whether the value may have references. If false, we don't need to bother
     /// performing lookups for cycle detection.
     var: PrecomputedHashMap<&'a Name, bool>,
-    attr: PrecomputedHashSet<&'a Name>,
+    attr: PrecomputedHashMap<&'a Namespace, PrecomputedHashSet<&'a Name>>,
 }
 
 #[derive(Default)]
@@ -798,6 +798,8 @@
     }
 }
 
+type NonCustomPropertyReferences = NonCustomReferenceMap<Vec<(LonghandId, Arc<UnparsedValue>)>>;
+
 pub(crate) struct Cascade<'a> {
     first_line_reparenting: FirstLineReparenting<'a>,
     stylist: &'a Stylist,
@@ -807,7 +809,7 @@
     author_or_user_specified: LonghandIdSet,
     declarations_to_apply_unless_overridden: DeclarationsToApplyUnlessOverriden,
     may_have_custom_property_cycles: bool,
-    references_from_non_custom_properties: NonCustomReferenceMap<Vec<Arc<UnparsedValue>>>,
+    references_from_non_custom_properties: NonCustomPropertyReferences,
     /// Set of prioritary properties that have already been applied.
     ensured_prioritary: PrioritaryPropertyIdSet,
 }
@@ -883,8 +885,7 @@
             context.builder.stylist.is_some(),
             "Need a Stylist to substitute variables!"
         );
-        declaration.value.substitute_variables(
-            declaration.id,
+        declaration.substitute_variables(
             context.builder.substitution_functions(),
             context.builder.stylist.unwrap(),
             context,
@@ -1803,7 +1804,7 @@
                     // afterwards.
                     substitute_references_if_needed_and_apply(
                         name,
-                        SubstitutionFunctionKind::Var,
+                        None,
                         unparsed_value,
                         self.stylist,
                         context,
@@ -1915,9 +1916,6 @@
         // values, which we need to track to support chained references and detect cycles.
         if refs.flags.intersects(ReferenceFlags::ATTR) {
             self.update_attributes_map(context, value, attribute_tracker);
-            if !refs.flags.intersects(ReferenceFlags::VAR) {
-                return;
-            }
         }
 
         // The non-custom node(s) this property feeds. We don't try to figure out here which
@@ -1940,7 +1938,7 @@
         references.for_each_non_custom(context.is_root_element(), |idx| {
             self.references_from_non_custom_properties[idx]
                 .get_or_insert_with(Vec::new)
-                .push(v.value.clone());
+                .push((v.id, v.value.clone()));
         });
     }
 
@@ -2057,22 +2055,42 @@
         }
         self.may_have_custom_property_cycles = true;
 
-        for next in &refs.refs {
-            if !next.is_attr_with_type() || !self.seen.custom.attr.insert(&next.name) {
-                // Only type() can have nested references, so we don't need to eagerly look at
-                // others.
-                continue;
-            }
-            if let Ok(v) = get_attr_value_for_cycle_resolution(
-                &next.name,
-                &next.attribute_data,
-                &value.url_data,
-                attribute_tracker,
-            ) {
-                context
-                    .builder
-                    .substitution_functions
-                    .insert_attr(&next.name, v);
+        let mut refs_stack = SmallVec::<[&References; 5]>::new();
+        refs_stack.push(refs);
+        while let Some(refs) = refs_stack.pop() {
+            for next in &refs.refs {
+                if let Some(ref fallback) = next.fallback {
+                    refs_stack.push(&fallback.references);
+                }
+                if !next.is_attr_with_type() {
+                    // Only type() can have nested references, so we don't need to eagerly look at
+                    // others.
+                    continue;
+                }
+                let Some(namespace) = next.attribute_data.namespace() else {
+                    continue;
+                };
+                if !self
+                    .seen
+                    .custom
+                    .attr
+                    .entry(namespace)
+                    .or_default()
+                    .insert(&next.name)
+                {
+                    continue;
+                }
+                if let Ok(v) = get_attr_value_for_cycle_resolution(
+                    &next.name,
+                    &next.attribute_data,
+                    &value.url_data,
+                    attribute_tracker,
+                ) {
+                    context
+                        .builder
+                        .substitution_functions
+                        .insert_attr(&next.name, namespace, v);
+                }
             }
         }
     }
@@ -2124,7 +2142,7 @@
 
 fn substitute_all(
     seen: &SeenSubstitutionFunctions,
-    references_from_non_custom_properties: &NonCustomReferenceMap<Vec<Arc<UnparsedValue>>>,
+    references_from_non_custom_properties: &NonCustomPropertyReferences,
     stylist: &Stylist,
     computed_context: &mut computed::Context,
     cascade: &mut Cascade,
@@ -2140,9 +2158,18 @@
 
     #[derive(Clone, Eq, PartialEq, Debug)]
     enum VarType {
-        Attr(Name),
+        Attr(Name, Namespace),
         Custom(Name),
         NonCustom(SingleNonCustomReference),
+    }
+
+    impl VarType {
+        fn namespace(&self) -> Option<&Namespace> {
+            match self {
+                Self::Attr(_, namespace) => Some(namespace),
+                _ => None,
+            }
+        }
     }
 
     /// Struct recording necessary information for each variable.
@@ -2163,7 +2190,7 @@
         /// The map from the custom property name to its order index.
         var: PrecomputedHashMap<Name, usize>,
         /// The map from the attribute name to its order index.
-        attr: PrecomputedHashMap<Name, usize>,
+        attr: PrecomputedHashMap<Namespace, PrecomputedHashMap<Name, usize>>,
     }
 
     impl OrderIndexMap {
@@ -2224,11 +2251,11 @@
         /// Marks a given `name` as being in a loop.
         fn handle_loop(&mut self, name: &VarType) {
             match name {
-                VarType::Attr(name) => {
+                VarType::Attr(name, namespace) => {
                     self.computed_context
                         .builder
                         .substitution_functions
-                        .remove_attr(name);
+                        .remove_attr(name, namespace);
                 },
                 VarType::Custom(name) => {
                     // This variable is in a loop. Resolve to invalid.
@@ -2281,8 +2308,9 @@
         var: &VarType,
         root: &References,
         url_data: &UrlExtraData,
+        property_id: Option<PropertyIdRef>,
         index: usize,
-        references_from_non_custom_properties: &NonCustomReferenceMap<Vec<Arc<UnparsedValue>>>,
+        references_from_non_custom_properties: &NonCustomPropertyReferences,
         context: &mut Context<'a, 'b, 'c, 'd>,
         lowlink: &mut usize,
         self_ref: &mut bool,
@@ -2317,7 +2345,13 @@
                     if !can_chain {
                         continue;
                     }
-                    if context.map().get_attr(&next.name).is_none()
+                    let Some(namespace) = next.attribute_data.namespace() else {
+                        if let Some(ref fallback) = next.fallback {
+                            refs_stack.push(&fallback.references);
+                        }
+                        continue;
+                    };
+                    if !context.map().contains_attr(&next.name, namespace)
                         && let Ok(val) = get_attr_value_for_cycle_resolution(
                             &next.name,
                             &next.attribute_data,
@@ -2325,9 +2359,9 @@
                             attribute_tracker,
                         )
                     {
-                        context.map_mut().insert_attr(&next.name, val);
+                        context.map_mut().insert_attr(&next.name, namespace, val);
                     }
-                    VarType::Attr(next.name.clone())
+                    VarType::Attr(next.name.clone(), namespace.clone())
                 } else {
                     VarType::Custom(next.name.clone())
                 };
@@ -2351,7 +2385,10 @@
                             context.stylist.get_custom_property_registration(&next.name);
                         context.map().get_var(registration, &next.name)
                     },
-                    SubstitutionFunctionKind::Attr => context.map().get_attr(&next.name),
+                    SubstitutionFunctionKind::Attr => next
+                        .attribute_data
+                        .namespace()
+                        .and_then(|namespace| context.map().get_attr(&next.name, namespace)),
                     SubstitutionFunctionKind::Env => unreachable!("Handled above"),
                 };
                 // The primary is guaranteed-invalid if it's absent from the map, or still
@@ -2365,6 +2402,17 @@
                         // Resolved and computed value, no other custom references left.
                         primary_valid = true;
                     }
+                    if primary_valid && next.is_attr_with_type() {
+                        let value = resolved.to_variable_value();
+                        primary_valid = next
+                            .attribute_data
+                            .parse_typed_value(
+                                &mut cssparser::Parser::new(&value.css),
+                                url_data,
+                                property_id,
+                            )
+                            .is_ok();
+                    }
                 }
 
                 if !primary_valid && let Some(ref fallback) = next.fallback {
@@ -2379,7 +2427,7 @@
     fn visit_link<'a, 'b, 'c, 'd>(
         var: VarType,
         index: usize,
-        non_custom_references: &NonCustomReferenceMap<Vec<Arc<UnparsedValue>>>,
+        non_custom_references: &NonCustomPropertyReferences,
         context: &mut Context<'a, 'b, 'c, 'd>,
         lowlink: &mut usize,
         self_ref: &mut bool,
@@ -2426,7 +2474,7 @@
     /// * There is no such variable at all.
     fn traverse<'a, 'b, 'c, 'd>(
         var: VarType,
-        references_from_non_custom_properties: &NonCustomReferenceMap<Vec<Arc<UnparsedValue>>>,
+        references_from_non_custom_properties: &NonCustomPropertyReferences,
         context: &mut Context<'a, 'b, 'c, 'd>,
         attribute_tracker: &mut AttributeTracker,
     ) -> Option<usize> {
@@ -2436,7 +2484,7 @@
         let mut value_non_custom_refs = ReferenceFlags::empty();
         let mut registered = false;
         let value = match var {
-            VarType::Custom(ref name) | VarType::Attr(ref name) => {
+            VarType::Custom(ref name) | VarType::Attr(ref name, _) => {
                 let map = &context.computed_context.builder.substitution_functions;
                 let (registration, value, kind) = if matches!(var, VarType::Custom(..)) {
                     let registration = context.stylist.get_custom_property_registration(name);
@@ -2449,7 +2497,8 @@
                     // `attr()` is always treated as unregistered.
                     (
                         PropertyDescriptors::unregistered(),
-                        map.get_attr(name)?.as_universal()?,
+                        map.get_attr(name, var.namespace().unwrap())?
+                            .as_universal()?,
                         SubstitutionFunctionKind::Attr,
                     )
                 };
@@ -2475,7 +2524,7 @@
                         let value = value.clone();
                         substitute_references_if_needed_and_apply(
                             name,
-                            kind,
+                            var.namespace(),
                             &value,
                             context.stylist,
                             context.computed_context,
@@ -2489,7 +2538,11 @@
                 let index_map = if kind == SubstitutionFunctionKind::Var {
                     &mut context.index_map.var
                 } else {
-                    &mut context.index_map.attr
+                    context
+                        .index_map
+                        .attr
+                        .entry(var.namespace().unwrap().clone())
+                        .or_default()
                 };
                 match index_map.entry_ref(name) {
                     EntryRef::Occupied(entry) => {
@@ -2527,15 +2580,20 @@
         let mut lowlink = index;
         if let Some(v) = value.as_ref() {
             debug_assert!(
-                matches!(var, VarType::Custom(_) | VarType::Attr(_)),
+                matches!(var, VarType::Custom(_) | VarType::Attr(..)),
                 "Non-custom property has references?"
             );
 
+            let property_id = match &var {
+                VarType::Custom(name) | VarType::Attr(name, _) => Some(PropertyIdRef::from(name)),
+                VarType::NonCustom(_) => unreachable!(),
+            };
             // Visit the references in this value...
             visit_value_references(
                 &var,
                 &v.references,
                 &v.url_data,
+                property_id,
                 index,
                 references_from_non_custom_properties,
                 context,
@@ -2584,18 +2642,20 @@
             }
             let entry = &references_from_non_custom_properties[non_custom];
             if let Some(values) = entry.as_ref() {
-                for value in values {
+                for (longhand_id, value) in values {
                     // Traverse the non-custom property's declaration value(s), creating edges to
                     // the custom properties they reference (directly or through a used fallback)
                     // that might cycle back to this node. Note we traverse unregistered/universal
                     // references too: while their own font-relative units are textual (resolved
                     // against the parent, see `find_non_custom_references`), they may chain to a
                     // registered property that does cycle back.
+                    let property_id = value.substitution_property_id(*longhand_id);
                     let value = &value.variable_value;
                     visit_value_references(
                         &var,
                         &value.references,
                         &value.url_data,
+                        Some(property_id),
                         index,
                         references_from_non_custom_properties,
                         context,
@@ -2651,18 +2711,13 @@
 
         // Not in a loop, apply the value.
         match var {
-            VarType::Custom(ref name) | VarType::Attr(ref name) => {
+            VarType::Custom(ref name) | VarType::Attr(ref name, _) => {
                 if let Some(ref v) = value {
-                    let kind = if matches!(var, VarType::Custom(..)) {
-                        SubstitutionFunctionKind::Var
-                    } else {
-                        SubstitutionFunctionKind::Attr
-                    };
                     // We know we're not in a loop now, perform substitution.
                     // TODO(emilio): Merge with the cycle detection loop instead?
                     substitute_references_if_needed_and_apply(
                         name,
-                        kind,
+                        var.namespace(),
                         v,
                         context.stylist,
                         context.computed_context,
@@ -2714,7 +2769,9 @@
     }
     // Traverse potentially untraversed chained references from `attr(type())` in non-custom
     // properties.
-    for attr in &seen.attr {
-        run_one(VarType::Attr((*attr).clone()));
+    for (namespace, attributes) in &seen.attr {
+        for attr in attributes {
+            run_one(VarType::Attr((*attr).clone(), (*namespace).clone()));
+        }
     }
 }
