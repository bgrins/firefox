"use strict";

/* exported ExtensionTestUtils, AddonTestUtils */

var { AddonTestUtils } = ChromeUtils.importESModule(
  "resource://testing-common/AddonTestUtils.sys.mjs"
);

ChromeUtils.defineESModuleGetters(this, {
  ExtensionTestUtils:
    "resource://testing-common/ExtensionXPCShellUtils.sys.mjs",
});

// Disable https_first for tests since nsHttpServer doesn't support https
Services.prefs.setBoolPref("dom.security.https_first", false);

// Run extensions in-process for simpler testing
Services.prefs.setBoolPref("extensions.webextensions.remote", false);

ExtensionTestUtils.init(this);
