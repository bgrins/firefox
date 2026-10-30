fn next_unprepared_font_input(
    decls: &Declarations,
    completed: &LonghandIdSet,
) -> Option<LonghandId> {
    decls.longhand_declarations.iter().find_map(|entry| {
        let PropertyDeclarationId::Longhand(id) = entry.decl.id() else {
            return None;
        };
        if completed.contains(id) {
            return None;
        }
        matches!(
            id.name(),
            "font-feature-settings"
                | "font-language-override"
                | "font-palette"
                | "font-synthesis-position"
                | "font-synthesis-small-caps"
                | "font-synthesis-style"
                | "font-synthesis-weight"
                | "font-variant-alternates"
                | "font-variant-east-asian"
                | "font-variant-ligatures"
                | "font-variant-numeric"
                | "font-variation-settings"
                | "font-variant-caps"
                | "font-kerning"
                | "font-variant-emoji"
                | "font-variant-position"
                | "font-optical-sizing"
                | "math-style"
                | "math-shift"
                | "-moz-osx-font-smoothing"
                | "-moz-math-variant"
        )
        .then_some(id)
    })
}

