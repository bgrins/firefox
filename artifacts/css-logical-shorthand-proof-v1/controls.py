LEAN_MUTATIONS = {
    'MappingBeforeCount': ('if a.shorthand then 2 else', 'if a.shorthand then (if a.logical then 3 else 2) else'),
    'OmitLogicalTie': ('(a.logical = false ∧ b.logical = true ∨ a.logical = b.logical ∧ a.idl ≤ b.idl))', 'a.idl ≤ b.idl)'),
    'ReverseIDL': ('(a.logical = false ∧ b.logical = true ∨ a.logical = b.logical ∧ a.idl ≤ b.idl))', '(a.logical = false ∧ b.logical = true ∨ a.logical = b.logical ∧ b.idl ≤ a.idl))'),
    'ReverseCount': ('a.components < b.components ∨ a.components = b.components ∧\n        (a.logical', 'b.components < a.components ∨ a.components = b.components ∧\n        (a.logical'),
    'DropMatch': ('if target ∈ d.targets then some d else firstMatch target ds', 'if target ∈ d.targets then firstMatch target ds else firstMatch target ds'),
    'WrongTarget': ('if target ∈ d.targets then some d else firstMatch target ds', 'if target ∉ d.targets then some d else firstMatch target ds'),
}
RUST_MUTATIONS = {
    'MappingBeforeCount': ('subprop_count_a\n        .cmp(&subprop_count_b)\n        .then_with(|| {\n            let a_is_logical = a.longhands().all(|id| id.is_logical());\n            let b_is_logical = b.longhands().all(|id| id.is_logical());\n            a_is_logical.cmp(&b_is_logical)\n        })', 'a.longhands().all(|id| id.is_logical())\n        .cmp(&b.longhands().all(|id| id.is_logical()))\n        .then_with(|| subprop_count_a.cmp(&subprop_count_b))'),
    'OmitLogicalTie': ('.then_with(|| {\n            let a_is_logical = a.longhands().all(|id| id.is_logical());\n            let b_is_logical = b.longhands().all(|id| id.is_logical());\n            a_is_logical.cmp(&b_is_logical)\n        })', ''),
    'ReverseLogicalTie': ('a_is_logical.cmp(&b_is_logical)', 'b_is_logical.cmp(&a_is_logical)'),
    'ReverseCount': ('.cmp(&subprop_count_b)', '.cmp(&subprop_count_b).reverse()'),
    'ReverseIDL': ('a.idl_name_sort_order().cmp(&b.idl_name_sort_order())', 'b.idl_name_sort_order().cmp(&a.idl_name_sort_order())'),
}
