import ProtectedSpan
import PreservationGuard
import ProtectedMetadata
import ProtectedBoundary
import ProtectedWitnesses
#print axioms ProtectedSpan.scan_append
#print axioms ProtectedSpan.scan_previous
#print axioms ProtectedSpan.split_partition
#print axioms ProtectedSpan.suffix_partition
#print axioms ProtectedSpan.retained_partition
#print axioms ProtectedSpan.split_white
#print axioms ProtectedSpan.split_coalesced
#print axioms ProtectedSpan.trailing_reference
#print axioms ProtectedSpan.removed_extent
#print axioms ProtectedSpan.bytes_append
#print axioms ProtectedSpan.exact_prefix
#print axioms ProtectedSpan.trim_bound
#print axioms ProtectedSpan.persistent_from
#print axioms ProtectedSpan.split_head
#print axioms ProtectedSpan.basePrefix_last
#print axioms ProtectedSpan.persistent_prefix
#print axioms ProtectedSpan.guard_with_suffix
#print axioms ProtectedSpan.standalone_guard
#print axioms ProtectedSpan.followed_terminal
#print axioms ProtectedSpan.admitted_standalone_guard
#print axioms ProtectedSpan.protected_extent_zero
#print axioms ProtectedSpan.protected_bytes
#print axioms ProtectedSpan.ordinary_reset
#print axioms ProtectedSpan.scan_first
#print axioms ProtectedSpan.scan_last
#print axioms ProtectedSpan.scan_nonwhite
#print axioms ProtectedSpan.suffix_white
#print axioms ProtectedSpan.basePrefix_first
#print axioms ProtectedSpan.metadata_first
#print axioms ProtectedSpan.suffix_last_white
#print axioms ProtectedSpan.metadata_last
#print axioms ProtectedSpan.stored_observations
#print axioms ProtectedSpan.initial_ready
#print axioms ProtectedSpan.trailing_nonwhite
#print axioms ProtectedSpan.repaired_no_trim
#print axioms ProtectedSpan.finish_partition
#print axioms ProtectedSpan.retained_slice
#print axioms ProtectedSpan.adjacent_backslash_keeps_whitespace
#print axioms ProtectedSpan.protected_component
#print axioms ProtectedSpan.Witnesses.lf_is_saved
#print axioms ProtectedSpan.Witnesses.crlf_is_saved
#print axioms ProtectedSpan.Witnesses.whole_run_is_saved
#print axioms ProtectedSpan.Witnesses.old_trim_loses_required_newline
#print axioms ProtectedSpan.Witnesses.saved_suffix_metadata
#print axioms ProtectedSpan.Witnesses.same_class_different_lexical_role
#print axioms ProtectedSpan.Witnesses.final_flags_are_not_equal
#print axioms ProtectedSpan.Witnesses.coalescing_is_required
#print axioms ProtectedSpan.Witnesses.terminal_backslash_guard_counterexample
#print axioms ProtectedSpan.Witnesses.integration_preserves_escaped_space
#print axioms ProtectedSpan.Witnesses.standalone_still_has_prior_bug
#print axioms ProtectedSpan.Witnesses.comment_resets_protection
#print axioms ProtectedSpan.Witnesses.outer_block_resets_protection
#print axioms ProtectedSpan.Witnesses.eof_ident_is_distinct
