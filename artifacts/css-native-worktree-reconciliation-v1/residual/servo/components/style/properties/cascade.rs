--- HEAD/servo/components/style/properties/cascade.rs
+++ after-recorded-reversals/servo/components/style/properties/cascade.rs
@@ -4,7 +4,7 @@
 
 //! The main cascading algorithm of the style system.
 
-use crate::{FxHashMap, Namespace};
+use crate::FxHashMap;
 use crate::applicable_declarations::{CascadePriority, RevertKind};
 use crate::color::AbsoluteColor;
 use crate::computed_value_flags::ComputedValueFlags;
@@ -21,8 +21,8 @@
 use crate::properties::{
     CASCADE_PROPERTY, CSSWideKeyword, ComputedValues, DeclarationImportanceIterator, LonghandId,
     LonghandIdSet, PrioritaryPropertyId, PrioritaryPropertyIdSet, PropertyDeclaration,
-    PropertyDeclarationId, PropertyFlags, PropertyIdRef, ShorthandsWithPropertyReferencesCache,
-    StyleBuilder, property_counts,
+    PropertyDeclarationBlock, PropertyDeclarationId, PropertyFlags, PropertyIdRef,
+    ShorthandsWithPropertyReferencesCache, StyleBuilder, property_counts,
 };
 use crate::properties::{CustomDeclaration, CustomDeclarationValue, UnparsedValue};
 use crate::properties_and_values::rule::Descriptors as PropertyDescriptors;
@@ -42,6 +42,7 @@
 use crate::values::specified::length::FontBaseSize;
 use crate::values::specified::position::PositionTryFallbacksTryTactic;
 use crate::values::{computed, specified};
+use crate::{FxHashMap, FxHashSet, Namespace};
 use hashbrown::hash_map::{Entry, EntryRef};
 use selectors::matching::ElementSelectorFlags;
 use servo_arc::Arc;
