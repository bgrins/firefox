# Baseline sandbox interruption

The first baseline transaction stopped before browser execution. Mach could not open its environment lock, and the sandbox also denied the process-group inspection used by the runner. The runner retained backups and the temporary fixtures rather than claiming restoration. Its failure receipts remain unchanged.

Root then used an approved process inspection to verify wrapper PID 20788 and lint process group 20934 were absent. The complete 9,378-entry application inventory, three extras, source hashes, HEAD, index and clean tracked tree matched BEFORE.json. Each temporary fixture matched its frozen input before deletion. Source/test/config pins were rechecked, then owned backups and the stale transaction lock were removed. RECOVERY.json records the successful recovery. No build or browser result came from baseline1.

Baseline2 uses the identical frozen inputs with local Mach/process permissions. It is a fresh transaction, not a reinterpretation of the failed attempt.
