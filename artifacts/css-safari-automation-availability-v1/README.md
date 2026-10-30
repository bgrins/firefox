# Safari automation availability

Actual probe 47807/de74e5/1 reached the owned driver, but Safari rejected session creation with HTTP 500 because Allow remote automation is disabled. No fixture, expression-support probe, or browser-behavior comparison ran. No preference was changed. The owned driver exited and its process group was verified absent.

The existing Firefox descendant investigation proceeds independently. An actual Safari comparison requires automation to be enabled separately; this result says nothing about CSS timing behavior or expression support. Do not rerun this completed probe merely because the driver status endpoint said ready: session admission failed afterward.

The saved probe creates only an owned localhost driver and automation session, deletes its own session if admitted, and stops its driver group. It does not enable settings, install software, or terminate unrelated Safari instances. This directory is a completed run; any future attempt needs a fresh output directory and current authorization/context.
