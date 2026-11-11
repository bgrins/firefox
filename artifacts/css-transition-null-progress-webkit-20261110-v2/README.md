# Unsuccessful system WebKit comparison

A small Swift/AppKit harness attempted to run the existing standalone transition probe in a non-persistent WKWebView. Compilation succeeded; execution timed out after 30 seconds and exited 1. No engine behavior result is available.

Revision 2 explicitly completed AppKit launch and activated the window. Its timeout reported phase executing, loading false, window visible true and occlusion visible false. This is consistent with an occluded animation-frame wait, but does not identify which JavaScript await remained pending. No scheduling override or synthetic animation-frame callback was used.

The source, compiler log, timeout result and binary hash are retained. Owned binaries/module-cache directories were removed after terminal execution. This is failed harness evidence, not a Safari/WebKit conformance result and not an additional Firefox bug.
