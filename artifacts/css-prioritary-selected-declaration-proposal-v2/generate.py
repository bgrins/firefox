from pathlib import Path
import hashlib, subprocess, difflib
HERE=Path(__file__).resolve().parent
REL=Path('servo/components/style/properties/cascade.rs')
predecessor=HERE.parent/'css-prioritary-selected-declaration-proposal-v1/candidate'/REL
assert hashlib.sha256(predecessor.read_bytes()).hexdigest()=='9698c84c9a3b4642d7f67a66d05c860e768cef708b7521f823c24754900c3a58'
s=predecessor.read_text()

def replace(old,new):
    global s
    assert s.count(old)==1,(old[:100],s.count(old))
    s=s.replace(old,new)

s=s.replace('ReferenceFlags, References, SingleNonCustomReference, SubstitutionFunctionKind, VariableValue,','ReferenceFlags, References, SubstitutionFunctionKind, VariableValue,')
replace('''        context: &computed::Context,
        longhand_id: LonghandId,
        priority: CascadePriority,
    ) -> bool {''','''        included_flags: RuleCascadeFlags,
        longhand_id: LonghandId,
        priority: CascadePriority,
    ) -> bool {''')
a=s.index('    fn longhand_is_eligible(');b=s.index('    fn prepare_longhand',a)
s=s[:a]+s[a:b].replace('context.included_cascade_flags','included_flags')+s[b:]
replace('self.longhand_is_eligible(context, longhand_id, priority)','self.longhand_is_eligible(context.included_cascade_flags, longhand_id, priority)')
replace('''self.cascade.longhand_is_eligible(
                    self.computed_context,
                    longhand,
                    priority
                )''','''self.cascade.longhand_is_eligible(
                    self.computed_context.included_cascade_flags,
                    longhand,
                    priority
                )''')
a=s.index('        let mut declaration =\n            self.substitute_variables_if_needed',s.index('    fn prepare_longhand'))
b=s.index('        let mut deferred =',a)
s=s[:a]+'''        let declaration = self.substitute_variables_if_needed(context, cache, declaration, attribute_tracker);
        self.adjust_prepared_longhand(context, longhand_id, declaration, priority)
    }

    fn adjust_prepared_longhand<'decl>(&self, context: &computed::Context,
        longhand_id: LonghandId, mut declaration: Cow<'decl, PropertyDeclaration>,
        priority: CascadePriority) -> PreparedLonghand<'decl> {
'''+s[b:]
replace('''            self.cascade.ensured_prioritary.insert(id);
            let prepared = self.prepared_priorities.remove(&longhand).unwrap();''','''            self.cascade.ensured_prioritary.insert(id);
            for dependency in id.dependencies().iter() {
                self.cascade.ensure_prioritary_property(self.computed_context, self.decls,
                    self.cache, attribute_tracker, dependency);
            }
            let prepared = self.prepared_priorities.remove(&longhand).unwrap();''')
s=s.replace('fn apply_prepared_priority(&mut self, longhand: LonghandId) {','fn apply_prepared_priority(&mut self, longhand: LonghandId, attribute_tracker: &mut AttributeTracker) {')
s=s.replace('context.apply_prepared_priority(non_custom);','context.apply_prepared_priority(non_custom, attribute_tracker);')
a=s.index('            for dependency in id.dependencies().iter() {',s.index('} else if let VarType::NonCustom(longhand) = var {'))
b=s.index('            let mut prepared = Vec::new();',a)
s=s[:a]+'''            if longhand == LonghandId::LineHeight {
                visit_link(VarType::NonCustom(LonghandId::FontSize), index,
                    references_from_non_custom_properties, context, &mut lowlink,
                    &mut self_ref, attribute_tracker);
            }
'''+s[b:]
a=s.index('                let eligible = context.cascade.longhand_is_eligible(',s.index('} else if let VarType::NonCustom(longhand) = var {'))
b=s.index('                if eligible {',a)
s=s[:a]+'''                let rollback_allows = reverted.is_none_or(|(priority, kind)| {
                    priority.allows_when_reverted(&entry.priority, kind)
                });
                let included = context.computed_context.included_cascade_flags;
                if rollback_allows
                    && entry.priority.flags().intersects(RuleCascadeFlags::APPEARANCE_BASE)
                    && !included.intersects(RuleCascadeFlags::APPEARANCE_BASE)
                    && context.cascade.longhand_is_eligible(included | RuleCascadeFlags::APPEARANCE_BASE,
                        longhand, entry.priority)
                {
                    visit_link(VarType::NonCustom(LonghandId::Appearance), index,
                        references_from_non_custom_properties, context, &mut lowlink,
                        &mut self_ref, attribute_tracker);
                }
                if lowlink != index || self_ref || context.stack.last() != Some(&index) {
                    break;
                }
                let eligible = rollback_allows && context.cascade.longhand_is_eligible(
                    context.computed_context.included_cascade_flags, longhand, entry.priority);
'''+s[b:]
needle='fn tweak_when_ignoring_colors('
helper='''fn prioritary_adjustment_dependency(
    ignore_colors: bool,
    longhand: LonghandId,
    declaration: &PropertyDeclaration,
    origin: CascadeOrigin,
) -> Option<LonghandId> {
    if !ignore_colors || !longhand.ignored_when_document_colors_disabled()
        || matches!(origin, CascadeOrigin::UA | CascadeOrigin::User)
        || declaration.get_css_wide_keyword().is_some()
    {
        return None;
    }
    debug_assert_eq!(longhand, LonghandId::ColorScheme);
    Some(LonghandId::ForcedColorAdjust)
}

'''
replace(needle,helper+needle)
a=s.index('                    let declaration = context\n                        .cascade\n                        .prepare_longhand(',s.index('} else if let VarType::NonCustom(longhand) = var {'))
b=s.index('                    let revert =',a)
s=s[:a]+'''                    let declaration = context.cascade.substitute_variables_if_needed(
                        context.computed_context, context.cache, entry.decl, attribute_tracker).into_owned();
                    if let Some(dependency) = prioritary_adjustment_dependency(
                        context.cascade.ignore_colors, longhand, &declaration,
                        entry.priority.cascade_level().origin())
                    {
                        visit_link(VarType::NonCustom(dependency), index,
                            references_from_non_custom_properties, context, &mut lowlink,
                            &mut self_ref, attribute_tracker);
                    }
                    if lowlink != index || self_ref || context.stack.last() != Some(&index) {
                        break;
                    }
                    let declaration = context.cascade.adjust_prepared_longhand(
                        context.computed_context, longhand, Cow::Owned(declaration), entry.priority).into_owned();
'''+s[b:]
out=HERE/'candidate'/REL;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(s)
formatter=Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustfmt')
assert hashlib.sha256(formatter.read_bytes()).hexdigest()=='ab19d01d0a7a3a901c62b6b013a98452d38084b5d7f446ccb20c5e83c10db99f'
subprocess.run([str(formatter),'--edition','2024','--config','match_block_trailing_comma=true,reorder_imports=true',str(out)],check=True)
s=out.read_text();base=(HERE/'base'/REL).read_text()
for name,old in [('native.patch',base),('V1-DELTA.patch',predecessor.read_text())]:
 (HERE/name).write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='a/'+str(REL),tofile='b/'+str(REL))))
print(hashlib.sha256(s.encode()).hexdigest(),len(s))
