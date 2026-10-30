import difflib
from pathlib import Path
import textwrap

HERE = Path(__file__).resolve().parent
rel = Path('servo/components/style/properties/cascade.rs')
s = (HERE / 'parent' / rel).read_text()
def replace(old, new):
    global s
    assert s.count(old) == 1, old[:120]
    s = s.replace(old, new, 1)
replace('    ComputedCustomProperties, ComputedSubstitutionFunctions, Name, NonCustomReferenceMap,', '    ComputedCustomProperties, ComputedSubstitutionFunctions, Name, NonCustomReferenceMap,\n    ComputedValue as ComputedPropertyValue, PreparedCustomValue,')

replace('    /// Struct recording necessary information for each variable.\n    #[derive(Debug)]\n    struct VarInfo {', '''    enum ClosedValue {
        Prepared(Name, PreparedCustomValue),
        Substitute(VarType, Arc<ComputedPropertyValue>),
        Prioritary(PrioritaryPropertyId),
    }

''' + textwrap.indent((HERE / 'PUBLICATION.rs').read_text(), '    ') + '''
    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum VisitResult {
        SemanticOpen(usize),
        ComputationPending(usize),
        Complete,
        CycleSettled,
    }

    /// Struct recording necessary information for each variable.
    struct VarInfo {''')
replace('        lowlink: usize,\n    }', '        lowlink: usize,\n        publication: NodePublication<ClosedValue>,\n    }')
replace('        fn reset(&mut self) {\n            self.count = 0;', '''        fn reset(&mut self) {
            assert!(self.stack.is_empty());
            assert!(self.var_info.iter().all(|info| info.publication.can_retire()));
            self.count = 0;''')
needle='''        fn map(&self) -> &ComputedSubstitutionFunctions {'''
replace(needle, '''        fn visited(&self, var: &VarType) -> Option<VisitResult> {
            let index = match var {
                VarType::Custom(name) => self.index_map.var.get(name).copied(),
                VarType::Attr(name, namespace) => self.index_map.attr.get(namespace)
                    .and_then(|map| map.get(name)).copied(),
                VarType::NonCustom(reference) => self.non_custom_index_map[*reference],
            }?;
            Some(match self.var_info[index].publication.readiness() {
                NodeReadiness::SemanticOpen => VisitResult::SemanticOpen(index),
                NodeReadiness::ComputationPending => VisitResult::ComputationPending(index),
                NodeReadiness::Complete => VisitResult::Complete,
                NodeReadiness::CycleSettled => VisitResult::CycleSettled,
            })
        }

        fn publish_closed(&mut self, index: usize, attr_tracker: &mut AttributeTracker) {
            let value = self.var_info[index].publication.take_ready(true).unwrap();
            match value {
                ClosedValue::Prepared(name, prepared) => {
                    prepared.apply(&name, self.stylist, self.computed_context);
                },
                ClosedValue::Substitute(var, value) => {
                    let name = match &var {
                        VarType::Custom(name) | VarType::Attr(name, _) => name,
                        VarType::NonCustom(_) => unreachable!(),
                    };
                    substitute_references_if_needed_and_apply(
                        name, var.namespace(), &value, self.stylist,
                        self.computed_context, attr_tracker,
                    );
                },
                ClosedValue::Prioritary(id) => self.apply_prioritary_property(id, attr_tracker),
            }
            self.var_info[index].publication.finish();
        }

''' + needle)
replace('''            Some(index) => index,
            // There is nothing to do if the next variable has been
            // fully resolved at this point.
            None => return,''','''            VisitResult::SemanticOpen(index) => index,
            VisitResult::Complete | VisitResult::CycleSettled => return,
            VisitResult::ComputationPending(_) => {
                unreachable!("Recursive traversal cannot resume a suspended publication")
            },''')
