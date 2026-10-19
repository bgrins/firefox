# Identifier round-trip isolation

All 36 diagnostic checks pass on the existing shared experimental build:
33 constructed-sheet cases (11 rule forms, three identifiers) and three import
layer cases that wait for their own stylesheet load/error events. Each initial
and reparsed rule must be accepted before comparing serialized text.

This isolates ordinary and escaped identifiers from the original test's
stylesheet-update timing. It does not prove all serializers correct, validate
rendering, or establish all input grammars. The original test's exact corpus is
retained in the separate final test correction. No native defect is inferred.
Pinned source, configuration, resources and binaries remain unchanged during
the run. The temporary WPT copy was removed after exact-byte verification.
