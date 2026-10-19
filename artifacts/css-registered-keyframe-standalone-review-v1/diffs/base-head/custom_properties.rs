--- base/servo/components/style/custom_properties.rs
+++ head/servo/components/style/custom_properties.rs
@@ -19,6 +19,7 @@
         SpecifiedValue as SpecifiedRegisteredValue,
     },
 };
+use crate::selector_map::PrecomputedHashMap;
 use crate::stylesheets::UrlExtraData;
 use crate::stylesheets::container_rule::AttrReferenceSet;
 use crate::stylist::Stylist;
@@ -676,7 +677,7 @@
     /// The applicable custom properties (includes inherited and non-inherited).
     pub custom_properties: ComputedCustomProperties,
     /// The applicable DOM attributes.
-    pub attributes: OwnMap,
+    pub attributes: PrecomputedHashMap<Namespace, OwnMap>,
 }
 
 impl ComputedSubstitutionFunctions {
@@ -685,7 +686,7 @@
     #[inline(always)]
     pub fn new(
         custom_properties: Option<ComputedCustomProperties>,
-        attributes: Option<OwnMap>,
+        attributes: Option<PrecomputedHashMap<Namespace, OwnMap>>,
     ) -> Self {
         Self {
             custom_properties: custom_properties.unwrap_or_default(),
@@ -703,9 +704,18 @@
         self.custom_properties.insert(registration, name, value);
     }
 
+    /// Store a computed attribute value by its expanded name.
     #[inline(always)]
-    pub(crate) fn insert_attr(&mut self, name: &Name, value: ComputedRegisteredValue) {
-        self.attributes.insert(name.clone(), Some(value));
+    pub fn insert_attr(
+        &mut self,
+        name: &Name,
+        namespace: &Namespace,
+        value: ComputedRegisteredValue,
+    ) {
+        self.attributes
+            .entry(namespace.clone())
+            .or_default()
+            .insert(name.clone(), Some(value));
     }
 
     #[inline(always)]
@@ -714,8 +724,11 @@
     }
 
     #[inline(always)]
-    pub(crate) fn remove_attr(&mut self, name: &Name) {
-        self.attributes.insert(name.clone(), None);
+    pub(crate) fn remove_attr(&mut self, name: &Name, namespace: &Namespace) {
+        self.attributes
+            .entry(namespace.clone())
+            .or_default()
+            .insert(name.clone(), None);
     }
 
     #[inline(always)]
@@ -728,8 +741,22 @@
     }
 
     #[inline(always)]
-    pub(crate) fn get_attr(&self, name: &Name) -> Option<&ComputedRegisteredValue> {
-        self.attributes.get(name).and_then(|p| p.as_ref())
+    pub(crate) fn contains_attr(&self, name: &Name, namespace: &Namespace) -> bool {
+        self.attributes
+            .get(namespace)
+            .is_some_and(|attributes| attributes.contains_key(name))
+    }
+
+    #[inline(always)]
+    pub(crate) fn get_attr(
+        &self,
+        name: &Name,
+        namespace: &Namespace,
+    ) -> Option<&ComputedRegisteredValue> {
+        self.attributes
+            .get(namespace)?
+            .get(name)
+            .and_then(|p| p.as_ref())
     }
 }
 
@@ -747,6 +774,37 @@
 pub struct AttributeData {
     kind: AttributeType,
     namespace: ParsedNamespace,
+}
+
+impl AttributeData {
+    pub(crate) fn parse_typed_value(
+        &self,
+        input: &mut Parser,
+        url_data: &UrlExtraData,
+        property_id: Option<PropertyIdRef>,
+    ) -> Result<SpecifiedRegisteredValue, ()> {
+        let AttributeType::Type(syntax) = &self.kind else {
+            return Err(());
+        };
+        SpecifiedRegisteredValue::parse(
+            input,
+            syntax,
+            url_data,
+            None,
+            AllowComputationallyDependent::Yes,
+            AttrTaint::default(),
+            property_id,
+        )
+        .map_err(|_| ())
+    }
+
+    /// The resolved namespace, including the null namespace.
+    pub fn namespace(&self) -> Option<&Namespace> {
+        match &self.namespace {
+            ParsedNamespace::Known(namespace) => Some(namespace),
+            ParsedNamespace::Unknown => None,
+        }
+    }
 }
 
 /// For a CSS string, the range, counted in bytes, that is attr()-tainted.
@@ -868,6 +926,26 @@
     }
 }
 
