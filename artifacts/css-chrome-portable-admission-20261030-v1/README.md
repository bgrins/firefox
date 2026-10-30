# Portable Chrome admission

Downloaded official pinned Chrome for Testing and ChromeDriver 156.0.8078.80 into an owned temporary directory. Both archive sizes and published transport MD5 values match; SHA-256 hashes and archive path/symlink checks are recorded. Extraction preserved the distributions unchanged.

The initial plan incorrectly required publisher signatures for this distribution. Actual checks found ad-hoc signatures, no TeamIdentifier, a failed outer-app resource-signature check, and Gatekeeper assessment rejection. These findings remain failures in SIGNATURE-CHECKS.json. The [Chrome for Testing maintainer](https://github.com/GoogleChromeLabs/chrome-for-testing/issues/175) states that the distribution is not signed. ADMISSION-DECISION.json records the revised choice to use the pinned official HTTPS distribution for this isolated test; no publisher signature verification is claimed.

Root version execution 27671/a31325/0 succeeded for both untouched binaries. No quarantine attributes, signatures, Gatekeeper settings or browser sandbox settings were changed. No browser profile or CSS test was opened by these version queries. Browser execution for the comparison belongs to the separate runner and requires its actual result; version success is not CSS evidence.

Actual download 56233/13a852/0; extraction 57953/056717/0; signature checks 2271/338c1d/0 (individual failures preserved). No application was installed in /Applications. OWNER.json identifies the temporary directory; retain it until the comparison finishes, then remove the owned files with a cleanup receipt. Binaries and archives are excluded from Git.
