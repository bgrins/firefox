# Frozen animation-taint follow-up suite

This package combines the six inherited/nested-fallback controls with the four direct-attr WPT V2 callbacks. All three HTML bodies and both shared harness bodies are exact copies of their sealed sources. The explicit-body correction in direct-attr V2 is retained. Common harness files occur once.

INPUTS.json, ROSTER.json and MANIFEST.json describe ten callbacks, three pages, thirteen callback/page-ending signatures and five resources. The manifest merges the original genuine WPT entries without changing their blob IDs or item metadata. No JavaScript, assertions, callback names or observations were changed. Existing fixture static checks remain applicable; assembly checks authenticate exact bytes and manifest membership.

UNION-ROSTER.json, UNION-MANIFEST.json and UNION.json separately describe appending these pages to the original 106-case suite: 116 callbacks, fifteen pages, 131 signatures and nineteen resources. The nineteen include the existing two harness header files. All old page names, callback names, resource bodies and metadata descriptors remain unchanged. This is a resource/roster union, not a changed expectation set: no prior PASS or FAIL is relabeled and no new expected status is supplied.

The package has no execution owner, browser result or current-state binding. A future root-owned original admission must freshly verify source/application state after restoration, preserve inherited metadata checks, and add appropriate absent-metadata checks for the three authored pages. Saved null metadata hashes are historical absence descriptors, not new live filesystem assertions. Candidate comparison must use that fresh original observation rather than assume these new callbacks pass.

Source manifests are cde8220e (inherited/fallback), 01421530 (direct-attr V2), and the completed original owner manifest 29df9173. REFERENCES.json pins the exact saved inputs. All work is artifact-only; no native, browser, process, Git, control or live epoch operation was performed.
