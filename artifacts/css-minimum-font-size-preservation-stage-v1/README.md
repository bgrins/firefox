# Minimum-size preservation staging

This stages the two immutable css-minimum-font-size-preservation-probe-v1 pages without changing HTML, JavaScript, preferences or oracles. The existing manifest/lint preparer now loads the shared script into an inert Node context with the page's off/on dataset; test callbacks are collected, not executed. Actual preparation129c89/0 produced a genuine explicit-file WPT manifest, seven distinct callbacks per page and zero upstream path/content lint findings for both pages and the shared JavaScript.

The manifest correctly retains timeout:long for both pages and classifies the shared script as support. INPUTS.json pins exact resources, the manifest, preference profiles and two metadata files. Future lanes must select one page each and stage its explicit preferences; calibration callbacks test whether the intended minimum preference took effect. The stage is not a browser result or a new native acceptance. No live WPT install, Mach, browser, Git or source change occurred.

PREPARE-DELTA.patch preserves the bounded adaptation of the existing preparer. REFERENCES.json authenticates all original resources and the sealed source package. The original harness limitations, including ordinary references sharing common metric defects and unproved pre-ensured-ratio reachability, are unchanged.
