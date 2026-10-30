from pathlib import Path
import difflib,json,subprocess,textwrap
H=Path(__file__).resolve().parent
relative=Path('servo/components/style/properties/cascade.rs')
s=(H/'parent'/relative).read_text()
def replace(a,b):
 global s
 assert s.count(a)==1,a[:120]
 s=s.replace(a,b,1)
replace('enum ReferenceReadiness {\n        Ready,','enum ReferenceReadiness {\n        Ready,\n        SemanticOpen,')
# Retain the existing eager implementation as the comparison path.
a=s.index('    fn traverse<');b=s.index('        let mut self_ref = false;',a)
start=s[a:b]
start=start.replace('fn traverse<','fn start_frame<',1)
start=start.replace('        references_from_non_custom_properties: &NonCustomPropertyReferences,\n','',1)
start=start.replace(') -> VisitResult {',') -> Result<TraversalFrame, VisitResult> {',1)
start=start.replace('return result;','return Err(result);')
for v in ['VisitResult::Complete','VisitResult::SemanticOpen(*entry.get())','VisitResult::SemanticOpen(*v)']:
 start=start.replace('return '+v+';', 'return Err('+v+');')
# match-arm early returns differ from statements.
start=start.replace('None => return VisitResult::Complete,','None => return Err(VisitResult::Complete),')
start+='''        let phase = if value.is_some() { FramePhase::References } else { FramePhase::PrioritySize };
        Ok(TraversalFrame {
            var, index, lowlink: index, self_ref: false, registered,
            selected_dependency_eligible, value_non_custom_refs, value,
            prepared_custom: None, phase, walk: None, unit_links: SmallVec::new(),
            unit_cursor: 0, priority_cursor: 0, waiting: None, reference_reply: None,
        })
    }

'''
s=s[:a]+textwrap.indent((H/'FRAME.rs').read_text(),'    ')+'\n'+start+s[a:]
replace('        var_info: SmallVec<[VarInfo; 5]>,','''        var_info: SmallVec<[VarInfo; 5]>,
        frames: Vec<TraversalFrame>,
        frame_root: Option<VarType>,
        frame_reply: Option<(VarType, VisitResult)>,''')
replace('        fn reset(&mut self) {\n            assert!(self.stack.is_empty());','''        fn reset(&mut self) {
            assert!(self.frames.is_empty() && self.frame_root.is_none() && self.frame_reply.is_none());
            assert!(self.stack.is_empty());''')
replace('        fn visited(&self, var: &VarType)',textwrap.indent((H/'POLL.rs').read_text(),'        ')+'\n        fn visited(&self, var: &VarType)')
replace('        var_info: SmallVec::new(),\n        stylist,','''        var_info: SmallVec::new(),
        frames: Vec::new(),
        frame_root: None,
        frame_reply: None,
        stylist,''')
replace('''        let result = traverse(
            var,
            references_from_non_custom_properties,
            &mut context,
            attr_tracker,
        );''','''        let use_retained_frames = true;
        let result = if use_retained_frames {
            context.poll_root(var, references_from_non_custom_properties, attr_tracker, &mut |_| true)
        } else {
            traverse(var, references_from_non_custom_properties, &mut context, attr_tracker)
        };''')
q=H/'candidate'/relative;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(s)
tools=json.loads((H/'TOOLCHAIN.json').read_bytes())
subprocess.run([tools['rustfmt'],'--config-path',str(H.parents[1]/tools['config']),str(q)],check=True)
for name,folder in [('PARENT-DELTA.patch','parent'),('native.patch','base')]:
 (H/name).write_text(''.join(difflib.unified_diff((H/folder/relative).read_text().splitlines(True),q.read_text().splitlines(True),fromfile='a/'+str(relative),tofile='b/'+str(relative))))
