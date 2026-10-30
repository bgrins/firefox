from pathlib import Path
import difflib,json,subprocess,textwrap
H=Path(__file__).resolve().parent
rel=Path('servo/components/style/properties/cascade.rs')
s=(H/'parent'/rel).read_text()
def replace(old,new,count=1):
 global s
 assert s.count(old)==count,(old[:100],s.count(old))
 s=s.replace(old,new)
a=s.index('struct PreparedMetricDeclaration {');b=s.index('#[derive(Clone, Copy, Debug, Eq, PartialEq)]\nenum ComputationStatus',a)
stage=s[a:b]
stage=stage.replace('    id: PrioritaryPropertyId,','    longhand: LonghandId,',1)
start=stage.index("    fn begin_metric_preparation<'a, 'b>(");end=stage.index('    // `completed`',start)
stage=stage[:start]+(H/'BEGIN.rs').read_text()+'\n'+stage[end:]
stage=stage.replace('let longhand = state.id.to_longhand();','let longhand = state.longhand;\n        let priority = PrioritaryPropertyId::from_longhand(longhand);')
stage=stage.replace('self.ensured_prioritary.contains(state.id)','priority.is_some_and(|id| self.ensured_prioritary.contains(id))')
stage=stage.replace('        let prerequisites = state.id.dependencies();\n        if !completed.contains_all(prerequisites) {\n            return MetricPreparationStep::Prerequisites(prerequisites);\n        }','        if let Some(id) = priority {\n            let prerequisites = id.dependencies();\n            if !completed.contains_all(prerequisites) {\n                return MetricPreparationStep::Prerequisites(prerequisites);\n            }\n        }')
stage=stage.replace('!completed.contains_all(state.id.dependencies())','priority.is_some_and(|id| !completed.contains_all(id.dependencies()))')
stage=stage.replace('        if self.seen.longhands.contains(longhand) {\n            self.did_apply_prioritary_property(context, state.id);\n        }\n        self.ensured_prioritary.insert(state.id);','        if let Some(id) = priority {\n            if self.seen.longhands.contains(longhand) {\n                self.did_apply_prioritary_property(context, id);\n            }\n            self.ensured_prioritary.insert(id);\n        }')
stage=stage.replace('    cursor: DeclarationIndex,', '    cursor: Option<usize>,')
sa=stage.index('    fn advance(&mut self) {');sb=stage.index('\n}\n\nimpl Cascade',sa)
stage=stage[:sa]+"""    fn advance(&mut self) {
        let index = self.cursor.expect("advancing an exhausted declaration cursor");
        if PrioritaryPropertyId::from_longhand(self.longhand).is_none() {
            self.cursor = next_font_declaration(self.declarations, self.longhand, index + 1);
            return;
        }
        let next = self.declarations.longhand_declarations[index].next_index;
        self.cursor = (next != 0).then_some(next as usize);
    }
"""+stage[sb:]
stage=stage.replace('            if state.cursor == DeclarationIndex::MAX {\n                state.complete = true;\n                continue;\n            }\n            let entry = state.declarations.longhand_declarations[state.cursor as usize];', '            let Some(index) = state.cursor else {\n                state.complete = true;\n                continue;\n            };\n            let entry = state.declarations.longhand_declarations[index];')
assert 'state.id' not in stage
s=s[:a]+(H/'TARGET.rs').read_text()+'\n'+stage+s[b:]
replace('fn has_unprepared_font_inputs(decls: &Declarations) -> bool {','fn next_unprepared_font_input(decls: &Declarations, completed: &LonghandIdSet) -> Option<LonghandId> {')
replace('    decls.longhand_declarations.iter().any(|entry| {','    decls.longhand_declarations.iter().find_map(|entry| {')
replace('            return false;\n        };\n        matches!(\n            id.name(),','            return None;\n        };\n        if completed.contains(id) { return None; }\n        matches!(\n            id.name(),')
# Scope inventory tail precisely rather than changing another matches expression.
a=s.index('fn next_unprepared_font_input');b=s.index('#[derive(Clone, Copy, Debug, Eq, PartialEq)]\nenum FontTarget',a)
part=s[a:b];part=part.replace('        )\n    })\n}','        ).then_some(id)\n    })\n}');s=s[:a]+part+s[b:]
replace('    unprepared_font_inputs: bool,','    unprepared_font_inputs: Option<LonghandId>,')
replace('        if demand >= FontDependencyDemand::FontMetrics && unprepared_font_inputs {\n            return PublicationDemand::Unresolved;\n        }','        if demand >= FontDependencyDemand::FontMetrics && let Some(id) = unprepared_font_inputs {\n            return if is_synthesis_longhand(id) { PublicationDemand::Synthesis(id) } else { PublicationDemand::Unresolved };\n        }')
replace('        Metric(PrioritaryPropertyId),\n        Unresolved,','        Metric(PrioritaryPropertyId),\n        Synthesis(LonghandId),\n        Unresolved,')
replace('        prerequisite: PrioritaryPropertyId,','        prerequisite: FontTarget,')
replace('        Published(PrioritaryPropertyId),','        Published(FontTarget),')
replace('        Pending(Option<PrioritaryPropertyId>),','        Pending(Option<FontTarget>),')
replace('PublicationDemand::Metric(id) => return FrameStep::Pending(Some(id))','PublicationDemand::Metric(id) => return FrameStep::Pending(Some(FontTarget::Metric(id)))')
replace('                            PublicationDemand::Unresolved => return FrameStep::Pending(None),','                            PublicationDemand::Synthesis(id) => return FrameStep::Pending(Some(FontTarget::Synthesis(id))),\n                            PublicationDemand::Unresolved => return FrameStep::Pending(None),')
replace('                bool,\n            ) -> PublicationDemand,','                Option<LonghandId>,\n            ) -> PublicationDemand,',2)
replace('has_unprepared_font_inputs(context.decls)','next_unprepared_font_input(context.decls, &context.completed_font_inputs)',2)
replace('        metric_action: Option<MetricAction>,',"        metric_action: Option<MetricAction>,\n        font_preparation: Option<MetricPreparation<'a, 'd>>,\n        completed_font_inputs: LonghandIdSet,\n        font_completion_flags: Option<RuleCascadeFlags>,")
replace('            assert!(self.metric_action.is_none());','            assert!(self.metric_action.is_none() && self.font_preparation.is_none());')
replace('        fn import_priority_completion(&mut self) {','        fn import_priority_completion(&mut self) {\n            if self.font_completion_flags != Some(self.computed_context.included_cascade_flags) {\n                self.completed_font_inputs = LonghandIdSet::default();\n                self.font_completion_flags = Some(self.computed_context.included_cascade_flags);\n            }')
a=s.index('        fn perform_metric_action(');b=s.index('        fn visited(',a)
part=s[a:b]
x=part.index('            use PrioritaryPropertyId::*;')
part=part[:x]+'            let target_id = match action.prerequisite {\n                FontTarget::Metric(id) => id,\n                FontTarget::Synthesis(longhand) => return self.perform_synthesis_action(longhand, attribute_tracker),\n            };\n'+part[x:].replace('action.prerequisite','target_id').replace('MetricActionProgress::Published(id)','MetricActionProgress::Published(FontTarget::Metric(id))')
s=s[:a]+part+textwrap.indent((H/'SYNTHESIS-ACTION.rs').read_text(),'        ')+'\n'+s[b:]
replace('        metric_action: None,\n        stylist,','        metric_action: None,\n        font_preparation: None,\n        completed_font_inputs: LonghandIdSet::default(),\n        font_completion_flags: None,\n        stylist,')
q=H/'candidate'/rel;q.write_text(s)
t=json.loads((H/'TOOLCHAIN.json').read_bytes())
subprocess.run([t['rustfmt'],'--config-path',str(H.parents[1]/t['config']),str(q)],check=True)
for name,folder in [('PARENT-DELTA.patch','parent'),('native.patch','base')]:
 paths=[rel,Path('servo/components/style/custom_properties.rs')]
 (H/name).write_text(''.join(''.join(difflib.unified_diff((H/folder/r).read_text().splitlines(True),(H/'candidate'/r).read_text().splitlines(True),fromfile='a/'+str(r),tofile='b/'+str(r))) for r in paths))
