# Capacity build header comparison

The completed original and candidate builds produced identical `ServoStyleConsts.h` bytes: SHA-256 `ce92a682ea254c2fd02d21cc66fe607d3e9d7c5701e72427b720c3ea72ada03c`, 910,719 bytes. The header is stored once as `original-during-build.h`; the later observations independently matched it after each build command completed successfully. Duplicate copies were removed after exact byte comparison.

Root captured the completed original while the original cascade source was still installed (16099b), and the completed candidate while the u32 candidate was installed (22684d). The records pin each source and its actual build result. The earlier in-build observation is retained as historical provenance, not substituted for the completed checks.

The original build log reports 1,335 seconds; the following candidate build reports 54 seconds. This is an incremental-build observation on this checkout, not a benchmark or a prediction for clean builds. Unchanged generated-header bytes explain why this particular edit did not require another broad C++ recompilation; they do not measure browser performance or prove native layout equivalence. Browser acceptance and restoration are separate obligations.
