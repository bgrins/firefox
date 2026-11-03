# Candidate archive after its first browser startup

The verified candidate archive ran the unchanged four supplemental cases through the Firefox connector. All four matched expectations: both selected-empty custom-value cases now reject the URL, while direct adjacent-URL and unused-fallback controls stay valid. All empty calibrations computed3px, all literal/feature/standards/absent-attribute controls passed, and all iframes were removed. The connector was closed and configured back to installed Firefox.

Browser startup consumed exactly one archive file: Contents/Resources/browser/.purgecaches, whose recorded content was a single newline. Root did not remove or rewrite any archive file. Every other retained path has its exact pre-startup hash, size and mode; there are no added files or symlinks. The ready archive has8326 files/819801859 bytes. The pre-startup snapshot remains unchanged and separately sealed. SNAPSHOT.json carries the same build receipt, candidate source and application metadata, plus this explicit one-file startup transition.

This ready snapshot is the strict before/after inventory for the upcoming combined28 WPT runs. The four standalone observations are supplemental evidence, not a substitute for that harness validation. Retain only for those checks and remove the exact owned parent once no longer needed. Browser binaries remain outside the repository.
