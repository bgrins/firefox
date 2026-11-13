# High-bit domain target v2: notation repair

The only Lean source change replaces unsupported unique-existence notation with explicit existence plus uniqueness of the same admissible class. target.patch and AMENDMENT.json pin both spans and the exact inverse. All fifteen obligation fields and six control fields are retained; Controls.lean and Types.lean are byte-identical to v1. Tail/context/UTF-8 boundaries are unchanged.

The original v1 target and failed definition attempt remain frozen, including the parser diagnostic and fresh process-group absence. Root approved this source-only repair before preparation. No successor Lean command or proof has run. Source authentication does not supply parsed types; the successor definition gate remains subject to separate review and explicit lane release.
