# Installed-release observations after the v25 checkpoint

This successor changes the observation HEAD and workspace epoch to 9abc806ef333f4cf9567ba28c3243ab9d9bc26e8 and e217c07f258532130bc286bd5944f9f0c2805ad794803f636ac84d44f36bbd72. The three intervening signed commits are checked against actual Git parents, trees, exact artifact-only paths and SSH signatures. Nonartifact pins, installed identities, parked state and the nested repository remain unchanged.

run.py, assess.py, all exact mixed16/lh16 fixture captures, resources, metadata, genuine manifest and the 110-entry external application inventory are byte-identical to v1 (e893c6/0). Existing parser and metadata controls are unchanged and their passing v1 results remain historical evidence; they were not represented as new execution. The necessary saved-state/external application binding checks passed 11a29f/0, including eight corruption controls. No browser, native build or wrapper main ran during preparation.

The browser is `/Applications/Firefox.app`: Firefox 158.0, BuildID 20261007201254, release SourceStamp eb9a6e3a736802c8e080a76c44dc81f409d99d54. The WPT run_info revision denotes the current harness checkout, not the browser source revision. Repository sources did not build this release binary. This is installed release under current WPT preferences and metadata, not a stock-default-profile claim.

The inherited private-profile, ephemeral-port, owned-process cleanup, full root/nested/index preservation and application bytes/identity checks remain unchanged. PASS and FAIL are observations; crashes, incomplete assertions or preservation failures fail the wrapper. There is no causal pair or native acceptance gate.

Run `python3 -I -S -B run.py CAPSULE_SHA observation-1 /Users/bgrins/code/firefox/artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json e217c07f258532130bc286bd5944f9f0c2805ad794803f636ac84d44f36bbd72 /Users/bgrins/code/firefox/artifacts/css-registered-provider-release-observation-runtime-1` with the sealed FILES.json digest. Root owns execution and a fresh outer log.