+fn resolved_token_dependencies(mut css: &str) -> Option<ReferenceFlags> {
+    let mut flags = ReferenceFlags::empty();
+    while !css.is_empty() {
+        // Restart at each token to visit block contents without recursion.
+        let mut input = Parser::new(css);
+        match input.next_including_whitespace_and_comments().ok()? {
+            Token::Dimension { unit, .. } => flags.insert(ReferenceFlags::from_unit(unit)),
+            Token::Function(name) if SubstitutionFunctionKind::from_ident(name).is_ok() => {
+                return None;
+            },
+            Token::BadUrl(_) | Token::BadString(_) => return None,
+            _ => {},
+        }
+        let consumed = input.position().byte_index();
+        debug_assert!(consumed > 0);
+        css = &css[consumed..];
+    }
+    Some(flags)
+}
+
 impl VariableValue {
     fn empty(url_data: &UrlExtraData) -> Self {
         Self {
@@ -898,6 +976,20 @@
         }
     }
 
+    fn new_resolved(
+        css: String,
+        url_data: &UrlExtraData,
+        first_token_type: TokenSerializationType,
+        last_token_type: TokenSerializationType,
+    ) -> Self {
+        let mut value = Self::new(css, url_data, first_token_type, last_token_type);
+        // Unresolved env payloads keep the previous empty summary.
+        if let Some(flags) = resolved_token_dependencies(&value.css) {
+            value.references.flags = flags;
+        }
+        value
+    }
+
     fn push(
         &mut self,
         css: &str,
@@ -953,6 +1045,7 @@
     ) -> Result<Self, ParseError> {
         let mut references = References::default();
         let mut missing_closing_characters = String::new();
+        let mut removed_backslash = false;
         let start_position = input.position();
         let (first_token_type, last_token_type) = parse_declaration_value(
             input,
@@ -960,6 +1053,7 @@
             namespaces,
             &mut references,
             &mut missing_closing_characters,
+            &mut removed_backslash,
         )?;
         let mut css = input
             .slice_from(start_position)
@@ -967,9 +1061,7 @@
             .to_owned();
         if !missing_closing_characters.is_empty() {
             // Unescaped backslash at EOF in a quoted string is ignored.
-            if css.ends_with("\\")
-                && matches!(missing_closing_characters.as_bytes()[0], b'"' | b'\'')
-            {
+            if removed_backslash {
                 css.pop();
             }
             css.push_str(&missing_closing_characters);
@@ -1105,6 +1197,7 @@
     namespaces: Option<&FxHashMap<Prefix, Namespace>>,
     references: &mut References,
     missing_closing_characters: &mut String,
+    removed_backslash: &mut bool,
 ) -> Result<(TokenSerializationType, TokenSerializationType), ParseError> {
     input.parse_until_before(Delimiter::Bang | Delimiter::Semicolon, |input| {
         parse_declaration_value_block(
@@ -1113,6 +1206,7 @@
             namespaces,
             references,
             missing_closing_characters,
+            removed_backslash,
         )
     })
 }
@@ -1124,6 +1218,7 @@
     namespaces: Option<&FxHashMap<Prefix, Namespace>>,
     references: &mut References,
     missing_closing_characters: &mut String,
+    removed_backslash: &mut bool,
 ) -> Result<(TokenSerializationType, TokenSerializationType), ParseError> {
     let mut is_first = true;
     let mut first_token_type = TokenSerializationType::Nothing;
@@ -1153,6 +1248,7 @@
                         namespaces,
                         references,
                         missing_closing_characters,
+                        removed_backslash,
                     )?;
                     inner_end_position = Some(input.position());
                     Ok(result)
@@ -1279,6 +1375,7 @@
                                 namespaces,
                                 &mut references,
                                 missing_closing_characters,
+                                removed_backslash,
                             )?;
                             fallback = Some(VariableFallback {
                                 start: fallback_start,
@@ -1298,6 +1395,7 @@
                                 namespaces,
                                 references,
                                 missing_closing_characters,
+                                removed_backslash,
                             )?;
                             input_end_position = Some(input.position());
                             input.reset(&state);
@@ -1310,7 +1408,8 @@
                     prev_reference_index = Some(our_ref_index);
                     let reference = &mut references.refs[our_ref_index];
                     reference.end = input.position().byte_index() - input_start.byte_index()
-                        + missing_closing_characters.len();
+                        + missing_closing_characters.len()
+                        - usize::from(*removed_backslash);
                     reference.fallback = fallback;
                     references.flags |= match substitution_kind {
                         SubstitutionFunctionKind::Var => ReferenceFlags::VAR,
@@ -1338,7 +1437,24 @@
                 let token_slice = input.slice_from(token_start);
                 let quote = &token_slice[..1];
                 debug_assert!(matches!(quote, "\"" | "'"));
-                if !(token_slice.ends_with(quote) && token_slice.len() > 1) {
+                if !(token_slice.ends_with(quote)
+                    && token_slice.len() > 1
+                    && token_slice[..token_slice.len() - 1]
+                        .bytes()
+                        .rev()
+                        .take_while(|&byte| byte == b'\\')
+                        .count()
+                        % 2
+                        == 0)
+                {
+                    *removed_backslash = missing_closing_characters.is_empty()
+                        && token_slice
+                            .bytes()
+                            .rev()
+                            .take_while(|&byte| byte == b'\\')
+                            .count()
+                            % 2
+                            == 1;
                     missing_closing_characters.push_str(quote)
                 }
             },
@@ -1350,7 +1466,9 @@
             | Token::Dimension {
                 unit: ref value, ..
             } => {
-                references.flags.insert(ReferenceFlags::from_unit(value));
+                if matches!(token, Token::Dimension { .. }) {
+                    references.flags.insert(ReferenceFlags::from_unit(value));
+                }
                 let is_unquoted_url = matches!(token, Token::UnquotedUrl(_));
                 if value.ends_with("�") && input.slice_from(token_start).ends_with("\\") {
                     // Unescaped backslash at EOF in these contexts is interpreted as U+FFFD
@@ -1460,14 +1578,13 @@
 /// Replace `var()`, `env()`, and `attr()` functions in a pre-existing variable value.
 pub fn substitute_references_if_needed_and_apply(
     name: &Name,
-    kind: SubstitutionFunctionKind,
+    namespace: Option<&Namespace>,
     value: &Arc<VariableValue>,
     stylist: &Stylist,
     context: &mut computed::Context,
     attribute_tracker: &mut AttributeTracker,
 ) {
-    debug_assert_ne!(kind, SubstitutionFunctionKind::Env);
-    let is_var = matches!(kind, SubstitutionFunctionKind::Var);
+    let is_var = namespace.is_none();
     let registration = stylist.get_custom_property_registration(name);
     if is_var && !value.has_references() && registration.is_universal() {
         // Trivial path: no references and no need to compute the value, just apply it directly.
@@ -1494,8 +1611,11 @@
     let Ok(substitution) = substitution else {
         if is_var {
             handle_invalid_at_computed_value_time(name, registration, context);
-        } else {
-            context.builder.substitution_functions.remove_attr(name);
+        } else if let Some(namespace) = namespace {
+            context
+                .builder
+                .substitution_functions
+                .remove_attr(name, namespace);
         }
         return;
     };
@@ -1556,8 +1676,8 @@
         }
     }
 
-    match kind {
-        SubstitutionFunctionKind::Var => {
+    match namespace {
+        None => {
             let value = match substitution.into_value(
                 url_data,
                 registration,
@@ -1575,20 +1695,20 @@
                 .substitution_functions
                 .insert_var(registration, name, value);
         },
-        SubstitutionFunctionKind::Attr => {
-            let mut value = ComputedRegisteredValue::universal(Arc::new(VariableValue::new(
-                substitution.css.into_owned(),
-                url_data,
-                substitution.first_token_type,
-                substitution.last_token_type,
-            )));
+        Some(namespace) => {
+            let mut value =
+                ComputedRegisteredValue::universal(Arc::new(VariableValue::new_resolved(
+                    substitution.css.into_owned(),
+                    url_data,
+                    substitution.first_token_type,
+                    substitution.last_token_type,
+                )));
             value.attr_tainted |= substitution.attr_tainted;
             context
                 .builder
                 .substitution_functions
-                .insert_attr(name, value);
+                .insert_attr(name, namespace, value);
         },
-        SubstitutionFunctionKind::Env => unreachable!("Kind cannot be env."),
     }
 }
 
@@ -1618,12 +1738,13 @@
         property_id: Option<PropertyIdRef>,
     ) -> Result<ComputedRegisteredValue, ()> {
         if registration.is_universal() {
-            let mut value = ComputedRegisteredValue::universal(Arc::new(VariableValue::new(
-                self.css.into_owned(),
-                url_data,
-                self.first_token_type,
-                self.last_token_type,
-            )));
+            let mut value =
+                ComputedRegisteredValue::universal(Arc::new(VariableValue::new_resolved(
+                    self.css.into_owned(),
+                    url_data,
+                    self.first_token_type,
+                    self.last_token_type,
+                )));
             value.attr_tainted |= self.attr_tainted;
             return Ok(value);
         }
@@ -1912,7 +2033,7 @@
                                 attr
                             } else {
                                 substitution_functions
-                                    .get_attr(&reference.name)
+                                    .get_attr(&reference.name, namespace?)
                                     .map(|v| v.to_variable_value())?
                                     .css
                             }
@@ -1924,8 +2045,11 @@
                             AttributeType::Unit(unit) => {
                                 let css = {
                                     // Verify that attribute data is a <number-token>.
+                                    parser.skip_whitespace();
+                                    let start = parser.position();
                                     parser.expect_number().ok()?;
-                                    let mut s = attr.clone();
+                                    let mut s = String::from(parser.slice_from(start));
+                                    parser.expect_exhausted().ok()?;
                                     s.push_str(unit.as_ref());
                                     s
                                 };
@@ -1940,17 +2064,11 @@
                                     value, /* attr_tainted */ true,
                                 ))
                             },
-                            AttributeType::Type(syntax) => {
-                                let value = SpecifiedRegisteredValue::parse(
-                                    &mut parser,
-                                    syntax,
-                                    url_data,
-                                    None,
-                                    AllowComputationallyDependent::Yes,
-                                    AttrTaint::default(),
-                                    property_id,
-                                )
-                                .ok()?;
+                            AttributeType::Type(_) => {
+                                let value = reference
+                                    .attribute_data
+                                    .parse_typed_value(&mut parser, url_data, property_id)
+                                    .ok()?;
                                 let value = value.to_variable_value();
                                 Some(Substitution::from_value(
                                     value, /* attr_tainted */ true,
