--- base/servo/ports/geckolib/glue.rs
+++ head/servo/ports/geckolib/glue.rs
@@ -663,7 +663,7 @@
                                 segment.mToComposite != CompositeOperation::Replace ||
                                 // ... or if we accumulate onto the last value and it is null.
                                 (iteration_composite == IterationCompositeOperation::Accumulate &&
-                                 computed_timing.mCurrentIteration > 0 &&
+                                 computed_timing.mCurrentIterationForAccumulation > 0 &&
                                  last_segment.mToValue.mServo.mRawPtr.is_null());
 
     // If either of the segment endpoints are null, get the underlying value to
@@ -701,7 +701,7 @@
         underlying_value,
         last_value,
         iteration_composite,
-        computed_timing.mCurrentIteration,
+        computed_timing.mCurrentIterationForAccumulation,
         progress,
         position,
     );
@@ -8338,13 +8338,16 @@
         unsafe { bindings::Gecko_NoteDirtySubtreeForInvalidation(element.0) };
     } else if result.has_invalidated_self() {
         unsafe { bindings::Gecko_NoteDirtyElement(element.0) };
-        let flags = element
-            .parent_element()
-            .map_or(ElementSelectorFlags::empty(), |e| e.slow_selector_flags());
-        // We invalidated up to the anchor, and it has a flag for nth-of invalidation.
-        if !flags.is_empty() {
-            restyle_for_nth_of(element, flags);
+    }
+    let flags = element
+        .parent_element()
+        .map_or(ElementSelectorFlags::empty(), |e| e.slow_selector_flags());
+    // A potential anchor change can affect filtered positions even without an outer match.
+    if !flags.is_empty() {
+        unsafe {
+            element.note_explicit_hints(RestyleHint::restyle_subtree(), nsChangeHint(0));
         }
+        restyle_for_nth_of(element, flags);
     }
 }
 
@@ -11529,30 +11532,27 @@
     // Build the attributes Map that ComputedSubstitutionFunctions needs
     let stylist = &data.stylist;
     let mut attribute_tracker = AttributeTracker::new(&element);
-    let attributes: style::custom_properties_map::OwnMap = variable_value
-        .references
-        .refs
-        .iter()
-        .filter_map(|reference| {
-            if !reference.is_attr_with_type() {
-                return None;
-            }
-
-            let value = custom_properties::get_attr_value_for_cycle_resolution(
-                &reference.name,
-                &reference.attribute_data,
-                &variable_value.url_data,
-                &mut attribute_tracker,
-            )
-            .ok()?;
-
-            Some((reference.name.clone(), Some(value)))
-        })
-        .collect();
-    let substitution_functions = custom_properties::ComputedSubstitutionFunctions::new(
+    let mut substitution_functions = custom_properties::ComputedSubstitutionFunctions::new(
         Some(style.custom_properties().clone()),
-        Some(attributes),
+        None,
     );
+    for reference in &variable_value.references.refs {
+        if !reference.is_attr_with_type() {
+            continue;
+        }
+        let Some(namespace) = reference.attribute_data.namespace() else {
+            continue;
+        };
+        let Ok(value) = custom_properties::get_attr_value_for_cycle_resolution(
+            &reference.name,
+            &reference.attribute_data,
+            &variable_value.url_data,
+            &mut attribute_tracker,
+        ) else {
+            continue;
+        };
+        substitution_functions.insert_attr(&reference.name, namespace, value);
+    }
 
     let Ok(result) = custom_properties::substitute(
         &variable_value,
