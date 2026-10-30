fn priority_has_dynamic_declarations(
    decls: &Declarations,
    id: PrioritaryPropertyId,
) -> bool {
    let mut index = decls.prioritary_positions[id as usize].most_important;
    if index == DeclarationIndex::MAX {
        return false;
    }
    loop {
        let entry = &decls.longhand_declarations[index as usize];
        if matches!(entry.decl, PropertyDeclaration::WithVariables(..)) {
            return true;
        }
        index = entry.next_index;
        if index == 0 {
            return false;
        }
    }
}
