# Source and model joins

| Frozen source path | Model and required domain |
| --- | --- |
| ComputeStickyLimits missing offsets, normalization OR/AND, computed/effective values | WideNormalization.source/machine/reference and Safe; WideCallers.selected/machineSelected |
| signed64 view subtraction, delta, selected-end subtraction and signed32 compound assignment | machine_end_refines; provider_bounds_supply_narrowing; every_old_defined_normalization_unchanged |
| containing-block writing mode versus legacy direction | WideCallers.mode_mapping, StickyWritingMode.end_selection_refines; source-extracted native helpers |
| frame offset, margin difference, both Deflates, containment MoveBy and each direct stick setter | WideGeometry.constructWith writes; complete_machine_limits and complete_contain_record |
| old near/far setter temporaries and queried edge reconstruction | LegacyStorageSafe and defined_legacy_edges, together with old-defined normalization theorem |
| DoComputePosition in both scroll spaces | complete_position/both_positions; masked positionReference; closest_feasible_position |
| ComputeTranslationIgnoringScrolling full nsPoint subtraction | both_translation_components; TranslationSafe checks both coordinate subtractions |
| GetScrollRanges direct stick record, containment FromRect, all side writes | complete_contain_join; RangeSafe; direct_absolute_machine |
| Intersect, cross-axis zeroing, IsEmpty, MoveInsideAndClamp | StickyAbsolute expression subtree, reference intersection/projection, complete_absolute_caller |
| GetStickyScrollRangesForAxis early returns, both-axis ComputeStickyLimits, optional thresholds/distances and ordering clear | WideAxisRanges.Safe/DebugSafe and complete_axis_caller |
| scrolled-content padding Deflate before TransformRect | WideProviders.PaddingSafe, both_padding_components, prepared caller theorems |
| ordinary content union/transform output/first continuation | Explicit raw provider and canonical-first-frame boundary in ADMISSIONS; complete native extraction and trace calibration |

The four bindings JSON files contain complete source bodies, byte offsets, and hashes. native/generate.py substitutes those complete bodies into the visible native/prefix.cpp adapter and inserts the actual frozen StickyLimits record. It does not substitute live source or reconstruct after-source from before-source. The genuine before/after files and their original test roles are authenticated by source_roles.py.

The corpus independently compares Python minimum/projection semantics, executed Lean references and extracted native observations. Exact source mapping and finite calibration support the human-reviewed C++/model relationship; they do not replace that relationship with a verified compiler theorem.
