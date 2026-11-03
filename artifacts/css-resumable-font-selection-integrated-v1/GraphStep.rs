fn step(&mut self,_:&NonCustomPropertyReferences,context:&mut Context,attribute_tracker:&mut AttributeTracker,_:&mut impl FnMut(FontDependencyDemand,&PrioritaryPropertyIdSet,Option<LonghandId>)->PublicationDemand)->FrameStep{
 loop{match self.phase{
 FramePhase::References=>{assert!(self.guarded_custom.is_some());if let Some(step)=self.guarded_references(context,attribute_tracker){return step;}},
 FramePhase::Prepare=>{if self.registered{self.value_non_custom_refs.for_each_non_custom(context.computed_context.is_root_element(),|r|self.unit_links.push(r));}self.phase=FramePhase::Units;},
 UNITS_BODY,
 FramePhase::LateDefault=>{self.phase=FramePhase::Close;},
 CLOSE_BODY,
 FramePhase::Publish=>{assert!(context.publish_closed(self.index,attribute_tracker)==ComputationStatus::Ready);return FrameStep::Complete(VisitResult::Complete);}
 }}
}
