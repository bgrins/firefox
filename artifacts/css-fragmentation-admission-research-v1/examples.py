import json

rows = []
def record(name, actual, expected):
    assert actual == expected, (name, actual, expected)
    rows.append({'case': name, 'observation': actual})

# Synthetic arithmetic checks, not native layout or normative certification.
record('legal point beyond capacity', {'allowed_nonempty': True, 'fitting_nonempty': 4 <= 2},
       {'allowed_nonempty': True, 'fitting_nonempty': False})
record('two emergency interpretations on same complete opportunity',
       {'all_future_points_no_below_top': all(y == 0 for y in [4]),
        'within_capacity_points_no_below_top': all(y == 0 for y in [4] if y <= 2)},
       {'all_future_points_no_below_top': False, 'within_capacity_points_no_below_top': True})
record('zero prefix is not geometric progress', {'cut_index_positive': 1 > 0, 'offset_positive': sum([0]) > 0},
       {'cut_index_positive': True, 'offset_positive': False})
record('zero after fitted versus overflowing predecessor',
       {'after_2_in_capacity_2_fits': 2 <= 2, 'after_4_in_capacity_2_fits': 4 <= 2},
       {'after_2_in_capacity_2_fits': True, 'after_4_in_capacity_2_fits': False})
record('point on capacity boundary is fitting', 2 <= 2, True)
record('forced break cannot be erased by completion fit',
       {'whole_fits': sum([1, 1]) <= 2, 'pending_force_after_first': True},
       {'whole_fits': True, 'pending_force_after_first': True})
record('candidate-dependent active decoration',
       {'real_prefix_fits': [1 <= 2, 2 + 2 <= 2],
        'constant_zero_fits': [1 <= 2, 2 <= 2],
        'constant_two_fits': [1 + 2 <= 2, 2 + 2 <= 2]},
       {'real_prefix_fits': [True, False], 'constant_zero_fits': [True, True], 'constant_two_fits': [False, False]})
record('paragraph-local failure misses legal preceding deferral',
       {'nine_lines_finish_in_remaining_eight': 9 <= 8,
        'local_split_meets_orphans10_widows20': any(k >= 10 and 9-k >= 20 for k in range(1, 9)),
        'whole_paragraph_fits_fresh_capacity40': 9 <= 40},
       {'nine_lines_finish_in_remaining_eight': False,
        'local_split_meets_orphans10_widows20': False,
        'whole_paragraph_fits_fresh_capacity40': True})
print(json.dumps({'status':'pass','scope':'eight finite arithmetic distinctions; no browser/spec equivalence','cases':rows},indent=2))