start = s.index('    /// This function combines the traversal for cycle removal')
end = s.index('    fn traverse<', start)
s = s[:start] + '    /// Separates semantic ancestry from completed map outcomes.\n' + s[end:]
replace('''    ) -> Option<usize> {
        // Some shortcut checks.''', '''    ) -> VisitResult {
        if let Some(result) = context.visited(&var) {
            return result;
        }
        // Some shortcut checks.''')
replace('''                        map.get_var(registration, name)?.as_universal()?,''','''                        match map.get_var(registration, name).and_then(|value| value.as_universal()) {
                            Some(value) => value,
                            None => return VisitResult::Complete,
                        },''')
replace('''                        map.get_attr(name, var.namespace().unwrap())?
                            .as_universal()?,''','''                        match map.get_attr(name, var.namespace().unwrap()).and_then(|value| value.as_universal()) {
                            Some(value) => value,
                            None => return VisitResult::Complete,
                        },''')
# Scoped replacements in traverse body.
a=s.index('    fn traverse<');b=s.index('    let mut context = Context {',a);part=s[a:b]
part=part.replace('return None;', 'return VisitResult::Complete;').replace('return Some(*entry.get());','return VisitResult::SemanticOpen(*entry.get());').replace('return Some(*v);','return VisitResult::SemanticOpen(*v);').replace('return Some(index);','return VisitResult::SemanticOpen(index);')
part=part.replace('            lowlink: index,\n        });','            lowlink: index,\n            publication: NodePublication::SemanticOpen,\n        });')
part=part.replace('        let mut in_loop = self_ref;','        let mut in_loop = self_ref;\n        let mut cycle_members = SmallVec::<[usize; 5]>::new();')
part=part.replace('''            if in_loop {
                context.handle_loop(&var_name);
            }''','''            if in_loop {
                context.var_info[var_index].publication.begin_cycle();
                cycle_members.push(var_index);
                context.handle_loop(&var_name);
            }''')
part=part.replace('''        if in_loop {
            return VisitResult::Complete;
        }''','''        if in_loop {
            for member in cycle_members {
                context.var_info[member].publication.settle_cycle();
            }
            return VisitResult::CycleSettled;
        }''')
start=part.index('        // Not in a loop, apply the value.')
part=part[:start]+'''        let publication = match var {
            VarType::Custom(ref name) | VarType::Attr(ref name, _) => {
                if let Some(prepared) = prepared_custom {
                    ClosedValue::Prepared(name.clone(), prepared)
                } else {
                    ClosedValue::Substitute(var, value.expect("Custom and attr nodes retain their value"))
                }
            },
            VarType::NonCustom(non_custom) => ClosedValue::Prioritary(non_custom.to_prioritary_id()),
        };
        context.var_info[index].publication.close(publication);
        context.publish_closed(index, attribute_tracker);
        VisitResult::Complete
    }

'''
s=s[:a]+part+s[b:]
replace('''        traverse(
            var,
            references_from_non_custom_properties,
            &mut context,
            attr_tracker,
        );''','''        let result = traverse(
            var,
            references_from_non_custom_properties,
            &mut context,
            attr_tracker,
        );
        assert!(matches!(result, VisitResult::Complete | VisitResult::CycleSettled));''')
# Ensure even the last root cannot retire outstanding publication.
assert s.endswith('}\n')
pos=s.rfind('    }\n}')
s=s[:pos+6]+'''    assert!(context.stack.is_empty());
    assert!(context.var_info.iter().all(|info| info.publication.can_retire()));
'''+s[pos+6:]
q=HERE/'candidate'/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(s)

import json
import subprocess
tools = json.loads((HERE / 'TOOLCHAIN.json').read_bytes())
subprocess.run([tools['rustfmt'], '--config-path', str(HERE.parents[1] / tools['config']), str(q)], check=True)
for name, folder in [('PARENT-DELTA.patch', 'parent'), ('native.patch', 'base')]:
    (HERE / name).write_text(''.join(difflib.unified_diff((HERE / folder / rel).read_text().splitlines(True), q.read_text().splitlines(True), fromfile='a/' + str(rel), tofile='b/' + str(rel))))
