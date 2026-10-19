import HexPrefix
import Escape
import Name
import Boundary
import CommentScan
import CommentObservers
import CommentDirectives
import CommentExecution
import CommentUTF8
import CommentCodepoints
import CommentNativeBounds
import StringTransitions
import StringUTF8
import StringContracts
import StringTrace
import StringAdmission
#print axioms HexPrefix.digit_classification
#print axioms HexPrefix.digit_bound
#print axioms HexPrefix.selected_none
#print axioms HexPrefix.selected_some
#print axioms HexPrefix.run_reference
#print axioms HexPrefix.selected_length_le
#print axioms HexPrefix.count_bound
#print axioms HexPrefix.exact_remainder
#print axioms HexPrefix.consumed_plus_remaining
#print axioms HexPrefix.value_bound
#print axioms HexPrefix.six_digits_u32
#print axioms Escape.scalar_mapping
#print axioms Escape.whitespace_reference
#print axioms Escape.whitespace_bound
#print axioms Escape.native_reference
#print axioms Escape.consumption_bound
#print axioms Escape.residual_bound
#print axioms Name.ordinary_classification
#print axioms Name.nonordinary_ascii
#print axioms Name.ordinary_prefix
#print axioms Name.simple_ordinary
#print axioms Name.fast_prefix
#print axioms Name.native_fast_chunk
#print axioms Name.fast_chunk_advance_domain
#print axioms Name.consumed_bound
#print axioms Name.exact_remainder
#print axioms Name.positive_ordinary
#print axioms Name.positive_nul
#print axioms Name.positive_escape
#print axioms Name.return_boundary
#print axioms Boundary.name_return_marker
#print axioms Boundary.unit_ascii_singleton
#print axioms Boundary.unit_nonempty
#print axioms Boundary.complete_unit_marker
#print axioms Boundary.ascii_step
#print axioms Boundary.ascii_prefix
#print axioms Boundary.digit_ascii
#print axioms Boundary.hex_suffix
#print axioms CommentScan.marks_cons
#print axioms CommentScan.index_cons
#print axioms CommentScan.marks_length
#print axioms CommentScan.index_bound
#print axioms CommentScan.scan_reference
#print axioms CommentScan.stop_tail
#print axioms CommentScan.consumed_bound
#print axioms CommentScan.body_count
#print axioms CommentScan.exact_body
#print axioms CommentScan.remainder_decomposition
#print axioms CommentScan.grouped_scan
#print axioms CommentObservers.width_classification
#print axioms CommentObservers.irrelevant_pending
#print axioms CommentObservers.native_reference
#print axioms CommentObservers.reference_offset
#print axioms CommentObservers.consumed_offset
#print axioms CommentDirectives.whitespace_classification
#print axioms CommentDirectives.literal_prefix
#print axioms CommentDirectives.directive_reference
#print axioms CommentDirectives.map_key
#print axioms CommentDirectives.source_key
#print axioms CommentDirectives.update_reference
#print axioms CommentDirectives.preserves_map
#print axioms CommentDirectives.preserves_source
#print axioms CommentDirectives.history_reference
#print axioms CommentDirectives.empty_url_overwrites
#print axioms CommentExecution.run_scan
#print axioms CommentExecution.head_take_not
#print axioms CommentExecution.run_observer
#print axioms CommentExecution.execution_reference
#print axioms CommentExecution.body_reference
#print axioms CommentExecution.raw_reference
#print axioms CommentUTF8.stop_false
#print axioms CommentUTF8.prefix_scan
#print axioms CommentUTF8.drop_prefix
#print axioms CommentUTF8.unit_nonstar
#print axioms CommentUTF8.valid_body_and_suffix
#print axioms CommentUTF8.raw_opening_suffix
#print axioms CommentUTF8.raw_body_and_suffix
#print axioms CommentUTF8.takeWhile_prefix
#print axioms CommentUTF8.valid_takeWhile
#print axioms CommentUTF8.url_prefix_utf8
#print axioms CommentUTF8.literal_suffix_utf8
#print axioms CommentUTF8.directive_value_utf8
#print axioms CommentCodepoints.continuation_step
#print axioms CommentCodepoints.continuation_fold
#print axioms CommentCodepoints.unit_observer
#print axioms CommentCodepoints.raw_units_observer
#print axioms CommentCodepoints.native_units_observer
#print axioms CommentNativeBounds.ordinary_column
#print axioms CommentNativeBounds.continuation_column
#print axioms CommentNativeBounds.four_intro_column
#print axioms CommentNativeBounds.newline_column
#print axioms CommentNativeBounds.wrapping_projection
#print axioms CommentNativeBounds.packed_line_decode
#print axioms CommentNativeBounds.packed_line_step
#print axioms CommentNativeBounds.step_bounds
#print axioms CommentNativeBounds.fold_bounds
#print axioms CommentNativeBounds.native_bounds
#print axioms CommentNativeBounds.run_endpoint
#print axioms CommentNativeBounds.raw_endpoint_bound
#print axioms CommentNativeBounds.native_capacity
#print axioms StringTransitions.class_equivalence
#print axioms StringTransitions.newline_equivalence
#print axioms StringTransitions.newline_count
#print axioms StringTransitions.escape_equivalence
#print axioms StringTransitions.escape_bound
#print axioms StringTransitions.owned_reference
#print axioms StringTransitions.borrowed_reference
#print axioms StringTransitions.prefix_composition
#print axioms StringTransitions.reference_bound
#print axioms StringTransitions.escaped_eof_distinction
#print axioms StringUTF8.valid_nil
#print axioms StringUTF8.valid_append
#print axioms StringUTF8.valid_ascii
#print axioms StringUTF8.encode_shape
#print axioms StringUTF8.scalar_domain
#print axioms StringUTF8.replacement_valid
#print axioms StringUTF8.whitespace_suffix
#print axioms StringUTF8.escape_valid
#print axioms StringUTF8.string_escape_valid
#print axioms StringUTF8.copy_prefix
#print axioms StringUTF8.nonascii_copy
#print axioms StringUTF8.unit_copy
#print axioms StringUTF8.noncopy_ascii
#print axioms StringUTF8.reference_valid
#print axioms StringUTF8.owned_return_valid
#print axioms StringUTF8.borrowed_return_valid
#print axioms StringUTF8.owned_copy_prefix
#print axioms StringUTF8.partial_copy_rejoin
#print axioms StringUTF8.partial_copy_return_valid
#print axioms StringContracts.bad_class
#print axioms StringContracts.bad_newline
#print axioms StringContracts.eof_exhausts
#print axioms StringContracts.borrowed_slice
#print axioms StringContracts.raw_reference
#print axioms StringContracts.raw_progress
#print axioms StringTrace.value_reference
#print axioms StringTrace.consumed_bound
#print axioms StringTrace.take_split
#print axioms StringTrace.trace_exact
#print axioms StringTrace.observer_reference
#print axioms StringTrace.endpoint
#print axioms StringTrace.borrowed_observation
#print axioms StringTrace.urls_unchanged
#print axioms StringTrace.location_capacity
#print axioms StringAdmission.encoded_length
#print axioms StringAdmission.generic_escape_output_bound
#print axioms StringAdmission.escape_output_bound
#print axioms StringAdmission.output_bound
#print axioms StringAdmission.owned_output_bound
#print axioms StringAdmission.raw_valid
#print axioms StringAdmission.quote_observer
#print axioms StringAdmission.raw_observer_reference
