    fn begin_metric_preparation<'a, 'b>(
        &self,
        context: &computed::Context,
        declarations: &'a Declarations<'b>,
        id: PrioritaryPropertyId,
    ) -> MetricPreparation<'a, 'b> {
        use PrioritaryPropertyId::*;
        assert!(matches!(id, FontWeight | FontWidth | FontStyle | FontSizeAdjust | Direction | WritingMode | TextOrientation));
        self.begin_font_preparation(context, declarations, id.to_longhand())
    }

    fn begin_font_preparation<'a, 'b>(
        &self,
        context: &computed::Context,
        declarations: &'a Declarations<'b>,
        longhand: LonghandId,
    ) -> MetricPreparation<'a, 'b> {
        let cursor = if let Some(id) = PrioritaryPropertyId::from_longhand(longhand) {
            let index = declarations.prioritary_positions[id as usize].most_important;
            (index != DeclarationIndex::MAX).then_some(index as usize)
        } else {
            assert!(is_synthesis_longhand(longhand));
            next_font_declaration(declarations, longhand, 0)
        };
        let initial_revert = self.reverted.longhands.get(&longhand).copied();
        MetricPreparation {
            longhand,
            declarations,
            cursor,
            flags: context.included_cascade_flags,
            initial_revert,
            revert: initial_revert,
            waiting: None,
            prepared: SmallVec::new(),
            complete: false,
        }
    }
