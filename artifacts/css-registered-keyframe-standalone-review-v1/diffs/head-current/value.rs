--- head/servo/components/style/properties_and_values/value.rs
+++ current/servo/components/style/properties_and_values/value.rs
@@ -674,7 +674,8 @@
 }
 
 impl CustomAnimatedValue {
-    pub(crate) fn from_computed(
+    /// Construct an animation value with the computed value of this custom property.
+    pub fn from_computed(
         name: &crate::custom_properties::Name,
         value: Option<&ComputedValue>,
     ) -> Self {
