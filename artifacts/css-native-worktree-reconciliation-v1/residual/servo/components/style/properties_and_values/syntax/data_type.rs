--- HEAD/servo/components/style/properties_and_values/syntax/data_type.rs
+++ after-recorded-reversals/servo/components/style/properties_and_values/syntax/data_type.rs
@@ -9,12 +9,12 @@
 use std::fmt::{self, Debug, Write};
 use style_traits::{CssWriter, ToCss};
 
-/// Some types (lengths and colors) depend on other properties to resolve correctly.
+/// Types whose values can depend on other properties to resolve correctly.
 #[derive(Clone, Copy, Debug, Default, PartialEq, Eq, MallocSizeOf, ToShmem)]
 pub struct DependentDataTypes(u8);
 bitflags! {
     impl DependentDataTypes: u8 {
-        /// <length> values depend on font-size/line-height/zoom...
+        /// Length operands, including those in numeric math, depend on font metrics.
         const LENGTH = 1 << 0;
         /// <color> values depend on color-scheme, etc..
         const COLOR= 1 << 1;
@@ -101,19 +101,18 @@
         match self {
             DataType::Length
             | DataType::LengthPercentage
+            | DataType::Number
+            | DataType::Integer
+            | DataType::Percentage
+            | DataType::Angle
+            | DataType::Time
+            | DataType::Resolution
             | DataType::TransformFunction
             | DataType::TransformList => DependentDataTypes::LENGTH,
             DataType::Color => DependentDataTypes::COLOR,
-            DataType::Number
-            | DataType::Percentage
-            | DataType::Image
-            | DataType::Url
-            | DataType::Integer
-            | DataType::Angle
-            | DataType::Time
-            | DataType::Resolution
-            | DataType::CustomIdent
-            | DataType::String => DependentDataTypes::empty(),
+            DataType::Image | DataType::Url | DataType::CustomIdent | DataType::String => {
+                DependentDataTypes::empty()
+            },
         }
     }
 }
