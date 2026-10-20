import Origin
import Normalization
import Intervals
import Slices
import Chunks
import ByteSlices
import Output
import ScanOutput
import Fallback
import EmbeddedScan
import Repair
import FastPaths
import Closure

#print axioms VariableOrigin.byteLength_nil
#print axioms VariableOrigin.byteLength_append
#print axioms VariableOrigin.boundary_zero
#print axioms VariableOrigin.boundary_end
#print axioms VariableOrigin.boundary_le
#print axioms VariableOrigin.boundary_left
#print axioms VariableOrigin.boundary_right
#print axioms VariableOrigin.translated_zero
#print axioms VariableOrigin.translated_append
#print axioms VariableOrigin.translated_compose
#print axioms VariableOrigin.collector_layout
#print axioms VariableOrigin.translated_mem
#print axioms VariableOrigin.layout_boundary
#print axioms VariableOrigin.collected_common_origin
#print axioms VariableOrigin.collected_safe
#print axioms VariableOrigin.whitespace_partition
#print axioms VariableOrigin.strip_padding
#print axioms VariableOrigin.normalized_matches_reference
#print axioms VariableOrigin.normalized_text
#print axioms VariableOrigin.normalized_points_safe
#print axioms VariableOrigin.old_extra_shift
#print axioms VariableOrigin.old_out_of_bounds
#print axioms VariableOrigin.candidate_witness
#print axioms VariableOrigin.vertical_tab_retained
#print axioms VariableOrigin.nbsp_retained
#print axioms VariableOrigin.comment_prefix_retained
#print axioms VariableOrigin.spanPoints_shift
#print axioms VariableOrigin.flatMap_shift
#print axioms VariableOrigin.spans_layout
#print axioms VariableOrigin.shift_ordered
#print axioms VariableOrigin.spans_ordered
#print axioms VariableOrigin.span_boundaries
#print axioms VariableOrigin.bytes_zero_empty
#print axioms VariableOrigin.boundaries_make_slice
#print axioms VariableOrigin.constructed_reference_slice
#print axioms VariableOrigin.fallback_end_boundary
#print axioms VariableOrigin.constructed_fallback_slice
#print axioms VariableOrigin.outer_mem_all
#print axioms VariableOrigin.shifted_separated
#print axioms VariableOrigin.outer_separated
#print axioms VariableOrigin.ordered_scan_safe
#print axioms VariableOrigin.constructed_chunk_scan
#print axioms VariableOrigin.takeBytes_zero
#print axioms VariableOrigin.dropBytes_zero
#print axioms VariableOrigin.takeBytes_prefix
#print axioms VariableOrigin.dropBytes_prefix
#print axioms VariableOrigin.slice_exact
#print axioms VariableOrigin.safe_slice_decomposition
#print axioms VariableOrigin.append_projection
#print axioms VariableOrigin.output_history_refinement
#print axioms VariableOrigin.range_extend
#print axioms VariableOrigin.append_safe
#print axioms VariableOrigin.output_history_safe
#print axioms VariableOrigin.fresh_tainted_range
#print axioms VariableOrigin.empty_keeps_provenance
#print axioms VariableOrigin.nonempty_tainted_covered_after_suffix
#print axioms VariableOrigin.checked_success_safe
#print axioms VariableOrigin.reading_erases
#print axioms VariableOrigin.safe_scan_has_reading
#print axioms VariableOrigin.constructed_substitution_output
#print axioms VariableOrigin.failed_provider_no_publication
#print axioms VariableOrigin.fragment_left
#print axioms VariableOrigin.fragment_right
#print axioms VariableOrigin.fallback_fragment
#print axioms VariableOrigin.fallback_slice_content
#print axioms VariableOrigin.constructed_fallback_occurrence
#print axioms VariableOrigin.recursive_fallback_scan
#print axioms VariableOrigin.embedded_slice
#print axioms VariableOrigin.scan_embedding
#print axioms VariableOrigin.constructed_global_fallback_scan
#print axioms VariableOrigin.backslash_bytes
#print axioms VariableOrigin.terminal_raw_prefix
#print axioms VariableOrigin.terminal_repair_prefix
#print axioms VariableOrigin.repair_byte_length
#print axioms VariableOrigin.repair_normalized_endpoint
#print axioms VariableOrigin.no_padding_overlap
#print axioms VariableOrigin.direct_safe
#print axioms VariableOrigin.direct_payload_and_provenance
#print axioms VariableOrigin.direct_empty_taint
#print axioms VariableOrigin.direct_vs_append
#print axioms VariableOrigin.native_dispatch_safe
#print axioms VariableOrigin.whole_covers_only
#print axioms VariableOrigin.constructor_consumer_safety
#print axioms VariableOrigin.byte_not_character_offset
#print axioms VariableOrigin.skipped_comment_changes_source
#print axioms VariableOrigin.omitted_reset_changes_first_token
#print axioms VariableOrigin.empty_fallback_nonvacuous
#print axioms VariableOrigin.lookahead_same_epoch
