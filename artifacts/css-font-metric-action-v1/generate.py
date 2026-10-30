from pathlib import Path
import difflib,json,subprocess,textwrap
H=Path(__file__).resolve().parent
rel=Path('servo/components/style/properties/cascade.rs')
s=(H/'parent'/rel).read_text()
def replace(a,b):
 global s
 assert s.count(a)==1,(a[:100],s.count(a));s=s.replace(a,b,1)
replace('    enum FrameStep {\n        Link(VarType),\n        Complete(VisitResult),\n        Pending,\n    }','    enum FrameStep {\n        Link(VarType),\n        Complete(VisitResult),\n        Pending(Option<PrioritaryPropertyId>),\n    }')
s=s.replace('publication_ready: &mut impl FnMut(&VarType) -> bool','publication_ready: &mut impl FnMut(&VarType, &PrioritaryPropertyIdSet) -> PublicationDemand')
replace('''                        if !publication_ready(&self.var) {
                            return FrameStep::Pending;
                        }''','''                        match publication_ready(&self.var, &context.priority_completion.complete) {
                            PublicationDemand::Ready => {},
                            PublicationDemand::Metric(id) => return FrameStep::Pending(Some(id)),
                            PublicationDemand::Unresolved => return FrameStep::Pending(None),
                        }''')
replace('''        frame_reply: Option<(VarType, VisitResult)>,''','''        frame_reply: Option<(VarType, VisitResult)>,
        priority_completion: PriorityCompletion,
        metric_drain: MetricDrain<'a, 'd>,
        metric_action: Option<MetricAction>,''')
replace('''        fn reset(&mut self) {''','''        fn reset(&mut self) {
            assert!(self.metric_action.is_none());''')
replace('''            loop {
                let mut frame = self.frames.pop().expect("Active root owns a frame");''','''            if let Some(action) = &self.metric_action {
                return VisitResult::ComputationPending(action.index);
            }
            loop {
                let mut frame = self.frames.pop().expect("Active root owns a frame");''')
replace('''                    FrameStep::Pending => {
                        let index = frame.index;
                        self.frames.push(frame);
                        return VisitResult::ComputationPending(index);
                    },''','''                    FrameStep::Pending(prerequisite) => {
                        let index = frame.index;
                        self.metric_action = prerequisite.map(|prerequisite| MetricAction {
                            identity: Arc::new(()),
                            root: self.frame_root.as_ref().unwrap().clone(),
                            owner: frame.var.clone(),
                            index,
                            prerequisite,
                        });
                        self.frames.push(frame);
                        return VisitResult::ComputationPending(index);
                    },''')
replace('        fn visited(&self, var: &VarType)',textwrap.indent((H/'ACTION-METHODS.rs').read_text(),'        ')+'\n        fn visited(&self, var: &VarType)')
replace('    #[derive(Clone, Copy)]\n    enum FramePhase',textwrap.indent((H/'ACTION.rs').read_text(),'    ')+'\n    #[derive(Clone, Copy)]\n    enum FramePhase')
replace('''        frame_reply: None,
        stylist,''','''        frame_reply: None,
        priority_completion: PriorityCompletion::default(),
        metric_drain: MetricDrain::new(decls),
        metric_action: None,
        stylist,''')
replace('''                &mut |_| true,''','''                &mut |_, _| PublicationDemand::Ready,''')
q=H/'candidate'/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(s)
t=json.loads((H/'TOOLCHAIN.json').read_bytes());subprocess.run([t['rustfmt'],'--config-path',str(H.parents[1]/t['config']),str(q)],check=True)
for name,folder in [('PARENT-DELTA.patch','parent'),('native.patch','base')]:
 (H/name).write_text(''.join(difflib.unified_diff((H/folder/rel).read_text().splitlines(True),q.read_text().splitlines(True),fromfile='a/'+str(rel),tofile='b/'+str(rel))))
