#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum FontTarget {
    Metric(PrioritaryPropertyId),
    Synthesis(LonghandId),
}

fn is_synthesis_longhand(id: LonghandId) -> bool {
    matches!(id, LonghandId::FontSynthesisWeight | LonghandId::FontSynthesisStyle | LonghandId::FontSynthesisSmallCaps | LonghandId::FontSynthesisPosition)
}

fn next_font_declaration(declarations: &Declarations, longhand: LonghandId, start: usize) -> Option<usize> {
    declarations.longhand_declarations.iter().enumerate().skip(start).find_map(|(index, entry)| {
        (entry.decl.id() == PropertyDeclarationId::Longhand(longhand)).then_some(index)
    })
}
