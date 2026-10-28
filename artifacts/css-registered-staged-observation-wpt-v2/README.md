# Container and provider-readiness observations

This successor runs the same two captured WPT pages as the disabled archive: 16 unzoomed-source container controls and 16 writing-mode provider-readiness assertions. All completed PASS and FAIL results are observations; this is not a causal pair or native acceptance gate.

The ordinary preservation guard requires clean staging and preserves actual source, binary, inode, index and nested-repository state before and after execution. The headless lifecycle retains raw logs, automatic server ports, private temporary profiles and owned-process cleanup. No live test installation, signing, index update or epoch rewrite occurs.

The compiled build remains the actual candidate build at HEAD d6243f35307b62a4a4f6067367d78c948d3f468c and epoch2428aabb. The observation uses signed HEAD749b1227b09bee3adfac517e49de87d0fb2b89de and synchronized epoch09d8cbe0. `bindings.py` verifies the five actual signed artifact-only successor commits and requires identical non-artifact source/binary/configuration pins, installed identities and compiled role. Build metadata is not relabeled: `PHASE-BINDING.json` records historical build and current observation revisions separately; application.ini bytes, identity and BuildID remain bound before and after the run.

The genuine manifest contains exactly two harness pages and 32 named assertions. Fixture, resource, metadata and manifest inputs are byte-identical to the disabled predecessor. `CONTROLS.json` records two positive observation cases and 44 rejection cases. `CHECK.json` records actual signature/continuity and ordinary preservation validation plus 12 binding corruptions rejected. These checks did not launch a browser or mutate live state.

Root invokes `run.py` with the sealed manifest SHA, `observation-1`, absolute current epoch path, epoch SHA and an absent absolute output directory directly under `artifacts` whose name starts `css-registered-staged-observation-wpt-runtime-`. Any later signing or source transition requires a reviewed successor. The former pending207 staged-state guard is absent and is not projected into this execution.
