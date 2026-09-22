# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Generate the Info.plist of an iOS bundle: the keys every bundle needs, plus
# the keys specific to it from a partial Info.plist.

import plistlib

import buildconfig


def _write(output, package_type, executable, bundle_id, extra):
    simulator = buildconfig.substs.get("IPHONEOS_IS_SIMULATOR")
    values = {
        "CFBundleDevelopmentRegion": "en",
        "CFBundleExecutable": executable,
        "CFBundleIdentifier": bundle_id,
        "CFBundleInfoDictionaryVersion": "6.0",
        "CFBundleName": executable,
        "CFBundlePackageType": package_type,
        "CFBundleShortVersionString": "1.0",
        "CFBundleSupportedPlatforms": ["iPhoneSimulator" if simulator else "iPhoneOS"],
        "CFBundleVersion": "1",
        "DTPlatformName": "iphonesimulator" if simulator else "iphoneos",
        "MinimumOSVersion": buildconfig.substs["IPHONEOS_DEPLOYMENT_TARGET"],
        "UIDeviceFamily": [1, 2],
    }
    values.update(extra)
    plistlib.dump(values, output, sort_keys=True)


def _load(source, executable):
    with open(source, "rb") as fh:
        text = fh.read()
    return plistlib.loads(text.replace(b"$(PRODUCT_MODULE_NAME)", executable.encode()))


def app(output, source, executable, bundle_id):
    extra = {
        "LSRequiresIPhoneOS": True,
        # An empty UILaunchScreen gives the blank launch screen a storyboard
        # would, without needing ibtool to compile one.
        "UILaunchScreen": {},
    }
    extra.update(_load(source, executable))
    _write(output, "APPL", executable, bundle_id, extra)


def extension(output, source, executable, bundle_id):
    _write(output, "XPC!", executable, bundle_id, _load(source, executable))


def framework(output, executable, bundle_id):
    _write(output, "FMWK", executable, bundle_id, {})
