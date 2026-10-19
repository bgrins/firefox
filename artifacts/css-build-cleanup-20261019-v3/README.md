# Completed parser replay cleanup

Removed the completed public-history replay output after authenticating its 300-file inventory, confirming no matching process or open file, and checking it contains no tracked files. The sealed source, producer receipts and independent replay evidence remain. All 761 retained files are unchanged.

Removed 42,392,381 logical bytes / 42,056 KiB of allocated outputs. This is output size, not a measurement of net filesystem free-space change. Exact paths, pins and checks are in PREDELETE.json, RETAINED-PINS.json and RESULT.json. The active wrapper work and Firefox object directories were retained.
