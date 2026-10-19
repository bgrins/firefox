--- base/servo/components/style/properties/declaration_block.rs
+++ head/servo/components/style/properties/declaration_block.rs
@@ -717,6 +717,57 @@
         true
     }
 
+    fn declaration_update(
+        &self,
+        declaration: &PropertyDeclaration,
+        importance: Importance,
+    ) -> DeclarationUpdate {
+        if !self.contains(declaration.id()) {
+            return DeclarationUpdate::Append;
+        }
+        let longhand_id = declaration.id().as_longhand();
+        if let Some(longhand_id) = longhand_id
+            && let Some(logical_group) = longhand_id.logical_group()
+        {
+            let mut needs_append = false;
+            for (pos, decl) in self.declarations.iter().enumerate().rev() {
+                let id = match decl.id().as_longhand() {
+                    Some(id) => id,
+                    None => continue,
+                };
+                if id == longhand_id {
+                    if needs_append {
+                        return DeclarationUpdate::AppendAndRemove { pos };
+                    }
+                    let important = self.declarations_importance[pos];
+                    if decl == declaration && important == importance.important() {
+                        return DeclarationUpdate::None;
+                    }
+                    return DeclarationUpdate::UpdateInPlace { pos };
+                }
+                if !needs_append
+                    && id.logical_group() == Some(logical_group)
+                    && id.is_logical() != longhand_id.is_logical()
+                {
+                    needs_append = true;
+                }
+            }
+            unreachable!("Longhand should be found in loop above");
+        }
+        self.declarations
+            .iter()
+            .enumerate()
+            .find(|&(_, decl)| decl.id() == declaration.id())
+            .map_or(DeclarationUpdate::Append, |(pos, decl)| {
+                let important = self.declarations_importance[pos];
+                if decl == declaration && important == importance.important() {
+                    DeclarationUpdate::None
+                } else {
+                    DeclarationUpdate::UpdateInPlace { pos }
+                }
+            })
+    }
+
     /// Prepares updating this declaration block with the given
     /// `SourcePropertyDeclaration` and importance, and returns whether
     /// there is something to update.
@@ -733,18 +784,7 @@
             return source_declarations
                 .all_shorthand
                 .declarations()
-                .any(|decl| {
-                    !self.contains(decl.id())
-                        || self
-                            .declarations
-                            .iter()
-                            .enumerate()
-                            .find(|&(_, d)| d.id() == decl.id())
-                            .is_none_or(|(i, d)| {
-                                let important = self.declarations_importance[i];
-                                *d != decl || important != importance.important()
-                            })
-                });
+                .any(|decl| self.declaration_update(&decl, importance) != DeclarationUpdate::None);
         }
         // Fill `updates` with update information.
         let mut any_update = false;
@@ -755,52 +795,7 @@
             source_declarations
                 .declarations
                 .iter()
-                .map(|declaration| {
-                    if !self.contains(declaration.id()) {
-                        return DeclarationUpdate::Append;
-                    }
-                    let longhand_id = declaration.id().as_longhand();
-                    if let Some(longhand_id) = longhand_id
-                        && let Some(logical_group) = longhand_id.logical_group()
-                    {
-                        let mut needs_append = false;
-                        for (pos, decl) in self.declarations.iter().enumerate().rev() {
-                            let id = match decl.id().as_longhand() {
-                                Some(id) => id,
-                                None => continue,
-                            };
-                            if id == longhand_id {
-                                if needs_append {
-                                    return DeclarationUpdate::AppendAndRemove { pos };
-                                }
-                                let important = self.declarations_importance[pos];
-                                if decl == declaration && important == importance.important() {
-                                    return DeclarationUpdate::None;
-                                }
-                                return DeclarationUpdate::UpdateInPlace { pos };
-                            }
-                            if !needs_append
-                                && id.logical_group() == Some(logical_group)
-                                && id.is_logical() != longhand_id.is_logical()
-                            {
-                                needs_append = true;
-                            }
-                        }
-                        unreachable!("Longhand should be found in loop above");
-                    }
-                    self.declarations
-                        .iter()
-                        .enumerate()
-                        .find(|&(_, decl)| decl.id() == declaration.id())
-                        .map_or(DeclarationUpdate::Append, |(pos, decl)| {
-                            let important = self.declarations_importance[pos];
-                            if decl == declaration && important == importance.important() {
-                                DeclarationUpdate::None
-                            } else {
-                                DeclarationUpdate::UpdateInPlace { pos }
-                            }
-                        })
-                })
+                .map(|declaration| self.declaration_update(declaration, importance))
                 .inspect(|update| {
                     if matches!(update, DeclarationUpdate::None) {
                         return;
@@ -831,20 +826,22 @@
         if !matches!(drain.all_shorthand, AllShorthand::NotSet) {
             debug_assert!(updates.updates.is_empty());
             for decl in drain.all_shorthand.declarations() {
-                let id = decl.id();
-                if self.property_ids.insert(id) {
-                    self.declarations.push(decl);
-                    self.declarations_importance.push(important);
-                } else {
-                    let (idx, slot) = self
-                        .declarations
-                        .iter_mut()
-                        .enumerate()
-                        .find(|(_, d)| d.id() == decl.id())
-                        .unwrap();
-                    *slot = decl;
-                    self.declarations_importance.set(idx, important);
+                match self.declaration_update(&decl, importance) {
+                    DeclarationUpdate::None => continue,
+                    DeclarationUpdate::UpdateInPlace { pos } => {
+                        self.declarations[pos] = decl;
+                        self.declarations_importance.set(pos, important);
+                        continue;
+                    },
+                    DeclarationUpdate::AppendAndRemove { pos } => {
+                        self.declarations.remove(pos);
+                        self.declarations_importance.remove(pos);
+                    },
+                    DeclarationUpdate::Append => {},
                 }
+                self.property_ids.insert(decl.id());
+                self.declarations.push(decl);
+                self.declarations_importance.push(important);
             }
             return;
         }
@@ -1033,9 +1030,7 @@
             // |computed_values| is supplied, we use it to expand such variable
             // declarations. This will be fixed properly in Gecko bug 1391537.
             (PropertyDeclaration::WithVariables(declaration), Some(_)) => declaration
-                .value
                 .substitute_variables(
-                    declaration.id,
                     &context.builder.substitution_functions,
                     stylist,
                     &context,
