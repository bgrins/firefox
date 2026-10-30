fn poll_root(
    &mut self,
    var: VarType,
    references: &NonCustomPropertyReferences,
    attribute_tracker: &mut AttributeTracker,
    publication_ready: &mut impl FnMut(&VarType) -> bool,
) -> VisitResult {
    if let Some(root) = &self.frame_root {
        assert_eq!(*root, var);
    } else {
        assert!(self.frames.is_empty() && self.frame_reply.is_none());
        self.frame_root = Some(var.clone());
        match start_frame(var, self, attribute_tracker) {
            Ok(frame) => self.frames.push(frame),
            Err(result) => {
                self.frame_root = None;
                return result;
            },
        }
    }
    loop {
        let mut frame = self.frames.pop().expect("Active root owns a frame");
        if let Some((target, _)) = &frame.waiting {
            if let Some((target, result)) = self.frame_reply.take() {
                assert!(frame.receive(target, result, self));
            } else {
                let target = target.clone();
                self.frames.push(frame);
                match start_frame(target.clone(), self, attribute_tracker) {
                    Ok(child) => self.frames.push(child),
                    Err(VisitResult::ComputationPending(index)) => {
                        return VisitResult::ComputationPending(index);
                    },
                    Err(result) => self.frame_reply = Some((target, result)),
                }
                continue;
            }
        } else {
            assert!(self.frame_reply.is_none());
        }
        match frame.step(references, self, attribute_tracker, publication_ready) {
            FrameStep::Link(_) => self.frames.push(frame),
            FrameStep::Pending => {
                let index = frame.index;
                self.frames.push(frame);
                return VisitResult::ComputationPending(index);
            },
            FrameStep::Complete(result) => {
                if self.frames.is_empty() {
                    assert_eq!(self.frame_root.as_ref(), Some(&frame.var));
                    self.frame_root = None;
                    return result;
                }
                assert!(self.frame_reply.is_none());
                self.frame_reply = Some((frame.var, result));
            },
        }
    }
}
