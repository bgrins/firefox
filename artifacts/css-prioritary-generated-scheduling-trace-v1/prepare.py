import difflib
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = 'servo/components/style/properties/cascade.rs'
SOURCE = ROOT / 'artifacts/css-prioritary-published-rebase-diagnostic-v1/candidate' / REL
base = SOURCE.read_text()
source = base
insertions = []

def insert(anchor, body, after=False):
    global source
    assert source.count(anchor) == 1, anchor
    marker = '/* CSS_PRIORITY_TRACE_BEGIN */\n' + body + '/* CSS_PRIORITY_TRACE_END */\n'
    replacement = anchor + marker if after else marker + anchor
    source = source.replace(anchor, replacement, 1)
    insertions.append({'anchor': anchor, 'body': body, 'after': after})

insert('fn is_base_appearance(context: &computed::Context) -> bool {', '''macro_rules! priority_trace {
    ($cascade:expr, $longhand:expr, $event:expr, $($args:tt)*) => {
        if matches!($longhand, LonghandId::Appearance | LonghandId::FontSize | LonghandId::FontFamily | LonghandId::XTextScale | LonghandId::ColorScheme)
            && std::env::var_os("MOZ_CSS_PRIORITY_TRACE").as_deref() == Some(std::ffi::OsStr::new("1"))
        {
            use std::io::Write;
            let _ = writeln!(std::io::stderr().lock(), "CSS_PRIORITY_TRACE thread={:?} cascade={:p} property={:?} event={} {}",
                std::thread::current().id(), std::ptr::from_ref($cascade), $longhand, $event, format_args!($($args)*));
        }
    };
}

''')
insert('''        if self.ensured_prioritary.contains(id) {
            return;
        }
        self.ensured_prioritary.insert(id);''', '''        priority_trace!(&*self, id.to_longhand(), "ordinary-ensure-enter",
            "ensured={} seen={} appearance={:?} base_flag={}",
            self.ensured_prioritary.contains(id), self.seen.longhands.contains(id.to_longhand()),
            context.builder.get_box().get_appearance(),
            context.included_cascade_flags.intersects(RuleCascadeFlags::APPEARANCE_BASE));
''')
insert('''                self.ensure_prioritary_property(context, decls, cache, attribute_tracker, dep);''','''                priority_trace!(&*self, id.to_longhand(), "ordinary-ensure-dependency", "dependency={:?}", dep.to_longhand());
''')
insert('''        self.apply_one_prioritary_property(context, decls, cache, id, attribute_tracker);
''','''        priority_trace!(&*self, id.to_longhand(), "ordinary-ensure-return",
            "seen={} appearance={:?} base_flag={}", self.seen.longhands.contains(id.to_longhand()),
            context.builder.get_box().get_appearance(),
            context.included_cascade_flags.intersects(RuleCascadeFlags::APPEARANCE_BASE));
''',True)
insert('        let declaration =\n            self.substitute_variables_if_needed(context, cache, declaration, attribute_tracker);', '        if std::env::var_os("MOZ_CSS_PRIORITY_TRACE").as_deref() == Some(std::ffi::OsStr::new("1")) {\n            if let PropertyDeclaration::WithVariables(value) = declaration {\n                for reference in &value.value.variable_value.references.refs {\n                    if reference.substitution_kind == SubstitutionFunctionKind::Attr {\n                        let cached = reference.attribute_data.namespace().and_then(|ns| context.builder.substitution_functions.get_attr(&reference.name, ns));\n                        priority_trace!(&*self, longhand_id, "ordinary-attr-cache",\n                            "name={:?} present={} unresolved={:?}", reference.name, cached.is_some(),\n                            cached.and_then(|v| v.as_universal()).map(|v| v.has_references()));\n                    }\n                }\n            }\n        }\n')
insert('''        self.seen.longhands.insert(longhand_id);
        if origin != CascadeOrigin::UA {''','''        priority_trace!(&*self, longhand_id, "resolved-apply-before",
            "wide={:?} skip={} already_seen={} appearance={:?} base_flag={}",
            declaration.get_css_wide_keyword(), can_skip_apply, self.seen.longhands.contains(longhand_id),
            context.builder.get_box().get_appearance(),
            context.included_cascade_flags.intersects(RuleCascadeFlags::APPEARANCE_BASE));
''')
insert('    }\n\n    #[inline]\n    unsafe fn do_apply_declaration', '        priority_trace!(&*self, longhand_id, "resolved-apply-return",\n            "skip={} appearance={:?} base_flag={}", can_skip_apply,\n            context.builder.get_box().get_appearance(),\n            context.included_cascade_flags.intersects(RuleCascadeFlags::APPEARANCE_BASE));\n')
insert('''            let id = PrioritaryPropertyId::from_longhand(longhand).unwrap();
            self.cascade.ensured_prioritary.insert(id);''','''            priority_trace!(&*self.cascade, longhand, "prepared-commit-enter",
                "appearance_active={} seen={} appearance={:?}",
                self.non_custom_index_map.get(&LonghandId::Appearance).is_some_and(|i| self.var_info.get(*i).is_some_and(|info| info.var.is_some())),
                self.cascade.seen.longhands.contains(longhand), self.computed_context.builder.get_box().get_appearance());
''')
insert('''                self.cascade.ensure_prioritary_property(
                    self.computed_context,''','''                priority_trace!(&*self.cascade, longhand, "prepared-ensure-dependency",
                    "dependency={:?} appearance_active={}", dependency.to_longhand(),
                    self.non_custom_index_map.get(&LonghandId::Appearance).is_some_and(|i| self.var_info.get(*i).is_some_and(|info| info.var.is_some())));
''')
insert('''                debug_assert!(self.cascade.longhand_is_eligible(
''','''                priority_trace!(&*self.cascade, longhand, "prepared-apply-before",
                    "eligible_now={} wide={:?} appearance={:?}",
                    self.cascade.longhand_is_eligible(self.computed_context.included_cascade_flags, longhand, priority),
                    declaration.declaration.get_css_wide_keyword(), self.computed_context.builder.get_box().get_appearance());
''')
insert('''        } else if let VarType::NonCustom(longhand) = var {
''','''            priority_trace!(&*context.cascade, longhand, "graph-enter",
                "index={} stack_len={} ensured={} seen={} appearance={:?} base_flag={}",
                index, context.stack.len(),
                context.cascade.ensured_prioritary.contains(PrioritaryPropertyId::from_longhand(longhand).unwrap()),
                context.cascade.seen.longhands.contains(longhand), context.computed_context.builder.get_box().get_appearance(),
                context.computed_context.included_cascade_flags.intersects(RuleCascadeFlags::APPEARANCE_BASE));
''',True)
insert('''                if eligible {
                    if let PropertyDeclaration::WithVariables(declaration) = entry.decl {''','''                priority_trace!(&*context.cascade, longhand, "graph-eligibility",
                    "index={} declaration={} eligible={} rollback={} base_flag={}", index, declaration_index, eligible, rollback_allows,
                    context.computed_context.included_cascade_flags.intersects(RuleCascadeFlags::APPEARANCE_BASE));
''')
anchor='''                        visit_value_references(
                            &value.variable_value.references,'''
