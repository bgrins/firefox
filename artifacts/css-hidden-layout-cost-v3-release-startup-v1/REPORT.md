# Installed Firefox launcher diagnostic

The controlled-startup/progress launcher reaches all220 progress markers and returns one completed84-row observation in Firefox158. This establishes fixture execution for this attempt; it does not explain the prior combined local-build timeout. No performance result is accepted from this run.

Firefox invokes its installed updater and relaunches the exact owned profile in a new process group/session. The original group ends cleanly, but profile deletion fails with Directory not empty. The original RESULT remains rejected, with its cleanup error preserved. This is a concrete instance of the runner's documented escaped-session boundary.

Root subsequently identifies the relaunched Firefox by the exact owned profile command, verifies PID/birth/UID/group, and sends SIGTERM only to that process. A final inspection finds both owned groups empty and no Firefox naming that profile; the owned profile is then removed. These separate cleanup receipts do not retroactively turn the original run into a clean measurement.

The firefox and XUL binary hashes stay unchanged across the attempt. Updater xattr errors are retained; no claim is made about every installed application file or updater state. No further installed-Firefox run is authorized by this artifact. A successor must disable updates in its isolated test profile using the implementation's test preference, while preserving strict cleanup gates. No production source, native fix or Git mutation occurs here.
