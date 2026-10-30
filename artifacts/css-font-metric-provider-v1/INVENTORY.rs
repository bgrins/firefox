fn has_unprepared_font_inputs(decls: &Declarations) -> bool {
    decls.longhand_declarations.iter().any(|entry| {
        let PropertyDeclarationId::Longhand(id) = entry.decl.id() else {
            return false;
        };
        matches!(id.name(),
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
    })
}