insert(anchor,'''                        if std::env::var_os("MOZ_CSS_PRIORITY_TRACE").as_deref() == Some(std::ffi::OsStr::new("1")) {
                            for reference in &value.variable_value.references.refs {
                                if reference.substitution_kind == SubstitutionFunctionKind::Attr {
                                    let cached = reference.attribute_data.namespace().and_then(|ns| context.map().get_attr(&reference.name, ns));
                                    priority_trace!(&*context.cascade, longhand, "graph-attr-cache",
                                        "index={} name={:?} present={} unresolved={:?}", index, reference.name, cached.is_some(),
                                        cached.and_then(|v| v.as_universal()).map(|v| v.has_references()));
                                }
                            }
                        }
''')
insert('''                    let declaration = context
                        .cascade
                        .substitute_variables_if_needed(''','''                    priority_trace!(&*context.cascade, longhand, "graph-resume",
                        "index={} eligible_before={} eligible_now={} seen={} appearance={:?} base_flag={}", index, eligible,
                        context.cascade.longhand_is_eligible(context.computed_context.included_cascade_flags, longhand, entry.priority),
                        context.cascade.seen.longhands.contains(longhand), context.computed_context.builder.get_box().get_appearance(),
                        context.computed_context.included_cascade_flags.intersects(RuleCascadeFlags::APPEARANCE_BASE));
''')
insert('''                    if let Some(dependency) = prioritary_adjustment_dependency(''','''                    priority_trace!(&*context.cascade, longhand, "graph-substituted", "index={} wide={:?}", index, declaration.get_css_wide_keyword());
''')
# A trace removal check is done before formatting.
import re
stripped = re.sub(r'/\* CSS_PRIORITY_TRACE_BEGIN \*/\n.*?/\* CSS_PRIORITY_TRACE_END \*/\n', '', source, flags=re.S)
assert stripped == base
for name,body in [('base',base),('candidate',source)]:
    path=HERE/name/REL;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(body)
tool=json.loads((ROOT/'artifacts/css-prioritary-selected-declaration-proposal-v4/TOOLCHAIN.json').read_text())
assert hashlib.sha256(Path(tool['rustfmt']).read_bytes()).hexdigest()==tool['sha256']
subprocess.run([tool['rustfmt'],'--config-path',str(ROOT/tool['config_source']),str(HERE/'candidate'/REL)],check=True,capture_output=True,text=True)
formatted=(HERE/'candidate'/REL).read_text()
(HERE/'native.patch').write_text(''.join(difflib.unified_diff(base.splitlines(True),formatted.splitlines(True),fromfile='a/'+REL,tofile='b/'+REL)))
(HERE/'TOOLCHAIN.json').write_text(json.dumps(tool,indent=2)+'\n')
print(json.dumps({'unformatted_trace_removal_exact':True,'base_sha256':hashlib.sha256(base.encode()).hexdigest(),'candidate_sha256':hashlib.sha256(formatted.encode()).hexdigest(),'native_compile':False}))
